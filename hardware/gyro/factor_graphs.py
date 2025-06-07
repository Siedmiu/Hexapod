import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as R
import warnings
import os.path
warnings.filterwarnings('ignore')

class DualIMUFactorGraph:
    def __init__(self):
        # Węzły grafu - stany w czasie
        self.poses = {}  # pozycja i orientacja
        self.velocities = {}  # prędkości
        self.biases = {}  # bias dla obu IMU
        
        # Faktory (ograniczenia)
        self.factors = []
        
        # Parametry
        self.gravity = np.array([0, 0, -9.81])
        self.dt = 0.01  # krok czasowy
        
        # Macierze szumu
        self.imu_noise = np.eye(6) * 0.01  # szum IMU [acc, gyro]
        self.consistency_noise = np.eye(6) * 0.1  # szum spójności
        self.zupt_noise = np.eye(3) * 0.001  # szum ZUPT
        
        # Względna transformacja między IMU (do estymacji)
        self.relative_transform = np.eye(4)
        
    def quaternion_multiply(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])
    
    def quaternion_to_rotation_matrix(self, q):
        w, x, y, z = q
        return np.array([
            [1-2*(y**2+z**2), 2*(x*y-w*z), 2*(x*z+w*y)],
            [2*(x*y+w*z), 1-2*(x**2+z**2), 2*(y*z-w*x)],
            [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x**2+y**2)]
        ])
    
    def euler_to_quaternion(self, roll, pitch, yaw):
        r = R.from_euler('xyz', [roll, pitch, yaw], degrees=True)
        return r.as_quat() 
    
    def detect_static_phase(self, acc_data, gyro_data, threshold=0.5):
        acc_magnitude = np.linalg.norm(acc_data, axis=1)
        gyro_magnitude = np.linalg.norm(gyro_data, axis=1)
        
        gravity_diff = np.abs(acc_magnitude - 9.81)
        is_static = (gravity_diff < threshold) & (gyro_magnitude < np.radians(10))
        
        return is_static
    
    def preintegrate_imu(self, acc_data, gyro_data, dt_values, bias_acc, bias_gyro):
        """Preintegracja pomiarów IMU"""
        delta_p = np.zeros(3)
        delta_v = np.zeros(3)
        delta_q = np.array([1, 0, 0, 0])  # w, x, y, z
        
        for i in range(len(acc_data)):
            # Korekcja bias
            acc_corrected = acc_data[i] - bias_acc
            gyro_corrected = gyro_data[i] - bias_gyro
            dt = dt_values[i]
            
            # Aktualizacja orientacji
            omega = gyro_corrected * dt
            omega_norm = np.linalg.norm(omega)
            
            if omega_norm > 1e-8:
                dq = np.array([
                    np.cos(omega_norm/2),
                    (omega[0]/omega_norm) * np.sin(omega_norm/2),
                    (omega[1]/omega_norm) * np.sin(omega_norm/2),
                    (omega[2]/omega_norm) * np.sin(omega_norm/2)
                ])
            else:
                dq = np.array([1, omega[0]/2, omega[1]/2, omega[2]/2])
            
            # Aktualizacja pozycji i prędkości
            R_matrix = self.quaternion_to_rotation_matrix(delta_q)
            delta_p += delta_v * dt + 0.5 * R_matrix @ acc_corrected * dt**2
            delta_v += R_matrix @ acc_corrected * dt
            delta_q = self.quaternion_multiply(delta_q, dq)
            delta_q = delta_q / np.linalg.norm(delta_q)
        
        return delta_p, delta_v, delta_q
    
    def add_imu_factor(self, t1, t2, imu_data, sensor_id):
        """Dodanie faktora IMU"""
        factor = {
            'type': 'imu',
            'time_start': t1,
            'time_end': t2,
            'sensor_id': sensor_id,
            'measurements': imu_data,
            'noise_model': self.imu_noise
        }
        self.factors.append(factor)
    
    def add_consistency_factor(self, timestamp, imu1_data, imu2_data):
        """Dodanie faktora spójności między IMU"""
        factor = {
            'type': 'consistency',
            'timestamp': timestamp,
            'imu1_data': imu1_data,
            'imu2_data': imu2_data,
            'noise_model': self.consistency_noise
        }
        self.factors.append(factor)
    
    def add_zupt_factor(self, timestamp, sensor_id):
        """Dodanie faktora ZUPT"""
        factor = {
            'type': 'zupt',
            'timestamp': timestamp,
            'sensor_id': sensor_id,
            'noise_model': self.zupt_noise
        }
        self.factors.append(factor)
    
    def compute_residuals(self, state_vector):
        """Obliczenie residuów dla wszystkich faktorów"""
        residuals = []
        
        # Rozpakowanie wektora stanu
        n_poses = len(self.poses)
        pose_dim = 7  # [x, y, z, qw, qx, qy, qz]
        vel_dim = 3   # [vx, vy, vz]
        bias_dim = 6  # [bias_acc_x, bias_acc_y, bias_acc_z, bias_gyro_x, bias_gyro_y, bias_gyro_z]
        
        poses = state_vector[:n_poses * pose_dim].reshape(n_poses, pose_dim)
        velocities = state_vector[n_poses * pose_dim:n_poses * (pose_dim + vel_dim)].reshape(n_poses, vel_dim)
        biases = state_vector[n_poses * (pose_dim + vel_dim):].reshape(-1, bias_dim)
        
        for factor in self.factors:
            if factor['type'] == 'imu':
                # Residuum faktora IMU
                t1_idx = list(self.poses.keys()).index(factor['time_start'])
                t2_idx = list(self.poses.keys()).index(factor['time_end'])
                
                pose1 = poses[t1_idx]
                pose2 = poses[t2_idx]
                vel1 = velocities[t1_idx]
                vel2 = velocities[t2_idx]
                
                sensor_idx = 0 if factor['sensor_id'] == 'imu1' else 1
                bias = biases[sensor_idx]
                
                # Preintegracja
                acc_data = factor['measurements']['acc']
                gyro_data = factor['measurements']['gyro']
                dt_values = factor['measurements']['dt']
                
                delta_p, delta_v, delta_q = self.preintegrate_imu(
                    acc_data, gyro_data, dt_values, bias[:3], bias[3:]
                )
                
                # Przewidywana zmiana stanu
                R1 = self.quaternion_to_rotation_matrix(pose1[3:])
                total_dt = np.sum(dt_values)
                
                predicted_p2 = pose1[:3] + vel1 * total_dt + 0.5 * self.gravity * total_dt**2 + R1 @ delta_p
                predicted_v2 = vel1 + self.gravity * total_dt + R1 @ delta_v
                predicted_q2 = self.quaternion_multiply(pose1[3:], delta_q)
                
                # Residuum
                pos_residual = pose2[:3] - predicted_p2
                vel_residual = vel2 - predicted_v2
                
                # Residuum orientacji (różnica kwaternionów)
                q_error = self.quaternion_multiply(pose2[3:], 
                                                 np.array([predicted_q2[0], -predicted_q2[1], -predicted_q2[2], -predicted_q2[3]]))
                ori_residual = q_error[1:4]  # część wektorowa
                
                factor_residual = np.concatenate([pos_residual, vel_residual, ori_residual])
                residuals.extend(factor_residual)
                
            elif factor['type'] == 'zupt':
                # Residuum ZUPT (prędkość powinna być zero)
                t_idx = list(self.poses.keys()).index(factor['timestamp'])
                vel = velocities[t_idx]
                residuals.extend(vel)
            
            elif factor['type'] == 'consistency':
                # Residuum spójności między IMU
                # Uproszczona implementacja - porównanie przyspieszenia
                acc1 = factor['imu1_data']['acc']
                acc2 = factor['imu2_data']['acc']
                
                # Różnica w pomiarach (po transformacji)
                acc_diff = np.mean(acc1, axis=0) - np.mean(acc2, axis=0)
                gyro1 = factor['imu1_data']['gyro']
                gyro2 = factor['imu2_data']['gyro']
                gyro_diff = np.mean(gyro1, axis=0) - np.mean(gyro2, axis=0)
                
                consistency_residual = np.concatenate([acc_diff, gyro_diff])
                residuals.extend(consistency_residual)
        
        return np.array(residuals)
    
    def optimize(self, max_iterations=50):
        # Inicjalizacja wektora stanu
        n_poses = len(self.poses)
        n_sensors = 2
        
        # Wektor stanu: [poses, velocities, biases]
        pose_dim = 7  # [x, y, z, qw, qx, qy, qz]
        vel_dim = 3   # [vx, vy, vz]
        bias_dim = 6  # [bias_acc, bias_gyro]
        
        state_size = n_poses * (pose_dim + vel_dim) + n_sensors * bias_dim
        initial_state = np.zeros(state_size)
        
        # Inicjalizacja pozycji i orientacji
        for i, (timestamp, pose) in enumerate(self.poses.items()):
            start_idx = i * pose_dim
            initial_state[start_idx:start_idx + 3] = pose[:3]  # pozycja
            initial_state[start_idx + 3:start_idx + 7] = pose[3:]  # kwaternion
        
        # Inicjalizacja prędkości (zero)
        vel_start = n_poses * pose_dim
        
        # Inicjalizacja bias (małe wartości losowe)
        bias_start = n_poses * (pose_dim + vel_dim)
        initial_state[bias_start:] = np.random.normal(0, 0.01, n_sensors * bias_dim)
        
        try:
            result = least_squares(self.compute_residuals, initial_state, 
                                 max_nfev=max_iterations * len(initial_state))
            
            # Rozpakowanie wyników
            optimized_state = result.x
            poses_opt = optimized_state[:n_poses * pose_dim].reshape(n_poses, pose_dim)
            velocities_opt = optimized_state[n_poses * pose_dim:n_poses * (pose_dim + vel_dim)].reshape(n_poses, vel_dim)
            biases_opt = optimized_state[n_poses * (pose_dim + vel_dim):].reshape(n_sensors, bias_dim)
            
            return poses_opt, velocities_opt, biases_opt, result.success
            
        except Exception as e:
            print(f"Błąd optymalizacji: {e}")
            return None, None, None, False

