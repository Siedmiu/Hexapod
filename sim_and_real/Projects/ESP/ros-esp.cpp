//TODO add time synchronization between ros and esp, as it doesnt operate in the same time now

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// Wi-Fi credentials
const char* ssid = "your_SSID";        
const char* password = "password";    

// WebSocket server details
const char* server_ip = "255.255.255.255";  //your computer IP, check by running in terminal> hostname -I
const int server_port = 8765; //you can change to (I guess) any port, but make sure to also adjust it in ros part and that it doenst conflict with anyching else

WebSocketsClient webSocket;

const int xPin = 4;

const int led1 = 15;
const int led2 = 16;
const int led3 = 17;

int currentLedState = 0;  
int lastXValue = -1;  

void updateLeds(int ledCount) {
    digitalWrite(led1, ledCount >= 1 ? HIGH : LOW);
    digitalWrite(led2, ledCount >= 2 ? HIGH : LOW);
    digitalWrite(led3, ledCount >= 3 ? HIGH : LOW);
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
    if (type == WStype_TEXT) {
        StaticJsonDocument<200> doc;
        deserializeJson(doc, payload);

        if (doc.containsKey("led_state")) {
            int newLedState = doc["led_state"];
            if (newLedState != currentLedState) {
                currentLedState = newLedState;
                updateLeds(currentLedState);
                Serial.printf("[STATE] ESP Updated LEDs to: %d   |      Received Time: %lu ms\n", currentLedState, millis());
            }
        }

        /*
        if (doc.containsKey("ros_send_time")) {
            unsigned long ros_sent_time = doc["ros_send_time"];
            unsigned long esp_received_time = millis();
            unsigned long ros_to_esp_delay = esp_received_time - ros_sent_time;
            Serial.printf("[LATENCY] ROS → ESP: %lu ms\n", ros_to_esp_delay);
        }
        */
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\nStarting ESP32...");

    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());

    webSocket.begin(server_ip, server_port, "/");
    webSocket.onEvent(webSocketEvent);

    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);
    pinMode(led3, OUTPUT);
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi Disconnected! Reconnecting...");
        WiFi.disconnect();
        WiFi.reconnect();
        delay(5000);
        return;
    }

    int xValue = analogRead(xPin);

    if (abs(xValue - lastXValue) > 100) {  
        lastXValue = xValue;

        StaticJsonDocument<200> doc;
        doc["joystick_x"] = xValue;
        // doc["timestamp"] = millis();  

        char jsonBuffer[200];
        serializeJson(doc, jsonBuffer);

        Serial.printf("[INPUT] Sending Joystick X: %d | ESP Sent Time: %lu ms\n", xValue, millis());
        webSocket.sendTXT(jsonBuffer);
    }

    webSocket.loop();
    delay(100);
}
