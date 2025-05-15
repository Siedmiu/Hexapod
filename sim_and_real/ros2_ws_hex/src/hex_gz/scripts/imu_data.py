#!/usr/bin/env python3

"""
Program do odczytu danych IMU z ESP32 przez port szeregowy
i tworzenia interaktywnych wykresów w czasie rzeczywistym.
"""

import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import threading
import argparse
import numpy as np

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
        """Inicjalizacja wykresów."""
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 12))
        plt.tight_layout(pad=3.0)
        
        # Wykres kwaternionów
        self.ax1.set_title('Orientacja (Kwaterniony)')
        self.ax1.set_ylabel('Wartość')
        self.ax1.set_xlabel('Czas (s)')
        self.ax1.grid(True)
        
        # Wykres kątów Eulera
        self.ax2.set_title('Orientacja (Kąty Eulera)')
        self.ax2.set_ylabel('Kąt (stopnie)')
        self.ax2.set_xlabel('Czas (s)')
        self.ax2.grid(True)
        
        # Wykres przyspieszenia
        self.ax3.set_title('Przyspieszenie liniowe')
        self.ax3.set_ylabel('Przyspieszenie (g)')
        self.ax3.set_xlabel('Czas (s)')
        self.ax3.grid(True)
        
        # Linie dla kwaternionów
        self.line_qw, = self.ax1.plot([], [], 'r-', label='qw')
        self.line_qx, = self.ax1.plot([], [], 'g-', label='qx')
        self.line_qy, = self.ax1.plot([], [], 'b-', label='qy')
        self.line_qz, = self.ax1.plot([], [], 'y-', label='qz')
        self.ax1.legend()
        
        # Linie dla kątów Eulera
        self.line_roll, = self.ax2.plot([], [], 'r-', label='Roll')
        self.line_pitch, = self.ax2.plot([], [], 'g-', label='Pitch')
        self.line_yaw, = self.ax2.plot([], [], 'b-', label='Yaw')
        self.ax2.legend()
        
        # Linie dla przyspieszenia
        self.line_accel_x, = self.ax3.plot([], [], 'r-', label='X')
        self.line_accel_y, = self.ax3.plot([], [], 'g-', label='Y')
        self.line_accel_z, = self.ax3.plot([], [], 'b-', label='Z')
        self.ax3.legend()
        
        plt.tight_layout()
        
        # Inicjalizacja animacji
        self.ani = FuncAnimation(
            self.fig, 
            self.update_plot, 
            interval=UPDATE_INTERVAL,
            blit=True
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
        """Aktualizacja wykresu z nowymi danymi."""
        # Jeśli dane nie są jeszcze dostępne, zwróć puste linie
        if not self.timestamps or not self.initialized:
            return [self.line_qw, self.line_qx, self.line_qy, self.line_qz,
                   self.line_roll, self.line_pitch, self.line_yaw,
                   self.line_accel_x, self.line_accel_y, self.line_accel_z]
        
        # Konwersja deque na listy dla matplotlib
        timestamps_list = list(self.timestamps)
        
        # Aktualizacja linii dla kwaternionów
        self.line_qw.set_data(timestamps_list, list(self.qw))
        self.line_qx.set_data(timestamps_list, list(self.qx))
        self.line_qy.set_data(timestamps_list, list(self.qy))
        self.line_qz.set_data(timestamps_list, list(self.qz))
        
        # Aktualizacja linii dla kątów Eulera
        self.line_roll.set_data(timestamps_list, list(self.roll))
        self.line_pitch.set_data(timestamps_list, list(self.pitch))
        self.line_yaw.set_data(timestamps_list, list(self.yaw))
        
        # Aktualizacja linii dla przyspieszenia
        self.line_accel_x.set_data(timestamps_list, list(self.accel_x))
        self.line_accel_y.set_data(timestamps_list, list(self.accel_y))
        self.line_accel_z.set_data(timestamps_list, list(self.accel_z))
        
        # Automatyczne dostosowywanie zakresu osi
        if len(timestamps_list) > 1:
            # Zakres osi X (czas)
            x_min = min(timestamps_list)
            x_max = max(timestamps_list)
            x_range = max(0.1, x_max - x_min)
            
            # Aktualizacja ograniczeń osi X dla wszystkich wykresów
            self.ax1.set_xlim(x_min, x_max + 0.05 * x_range)
            self.ax2.set_xlim(x_min, x_max + 0.05 * x_range)
            self.ax3.set_xlim(x_min, x_max + 0.05 * x_range)
            
            # Zakres osi Y dla kwaternionów
            quat_min = min(min(self.qw), min(self.qx), min(self.qy), min(self.qz))
            quat_max = max(max(self.qw), max(self.qx), max(self.qy), max(self.qz))
            quat_range = max(0.1, quat_max - quat_min)
            self.ax1.set_ylim(quat_min - 0.05 * quat_range, quat_max + 0.05 * quat_range)
            
            # Zakres osi Y dla kątów Eulera
            euler_min = min(min(self.roll), min(self.pitch), min(self.yaw))
            euler_max = max(max(self.roll), max(self.pitch), max(self.yaw))
            euler_range = max(10, euler_max - euler_min)
            self.ax2.set_ylim(euler_min - 0.05 * euler_range, euler_max + 0.05 * euler_range)
            
            # Zakres osi Y dla przyspieszenia
            accel_min = min(min(self.accel_x), min(self.accel_y), min(self.accel_z))
            accel_max = max(max(self.accel_x), max(self.accel_y), max(self.accel_z))
            accel_range = max(0.1, accel_max - accel_min)
            self.ax3.set_ylim(accel_min - 0.05 * accel_range, accel_max + 0.05 * accel_range)
        
        # Zwróć zaktualizowane linie
        return [self.line_qw, self.line_qx, self.line_qy, self.line_qz,
               self.line_roll, self.line_pitch, self.line_yaw,
               self.line_accel_x, self.line_accel_y, self.line_accel_z]
    
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
    parser = argparse.ArgumentParser(description="Plotowanie danych IMU z ESP32")
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