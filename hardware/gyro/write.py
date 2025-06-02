import serial
import csv
import time

ser = serial.Serial('COM3', 9600) 

with open('data.csv', mode='w', newline='') as data_file:
    data_writer = csv.writer(data_file)

    data_writer.writerow(["Time [ms]", "Accel X [m/s^2]", "Accel Y [m/s^2]", "Accel Z [m/s^2]", "Angle X [deg]", "Angle Y [deg]", "AngleZ [deg]"])

    print("Receiving data")
    try:
        while True:
            line = ser.readline().decode('utf-8').strip() 
            data = line.split(",")  
            print(data)
            data_writer.writerow(data)
            
    except KeyboardInterrupt:
        print("Done")
