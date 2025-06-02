//uses Jeff Rowberg's I2Cdev and MPU6050 libraries which are open source and MIT licence
//https://www.i2cdevlib.com/

#include <Wire.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

void calibrateMPU6050(); //not used currently
void sendDataToSerial();

//MPU control
MPU6050 mpu;
bool dmpReady = false;  //true if DMP init was successful
uint8_t mpuIntStatus;   //holds interrupt status
uint8_t devStatus;      //status after each device operation
uint16_t packetSize;    //DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation, motion
Quaternion q;           // [w, x, y, z]
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free compensated accel
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]
float ypr[3];           // [yaw, pitch, roll]

//sensor settle time
unsigned long startTime = 0;
bool initialPeriodComplete = false;
const unsigned long INITIAL_PERIOD_MS = 17000;

//MPU interrupt detection
volatile bool mpuInterrupt = false;
void IRAM_ATTR dmpDataReady() {
    mpuInterrupt = true;
}

void setup() {
    Serial.begin(115200);
    while (!Serial);

    //I2C
    Wire.begin(26, 25); // SDA, SCL pins, define as constants
    Wire.setClock(400000); //400kHz

    Serial.println("Initializing MPU6050...");
    mpu.initialize();
    Serial.println("Testing device connections...");
    Serial.println(mpu.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");
    Serial.println("Initializing DMP...");
    devStatus = mpu.dmpInitialize();
    
    //initialize ofsets before callibration
    mpu.setXGyroOffset(0);
    mpu.setYGyroOffset(0);
    mpu.setZGyroOffset(0);
    mpu.setXAccelOffset(0);
    mpu.setYAccelOffset(0);
    mpu.setZAccelOffset(0);
    
    //DMP initialization check
    if (devStatus == 0) {
        //Serial.println("Calibrating MPU6050...");
        //calibrateMPU6050();
        Serial.println("Enabling DMP...");
        mpu.setDMPEnabled(true);
        
        //enable interrupt detection
        Serial.println("Enabling interrupt detection (ESP32 pin 27)...");
        attachInterrupt(27, dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();
        
        Serial.println("DMP ready! Waiting for first interrupt...");
        dmpReady = true;
        
        // get packet size
        packetSize = mpu.dmpGetFIFOPacketSize();

        //settle time
        startTime = millis();
        Serial.println("Waiting for the sensor to settle...");
    } else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        Serial.print("DMP Initialization failed (code ");
        Serial.print(devStatus);
        Serial.println(")");
    }
}

void loop() {
    if (!dmpReady) return;
    if (!mpuInterrupt && fifoCount < packetSize) return;
    
    mpuInterrupt = false;
    mpuIntStatus = mpu.getIntStatus();

    if (!initialPeriodComplete && (millis() - startTime > INITIAL_PERIOD_MS)) {
        initialPeriodComplete = true;
        Serial.println("INIT_COMPLETE");
    }

    // Check for overflow
    fifoCount = mpu.getFIFOCount();
    if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
        mpu.resetFIFO();
        Serial.println("FIFO overflow!");
    
    } else if (mpuIntStatus & 0x02) {
        while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();
        
        // Read a packet from FIFO
        mpu.getFIFOBytes(fifoBuffer, packetSize);
        fifoCount -= packetSize;
        
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
        
        if (initialPeriodComplete) {
            sendDataToSerial();
        }
    }
}

void calibrateMPU6050() {
    const int numSamples = 2000;  // Number of samples for calibration
    const int settleTime = 2000;  // setteling delay
    
    //calibration sums
    int32_t ax_sum = 0, ay_sum = 0, az_sum = 0;
    int32_t gx_sum = 0, gy_sum = 0, gz_sum = 0;
    
    //Serial.println("Letting sensor settle...");
    //delay(settleTime);
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
    
    //compensate for gravity in z-axis (~16384 at rest with 2g sensitivity setting)
    //??? this won't work, what if the sensor is at an angle?
    //az_mean -= 16384;  
    
    //Set offsets
    mpu.setXAccelOffset(-ax_mean);
    mpu.setYAccelOffset(-ay_mean);
    mpu.setZAccelOffset(-az_mean);
    mpu.setXGyroOffset(-gx_mean);
    mpu.setYGyroOffset(-gy_mean);
    mpu.setZGyroOffset(-gz_mean);
    
    Serial.println("Calibration complete!");
    delay(100);
}

void sendDataToSerial() {
    // Timestamp
    Serial.print(millis());
    Serial.print(",");
    
    // Quaternion
    Serial.print(q.w);
    Serial.print(",");
    Serial.print(q.x);
    Serial.print(",");
    Serial.print(q.y);
    Serial.print(",");
    Serial.print(q.z);
    Serial.print(",");
    
    // Euler angles (in degrees)
    Serial.print(ypr[0] * 180/M_PI); // Yaw
    Serial.print(",");
    Serial.print(ypr[1] * 180/M_PI); // Pitch
    Serial.print(",");
    Serial.print(ypr[2] * 180/M_PI); // Roll
    Serial.print(",");
    
    // Raw acceleration
    //this value doesn't change, why?
    Serial.print(aa.x);
    Serial.print(",");
    Serial.print(aa.y);
    Serial.print(",");
    Serial.print(aa.z);
    Serial.print(",");
    
    // World acceleration (gravity compensated)
    Serial.print(aaWorld.x);
    Serial.print(",");
    Serial.print(aaWorld.y);
    Serial.print(",");
    Serial.print(aaWorld.z);
    
    Serial.println();
}