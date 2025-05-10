#include <WiFi.h> 
#include <WebSocketsClient.h> // links2004/WebSockets@^2.6.1
#include <ArduinoJson.h> // bblanchon/ArduinoJson@^7.3.1
#include <Adafruit_NeoPixel.h> // adafruit/Adafruit NeoPixel @ ^1.12.2

#define PIN_PIXS 48
#define PIX_NUM 1

// Wi-Fi credentials
const char* ssid = "SSID";        
const char* password = "password";    

// WebSocket server details
const char* server_ip = "server_ip";
const int server_port = 8765;

WebSocketsClient webSocket;
Adafruit_NeoPixel pixels(PIX_NUM, PIN_PIXS, NEO_GRB + NEO_KHZ800);

void showPixelColor(uint32_t c) {
    pixels.setPixelColor(0, c);
    pixels.show();
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
    switch(type) {
        case WStype_CONNECTED:
            Serial.printf("[WSc] Połączono z serwerem: %s\n", payload);
            break;

        case WStype_DISCONNECTED:
            Serial.printf("[WSc] Rozłączono!\n");
            break;
            
        case WStype_TEXT:
            if (length > 0) {
                String text = String((char*)payload);
                Serial.printf("[WSc] Otrzymano wiadomość: %s\n", text.c_str());
                
                JsonDocument doc;
                DeserializationError error = deserializeJson(doc, payload);
                
                if (error) {
                    Serial.print("deserializeJson() failed: ");
                    Serial.println(error.c_str());
                    return;
                }
                
                if (doc["led_color"].is<uint32_t>()) {
                    uint32_t ledColor = doc["led_color"];
                    Serial.printf("[STATE] ESP Updated LED to color: 0x%X   |      Received Time: %lu ms\n", ledColor, millis());
                    showPixelColor(ledColor);
                }
            }
            break;

        case WStype_ERROR:
            Serial.printf("[WSc] Błąd: %s\n", payload);
            break;
            
        case WStype_PING:
            Serial.println("[WSc] Otrzymano PING");
            break;

        case WStype_PONG:
            Serial.println("[WSc] Otrzymano PONG");
            break;

        default:
            Serial.printf("[WSc] Nieobsługiwany typ zdarzenia: %d\n", type);
            break;
            
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
    webSocket.setReconnectInterval(5000);

    pixels.begin();
    showPixelColor(0x000000);
}

void loop() {
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