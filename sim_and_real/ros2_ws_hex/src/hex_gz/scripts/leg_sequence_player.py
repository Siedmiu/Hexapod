#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from rosgraph_msgs.msg import Clock
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation


matplotlib.use('TkAgg')

def katy_serw(P3, l1, l2, l3):
    # wyznaczenie katow potrzebnych do osiagniecia przez stope punktu docelowego
    alfa_1 = np.arctan2(P3[1], P3[0])

    P1 = np.array([l1 * np.cos(alfa_1), l1 * np.sin(alfa_1), 0])

    d = np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2 + (P3[2] - P1[2]) ** 2)

    cos_fi = (l2 ** 2 + l3 ** 2 - d ** 2) / (2 * l2 * l3)
    fi = np.arccos(cos_fi)
    alfa_3 = np.deg2rad(180) - fi

    epsilon = np.arcsin(np.sin(fi) * l3 / d)
    tau = np.arctan2(P3[2] - P1[2], np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2))

    alfa_2 = -(epsilon + tau)
    return [alfa_1, alfa_2, alfa_3]

def polozenie_przegub_1(l1, alfa1, przyczep):
    return np.array([l1 * np.cos(alfa1) + przyczep[0], l1 * np.sin(alfa1) + przyczep[1], przyczep[2]])

def polozenie_przegub_2(l1, l2, alfa1, alfa2, przyczep):
    return polozenie_przegub_1(l1, alfa1, przyczep) + np.array(
        [l2 * np.cos(alfa1) * np.cos(alfa2), l2 * np.sin(alfa1) * np.cos(alfa2), l2 * np.sin(alfa2)])

def funkcja_ruchu_nogi(r, h, y_punktu): #y_punktu jest w ukladzie wspolrzednych srodka robota
    return (-4 * h * (y_punktu ** 2)) / (r ** 2) + (4 * h * y_punktu) / r

def dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek): #funkcja liczy długosc funkcji na przedziale miedzy miescami zerowymi
    suma = 0
    for i in range(1,ilosc_probek):
        y_0 = funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
        y_1 = funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
        dlugosc = np.sqrt((y_1 - y_0) ** 2 + (r/ilosc_probek) ** 2)
        suma += dlugosc
    return suma

def znajdz_punkty_rowno_odlegle_na_paraboli(r, h, ilosc_punktow_na_krzywej, ilosc_probek, bufor_y):
    L = dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek)
    dlugosc_kroku = L/ilosc_punktow_na_krzywej
    suma = 0
    punkty = []
    for i in range(1,ilosc_probek):
        z_0 = funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
        z_1 = funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
        dlugosc = np.sqrt((z_1 - z_0) ** 2 + (r/ilosc_probek) ** 2)
        suma += dlugosc
        if(suma > dlugosc_kroku):
            suma = suma - dlugosc_kroku
            punkty.append([0, i/ilosc_probek * r + bufor_y, z_1])
        if(len(punkty) == ilosc_punktow_na_krzywej - 1):
            break
    punkty.append([0, bufor_y + r, 0])
    return punkty

def calculate_optimal_r_and_cycles(target_distance, l3):
    """
    Oblicza optymalne r i liczbę cykli dla danej odległości
    target_distance = r (startup+shutdown) + cycles * 2r (main_loop)
    target_distance = r * (1 + 2*cycles)
    """
    r_max = l3 / 3  # maksymalne r (obecna wartość)
    r_min = l3 / 100  # minimalne r
    
    best_r = None
    best_cycles = None
    
    # Sprawdzaj od największych wartości r w dół
    for cycles in range(1, 1000):
        required_r = target_distance / (1 + 2 * cycles)
        
        if r_min <= required_r <= r_max:
            if best_r is None or required_r > best_r:
                best_r = required_r
                best_cycles = cycles
                
        # Jeśli r stało się za małe, przerwij
        if required_r < r_min:
            break
    
    return best_r, best_cycles

