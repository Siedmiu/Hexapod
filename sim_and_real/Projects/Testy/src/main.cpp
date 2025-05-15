// IMU sensor and servo control with WebSocket interface and optimized Serial IMU data
// Uses Jeff Rowberg's I2Cdev and MPU6050 libraries (MIT license)
// https://www.i2cdevlib.com/

#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

// WiFi credentials
const char* ssid = "FlyBozon";
const char* password = "12345678";

// Two PCA9685 drivers
Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(0x40);  // first board
Adafruit_PWMServoDriver pwm2 = Adafruit_PWMServoDriver(0x41);  // second board

const int SERVO_MIN = 102;
const int SERVO_MAX = 512;

// WebSocket server
AsyncWebServer server(80);
AsyncWebSocket ws("/");

// MPU control
MPU6050 mpu;
bool dmpReady = false;  // true if DMP init was successful
uint8_t mpuIntStatus;   // holds interrupt status
uint8_t devStatus;      // status after each device operation
uint16_t packetSize;    // DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// Orientation, motion variables
Quaternion q;           // [w, x, y, z]
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free compensated accel
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]
float ypr[3];           // [yaw, pitch, roll]   Euler angles in radians

// Sensor settle time
unsigned long startTime = 0;
bool initialPeriodComplete = false;
const unsigned long INITIAL_PERIOD_MS = 5000;  // Reduced to 5 seconds for faster startup

// IMU data publish rate
unsigned long lastImuPublish = 0;
const unsigned long IMU_PUBLISH_INTERVAL_MS = 100;  // 10Hz publish rate

// Serial IMU data publish rate
unsigned long lastSerialImuPublish = 0;
const unsigned long SERIAL_IMU_PUBLISH_INTERVAL_MS = 100;  // 10Hz publish rate

// Threshold for data filtering
const float MOTION_THRESHOLD = 0.01;  // Threshold for change detection

// Variables to track previous values
float prev_qw = 0, prev_qx = 0, prev_qy = 0, prev_qz = 0;
float prev_roll = 0, prev_pitch = 0, prev_yaw = 0;
float prev_accel_x = 0, prev_accel_y = 0, prev_accel_z = 0;
bool first_reading = true;

// MPU interrupt detection
volatile bool mpuInterrupt = false;
void IRAM_ATTR dmpDataReady() {
    mpuInterrupt = true;
}

// Function prototypes
void calibrateMPU6050();
void setServoAngle(uint8_t servoIndex, float angle);
void onWebSocketMessage(void *arg, uint8_t *data, size_t len);
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
             AwsEventType type, void *arg, uint8_t *data, size_t len);
void sendImuData();
void sendSerialImuData();
void processImuData();

