import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np
from scipy.signal import butter, filtfilt

csv_file = 'data.csv'
csv_file_2 = 'data_cst_old.csv'

timeOffset = 10
g_vect = np.array([0, 0, 9.81])

# Filter parameters
accel_lpf_cutoff = 2.0  # Low-pass filter cutoff frequency for accelerometer (Hz)
vel_hpf_cutoff = 0.1    # High-pass filter cutoff frequency for velocity (Hz)
sample_rate = 100      # Estimated sample rate (Hz) - adjust based on your data

# Zero velocity detection parameters
zero_velocity_threshold = 0.05  # Threshold for zero velocity detection
zero_velocity_window = 10       # Window size for zero velocity detection

def butter_lowpass(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_highpass(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def apply_filter(data, b, a):
    return filtfilt(b, a, data)

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

    R1 = np.dot(R_x, R_y)
    R = np.dot(R1, R_z)

    a_global = np.dot(R, a)
    return a_global[0], a_global[1], a_global[2]

def detect_zero_velocity(accel_magnitude, threshold, window_size):
    
    is_stationary = np.zeros(len(accel_magnitude), dtype=bool)
    
    for i in range(window_size, len(accel_magnitude)):
        window = accel_magnitude[i-window_size:i]
        if np.std(window) < threshold:
            is_stationary[i] = True
            
    return is_stationary

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

    # Calculate actual sample rate from time data
    if len(time) > 1:
        avg_dt = np.mean(np.diff(time)) / 1000.0 
        sample_rate = 1.0 / avg_dt
        #print(f"Calculated sample rate: {sample_rate:.2f} Hz")
    
    
    lpf_b, lpf_a = butter_lowpass(accel_lpf_cutoff, sample_rate)
    hpf_b, hpf_a = butter_highpass(vel_hpf_cutoff, sample_rate)
    
    # Apply low-pass filter to accelerometer data to reduce noise
    filtered_accel_x = apply_filter(accel_x, lpf_b, lpf_a)
    filtered_accel_y = apply_filter(accel_y, lpf_b, lpf_a)
    filtered_accel_z = apply_filter(accel_z, lpf_b, lpf_a)
    
    # Calculate acceleration magnitude for zero velocity detection
    accel_magnitude = np.sqrt(
        np.array(filtered_accel_x)**2 + 
        np.array(filtered_accel_y)**2 + 
        np.array(filtered_accel_z)**2
    )
    
  
    is_stationary = detect_zero_velocity(accel_magnitude, zero_velocity_threshold, zero_velocity_window)

    positions_x = [0]  
    positions_y = [0] 
    positions_z = [0]

    vx = 0
    vy = 0
    vz = 0
    
 
    vel_x = [0]
    vel_y = [0]
    vel_z = [0]

    for i in range(1, len(time)-1-timeOffset):
        dt = (time[i] - time[i-1])/1000

      
        g_x, g_y, g_z = multiply3(g_vect, np.radians(angle_x[i]), np.radians(angle_y[i]), np.radians(angle_z[i]))

       
        a = np.array([
            filtered_accel_x[i + timeOffset] - g_x, 
            filtered_accel_y[i + timeOffset] - g_y, 
            filtered_accel_z[i + timeOffset] - g_z
        ])

       
        act_acc_x, act_acc_y, act_acc_z = multiply3(a, np.radians(angle_x[i]), np.radians(angle_y[i]), np.radians(angle_z[i]))

     
        if i + timeOffset < len(is_stationary) and is_stationary[i + timeOffset]:
            vx = 0
            vy = 0
            vz = 0
        else:
           
            vx += act_acc_x * dt
            vy += act_acc_y * dt
            vz += act_acc_z * dt
            
            # Apply threshold to vertical acceleration to reduce drift
            if abs(act_acc_z) < 0.05:
                vz *= 0.95  # Damping factor to reduce drift
        
      
        vel_x.append(vx)
        vel_y.append(vy)
        vel_z.append(vz)
        
        # Integrate velocity to get position
        x = vx * dt + positions_x[-1]
        y = vy * dt + positions_y[-1]
        z = vz * dt + positions_z[-1]

        positions_x.append(x)
        positions_y.append(y)
        positions_z.append(z)

    
    if len(vel_x) > 3:  
        filtered_vel_x = apply_filter(vel_x, hpf_b, hpf_a)
        filtered_vel_y = apply_filter(vel_y, hpf_b, hpf_a)
        filtered_vel_z = apply_filter(vel_z, hpf_b, hpf_a)
        
       
        filtered_pos_x = [0]
        filtered_pos_y = [0]
        filtered_pos_z = [0]
        
        for i in range(1, len(filtered_vel_x)):
            dt = (time[min(i, len(time)-1)] - time[min(i-1, len(time)-1)])/1000
            x = filtered_vel_x[i] * dt + filtered_pos_x[-1]
            y = filtered_vel_y[i] * dt + filtered_pos_y[-1]
            z = filtered_vel_z[i] * dt + filtered_pos_z[-1]
            
            filtered_pos_x.append(x)
            filtered_pos_y.append(y)
            filtered_pos_z.append(z)
        
       
        positions_x = filtered_pos_x
        positions_y = filtered_pos_y
        positions_z = filtered_pos_z

    # Visualization
    fig = plt.figure(figsize=(12, 10))
    
    # 3D trajectory plot
    ax1 = fig.add_subplot(221, projection='3d')
    ax1.plot(positions_x, positions_y, positions_z, label="Filtered Trajectory", color='b')
    ax1.set_title("3D Motion Trajectory")
    ax1.set_xlabel("X Position [m]")
    ax1.set_ylabel("Y Position [m]")
    ax1.set_zlabel("Z Position [m]")
    ax1.legend()
    
    # Acceleration plot
    ax2 = fig.add_subplot(222)
    ax2.plot(time[:-timeOffset], filtered_accel_x[timeOffset:], 'r-', label='X')
    ax2.plot(time[:-timeOffset], filtered_accel_y[timeOffset:], 'g-', label='Y')
    ax2.plot(time[:-timeOffset], filtered_accel_z[timeOffset:], 'b-', label='Z')
    ax2.set_title("Filtered Acceleration")
    ax2.set_xlabel("Time [ms]")
    ax2.set_ylabel("Acceleration")
    ax2.legend()
    
    # Velocity plot
    ax3 = fig.add_subplot(223)
    ax3.plot(time[:len(filtered_vel_x)], filtered_vel_x, 'r-', label='X')
    ax3.plot(time[:len(filtered_vel_y)], filtered_vel_y, 'g-', label='Y')
    ax3.plot(time[:len(filtered_vel_z)], filtered_vel_z, 'b-', label='Z')
    ax3.set_title("Filtered Velocity")
    ax3.set_xlabel("Time [ms]")
    ax3.set_ylabel("Velocity [m/s]")
    ax3.legend()
    
    # Position plot
    ax4 = fig.add_subplot(224)
    ax4.plot(time[:len(positions_x)], positions_x, 'r-', label='X')
    ax4.plot(time[:len(positions_y)], positions_y, 'g-', label='Y')
    ax4.plot(time[:len(positions_z)], positions_z, 'b-', label='Z')
    ax4.set_title("Position")
    ax4.set_xlabel("Time [ms]")
    ax4.set_ylabel("Position [m]")
    ax4.legend()
    
    plt.tight_layout()
    plt.show()