def generate_walking_trajectory(target_distance, l1, l2, l3):
    """
    Generuje trajektorię chodu dla zadanej odległości
    """
    # Oblicz optymalne r i liczbę cykli
    optimal_r, optimal_cycles = calculate_optimal_r_and_cycles(target_distance, l3)
    
    if optimal_r is None:
        raise ValueError(f"Nie można wygenerować trajektorii dla odległości {target_distance}m")
    
    print(f"Obliczone parametry:")
    print(f"  Docelowa odległość: {target_distance}m")
    print(f"  Optymalne r: {optimal_r:.4f}m")
    print(f"  Liczba cykli main_loop: {optimal_cycles}")
    print(f"  Rzeczywista odległość: {optimal_r * (1 + 2 * optimal_cycles):.4f}m")
    
    # Używaj optimal_r zamiast stałego r
    r = optimal_r
    h = l3 / 4  # wysokość pozostaje stała
    ilosc_punktow_na_krzywych = 10

    punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
    punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
    punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
    punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, ilosc_punktow_na_krzywych)
    punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
    punkty_etap4_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r, h, 2 * ilosc_punktow_na_krzywych, 20000, -r)
    punkty_etap5_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, -r)

    # Startup
    cykl_ogolny_nog_1_3_5 = punkty_etap1_ruchu.copy()
    cykl_ogolny_nog_2_4_6 = punkty_etap3_ruchu.copy()

    # Main loop z obliczoną liczbą cykli
    for _ in range(optimal_cycles):
        cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap4_ruchu
        cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu + punkty_etap3_ruchu

    # Shutdown
    cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap5_ruchu
    cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu

    cykl_ogolny_nog_1_3_5 = np.array(cykl_ogolny_nog_1_3_5)
    cykl_ogolny_nog_2_4_6 = np.array(cykl_ogolny_nog_2_4_6)

    
    return np.array(cykl_ogolny_nog_1_3_5), np.array(cykl_ogolny_nog_2_4_6)

# Długosci segmentow nog - ZAKTUALIZOWANE z rotation.py
l1 = 0.17995 - 0.12184
l2 = 0.30075 - 0.17995
l3 = 0.50975 - 0.30075

# Położenie punktu spoczynku od przyczepu nogi wyznaczone na bazie katow przgubow podczas spoczynku
# WAZNE !!! jest to polozenie stopy w ukladzie punktu zaczepienia stopy a nie ukladu XYZ
# w ktorym X1 to prostopadła prosta do boku platformy do ktorej noga jest zaczepiona i rosnie w kierunku od hexapoda
# Y1 to os pokrywajaca sie z bokiem platformy do ktorego jest przyczepiona noga i rosnie w kierunku przodu hexapoda
# Z1 pokrywa sie z osia Z ukladu XYZ

# zalozone katy spoczynkowe przegubow
alfa_1 = 0
alfa_2 = np.radians(0)
alfa_3 = np.radians(60)

P0 = np.array([0, 0, 0])
P1 = P0 + np.array([l1 * np.cos(alfa_1), l1 *np.sin(alfa_1), 0])
P2 = P1 + np.array([np.cos(alfa_1)*np.cos(alfa_2)*l2,np.sin(alfa_1)*np.cos(alfa_2)*l2, np.sin(alfa_2) * l2])
P3 = P2 + np.array([np.cos(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_2 - alfa_3) * l3])

stopa_spoczynkowa = P3
wysokosc_start = -stopa_spoczynkowa[2]

przyczepy_nog_do_tulowia = np.array([
    [ 0.073922, 0.055095 ,0.003148],
    [ 0.0978, -0.00545, 0.003148],
    [ 0.067301, -0.063754, 0.003148],
    [ -0.067301, -0.063754 , 0.003148],
    [ -0.0978 , -0.00545,0.003148],
    [ -0.073922, 0.055095,0.003148],
])

nachylenia_nog_do_bokow_platformy_pajaka = np.array([
    np.deg2rad(37.169), 0, np.deg2rad(-37.169), np.deg2rad(180 + 37.169), np.deg2rad(180), np.deg2rad(180 - 37.169)
])

# Polozenie spoczynkowe stop
polozenie_spoczynkowe_stop = np.array([
    przyczepy_nog_do_tulowia[i] + np.array([
        stopa_spoczynkowa[0] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[i]) -
        stopa_spoczynkowa[1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[i]),

        stopa_spoczynkowa[0] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[i]) +
        stopa_spoczynkowa[1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[i]),

        stopa_spoczynkowa[2]
    ]) for i in range(6)
])

