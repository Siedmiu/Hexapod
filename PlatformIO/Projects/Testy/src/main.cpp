#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// WiFi credentials
const char* ssid = "Twoja_Siec";
const char* password = "Twoje_Haslo";

// Servo driver
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
const int SERVO_MIN = 102;
const int SERVO_MAX = 512;

// WebSocket server
AsyncWebServer server(80);
AsyncWebSocket ws("/");

void setServoAngle(uint8_t channel, float angle) {
  angle = constrain(angle, 0, 180);
  uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
  pwm.setPWM(channel, 0, pulse);
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

        int servoNum = servoStr.toInt() - 1;  // kanał 0–15
        int angle = angleStr.toInt();

        if (servoNum >= 0 && servoNum < 16 && angle >= 0 && angle <= 180) {
          setServoAngle(servoNum, angle);
          Serial.printf("Servo %d moved to %d°\n", servoNum, angle);
        } else {
          Serial.println("Invalid servo number or angle.");
        }
      } else {
        Serial.println("Invalid command format.");
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

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pwm.begin();
  pwm.setPWMFreq(60);
  Serial.println("PCA9685 initialized.");

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  ws.onEvent(onEvent);
  server.addHandler(&ws);
  server.begin();
}

void loop() {
  // WebSocket działa asynchronicznie – nic nie trzeba robić w pętli
}