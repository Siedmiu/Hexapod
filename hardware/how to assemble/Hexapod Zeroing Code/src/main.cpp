#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Servo driver setup
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
const int SERVO_MIN = 205;
const int SERVO_MAX = 410;

void setServoAngle(uint8_t channel, float angle) {
  angle = constrain(angle, 0, 180);
  uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
  pwm.setPWM(channel, 0, pulse);
}

void setup() {
  Wire.begin();
  pwm.begin();
  pwm.setPWMFreq(60);
}

void loop() {
  for (int i = 0; i <= 36; i++) {
    if (i % 3 == 0) setServoAngle(i, 90);
    if (i % 3 == 1) setServoAngle(i, 150);
    if (i % 3 == 2) setServoAngle(i, 180);
  }
}
