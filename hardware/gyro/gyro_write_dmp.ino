#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include <Wire.h>

MPU6050 mpu;

const float accScale = 9.80665 / 16384.0;

// zmienne DMP
bool dmpReady = false;
uint8_t mpuIntStatus;
uint8_t devStatus;
uint16_t packetSize;
uint16_t fifoCount;
uint8_t fifoBuffer[64];

Quaternion q;            // [w, x, y, z]
VectorFloat gravity;     // [x, y, z]
VectorInt16 aa;          // surowe przyspieszenie
VectorInt16 aaReal;      // rzeczywiste przyspieszenie (bez grawitacji)
float ypr[3];            // [yaw, pitch, roll]

void setup() {
    Serial.begin(9600);
    Wire.begin();

    mpu.initialize();
    devStatus = mpu.dmpInitialize();

    if (devStatus == 0) {
        mpu.setDMPEnabled(true);
        dmpReady = true;
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        Serial.print("Błąd inicjalizacji DMP: ");
        Serial.println(devStatus);
    }
}

void loop() {
    if (!dmpReady) return;

    fifoCount = mpu.getFIFOCount();
    if (fifoCount == 1024) {
        mpu.resetFIFO(); // overflow
        // Serial.println("FIFO overflow!");
    } else if (fifoCount >= packetSize) {
        mpu.getFIFOBytes(fifoBuffer, packetSize);
        
        // odczyt orientacji
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        
        // odczyt przyspieszenia
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);

        Serial.print(millis());
        Serial.print(",");
        //Serial.print("Accel (real) X: ");
        Serial.print(aaReal.x * accScale, 3);
        Serial.print(",");
        //Serial.print(" Y: ");
        Serial.print(aaReal.y * accScale, 3);
        Serial.print(",");
        //Serial.print(" Z: ");
        Serial.print(aaReal.z * accScale, 3);
        Serial.print(",");

        // wypisywanie danych
        //Serial.print(" Roll: ");
        Serial.print(ypr[2] * 180/M_PI);
        Serial.print(",");
        //Serial.print(" Pitch: ");
        Serial.print(ypr[1] * 180/M_PI);
        Serial.print(",");
        //Serial.print("Yaw: ");
        Serial.println(ypr[0] * 180/M_PI);
    }
}
