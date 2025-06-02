These files contains code for acquiring and dealing with data provided by MPU-6050

gyro_write.ino is a script for Arduino to acquire data from gyroscope
Write.py is a script that writes the data to .csv file
traj.py calculates trajectory based of the data about angles and acceleration

============================================================================

_dmp files works as these above but are using DMP which provides better data

trajectory_integrated calculates trajectory using two data sets from IMU as now uses simple complementary filter

MPU-6050 datasheet: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf

================19.04.2025==============
I am testing an alternative approach, and created new implementation.
The program runs through Matlab and directly connects to the esp, remember to define the COM port.

I want to use the onboard Digital Motion Processor (DMP) to get accurate orientation data while minimizing drift.

Data looks promising with minimal diviation and fast responses, but the acceleration scaling
needs to be fixed.