void setup() {
    Serial.begin(115200);
    // Don't wait for Serial in production
    delay(1000);

    // Initialize I2C for MPU6050
    Wire.begin(21, 22); // SDA, SCL pins for IMU
    Wire.setClock(400000); // 400kHz

    // Initialize the two servo drivers
    pwm1.begin();
    pwm1.setPWMFreq(60);
    pwm2.begin();
    pwm2.setPWMFreq(60);
    Serial.println("Both PCA9685 initialized.");

    // Initialize MPU6050
    Serial.println("Initializing MPU6050...");
    mpu.initialize();
    Serial.println("Testing device connections...");
    Serial.println(mpu.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");
    Serial.println("Initializing DMP...");
    devStatus = mpu.dmpInitialize();
    
    // Initialize offsets before calibration
    mpu.setXGyroOffset(0);
    mpu.setYGyroOffset(0);
    mpu.setZGyroOffset(0);
    mpu.setXAccelOffset(0);
    mpu.setYAccelOffset(0);
    mpu.setZAccelOffset(0);
    
    // DMP initialization check
    if (devStatus == 0) {
        // Uncomment to enable calibration
        // Serial.println("Calibrating MPU6050...");
        // calibrateMPU6050();
        
        Serial.println("Enabling DMP...");
        mpu.setDMPEnabled(true);
        
        // Enable interrupt detection
        Serial.println("Enabling interrupt detection (ESP32 pin 19)...");
        attachInterrupt(19, dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();
        
        Serial.println("DMP ready! Waiting for first interrupt...");
        dmpReady = true;
        
        // Get packet size
        packetSize = mpu.dmpGetFIFOPacketSize();

        // Start settle time countdown
        startTime = millis();
        Serial.println("Waiting for the sensor to settle...");
    } else {
        // ERROR!
        Serial.print("DMP Initialization failed (code ");
        Serial.print(devStatus);
        Serial.println(")");
    }

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    
    // Wait for WiFi connection with a timeout
    int wifiTimeout = 0;
    while (WiFi.status() != WL_CONNECTED && wifiTimeout < 20) {
        delay(500);
        Serial.print(".");
        wifiTimeout++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected.");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());

        // Setup WebSocket server
        ws.onEvent(onEvent);
        server.addHandler(&ws);
        server.begin();
    } else {
        Serial.println("\nWiFi connection failed, continuing without WiFi.");
    }

    // Initialize servo positions
    for (int i = 0; i < 18; i++) {
        if (i % 3 == 0) setServoAngle(i, 90);  // 90
        if (i % 3 == 1) setServoAngle(i, 120); // 150
        if (i % 3 == 2) setServoAngle(i, 30);  // 180
    }
    setServoAngle(2, 180);
    setServoAngle(14, 180);
    
    // Print header for serial IMU data
    Serial.println("IMU_DATA_START");
    Serial.println("F,timestamp,qw,qx,qy,qz,roll,pitch,yaw,accel_x,accel_y,accel_z");
}

void loop() {
    // Check if MPU is ready
    if (!dmpReady) return;
    
    // Wait for MPU interrupt or extra packet(s) available
    if (!mpuInterrupt && fifoCount < packetSize) {
        // Check if it's time to publish IMU data to WebSocket
        if (initialPeriodComplete && (millis() - lastImuPublish >= IMU_PUBLISH_INTERVAL_MS)) {
            // Send last valid IMU data to WebSocket
            sendImuData();
            lastImuPublish = millis();
        }
        
        // Check if it's time to publish IMU data to Serial
        if (initialPeriodComplete && (millis() - lastSerialImuPublish >= SERIAL_IMU_PUBLISH_INTERVAL_MS)) {
            // Send last valid IMU data to Serial
            sendSerialImuData();
            lastSerialImuPublish = millis();
        }
        return;
    }
    
    // Reset interrupt flag
    mpuInterrupt = false;
    mpuIntStatus = mpu.getIntStatus();

    // Check if initial period is complete
    if (!initialPeriodComplete && (millis() - startTime > INITIAL_PERIOD_MS)) {
        initialPeriodComplete = true;
        Serial.println("INIT_COMPLETE");
    }

    // Check for FIFO overflow
    fifoCount = mpu.getFIFOCount();
    if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
        mpu.resetFIFO();
        Serial.println("FIFO overflow!");
    
    } else if (mpuIntStatus & 0x02) {
        // Wait for correct packet size
        while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();
        
        // Read packet from FIFO
        mpu.getFIFOBytes(fifoBuffer, packetSize);
        fifoCount -= packetSize;
        
        // Process IMU data
        processImuData();
        
        // Send IMU data if initialization period is complete
        if (initialPeriodComplete) {
            // Check if it's time to publish to WebSocket
            if (millis() - lastImuPublish >= IMU_PUBLISH_INTERVAL_MS) {
                sendImuData();
                lastImuPublish = millis();
            }
            
            // Check if it's time to publish to Serial
            if (millis() - lastSerialImuPublish >= SERIAL_IMU_PUBLISH_INTERVAL_MS) {
                sendSerialImuData();
                lastSerialImuPublish = millis();
            }
        }
    }
}

void processImuData() {
    // Get all motion data from DMP
    mpu.dmpGetQuaternion(&q, fifoBuffer);
    mpu.dmpGetGravity(&gravity, &q);
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
    mpu.dmpGetAccel(&aa, fifoBuffer);
    mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
    mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
}

void sendSerialImuData() {
    // Calculate current values
    float current_roll = ypr[2] * 180/M_PI;
    float current_pitch = ypr[1] * 180/M_PI;
    float current_yaw = ypr[0] * 180/M_PI;
    float current_accel_x = aaWorld.x / 16384.0;
    float current_accel_y = aaWorld.y / 16384.0;
    float current_accel_z = aaWorld.z / 16384.0;
    
    // Check if data has changed significantly from previous readings
    bool significant_change = first_reading ||
        abs(q.w - prev_qw) > MOTION_THRESHOLD ||
        abs(q.x - prev_qx) > MOTION_THRESHOLD ||
        abs(q.y - prev_qy) > MOTION_THRESHOLD ||
        abs(q.z - prev_qz) > MOTION_THRESHOLD ||
        abs(current_roll - prev_roll) > MOTION_THRESHOLD * 10 ||
        abs(current_pitch - prev_pitch) > MOTION_THRESHOLD * 10 ||
        abs(current_yaw - prev_yaw) > MOTION_THRESHOLD * 10 ||
        abs(current_accel_x - prev_accel_x) > MOTION_THRESHOLD * 2 ||
        abs(current_accel_y - prev_accel_y) > MOTION_THRESHOLD * 2 ||
        abs(current_accel_z - prev_accel_z) > MOTION_THRESHOLD * 2;
    
    // Send data only if there's a significant change
    if (significant_change) {
        // Update previous values
        prev_qw = q.w; prev_qx = q.x; prev_qy = q.y; prev_qz = q.z;
        prev_roll = current_roll; prev_pitch = current_pitch; prev_yaw = current_yaw;
        prev_accel_x = current_accel_x; prev_accel_y = current_accel_y; prev_accel_z = current_accel_z;
        first_reading = false;
        
        // Format: F,timestamp,qw,qx,qy,qz,roll,pitch,yaw,accel_x,accel_y,accel_z
        Serial.print("F,");  // Prefix to indicate filtered data
        Serial.print(millis());
        Serial.print(",");
        
        // Quaternion (reduced precision to save bandwidth)
        Serial.print(q.w, 4);  // Reduced precision from 6 to 4 decimal places
        Serial.print(",");
        Serial.print(q.x, 4);
        Serial.print(",");
        Serial.print(q.y, 4);
        Serial.print(",");
        Serial.print(q.z, 4);
        Serial.print(",");
        
        // Euler angles (reduced precision)
        Serial.print(current_roll, 1); // Reduced precision from 2 to 1 decimal places
        Serial.print(",");
        Serial.print(current_pitch, 1);
        Serial.print(",");
        Serial.print(current_yaw, 1);
        Serial.print(",");
        
        // Linear acceleration (reduced precision)
        Serial.print(current_accel_x, 2);  // Reduced precision from 4 to 2 decimal places
        Serial.print(",");
        Serial.print(current_accel_y, 2);
        Serial.print(",");
        Serial.print(current_accel_z, 2);
        
        Serial.println();
    }
}

void sendImuData() {
    // Only send data over WebSocket if connected to WiFi
    if (WiFi.status() != WL_CONNECTED) return;
    
    // Calculate current values for use in threshold check
    float current_roll = ypr[2] * 180/M_PI;
    float current_pitch = ypr[1] * 180/M_PI;
    float current_yaw = ypr[0] * 180/M_PI;
    float current_accel_x = aaWorld.x / 16384.0;
    float current_accel_y = aaWorld.y / 16384.0;
    float current_accel_z = aaWorld.z / 16384.0;
    
    // Check for significant change (same logic as serial)
    bool significant_change = first_reading ||
        abs(q.w - prev_qw) > MOTION_THRESHOLD ||
        abs(q.x - prev_qx) > MOTION_THRESHOLD ||
        abs(q.y - prev_qy) > MOTION_THRESHOLD ||
        abs(q.z - prev_qz) > MOTION_THRESHOLD ||
        abs(current_roll - prev_roll) > MOTION_THRESHOLD * 10 ||
        abs(current_pitch - prev_pitch) > MOTION_THRESHOLD * 10 ||
        abs(current_yaw - prev_yaw) > MOTION_THRESHOLD * 10 ||
        abs(current_accel_x - prev_accel_x) > MOTION_THRESHOLD * 2 ||
        abs(current_accel_y - prev_accel_y) > MOTION_THRESHOLD * 2 ||
        abs(current_accel_z - prev_accel_z) > MOTION_THRESHOLD * 2;
    
    // Only send if there's a significant change
    if (significant_change) {
        // Create JSON string formatted similar to ROS IMU message
        String imuJson = "{\"imu\":{";
        
        // Add timestamp
        imuJson += "\"header\":{\"stamp\":" + String(millis()) + "},";
        
        // Add orientation (quaternion)
        imuJson += "\"orientation\":{\"x\":" + String(q.x, 4) + 
                   ",\"y\":" + String(q.y, 4) + 
                   ",\"z\":" + String(q.z, 4) + 
                   ",\"w\":" + String(q.w, 4) + "},";
        
        // Add orientation_covariance (simplified)
        imuJson += "\"orientation_covariance\":[0.01,0,0,0,0.01,0,0,0,0.01],";
        
        // Add angular_velocity (calculated from ypr differences - simplified)
        imuJson += "\"angular_velocity\":{\"x\":" + String(ypr[2], 4) + 
                   ",\"y\":" + String(ypr[1], 4) + 
                   ",\"z\":" + String(ypr[0], 4) + "},";
        
        // Add angular_velocity_covariance (simplified)
        imuJson += "\"angular_velocity_covariance\":[0.01,0,0,0,0.01,0,0,0,0.01],";
        
        // Add linear_acceleration (world frame, gravity compensated)
        imuJson += "\"linear_acceleration\":{\"x\":" + String(current_accel_x, 4) + 
                   ",\"y\":" + String(current_accel_y, 4) + 
                   ",\"z\":" + String(current_accel_z, 4) + "},";
        
        // Add linear_acceleration_covariance (simplified)
        imuJson += "\"linear_acceleration_covariance\":[0.01,0,0,0,0.01,0,0,0,0.01]";
        
        // Close JSON
        imuJson += "}}";
        
        // Send over WebSocket
        ws.textAll(imuJson);
    }
}

void calibrateMPU6050() {
    const int numSamples = 2000;  // Number of samples for calibration
    const int settleTime = 2000;  // Settling delay
    
    // Calibration sums
    int32_t ax_sum = 0, ay_sum = 0, az_sum = 0;
    int32_t gx_sum = 0, gy_sum = 0, gz_sum = 0;
    
    Serial.println("Collecting calibration samples...");
    for (int i = 0; i < numSamples; i++) {
        int16_t ax, ay, az, gx, gy, gz;
        mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
        
        ax_sum += ax;
        ay_sum += ay;
        az_sum += az;
        gx_sum += gx;
        gy_sum += gy;
        gz_sum += gz;
        
        delay(2);
    }
    
    int16_t ax_mean = ax_sum / numSamples;
    int16_t ay_mean = ay_sum / numSamples;
    int16_t az_mean = az_sum / numSamples;
    int16_t gx_mean = gx_sum / numSamples;
    int16_t gy_mean = gy_sum / numSamples;
    int16_t gz_mean = gz_sum / numSamples;
    
    // Set offsets
    mpu.setXAccelOffset(-ax_mean);
    mpu.setYAccelOffset(-ay_mean);
    mpu.setZAccelOffset(-az_mean);
    mpu.setXGyroOffset(-gx_mean);
    mpu.setYGyroOffset(-gy_mean);
    mpu.setZGyroOffset(-gz_mean);
    
    Serial.println("Calibration complete!");
    delay(100);
}

// Set angle for specific servo (0-17)
void setServoAngle(uint8_t servoIndex, float angle) {
    angle = constrain(angle, 0, 180);
    uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);

    if (servoIndex >= 0 && servoIndex < 9) {
        pwm1.setPWM(servoIndex, 0, pulse);  // channels 0-8
    } else if (servoIndex >= 9 && servoIndex < 18) {
        pwm2.setPWM(servoIndex - 9, 0, pulse);  // channels 0-8 on second board
    } else {
        Serial.println("Invalid servo index.");
    }
}

