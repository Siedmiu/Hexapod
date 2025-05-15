/*
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Mapowanie serw
// joint1_3 -> 0, ..., joint3_4 -> 17

// WiFi NIE jest potrzebne
// const char* ssid = "EspHex";
// const char* password = "74835915";

// Sterowniki PCA9685
Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(0x40);
Adafruit_PWMServoDriver pwm2 = Adafruit_PWMServoDriver(0x41);

const int SERVO_MIN = 205;
const int SERVO_MAX = 410;

void setServoAngle(uint8_t servoIndex, float angle) {
  angle = constrain(angle, 0, 180);
  uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);

  if (servoIndex >= 0 && servoIndex < 9) {
    pwm1.setPWM(servoIndex, 0, pulse);
  } else if (servoIndex >= 9 && servoIndex < 18) {
    pwm2.setPWM(servoIndex - 9, 0, pulse);
  } else {
    Serial.println("Invalid servo index.");
  }
}

void parseAndHandleCommand(String msg) {
  msg.trim();
  //Serial.printf("Received: '%s'\r\n", msg.c_str());

  if (msg.startsWith("servo")) {
    int servoNum = -1;
    int angle = -1;

    int digitPos = 5;
    while (digitPos < msg.length() && !isDigit(msg[digitPos])) {
      digitPos++;
    }

    int spacePos = msg.indexOf(' ', digitPos);
    if (spacePos != -1) {
      String servoStr = msg.substring(digitPos, spacePos);
      String angleStr = msg.substring(spacePos + 1);

      servoNum = servoStr.toInt();
      angle = angleStr.toInt();

      if(servoNum==0){
        Serial.printf("Parsed: servo=%d, angle=%d\r\n", servoNum, angle);
      }

      if (servoNum >= 0 && servoNum <= 17 && angle >= 0 && angle <= 180) {
        if (servoNum == 9 || servoNum == 12 || servoNum == 15 || servoNum % 3 == 2) {
          angle = 180 - angle;
        }
        setServoAngle(servoNum, angle);
        Serial.printf("Servo %d moved to %d°\r\n", servoNum, angle);
      } else {
        Serial.printf("Invalid servo number (%d) or angle (%d). Allowed: 0-17, 0-180\r\n",servoNum, angle);
      }
    } else {
      Serial.println("Invalid command format. Expected: 'servo<number> <angle>'");
    }
  } else {
    Serial.printf("Unknown command: '%s'\r\n", msg.c_str());
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
}

void loop() {
  static String inputString = "";
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (inputString.length() > 0) {
        parseAndHandleCommand(inputString);
        inputString = "";
      }
    } else {
      inputString += c;
    }
  }
}
*/