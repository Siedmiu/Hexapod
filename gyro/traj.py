import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np

csv_file = 'data.csv'

def multiply3(a, phi, theta, psi):
    R_z = np.array([
        [math.cos(psi), -math.sin(psi), 0],
        [math.sin(psi), math.cos(psi),  0],
        [0,           0,            1]
    ])

    R_y = np.array([
        [math.cos(theta),  0, math.sin(theta)],
        [0,              1, 0],
        [-math.sin(theta), 0, math.cos(theta)]
    ])

    R_x = np.array([
        [1, 0,              0],
        [0, math.cos(phi), -math.sin(phi)],
        [0, math.sin(phi),  math.cos(phi)]
    ])

    R1 =np.dot(R_x, R_y)
    R = np.dot(R1, R_z)

    a_global = np.dot(R, a)
    return a_global[0], a_global[1], a_global[2]


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

    g_vect = np.array([0, 0, 9.81])
    # gravity vector


    for i in range(1, len(time)-1):
        dt = (time[i] - time[i-1])/1000

        sumX += accel_x[i]
        sumY += accel_y[i]
        sumZ += accel_z[i]

        g_x, g_y, g_z = multiply3(g_vect, np.radians(angle_x[i]), np.radians(angle_y[i]), np.radians(angle_z[i]))
        # here gravity vect is rotated as our device to be then substracted from measured accels

        a = np.array([accel_x[i] - g_x, accel_y[i] - g_y, accel_z[i] - g_z])

        act_acc_x, act_acc_y, act_acc_z = multiply3(a, np.radians(angle_x[i]), np.radians(angle_y[i]), np.radians(angle_z[i]))

        print(( math.cos(np.radians(angle_z[i])) * math.sin(np.radians(angle_y[i])) * math.cos(np.radians(angle_x[i])) + math.sin(np.radians(angle_z[i])) * math.sin(np.radians(angle_x[i])) ))

        if abs(act_acc_z) < 0.2: act_acc_z = 0
        if abs(act_acc_y) < 0.1: act_acc_y = 0
        if abs(act_acc_x) < 0.09: act_acc_x = 0

        vx += act_acc_x*dt
        vy += act_acc_y*dt
        vz += act_acc_z*dt

        # there are some issues as due to some big accels the velocity grows
        # and provides largely too big distances in some cases

        print(i, ": ",accel_y[i], ", ", act_acc_y,  ", v: ", vy)

        z = vz*dt + positions_z[i-1]
        y = vy*dt + positions_y[i-1]
        x = vx*dt + positions_x[i-1]

        positions_z.append(z)
        positions_y.append(y)
        positions_x.append(x)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(positions_x, positions_y, positions_z, label="Trajektoria 3D", color='b')
    ax.set_title("Trajektoria ruchu 3D")
    ax.set_xlabel("Pozycja X [m]")
    ax.set_ylabel("Pozycja Y [m]")
    ax.set_zlabel("Pozycja Z [m]")
    ax.legend()

    plt.show()
