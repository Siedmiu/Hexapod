import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

csv_file = 'data.csv'

of_X = 0.64
of_Y = 0.07
of_Z = 11.64

time = []
accel_x = []
accel_y = []
accel_z = []
angle_x = []
angle_y = []

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

positions_x = [0]  
positions_y = [0] 
positions_z = [0]  
dt = (time[1] - time[0]) / 1000.0  

for i in range(1, len(time)):
    filtered_accel_z = accel_z[i] - of_Z  
    filtered_accel_y = accel_y[i] - of_Y
    filtered_accel_x = accel_x[i] - of_X

    corrected_accel_x = filtered_accel_x * math.cos(math.radians(angle_x[i]))
    corrected_accel_y = filtered_accel_y * math.cos(math.radians(angle_y[i]))

    vx = corrected_accel_x * dt
    vy = corrected_accel_y * dt
    vz = filtered_accel_z * dt

    positions_x.append(positions_x[-1] + vx * dt)
    positions_y.append(positions_y[-1] + vy * dt)
    positions_z.append(positions_z[-1] + vz * dt)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.plot(positions_x, positions_y, positions_z, label="Trajektoria 3D", color='b')
ax.set_title("Trajektoria ruchu 3D z filtrowaniem grawitacji")
ax.set_xlabel("Pozycja X [m]")
ax.set_ylabel("Pozycja Y [m]")
ax.set_zlabel("Pozycja Z [m]")
ax.legend()

plt.show()