void onWebSocketMessage(void *arg, uint8_t *data, size_t len) {
    AwsFrameInfo *info = (AwsFrameInfo*)arg;

    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
        String msg = String((char*)data);
        msg.trim();

        if (msg.startsWith("servo")) {
            int spaceIndex = msg.indexOf(' ');
            if (spaceIndex != -1) {
                String servoStr = msg.substring(5, spaceIndex);
                String angleStr = msg.substring(spaceIndex + 1);

                int servoNum = servoStr.toInt();  // servos 1-18
                int angle = angleStr.toInt();

                if (servoNum >= 1 && servoNum <= 18 && angle >= 0 && angle <= 180) {
                    setServoAngle(servoNum - 1, angle);  // indexed from 0
                    Serial.printf("Servo %d moved to %d°\n", servoNum, angle);
                } else {
                    Serial.println("Invalid servo number or angle.");
                }
            } else {
                Serial.println("Invalid command format.");
            }
        } else if (msg.startsWith("imu_req")) {
            // Send latest IMU data on demand
            if (initialPeriodComplete) {
                sendImuData();
            } else {
                ws.textAll("{\"error\":\"IMU still initializing\"}");
            }
        } else {
            Serial.println("Unknown command.");
        }
    }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
             AwsEventType type, void *arg, uint8_t *data, size_t len) {
    if (type == WS_EVT_CONNECT) {
        Serial.printf("Client connected: %u\n", client->id());
    } else if (type == WS_EVT_DISCONNECT) {
        Serial.printf("Client disconnected: %u\n", client->id());
    } else if (type == WS_EVT_DATA) {
        onWebSocketMessage(arg, data, len);
    }
}