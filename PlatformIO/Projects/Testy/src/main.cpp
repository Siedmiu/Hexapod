#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

const int SERVO_MIN = 102;  // PWM dla kąta 0
const int SERVO_MAX = 512;  // PWM dla kąta 180

void setServoAngle(uint8_t channel, float angle) {
  angle = constrain(angle, 0, 180);
  uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
  pwm.setPWM(channel, 0, pulse);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  pwm.begin();
  pwm.setPWMFreq(60);  // typowa częstotliwość dla serw

  Serial.println("PCA9685 initialized.");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // usuwa białe znaki

    if (command.startsWith("servo")) {
      int spaceIndex = command.indexOf(' ');
      if (spaceIndex != -1) {
        String servoStr = command.substring(5, spaceIndex);  // np. "1"
        String angleStr = command.substring(spaceIndex + 1); // np. "90"

        int servoNum = servoStr.toInt();
        int angle = angleStr.toInt();
        servoNum--;  // zmniejszamy o 1, aby pasowało do indeksu tablicy

        if (servoNum >= 0 && servoNum < 16 && angle >= 0 && angle <= 180) {
          setServoAngle(servoNum, angle);
          Serial.print("Servo ");
          Serial.print(servoNum);
          Serial.print(" moved to: ");
          Serial.println(angle);
        } else {
          Serial.println("Invalid servo number or angle.");
        }
      } else {
        Serial.println("Invalid format. Use: servoX angle");
      }
    } else {
      Serial.println("Unknown command.");
    }
  }
}
