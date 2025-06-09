import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from filterpy.kalman import KalmanFilter

class FederatedFilter:
    def __init__(self, num_imus=2, delta_time=0.01):
        self.dt = delta_time
        self.local_filters = [self.create_local_filter() for _ in range(num_imus)]
        self.master_filter = self.create_master_filter()
        
    def create_local_filter(self):
        kf = KalmanFilter(dim_x=9, dim_z=6)
        kf.F = np.eye(9)
        kf.F[0:3, 3:6] = np.eye(3) * self.dt
        kf.F[3:6, 6:9] = np.eye(3) * self.dt
        
        kf.H = np.zeros((6, 9))
        kf.H[0:3, 0:3] = np.eye(3)
        kf.H[3:6, 6:9] = np.eye(3)
        
        kf.Q = np.eye(9) * 0.01
        kf.P = np.eye(9) * 10
        kf.R = np.eye(6) * 1
        return kf
        
    def create_master_filter(self):
        kf = KalmanFilter(dim_x=9, dim_z=18)
        kf.F = np.eye(9)
        kf.H = np.vstack([np.eye(9), np.eye(9)])
        kf.Q = np.eye(9) * 0.1
        kf.P = np.eye(9) * 10
        kf.R = np.eye(18) * 2
        return kf
        
    def predict_update(self, measurements):
        local_states = []
        for kf, z in zip(self.local_filters, measurements):
            kf.predict()
            kf.update(z)
            local_states.append(kf.x.flatten())
        
        self.master_filter.predict()
        self.master_filter.update(np.concatenate(local_states))
        return self.master_filter.x.flatten()

def load_and_sync_data(file1, file2):
    imu1 = pd.read_csv(file1)
    imu2 = pd.read_csv(file2)
    
    common_times = np.intersect1d(imu1['Time [ms]'], imu2['Time [ms]'])
    return (
        imu1[imu1['Time [ms]'].isin(common_times)].reset_index(drop=True),
        imu2[imu2['Time [ms]'].isin(common_times)].reset_index(drop=True)
    )

def transform_to_global(accel_local, angles_deg):
    rot = R.from_euler('xyz', angles_deg, degrees=True)
    return rot.apply(accel_local) - np.array([0, 0, 9.81])

def process_imus(file1, file2, distance=0.2, ref_point=0.5, offset_body=np.array([0.2, 0, 0])):
    imu1, imu2 = load_and_sync_data(file1, file2)
    federated_filter = FederatedFilter(delta_time=0.01)
    
    trajectory = []
    pos_imu1 = np.zeros(3)
    pos_imu2 = np.zeros(3)
    
    for i in range(len(imu1)):
        # IMU1
        acc1 = imu1.loc[i, ["Accel X [m/s^2]", "Accel Y [m/s^2]", "Accel Z [m/s^2]"]].values.astype(float)
        ang1 = imu1.loc[i, ["Angle X [deg]", "Angle Y [deg]", "Angle Z [deg]"]].values.astype(float)
        acc1_global = transform_to_global(acc1, ang1)
        
        # IMU2
        acc2 = imu2.loc[i, ["Accel X [m/s^2]", "Accel Y [m/s^2]", "Accel Z [m/s^2]"]].values.astype(float)
        ang2 = imu2.loc[i, ["Angle X [deg]", "Angle Y [deg]", "Angle Z [deg]"]].values.astype(float)
        acc2_global = transform_to_global(acc2, ang2)
        
        #Offset
        rot = R.from_euler('xyz', ang1, degrees=True)
        offset_global = rot.apply(offset_body)
        
        # Federated update
        fused_state = federated_filter.predict_update([
            np.concatenate([pos_imu1, acc1_global]),
            np.concatenate([pos_imu2, acc2_global])
        ])
        
        #Position update
        pos_imu1 = fused_state[0:3]
        pos_imu2 = pos_imu1 + offset_global
        
        # Refrence point
        ref_pos = (1 - ref_point)*pos_imu1 + ref_point*pos_imu2
        trajectory.append(ref_pos)
    
    return np.array(trajectory)

trajectory = process_imus('data.csv', 'data1.csv', distance=0.2)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(trajectory[:,0], trajectory[:,1], trajectory[:,2], linewidth=2)
ax.set_xlabel('X [m]'), ax.set_ylabel('Y [m]'), ax.set_zlabel('Z [m]')
plt.title('Trajektoria')
plt.show()
