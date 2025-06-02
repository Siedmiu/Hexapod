import csv
import matplotlib.pyplot as plt
import numpy as np

csv_file_1 = 'data3.csv'
csv_file_2 = 'data2.csv'
timeOffset = 350  

def read_csv_data(file_path):
    time, ax, ay, az, gx, gy, gz = [], [], [], [], [], [], []
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
            time.append(float(row[0]))
            ax.append(float(row[1]))
            ay.append(float(row[2]))
            az.append(float(row[3]))
            gx.append(float(row[4]))
            gy.append(float(row[5]))
            gz.append(float(row[6]))
    return np.array(time), np.array(ax), np.array(ay), np.array(az), np.array(gx), np.array(gy), np.array(gz)

# Fuzja z interpolacją
def fuse_accel_with_interpolation(t_ref, a1, t2, a2, alpha=0.5):
    # Interpoluj a2 do czasu t_ref
    a2_interp = np.interp(t_ref, t2, a2)
    return alpha * a1 + (1 - alpha) * a2_interp

# Wczytanie danych z obu IMU
t1, ax1, ay1, az1, gx1, gy1, gz1 = read_csv_data(csv_file_1)
t2, ax2, ay2, az2, gx2, gy2, gz2 = read_csv_data(csv_file_2)

# Zmienne pozycji i prędkości
positions_x, positions_y, positions_z = [0], [0], [0]
vx = vy = vz = 0

# Przetwarzanie próbek względem czasu IMU1
for i in range(1 + timeOffset, len(t1) - 1):
    dt = (t1[i] - t1[i - 1]) / 1000.0 

    # Interpolowana fuzja przyspieszeń
    fx = fuse_accel_with_interpolation(t1[i], ax1[i], t2, ax2)
    fy = fuse_accel_with_interpolation(t1[i], ay1[i], t2, ay2)
    fz = fuse_accel_with_interpolation(t1[i], az1[i], t2, az2)

    vx += fx * dt
    vy += fy * dt
    if fz > 0.92: 
        vz += fz * dt

    x = positions_x[-1] + vx * dt
    y = positions_y[-1] + vy * dt
    z = positions_z[-1] + vz * dt

    positions_x.append(x)
    positions_y.append(y)
    positions_z.append(z)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(positions_x, positions_y, positions_z, label="Trajektoria 3D (z interpolacją i fuzją)", color='blue')
ax.set_title("Trajektoria 3D (2x IMU, interpolacja czasowa)")
ax.set_xlabel("Pozycja X [m]")
ax.set_ylabel("Pozycja Y [m]")
ax.set_zlabel("Pozycja Z [m]")
ax.legend()
plt.show()
