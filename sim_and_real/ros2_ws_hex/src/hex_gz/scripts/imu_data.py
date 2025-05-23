#!/usr/bin/env python3

"""
Program do odczytu danych IMU z ESP32 przez port szeregowy
i tworzenia interaktywnych wykresów 3D w czasie rzeczywistym.
"""

import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import threading
import argparse
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Parametry konfiguracyjne
BUFFER_SIZE = 100  # Liczba punktów do wyświetlenia na wykresie
UPDATE_INTERVAL = 50  # Interwał aktualizacji wykresu (ms)

class ImuPlotter:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        """Inicjalizacja plotera danych IMU."""
        # Inicjalizacja połączenia szeregowego
        self.serial = None
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        
        # Bufory danych do przechowywania ostatnich odczytów
        self.timestamps = deque(maxlen=BUFFER_SIZE)
        self.qw = deque(maxlen=BUFFER_SIZE)
        self.qx = deque(maxlen=BUFFER_SIZE)
        self.qy = deque(maxlen=BUFFER_SIZE)
        self.qz = deque(maxlen=BUFFER_SIZE)
        self.roll = deque(maxlen=BUFFER_SIZE)
        self.pitch = deque(maxlen=BUFFER_SIZE)
        self.yaw = deque(maxlen=BUFFER_SIZE)
        self.accel_x = deque(maxlen=BUFFER_SIZE)
        self.accel_y = deque(maxlen=BUFFER_SIZE)
        self.accel_z = deque(maxlen=BUFFER_SIZE)
        
        # Czas początkowy dla relatywnego wyświetlania czasu
        self.start_time = None
        
        # Flagi dla kontroli wątków
        self.running = True
        self.initialized = False
        
        # Inicjalizacja wykresów
        self.fig = None
        self.ani = None
        
        # Uruchom wątek połączenia z portem szeregowym
        self.connect_thread = threading.Thread(target=self.connect_serial)
        self.connect_thread.daemon = True
        self.connect_thread.start()
    
    def connect_serial(self):
        """Ustanawia połączenie z ESP32 przez port szeregowy."""
        while self.running and not self.connected:
            try:
                self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
                self.connected = True
                print(f"Połączono z {self.port} przy {self.baudrate} baud")
                
                # Uruchom wątek odczytu danych
                self.reader_thread = threading.Thread(target=self.read_serial_data)
                self.reader_thread.daemon = True
                self.reader_thread.start()
            except Exception as e:
                print(f"Błąd połączenia: {e}")
                time.sleep(2)
    
    def init_plots(self):
        """Inicjalizacja wykresów 3D."""
        self.fig = plt.figure(figsize=(15, 12))
        
        # Wykres 3D dla kwaternionów
        self.ax1 = self.fig.add_subplot(131, projection='3d')
        self.ax1.set_title('Orientacja (Kwaterniony)')
        self.ax1.set_xlabel('Czas (s)')
        self.ax1.set_ylabel('Składowa')
        self.ax1.set_zlabel('Wartość')
        
        # Wykres 3D dla kątów Eulera
        self.ax2 = self.fig.add_subplot(132, projection='3d')
        self.ax2.set_title('Orientacja (Kąty Eulera)')
        self.ax2.set_xlabel('Czas (s)')
        self.ax2.set_ylabel('Oś')
        self.ax2.set_zlabel('Kąt (stopnie)')
        
        # Wykres 3D dla przyspieszenia
        self.ax3 = self.fig.add_subplot(133, projection='3d')
        self.ax3.set_title('Przyspieszenie liniowe')
        self.ax3.set_xlabel('Czas (s)')
        self.ax3.set_ylabel('Oś')
        self.ax3.set_zlabel('Przyspieszenie (g)')
        
        # Tutaj będziemy przechowywać obiekty scatter dla każdego wykresu
        self.scatter_quat = None
        self.scatter_euler = None
        self.scatter_accel = None
        
        plt.tight_layout()
        
        # Inicjalizacja animacji
        self.ani = FuncAnimation(
            self.fig, 
            self.update_plot, 
            interval=UPDATE_INTERVAL,
            blit=False  # Blit=False dla wykresów 3D
        )
    
    def read_serial_data(self):
        """Ciągły odczyt danych z portu szeregowego."""
        init_line_found = False
        
        while self.running and self.connected:
            try:
                # Czytaj linię z portu szeregowego
                line = self.serial.readline().decode('utf-8').strip()
                
                # Czekaj na linię inicjalizacyjną
                if "IMU_DATA_START" in line:
                    init_line_found = True
                    print("Znaleziono nagłówek danych IMU")
                    continue
                
                # Pomijaj linie nagłówków
                if "timestamp" in line or not line:
                    continue
                
                # Jeśli inicjalizacja nie została zakończona, pomiń
                if not init_line_found:
                    continue
                
                # Sprawdź, czy linia zawiera dane IMU z prefixem F,
                if line.startswith("F,"):
                    # Usuń prefix "F," i podziel linię po przecinkach
                    values = line[2:].split(',')
                    
                    # Sprawdź, czy linia zawiera wszystkie oczekiwane wartości
                    if len(values) >= 11:
                        # Zapisz timestamp pierwszego odczytu jako czas początkowy
                        if self.start_time is None:
                            self.start_time = float(values[0]) / 1000.0  # ms -> s
                            self.initialized = True
                        
                        # Oblicz czas względny
                        timestamp = float(values[0]) / 1000.0  # ms -> s
                        relative_time = timestamp - self.start_time
                        
                        # Dodaj dane do buforów
                        self.timestamps.append(relative_time)
                        self.qw.append(float(values[1]))
                        self.qx.append(float(values[2]))
                        self.qy.append(float(values[3]))
                        self.qz.append(float(values[4]))
                        self.roll.append(float(values[5]))
                        self.pitch.append(float(values[6]))
                        self.yaw.append(float(values[7]))
                        self.accel_x.append(float(values[8]))
                        self.accel_y.append(float(values[9]))
                        self.accel_z.append(float(values[10]))
            except Exception as e:
                print(f"Błąd odczytu danych: {e}")
                self.connected = False
                # Próbuj ponownie nawiązać połączenie
                self.connect_thread = threading.Thread(target=self.connect_serial)
                self.connect_thread.daemon = True
                self.connect_thread.start()
                break
    
    def update_plot(self, frame):
        """Aktualizacja wykresów 3D z nowymi danymi."""
        # Jeśli dane nie są jeszcze dostępne, nic nie rób
        if not self.timestamps or not self.initialized:
            return
        
        # Konwersja deque na listy dla matplotlib
        timestamps_list = list(self.timestamps)
        
        # Wyczyść poprzednie dane
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Ustaw etykiety i tytuły
        self.ax1.set_title('Orientacja (Kwaterniony)')
        self.ax1.set_xlabel('Czas (s)')
        self.ax1.set_ylabel('Składowa')
        self.ax1.set_zlabel('Wartość')
        
        self.ax2.set_title('Orientacja (Kąty Eulera)')
        self.ax2.set_xlabel('Czas (s)')
        self.ax2.set_ylabel('Oś')
        self.ax2.set_zlabel('Kąt (stopnie)')
        
        self.ax3.set_title('Przyspieszenie liniowe')
        self.ax3.set_xlabel('Czas (s)')
        self.ax3.set_ylabel('Oś')
        self.ax3.set_zlabel('Przyspieszenie (g)')
        
        # Przygotowanie danych dla wykresu kwaternionów
        for i, (qdata, label, color) in enumerate(zip(
            [self.qw, self.qx, self.qy, self.qz], 
            ['qw', 'qx', 'qy', 'qz'], 
            ['r', 'g', 'b', 'y']
        )):
            # Tworzymy tablicę Y dla składowych kwaterniona (0=qw, 1=qx, 2=qy, 3=qz)
            y_values = np.ones(len(timestamps_list)) * i
            self.ax1.plot3D(timestamps_list, y_values, list(qdata), color, label=label)
        
        # Przygotowanie danych dla wykresu kątów Eulera
        for i, (euler_data, label, color) in enumerate(zip(
            [self.roll, self.pitch, self.yaw], 
            ['Roll', 'Pitch', 'Yaw'], 
            ['r', 'g', 'b']
        )):
            # Tworzymy tablicę Y dla składowych Eulera (0=roll, 1=pitch, 2=yaw)
            y_values = np.ones(len(timestamps_list)) * i
            self.ax2.plot3D(timestamps_list, y_values, list(euler_data), color, label=label)
        
        # Przygotowanie danych dla wykresu przyspieszenia
        for i, (accel_data, label, color) in enumerate(zip(
            [self.accel_x, self.accel_y, self.accel_z], 
            ['X', 'Y', 'Z'], 
            ['r', 'g', 'b']
        )):
            # Tworzymy tablicę Y dla składowych przyspieszenia (0=X, 1=Y, 2=Z)
            y_values = np.ones(len(timestamps_list)) * i
            self.ax3.plot3D(timestamps_list, y_values, list(accel_data), color, label=label)
        
        # Dodaj legendy
        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()
        
        # Automatyczne dostosowywanie zakresu osi
        if len(timestamps_list) > 1:
            # Zakres osi X (czas)
            x_min = min(timestamps_list)
            x_max = max(timestamps_list)
            x_range = max(0.1, x_max - x_min)
            
            # Zakres osi Y pozostaje stały (reprezentuje różne składowe)
            
            # Dopasowanie zakresu dla kwaternionów
            quat_min = min(min(self.qw), min(self.qx), min(self.qy), min(self.qz))
            quat_max = max(max(self.qw), max(self.qx), max(self.qy), max(self.qz))
            quat_range = max(0.1, quat_max - quat_min)
            
            # Dopasowanie zakresu dla kątów Eulera
            euler_min = min(min(self.roll), min(self.pitch), min(self.yaw))
            euler_max = max(max(self.roll), max(self.pitch), max(self.yaw))
            euler_range = max(10, euler_max - euler_min)
            
            # Dopasowanie zakresu dla przyspieszenia
            accel_min = min(min(self.accel_x), min(self.accel_y), min(self.accel_z))
            accel_max = max(max(self.accel_x), max(self.accel_y), max(self.accel_z))
            accel_range = max(0.1, accel_max - accel_min)
            
            # Ustawienie zakresów
            self.ax1.set_xlim(x_min, x_max + 0.05 * x_range)
            self.ax1.set_ylim(-0.5, 3.5)  # 4 składowe: qw, qx, qy, qz
            self.ax1.set_zlim(quat_min - 0.05 * quat_range, quat_max + 0.05 * quat_range)
            
            self.ax2.set_xlim(x_min, x_max + 0.05 * x_range)
            self.ax2.set_ylim(-0.5, 2.5)  # 3 składowe: roll, pitch, yaw
            self.ax2.set_zlim(euler_min - 0.05 * euler_range, euler_max + 0.05 * euler_range)
            
            self.ax3.set_xlim(x_min, x_max + 0.05 * x_range)
            self.ax3.set_ylim(-0.5, 2.5)  # 3 składowe: X, Y, Z
            self.ax3.set_zlim(accel_min - 0.05 * accel_range, accel_max + 0.05 * accel_range)
    
    def run(self):
        """Uruchom plotowanie w trybie interaktywnym."""
        # Inicjalizacja wykresów
        self.init_plots()
        plt.show(block=True)
    
    def close(self):
        """Zamknij połączenie i zasoby."""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Połączenie szeregowe zamknięte")
        plt.close(self.fig)

if __name__ == "__main__":
    # Parsowanie argumentów linii poleceń
    parser = argparse.ArgumentParser(description="Plotowanie danych IMU z ESP32 w 3D")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", 
                        help="Port szeregowy (domyślnie: /dev/ttyUSB0)")
    parser.add_argument("--baudrate", type=int, default=115200, 
                        help="Prędkość transmisji (domyślnie: 115200)")
    args = parser.parse_args()
    
    try:
        # Utwórz i uruchom ploter
        plotter = ImuPlotter(port=args.port, baudrate=args.baudrate)
        plotter.run()
    except KeyboardInterrupt:
        print("Program przerwany przez użytkownika")
    finally:
        # Upewnij się, że wszystkie zasoby zostały zwolnione
        if 'plotter' in locals():
            plotter.close()