def load_and_process_imu_data(file1, file2):
    try:
        if not os.path.exists(file1):
            print(f"Błąd: Nie znaleziono pliku '{file1}'")
            return None, None
        if not os.path.exists(file2):
            print(f"Błąd: Nie znaleziono pliku '{file2}'")
            return None, None
        
        imu1_data = pd.read_csv(file1)
        imu2_data = pd.read_csv(file2)
        
        print(f"Wczytano {len(imu1_data)} próbek z IMU1 i {len(imu2_data)} próbek z IMU2")
        
        required_columns = ['time', 'a_x', 'a_y', 'a_z', 'roll', 'pitch', 'yaw']
        
        for col in required_columns:
            if col not in imu1_data.columns:
                raise ValueError(f"Brak kolumny '{col}' w pliku {file1}")
            if col not in imu2_data.columns:
                raise ValueError(f"Brak kolumny '{col}' w pliku {file2}")
        
        imu1_data['time'] = imu1_data['time'] / 1000.0
        imu2_data['time'] = imu2_data['time'] / 1000.0
        
        for col in ['roll', 'pitch', 'yaw']:
            imu1_data[col] = np.radians(imu1_data[col])
            imu2_data[col] = np.radians(imu2_data[col])
        
        return imu1_data, imu2_data
        
    except FileNotFoundError as e:
        print(f"Błąd: Nie znaleziono pliku: {e}")
        return None, None
    except ValueError as e:
        print(f"Błąd struktury danych: {e}")
        return None, None
    except Exception as e:
        print(f"Błąd wczytywania danych: {e}")
        return None, None

