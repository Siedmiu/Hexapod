#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;
unsigned long currentTime;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Cannot connect with MPU6050!");
    while (1);
  }
  Serial.println("Time [ms],Accel X [m/s^2],Accel Y [m/s^2],Accel Z [m/s^2],Angle X [deg],Angle Y [deg]");
}

void loop() {
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  float accelX = ax / 16384.0 * 9.81;
  float accelY = ay / 16384.0 * 9.81;
  float accelZ = az / 16384.0 * 9.81;

  float angleX = atan2(accelY, accelZ) * 180 / PI;
  float angleY = atan2(accelX, accelZ) * 180 / PI;

  currentTime = millis();

  Serial.print(currentTime);
  Serial.print(",");
  Serial.print(accelX);
  Serial.print(",");
  Serial.print(accelY);
  Serial.print(",");
  Serial.print(accelZ);
  Serial.print(",");
  Serial.print(angleX);
  Serial.print(",");
  Serial.println(angleY);

  delay(500);
}
