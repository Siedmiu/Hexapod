#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Servo driver setup
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
const int SERVO_MIN = 102;
const int SERVO_MAX = 512;

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
  setServoAngle(0, 0);
  setServoAngle(1, 0);
  setServoAngle(2, 0);
  setServoAngle(3, 0);

  setServoAngle(4, 30);
  setServoAngle(5, 30);
  setServoAngle(6, 30);
  setServoAngle(7, 30);

  setServoAngle(8, 180);
  setServoAngle(9, 180);
  setServoAngle(10, 180);
  setServoAngle(11, 180);

  setServoAngle(12, 180);
  setServoAngle(13, 180);
  setServoAngle(14, 180);
  setServoAngle(15, 180);
}
