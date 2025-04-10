#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

// Wi-Fi credentials
const char* ssid = "your_SSID";
const char* password = "password";

// WebSocket server details
const char* server_ip = "255.255.255.255";  // Change to your ROS host IP
const int server_port = 8765;

// Joystick and LED pins
const int xPin = 4;
const int led1 = 15;
const int led2 = 16;
const int led3 = 17;

// NeoPixel setup
#define PIN_PIXS 48
#define PIX_NUM 1
Adafruit_NeoPixel pixels(PIX_NUM, PIN_PIXS, NEO_GRB + NEO_KHZ800);

// WebSocket instance
WebSocketsClient webSocket;

int currentLedState = 0;
int lastXValue = -1;

// LED update (3 separate LEDs)
void updateLeds(int ledCount) {
    digitalWrite(led1, ledCount >= 1 ? HIGH : LOW);
    digitalWrite(led2, ledCount >= 2 ? HIGH : LOW);
    digitalWrite(led3, ledCount >= 3 ? HIGH : LOW);
}

// NeoPixel single color update
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

            // Obsługa stanu LED
            if (!doc["led_state"].isNull()) {
                int newLedState = doc["led_state"];
                if (newLedState != currentLedState) {
                    currentLedState = newLedState;
                    updateLeds(currentLedState);
                    Serial.printf("[STATE] LED state: %d | Time: %lu ms\n", currentLedState, millis());
                }
            }

            // Obsługa koloru NeoPixela
            if (doc["led_color"].is<uint32_t>()) {
                uint32_t ledColor = doc["led_color"];
                showPixelColor(ledColor);
                Serial.printf("[STATE] NeoPixel color: 0x%X | Time: %lu ms\n", ledColor, millis());
            }

            /*
            // TODO: Add ROS-ESP time sync
            if (doc.containsKey("ros_send_time")) {
                unsigned long rosTime = doc["ros_send_time"];
                unsigned long espTime = millis();
                unsigned long latency = espTime - rosTime;
                Serial.printf("[LATENCY] ROS → ESP: %lu ms\n", latency);
            }
            */

            break;
        }

        case WStype_ERROR:
            Serial.printf("[WSc] Error: %s\n", payload);
            break;

        case WStype_PING:
            Serial.println("[WSc] PING received");
            break;

        case WStype_PONG:
            Serial.println("[WSc] PONG received");
            break;

        default:
            Serial.printf("[WSc] Unknown event type: %d\n", type);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("Starting ESP32...");

    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    // Initialize WebSocket
    webSocket.begin(server_ip, server_port, "/");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);

    // Initialize LED pins
    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);
    pinMode(led3, OUTPUT);

    // Initialize NeoPixel
    pixels.begin();
    showPixelColor(0x000000);  // Turn off at start
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi Disconnected! Reconnecting...");
        WiFi.disconnect();
        WiFi.reconnect();
        delay(5000);
        return;
    }

    // Joystick X-axis read and send
    int xValue = analogRead(xPin);
    if (abs(xValue - lastXValue) > 100) {
        lastXValue = xValue;

        StaticJsonDocument<200> doc;
        doc["joystick_x"] = xValue;
        // doc["timestamp"] = millis(); // Optional for time sync

        char jsonBuffer[200];
        serializeJson(doc, jsonBuffer);

        Serial.printf("[INPUT] Joystick X: %d | Time: %lu ms\n", xValue, millis());
        webSocket.sendTXT(jsonBuffer);
    }

    webSocket.loop();
    delay(100);
}