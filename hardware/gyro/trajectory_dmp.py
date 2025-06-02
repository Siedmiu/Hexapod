import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np

csv_file = 'data3.csv'

timeOffset = 350

if __name__ == "__main__":


    time = []
    accel_x = []
    accel_y = []
    accel_z = []
    angle_x = []
    angle_y = []
    angle_z = []

    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader) 

        for row in reader:
            time.append(float(row[0]))       
            accel_x.append(float(row[1]))     
            accel_y.append(float(row[2]))     
            accel_z.append(float(row[3]))     
            angle_x.append(float(row[4]))     
            angle_y.append(float(row[5]))
            angle_z.append(float(row[6]))        

    positions_x = [0]  
    positions_y = [0] 
    positions_z = [0]

    vx = 0
    vy = 0
    vz = 0

    sumX= 0
    sumY = 0
    sumZ = 0

    for i in range(1, len(time)-1-timeOffset):
        dt = (time[i] - time[i-1])/1000

        vx += accel_x[i+timeOffset]*dt
        vy += accel_y[i+timeOffset]*dt
        if accel_z[i+timeOffset] > 0.92:
            vz += accel_z[i+timeOffset]*dt

        z = vz*dt + positions_z[i-1]
        y = vy*dt + positions_y[i-1]
        x = vx*dt + positions_x[i-1]

        positions_z.append(z)
        positions_y.append(y)
        positions_x.append(x)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(positions_x, positions_y, positions_z, label="Trajektoria 3D", color='b')
    ax.set_title("Trajektoria ruchu 3D")
    ax.set_xlabel("Pozycja X [m]")
    ax.set_ylabel("Pozycja Y [m]")
    ax.set_zlabel("Pozycja Z [m]")
    ax.legend()

    plt.show()