def main():

    imu1_data, imu2_data = load_and_process_imu_data('data.csv', 'data1.csv')
    
    if imu1_data is None or imu2_data is None:
        print("\n" + "="*60)
        print("ERROR!")
        return
    
    if len(imu1_data) == 0 or len(imu2_data) == 0:
        print("\nBŁĄD: Wczytane pliki są puste!")
        print("Sprawdź czy pliki 'data.csv' i 'data1.csv' zawierają dane.")
        return

    min_time = max(imu1_data['time'].min(), imu2_data['time'].min())
    max_time = min(imu1_data['time'].max(), imu2_data['time'].max())
    
    # Sprawdzenie czy zakresy czasowe się pokrywają
    if min_time >= max_time:
        print("\nBŁĄD: Zakresy czasowe danych z obu IMU nie pokrywają się!")
        print(f"IMU1: {imu1_data['time'].min():.2f} - {imu1_data['time'].max():.2f}s")
        print(f"IMU2: {imu2_data['time'].min():.2f} - {imu2_data['time'].max():.2f}s")
        return
    
    # Filtrowanie danych do wspólnego zakresu czasowego
    imu1_sync = imu1_data[(imu1_data['time'] >= min_time) & (imu1_data['time'] <= max_time)].copy()
    imu2_sync = imu2_data[(imu2_data['time'] >= min_time) & (imu2_data['time'] <= max_time)].copy()
    
    if len(imu1_sync) < 10 or len(imu2_sync) < 10:
        print(f"\nBŁĄD: Za mało danych w wspólnym zakresie czasowym!")
        print(f"IMU1: {len(imu1_sync)} próbek, IMU2: {len(imu2_sync)} próbek")
        print("Potrzeba co najmniej 10 próbek z każdego IMU.")
        return
    
    print(f"Synchronizacja: {len(imu1_sync)} próbek z IMU1 i {len(imu2_sync)} próbek z IMU2")
    print(f"Zakres czasowy: {min_time:.2f}-{max_time:.2f}s")
    
    # Tworzenie grafu faktorów
    graph = DualIMUFactorGraph()
    
    # Inicjalizacja stanów
    window_size = 50  # Przetwarzaj w oknach po 50 próbek
    n_windows = min(len(imu1_sync), len(imu2_sync)) // window_size
    
    if n_windows == 0:
        print(f"\nBŁĄD: Za mało danych do przetworzenia!")
        print(f"Potrzeba co najmniej {window_size} próbek, dostępne: {min(len(imu1_sync), len(imu2_sync))}")
        return
    
    trajectory = []
    timestamps = []
    
    print(f"\nRozpoczynanie przetwarzania {min(n_windows, 20)} okien danych...")
    
    for window in range(min(n_windows, 20)):  # Ograniczenie do 20 okien dla szybkości
        start_idx = window * window_size
        end_idx = (window + 1) * window_size
        
        # Dane dla aktualnego okna
        imu1_window = imu1_sync.iloc[start_idx:end_idx]
        imu2_window = imu2_sync.iloc[start_idx:end_idx]
        
        if len(imu1_window) < 10 or len(imu2_window) < 10:
            continue
        
        # Detekcja faz statycznych
        imu1_acc = imu1_window[['a_x', 'a_y', 'a_z']].values
        imu1_gyro = imu1_window[['roll', 'pitch', 'yaw']].values
        imu2_acc = imu2_window[['a_x', 'a_y', 'a_z']].values
        imu2_gyro = imu2_window[['roll', 'pitch', 'yaw']].values
        
        imu1_static = graph.detect_static_phase(imu1_acc, imu1_gyro)
        imu2_static = graph.detect_static_phase(imu2_acc, imu2_gyro)
        
        # Dodanie stanów do grafu
        t_start = imu1_window['time'].iloc[0]
        t_end = imu1_window['time'].iloc[-1]
        
        # Inicjalizacja pozycji (prosta integracja)
        if window == 0:
            initial_pos = np.array([0, 0, 0])
            initial_ori = np.array([1, 0, 0, 0])  # kwaternion jednostkowy
        else:
            initial_pos = trajectory[-1][:3]
            initial_ori = trajectory[-1][3:]
        
        graph.poses[t_start] = np.concatenate([initial_pos, initial_ori])
        graph.velocities[t_start] = np.zeros(3)
        
        # Prosta estymacja następnej pozycji
        dt_values = np.diff(imu1_window['time'].values)
        if len(dt_values) == 0:
            dt_values = np.array([0.01])
        
        # Średnie przyspieszenie z obu IMU
        avg_acc = (np.mean(imu1_acc, axis=0) + np.mean(imu2_acc, axis=0)) / 2
        avg_acc[2] -= 9.81  # usunięcie grawitacji
        
        # Prosta integracja
        total_dt = np.sum(dt_values)
        next_pos = initial_pos + 0.5 * avg_acc * total_dt**2
        
        graph.poses[t_end] = np.concatenate([next_pos, initial_ori])
        graph.velocities[t_end] = avg_acc * total_dt
        
        # Dodanie faktorów IMU
        imu1_measurements = {
            'acc': imu1_acc,
            'gyro': imu1_gyro,
            'dt': dt_values
        }
        
        imu2_measurements = {
            'acc': imu2_acc,
            'gyro': imu2_gyro,
            'dt': dt_values
        }
        
        graph.add_imu_factor(t_start, t_end, imu1_measurements, 'imu1')
        graph.add_imu_factor(t_start, t_end, imu2_measurements, 'imu2')
        
        # Dodanie faktorów ZUPT jeśli wykryto fazę statyczną
        if np.any(imu1_static):
            graph.add_zupt_factor(t_start, 'imu1')
        if np.any(imu2_static):
            graph.add_zupt_factor(t_start, 'imu2')
        
        # Dodanie faktora spójności
        graph.add_consistency_factor(t_start, 
                                   {'acc': imu1_acc, 'gyro': imu1_gyro},
                                   {'acc': imu2_acc, 'gyro': imu2_gyro})
        
        trajectory.append(np.concatenate([next_pos, initial_ori]))
        timestamps.append(t_end)
        
        print(f"Okno {window+1}/{min(n_windows, 20)}: pozycja = [{next_pos[0]:.2f}, {next_pos[1]:.2f}, {next_pos[2]:.2f}]")
    
    print("\nRozpoczynanie optymalizacji grafu faktorów...")
    
    if len(graph.poses) > 1:
        poses_opt, velocities_opt, biases_opt, success = graph.optimize()
        
        if success and poses_opt is not None:
            print("Optymalizacja zakończona sukcesem!")
            trajectory_opt = poses_opt[:, :3]  # tylko pozycje
        else:
            print("Optymalizacja nie powiodła się, używam prostej integracji")
            trajectory_opt = np.array([traj[:3] for traj in trajectory])
    else:
        trajectory_opt = np.array([traj[:3] for traj in trajectory])
    
    # Wizualizacja wyników
    plt.figure(figsize=(15, 10))
    
    # Wykres 1: Trajektoria 3D
    ax1 = plt.subplot(2, 3, 1, projection='3d')
    if len(trajectory_opt) > 0:
        ax1.plot(trajectory_opt[:, 0], trajectory_opt[:, 1], trajectory_opt[:, 2], 'b-', linewidth=2, label='Trajektoria')
        ax1.scatter([trajectory_opt[0, 0]], [trajectory_opt[0, 1]], [trajectory_opt[0, 2]], color='green', s=100, label='Start')
        ax1.scatter([trajectory_opt[-1, 0]], [trajectory_opt[-1, 1]], [trajectory_opt[-1, 2]], color='red', s=100, label='Koniec')
    ax1.set_xlabel('X [m]')
    ax1.set_ylabel('Y [m]')
    ax1.set_zlabel('Z [m]')
    ax1.set_title('Trajektoria 3D')
    ax1.legend()
    
    # Wykres 2: Pozycja X, Y w czasie
    ax2 = plt.subplot(2, 3, 2)
    if len(trajectory_opt) > 0 and len(timestamps) > 0:
        ax2.plot(timestamps[:len(trajectory_opt)], trajectory_opt[:, 0], 'r-', label='X')
        ax2.plot(timestamps[:len(trajectory_opt)], trajectory_opt[:, 1], 'g-', label='Y')
    ax2.set_xlabel('Czas [s]')
    ax2.set_ylabel('Pozycja [m]')
    ax2.set_title('Pozycja X, Y w czasie')
    ax2.legend()
    ax2.grid(True)
    
    # Wykres 3: Pozycja Z w czasie
    ax3 = plt.subplot(2, 3, 3)
    if len(trajectory_opt) > 0 and len(timestamps) > 0:
        ax3.plot(timestamps[:len(trajectory_opt)], trajectory_opt[:, 2], 'b-', label='Z')
    ax3.set_xlabel('Czas [s]')
    ax3.set_ylabel('Pozycja Z [m]')
    ax3.set_title('Wysokość w czasie')
    ax3.legend()
    ax3.grid(True)
    
    # Wykres 4: Porównanie przyspieszenia z obu IMU
    ax4 = plt.subplot(2, 3, 4)
    sample_range = slice(0, min(200, len(imu1_sync)))
    ax4.plot(imu1_sync['time'].iloc[sample_range], imu1_sync['a_x'].iloc[sample_range], 'r-', alpha=0.7, label='IMU1 ax')
    ax4.plot(imu2_sync['time'].iloc[sample_range], imu2_sync['a_x'].iloc[sample_range], 'r--', alpha=0.7, label='IMU2 ax')
    ax4.set_xlabel('Czas [s]')
    ax4.set_ylabel('Przyspieszenie [m/s²]')
    ax4.set_title('Porównanie IMU1 vs IMU2')
    ax4.legend()
    ax4.grid(True)
    
    # Wykres 5: Trajektoria 2D (widok z góry)
    ax5 = plt.subplot(2, 3, 5)
    if len(trajectory_opt) > 0:
        ax5.plot(trajectory_opt[:, 0], trajectory_opt[:, 1], 'b-', linewidth=2)
        ax5.scatter([trajectory_opt[0, 0]], [trajectory_opt[0, 1]], color='green', s=100, label='Start')
        ax5.scatter([trajectory_opt[-1, 0]], [trajectory_opt[-1, 1]], color='red', s=100, label='Koniec')
    ax5.set_xlabel('X [m]')
    ax5.set_ylabel('Y [m]')
    ax5.set_title('Trajektoria 2D (widok z góry)')
    ax5.legend()
    ax5.grid(True)
    ax5.axis('equal')
    
    # Wykres 6: Statystyki
    ax6 = plt.subplot(2, 3, 6)
    stats_text = f"""Statystyki:
    
Liczba próbek IMU1: {len(imu1_sync)}
Liczba próbek IMU2: {len(imu2_sync)}
Czas trwania: {max_time - min_time:.1f}s
Liczba okien: {len(trajectory)}

Trajektoria:
Długość: {np.sum(np.linalg.norm(np.diff(trajectory_opt, axis=0), axis=1)) if len(trajectory_opt) > 1 else 0:.2f}m
Zasięg X: {np.ptp(trajectory_opt[:, 0]) if len(trajectory_opt) > 0 else 0:.2f}m
Zasięg Y: {np.ptp(trajectory_opt[:, 1]) if len(trajectory_opt) > 0 else 0:.2f}m
Zasięg Z: {np.ptp(trajectory_opt[:, 2]) if len(trajectory_opt) > 0 else 0:.2f}m
    """
    ax6.text(0.1, 0.5, stats_text, transform=ax6.transAxes, fontsize=10, verticalalignment='center')
    ax6.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    print(f"\nRekonstrukcja trajektorii zakończona!")
    print(f"Przetworzono {len(trajectory)} punktów trajektorii")
    if len(trajectory_opt) > 1:
        total_distance = np.sum(np.linalg.norm(np.diff(trajectory_opt, axis=0), axis=1))
        print(f"Całkowita długość trajektorii: {total_distance:.2f} m")

if __name__ == "__main__":
    main()