# Generuj trajektorię dla zadanej odległości
TARGET_DISTANCE = 2.07  # 25 cm
cykl_ogolny_nog_1_3_5, cykl_ogolny_nog_2_4_6 = generate_walking_trajectory(TARGET_DISTANCE, l1, l2, l3)

# tablica cykli, gdzie jest zapisana kazda z nog, kazdy punkt w cylku i jego wspolrzedne, kazda z nog musi miec swoj wlasny
# cykl poruszania ze wzgledu na katy pod jakimi sa ustawione wzgledem srodka robota

#RUCH DO TYŁU:
#cykl_ogolny_nog_1_3_5 = cykl_ogolny_nog_1_3_5[::-1]
#cykl_ogolny_nog_2_4_6 = cykl_ogolny_nog_2_4_6[::-1]

cykle_nog = np.array([
    [
        [cykl_ogolny_nog_1_3_5[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_1_3_5[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_1_3_5[i][2]]
        for i in range(len(cykl_ogolny_nog_1_3_5))
    ] if j in (0, 2, 4) else
    [
        [cykl_ogolny_nog_2_4_6[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_2_4_6[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_ogolny_nog_2_4_6[i][2]]
        for i in range(len(cykl_ogolny_nog_2_4_6))
    ]
    for j in range(6)
])

polozenia_stop_podczas_cyklu = np.array([ # polozenie_stop jest wzgledem ukladu nogi, gdzie przyczep do tulowia to punkt 0,0,0
    [[
        stopa_spoczynkowa[0] + cykle_nog[j][i][0],
        stopa_spoczynkowa[1] + cykle_nog[j][i][1],
        stopa_spoczynkowa[2] + cykle_nog[j][i][2]
    ]
    for i in range(len(cykl_ogolny_nog_1_3_5))]
    for j in range(6)
])

#wychyly podawane odpowiednio dla 1 2 i 3 przegubu w radianach
wychyly_serw_podczas_ruchu = np.array([
[katy_serw(polozenia_stop_podczas_cyklu[j][i], l1, l2, l3)
    for i in range(len(cykl_ogolny_nog_1_3_5))]
    for j in range(6)
])


class LegSequencePlayer(Node):
    def __init__(self):
        super().__init__('leg_sequence_player')
        self.get_logger().info('Inicjalizacja węzła do sekwencji ruchów')
        
        # Subskrypcja do czasu symulacji
        self.clock_subscriber = self.create_subscription(
            Clock,
            '/clock',
            self.clock_callback,
            10
        )
        
        self.sim_time = None
        self.last_sim_time = None
        
        # Wydawcy dla kontrolerów wszystkich nóg
        self.trajectory_publishers = {
            1: self.create_publisher(JointTrajectory, '/leg1_controller/joint_trajectory', 10),
            2: self.create_publisher(JointTrajectory, '/leg2_controller/joint_trajectory', 10),
            3: self.create_publisher(JointTrajectory, '/leg3_controller/joint_trajectory', 10),
            4: self.create_publisher(JointTrajectory, '/leg4_controller/joint_trajectory', 10),
            5: self.create_publisher(JointTrajectory, '/leg5_controller/joint_trajectory', 10),
            6: self.create_publisher(JointTrajectory, '/leg6_controller/joint_trajectory', 10)
        }
        
        # Listy stawów dla nóg
        self.joint_names = {
            1: ['joint1_1', 'joint2_1', 'joint3_1'],
            2: ['joint1_2', 'joint2_2', 'joint3_2'],
            3: ['joint1_3', 'joint2_3', 'joint3_3'],
            4: ['joint1_4', 'joint2_4', 'joint3_4'],
            5: ['joint1_5', 'joint2_5', 'joint3_5'],
            6: ['joint1_6', 'joint2_6', 'joint3_6']
        }

    def clock_callback(self, msg):
        """Callback do odbioru czasu symulacji"""
        self.last_sim_time = self.sim_time
        self.sim_time = msg.clock.sec + msg.clock.nanosec * 1e-9

    def wait_sim_time(self, duration_sec):
        """Czeka określony czas w czasie symulacji"""
        if self.sim_time is None:
            self.get_logger().warn('Brak czasu symulacji, używam time.sleep')
            time.sleep(duration_sec)
            return
            
        start_time = self.sim_time
        target_time = start_time + duration_sec
        
        while self.sim_time < target_time:
            rclpy.spin_once(self, timeout_sec=0.01)
            if self.sim_time is None:
                break

    def send_trajectory_to_all_legs_at_step(self, step_index, duration_sec=0.1):
        """
        Wysyła trajektorię do kontrolerów wszystkich nóg jednocześnie
        używając wartości z tablicy wychyly_serw_podczas_ruchu dla danego kroku
        """
        self.get_logger().info(f'Wysyłam trajektorię dla kroku {step_index}')
        
        # Sprawdź, czy indeks jest prawidłowy
        if step_index >= len(wychyly_serw_podczas_ruchu[0]):
            self.get_logger().error(f'Indeks kroku {step_index} jest poza zakresem!')
            return False
        
        # Ustaw czas trwania ruchu
        duration = Duration()
        duration.sec = int(duration_sec)
        duration.nanosec = int((duration_sec - int(duration_sec)) * 1e9)
        
        # Dla każdej nogi przygotuj i wyślij trajektorię
        for leg_num in range(1, 7):
            # Utwórz wiadomość trajektorii dla nogi
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names[leg_num]
            
            # Utwórz punkt trajektorii
            point = JointTrajectoryPoint()
            
            # Pobierz wartości z tablicy (indeks nogi to leg_num-1)
            joint_values = wychyly_serw_podczas_ruchu[leg_num-1][step_index]
            
            point.positions = [
                float(joint_values[0]),  # joint1
                float(joint_values[1]),  # joint2
                float(joint_values[2])   # joint3
            ]
            point.velocities = [0.0] * 3
            point.accelerations = [0.0] * 3
            
            # Ustaw czas trwania ruchu
            point.time_from_start = duration
            
            # Dodaj punkt do trajektorii
            trajectory.points.append(point)
            
            # Wyślij trajektorię
            self.trajectory_publishers[leg_num].publish(trajectory)
        
        self.get_logger().info('Wysłano trajektorie dla wszystkich nóg')
        return True
    
    def execute_sequence(self, start_step=0, end_step=None, step_duration=0.02):
        """
        Wykonanie sekwencji ruchów dla wszystkich nóg równocześnie
        używając wartości z tablicy wychyly_serw_podczas_ruchu
        """
        self.get_logger().info(f'Rozpoczynam sekwencję ruchów dla odległości {TARGET_DISTANCE}m')
        
        # Jeśli nie podano end_step, użyj całej tablicy
        if end_step is None:
            end_step = len(wychyly_serw_podczas_ruchu[0])
        
        # Czekanie na inicjalizację czasu symulacji
        self.get_logger().info('Czekam na czas symulacji...')
        while self.sim_time is None:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        # Przejście do pozycji początkowej (pierwszy punkt w tablicy)
        self.send_trajectory_to_all_legs_at_step(start_step, duration_sec=0.15)
        self.get_logger().info('Oczekiwanie na wykonanie początkowego ruchu...')
        self.wait_sim_time(0.15)
        
        # Wykonanie sekwencji ruchów
        for step in range(start_step + 1, end_step):
            self.send_trajectory_to_all_legs_at_step(step, duration_sec=step_duration)
            self.get_logger().info(f'Wykonano krok {step}, oczekiwanie {step_duration}s...')
            self.wait_sim_time(step_duration)
        
        self.get_logger().info(f'Sekwencja zakończona - robot przeszedł {TARGET_DISTANCE}m do przodu')


def main(args=None):
    rclpy.init(args=args)
    
    # Utworzenie węzła
    node = LegSequencePlayer()
    
    try:
        # Krótkie oczekiwanie na inicjalizację
        print("Inicjalizacja... Poczekaj 0.1 sekundy.")
        node.wait_sim_time(0.1)
        
        # Wykonanie sekwencji
        print(f"Rozpoczynam sekwencję chodu na odległość {TARGET_DISTANCE}m")
        node.execute_sequence()
        
        # Utrzymanie węzła aktywnego przez chwilę
        node.wait_sim_time(0.1)
        
    except KeyboardInterrupt:
        pass
    
    # Sprzątanie
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
