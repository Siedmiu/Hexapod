#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Mapowanie serw
// joint1_3 -> 0, ..., joint3_4 -> 17

// WiFi NIE jest potrzebne
// const char* ssid = "EspHex";
// const char* password = "74835915";

// Sterowniki PCA9685


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

      if(servoNum==13){
        
        Serial.printf("Parsed: servo=%d, angle=%d\r\n", servoNum, angle);
      }

      if (servoNum >= 0 && servoNum <= 17 && angle >= 0 && angle <= 180) {
        // if (servoNum == 9 || servoNum == 12 || servoNum == 15 || servoNum % 3 == 2) { // || servoNum % 3 == 1
        //   angle = 180 - angle;
        // }
        setServoAngle(servoNum, angle);
        if (servoNum == 13) {
          Serial.printf("Servo %d moved to %d°\r\n", servoNum, angle);
        }
        
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

  int all_j1_angle = 90;
  int all_j2_angle = 30;
  int all_j3_angle = 60;
  // joint 1
  setServoAngle(0, all_j1_angle);
  setServoAngle(3, all_j1_angle);
  setServoAngle(6, all_j1_angle);
  setServoAngle(9, all_j1_angle);
  setServoAngle(12, all_j1_angle);
  setServoAngle(15, all_j1_angle);

  // joint 2
  setServoAngle(1, all_j2_angle);
  setServoAngle(4, all_j2_angle);
  setServoAngle(7, all_j2_angle);
  setServoAngle(10, all_j2_angle);
  setServoAngle(13, all_j2_angle);
  setServoAngle(16, all_j2_angle);
  // joint 3
  setServoAngle(2, all_j3_angle);
  setServoAngle(5, all_j3_angle);
  setServoAngle(8, all_j3_angle);
  setServoAngle(11, all_j3_angle);
  setServoAngle(14, all_j3_angle);
  setServoAngle(17, all_j3_angle);
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
  // int all_j1_angle = 90;
  // int all_j2_angle = 150;
  // int all_j3_angle = 180;
  // // joint 1
  // setServoAngle(0, all_j1_angle);
  // setServoAngle(3, all_j1_angle);
  // setServoAngle(6, all_j1_angle);
  // setServoAngle(9, all_j1_angle);
  // setServoAngle(12, all_j1_angle);
  // setServoAngle(15, all_j1_angle);

  // // joint 2
  // setServoAngle(1, all_j2_angle);
  // setServoAngle(4, all_j2_angle);
  // setServoAngle(7, all_j2_angle);
  // setServoAngle(10, all_j2_angle);
  // setServoAngle(13, all_j2_angle);
  // setServoAngle(16, all_j2_angle);
  // // joint 3
  // setServoAngle(2, all_j3_angle);
  // setServoAngle(5, all_j3_angle);
  // setServoAngle(8, all_j3_angle);
  // setServoAngle(11, all_j3_angle);
  // setServoAngle(14, all_j3_angle);
  // setServoAngle(17, all_j3_angle);
}