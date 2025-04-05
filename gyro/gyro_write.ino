#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;
unsigned long currentTime;
float previousTime = 0;
float angleZ = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Cannot connect with MPU6050!");
    while (1);
  }
  mpu.CalibrateAccel();
  mpu.CalibrateGyro();

}

void loop() {
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  float gyroX = gx / 131.0;
  float gyroY = gy / 131.0;
  float gyroZ = gz / 131.0;


  float accelX = ax / 16384.0 * 9.81;
  float accelY = ay / 16384.0 * 9.81;
  float accelZ = az / 16384.0 * 9.81;

  currentTime = millis();

  float angleX = atan2(accelY, accelZ) * 180 / PI;
  float angleY = atan2(accelX, accelZ) * 180 / PI;
  angleZ += (currentTime - previousTime)/1000 * gyroZ;

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
  Serial.print(angleY);
  Serial.print(",");
  Serial.println(angleZ);

  previousTime = currentTime;

  delay(200);
}
