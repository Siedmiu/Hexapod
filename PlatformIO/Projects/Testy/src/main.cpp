#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// # Mapowanie nazw jointów na numery serw
// joint_to_servo = {
//     "joint1_3": 0,
//     "joint2_3": 1,
//     "joint3_3": 2,
//     "joint1_2": 3,
//     "joint2_2": 4,
//     "joint3_2": 5,
//     "joint1_1": 6,
//     "joint2_1": 7,
//     "joint3_1": 8,
//     "joint1_6": 9,
//     "joint2_6": 10,
//     "joint3_6": 11,
//     "joint1_5": 12,
//     "joint2_5": 13,
//     "joint3_5": 14,
//     "joint1_4": 15,
//     "joint2_4": 16,
//     "joint3_4": 17,
// }

// WiFi credentials
const char* ssid = "EspHex";
const char* password = "74835915";

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
    
    Serial.printf("Received: '%s'\r\n", msg.c_str());  // Dodaj to dla debugowania

    if (msg.startsWith("servo")) {
      // Wersja dla ROSa - bez spacji po "servo"
      int servoNum = -1;
      int angle = -1;
      
      // Znajdź pierwszą cyfrę po "servo"
      int digitPos = 5;  // "servo" ma 5 znaków
      while (digitPos < msg.length() && !isDigit(msg[digitPos])) {
        digitPos++;
      }
      
      // Znajdź spację po numerze serwa
      int spacePos = msg.indexOf(' ', digitPos);
      
      if (spacePos != -1) {
        String servoStr = msg.substring(digitPos, spacePos);
        String angleStr = msg.substring(spacePos + 1);
        
        servoNum = servoStr.toInt();
        angle = angleStr.toInt();
        
        Serial.printf("Parsed: servo=%d, angle=%d\r\n", servoNum, angle);
        
        if (servoNum >= 0 && servoNum <= 17 && angle >= 0 && angle <= 180) {
          setServoAngle(servoNum, angle);  // Używamy bezpośrednio numerów 0-17
          Serial.printf("Servo %d moved to %d°\r\n", servoNum, angle);
        } else {
          Serial.printf("Invalid servo number (%d) or angle (%d). Allowed: 0-17, 0-180\r\n", 
                       servoNum, angle);
        }
      } else {
        Serial.println("Invalid command format. Expected: 'servo<number> <angle>'");
      }
    } else {
      Serial.printf("Unknown command: '%s'\r\n", msg.c_str());
    }
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
             AwsEventType type, void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    Serial.printf("Client connected: %u\r\n", client->id());
  } else if (type == WS_EVT_DISCONNECT) {
    Serial.printf("Client disconnected: %u\r\n", client->id());
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