#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// WiFi credentials
const char* ssid = "Twoja_Siec";
const char* password = "Twoje_Haslo";

// Dwa sterowniki PCA9685
Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(0x40);  // pierwsza płytka
Adafruit_PWMServoDriver pwm2 = Adafruit_PWMServoDriver(0x41);  // druga płytka

const int SERVO_MIN = 102;
const int SERVO_MAX = 512;

// WebSocket server
AsyncWebServer server(80);
AsyncWebSocket ws("/");

// Ustaw kąt dla odpowiedniego serwa (1-18)
void setServoAngle(uint8_t servoIndex, float angle) {
  angle = constrain(angle, 0, 180);
  uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);

  if (servoIndex >= 0 && servoIndex < 9) {
    pwm1.setPWM(servoIndex, 0, pulse);  // kanały 0–8
  } else if (servoIndex >= 9 && servoIndex < 18) {
    pwm2.setPWM(servoIndex - 9, 0, pulse);  // kanały 0–8 na drugiej płytce
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

        int servoNum = servoStr.toInt();  // teraz serwa 1–18
        int angle = angleStr.toInt();

        if (servoNum >= 1 && servoNum <= 18 && angle >= 0 && angle <= 180) {
          setServoAngle(servoNum - 1, angle);  // indeksujemy od 0
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

  pwm1.begin();
  pwm1.setPWMFreq(60);
  pwm2.begin();
  pwm2.setPWMFreq(60);
  Serial.println("Both PCA9685 initialized.");

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

  for (int i = 0; i < 18; i++) {
    if (i % 3 == 0) setServoAngle(i, 90); //90
    if (i % 3 == 1) setServoAngle(i, 120);//150
    if (i % 3 == 2) setServoAngle(i, 30);//180
  }
  setServoAngle(2, 180);
  setServoAngle(14, 180);
}

void loop() {
  // Asynchroniczna obsługa WebSocket
}