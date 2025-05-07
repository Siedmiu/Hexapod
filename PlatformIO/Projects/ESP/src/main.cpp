#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Wi-Fi credentials
const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";

// WebSocket server details
const char* server_ip = "192.168.0.123";  // IP komputera z ROS2
const int server_port = 8765;

// NeoPixel setup
#define PIN_PIXS 48
#define PIX_NUM 1
Adafruit_NeoPixel pixels(PIX_NUM, PIN_PIXS, NEO_GRB + NEO_KHZ800);

// PCA9685
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
#define SERVOMIN  150
#define SERVOMAX  600

uint16_t angleToPWM(float angle) {
    angle = constrain(angle, 0, 180);
    return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

// WebSocket instance
WebSocketsClient webSocket;

int currentLedState = 0;
int lastXValue = -1;

void showPixelColor(uint32_t c) {
    pixels.setPixelColor(0, c);
    pixels.show();
}

// WebSocket event handler
void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
    switch (type) {
        case WStype_CONNECTED:
            Serial.printf("[WSc] Connected to server: %s\n", payload);
            break;

        case WStype_DISCONNECTED:
            Serial.println("[WSc] Disconnected!");
            break;

        case WStype_TEXT: {
            Serial.printf("[WSc] Message: %s\n", (char*)payload);

            JsonDocument doc;
            DeserializationError error = deserializeJson(doc, payload);
            if (error) {
                Serial.print("deserializeJson() failed: ");
                Serial.println(error.c_str());
                return;
            }

            // Kolor NeoPixela
            if (doc["led_color"].is<uint32_t>()) {
                uint32_t ledColor = doc["led_color"];
                showPixelColor(ledColor);
                Serial.printf("[STATE] NeoPixel color: 0x%X | Time: %lu ms\n", ledColor, millis());
            }

            // Odbiór kątów theta1, theta2, theta3
            if (doc.containsKey("theta1") && doc.containsKey("theta2") && doc.containsKey("theta3")) {
                float theta1 = doc["theta1"];
                float theta2 = doc["theta2"];
                float theta3 = doc["theta3"];

                uint16_t pwm1 = angleToPWM(theta1);
                uint16_t pwm2 = angleToPWM(theta2);
                uint16_t pwm3 = angleToPWM(theta3);

                pwm.setPWM(0, 0, pwm1);
                pwm.setPWM(1, 0, pwm2);
                pwm.setPWM(2, 0, pwm3);

                Serial.printf("[SERVOS] T1: %.1f → %d | T2: %.1f → %d | T3: %.1f → %d\n", theta1, pwm1, theta2, pwm2, theta3, pwm3);
            }

            break;
        }

        default:
            break;
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("Starting ESP32...");

    // Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    // WebSocket
    webSocket.begin(server_ip, server_port, "/");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);

    // NeoPixel
    pixels.begin();
    showPixelColor(0x000000);  // Off

    // PCA9685
    Wire.begin(); // domyślnie SDA: GPIO 21, SCL: GPIO 22
    pwm.begin();
    pwm.setPWMFreq(50);
    delay(10);
}

void loop() {
    // Wi-Fi check
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi Disconnected! Reconnecting...");
        WiFi.disconnect();
        WiFi.reconnect();
        delay(5000);
        return;
    }
    webSocket.loop();
    delay(100);
}