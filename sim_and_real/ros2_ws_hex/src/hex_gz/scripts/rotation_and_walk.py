#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from rosgraph_msgs.msg import Clock
import time

matplotlib.use('TkAgg')

# ============ FUNKCJE WSPÓLNE ============
def katy_serw(P3, l1, l2, l3):
    """Wyznaczenie kątów potrzebnych do osiągnięcia przez stopę punktu docelowego"""
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

# Długości segmentów nóg
l1 = 0.17995 - 0.12184
l2 = 0.30075 - 0.17995
l3 = 0.50975 - 0.30075

# ============ FUNKCJE DLA OBROTU (ORYGINALNE) ============
def turn_hexapod(R, alfa, x_start, z):
    x_new = (x_start + R) * np.cos(alfa) - R
    y_new = (x_start + R) * np.sin(alfa)
    return np.array([x_new, y_new, z])

def parabola_w_przestrzeni_z_punktow(w1, w2, w3, liczba_punktow):
    # rozwiązanie układu parametrycznego równania kwadratowego dla 1 punktu w t = 0, drugiego w t = 1 i trzeciego dla t = 2
    a = []
    b = []
    c = []
    dokladnosc = 1000
    for i in range(3):
        a.append(w1[i] / 2 - w2[i] + w3[i] / 2)
        b.append(-w1[i] * 3 / 2 + 2 * w2[i] - w3[i] / 2)
        c.append(w1[i])

    t = np.linspace(0, 2, dokladnosc)
    p = np.array([a[0] * t ** 2 + b[0] * t + c[0],
                  a[1] * t ** 2 + b[1] * t + c[1],
                  a[2] * t ** 2 + b[2] * t + c[2]]).T

    dlugosci_segmentow = np.sqrt(np.sum(np.diff(p, axis=0) ** 2, axis=1))
    dlugosci_luku = np.concatenate(([0], np.cumsum(dlugosci_segmentow)))

    # Równomierne rozmieszczenie punktów
    dlugosc_calkowita = dlugosci_luku[-1]
    dlugosci_celowe = np.linspace(0, dlugosc_calkowita, liczba_punktow + 1)

    # Interpolacja punktów dla równych odstępów
    punkty_rowne = np.array([
        np.interp(dlugosci_celowe, dlugosci_luku, p[:, i]) for i in range(3)
    ]).T

    punkty_rowne = punkty_rowne[1:]
    return punkty_rowne

def generate_rotation_sequence(kat_calkowity_deg):
    """Generowanie sekwencji obrotu - ORYGINALNA LOGIKA"""
    stala_naprawcza = 1.2025
    odleglosc_przegubow_od_srodka_hexapoda = 0.1218
    kat_obrotu_cyklu = np.radians(20)  # Tu można zmienić kąt cyklu
    kat_obrotu = kat_obrotu_cyklu / 2 * stala_naprawcza
    kat_calkowity = np.radians(kat_calkowity_deg)
    
    # Wyznaczenie kierunku obrotu
    kierunek = np.sign(kat_calkowity)
    kat_obrotu *= kierunek

    x_start = 0.28341  # poczatkowe wychylenie nogi pajaka w osi x
    z_start = -0.181  # poczatkowy z
    h = 0.1  # wysokosc paraboli
    ilosc_punktow_na_etap = 10

    punkt_start_dla_kazdej_nogi = [x_start, 0, z_start]
    punkt_P1 = turn_hexapod(odleglosc_przegubow_od_srodka_hexapoda, kat_obrotu, x_start, z_start)
    punkt_P2 = turn_hexapod(odleglosc_przegubow_od_srodka_hexapoda, -kat_obrotu, x_start, z_start)
    punkt_szczytowy_etapu_1 = (punkt_start_dla_kazdej_nogi + punkt_P1) / 2 + np.array([0, 0, h])
    punkt_szczytowy_etapu_5 = (punkt_start_dla_kazdej_nogi + punkt_P2) / 2 + np.array([0, 0, h])


    etap_1 = np.array(parabola_w_przestrzeni_z_punktow(punkt_start_dla_kazdej_nogi, punkt_szczytowy_etapu_1, punkt_P1, ilosc_punktow_na_etap))
    etap_2 = np.linspace(punkt_P1, punkt_start_dla_kazdej_nogi, ilosc_punktow_na_etap)[1:]
    etap_3 = np.linspace(punkt_start_dla_kazdej_nogi, punkt_P2, ilosc_punktow_na_etap)[1:]
    etap_5 = np.array(parabola_w_przestrzeni_z_punktow(punkt_P2, punkt_szczytowy_etapu_5, punkt_start_dla_kazdej_nogi, ilosc_punktow_na_etap))

    ilosc_cykli = int(np.abs(kat_calkowity) // kat_obrotu_cyklu)
    print(f"Liczba cykli obrotu: {ilosc_cykli}")
    pozostaly_kat = (np.abs(kat_calkowity) % kat_obrotu_cyklu) / 2 * stala_naprawcza * kierunek

    cykl_nog_1_3_5 = np.concatenate([etap_1, etap_2])
    cykl_nog_2_4_6 = np.concatenate([etap_3, etap_5])

    for _ in range(ilosc_cykli - 1):
        cykl_nog_1_3_5 = np.concatenate([cykl_nog_1_3_5, etap_1, etap_2])
        cykl_nog_2_4_6 = np.concatenate([cykl_nog_2_4_6, etap_3, etap_5])

    if np.abs(pozostaly_kat) > np.radians(1):
        punkt_P1 = turn_hexapod(odleglosc_przegubow_od_srodka_hexapoda, pozostaly_kat, x_start, z_start)
        punkt_P2 = turn_hexapod(odleglosc_przegubow_od_srodka_hexapoda, -pozostaly_kat, x_start, z_start)
        punkt_szczytowy_etapu_1 = (punkt_start_dla_kazdej_nogi + punkt_P1) / 2 + np.array([0, 0, h])
        punkt_szczytowy_etapu_5 = (punkt_start_dla_kazdej_nogi + punkt_P2) / 2 + np.array([0, 0, h])

        etap_1 = np.array(parabola_w_przestrzeni_z_punktow(punkt_start_dla_kazdej_nogi, punkt_szczytowy_etapu_1, punkt_P1, ilosc_punktow_na_etap))
        etap_2 = np.linspace(punkt_P1, punkt_start_dla_kazdej_nogi, ilosc_punktow_na_etap)[1:]
        etap_3 = np.linspace(punkt_start_dla_kazdej_nogi, punkt_P2, ilosc_punktow_na_etap)[1:]
        etap_5 = np.array(parabola_w_przestrzeni_z_punktow(punkt_P2, punkt_szczytowy_etapu_5, punkt_start_dla_kazdej_nogi, ilosc_punktow_na_etap))

        cykl_nog_1_3_5 = np.concatenate([cykl_nog_1_3_5, etap_1, etap_2])
        cykl_nog_2_4_6 = np.concatenate([cykl_nog_2_4_6, etap_3, etap_5])

    # Konwersja na kąty serwomechanizmów
    wychyly_serw_1_3_5 = []
    wychyly_serw_2_4_6 = []

    # Dla każdej nogi
    for punkt in cykl_nog_1_3_5:
        kat_obrotu_punkt = katy_serw(punkt, l1, l2, l3)
        wychyly_serw_1_3_5.append(kat_obrotu_punkt)

    for punkt in cykl_nog_2_4_6:
        kat_obrotu_punkt = katy_serw(punkt, l1, l2, l3)
        wychyly_serw_2_4_6.append(kat_obrotu_punkt)

    return np.array(wychyly_serw_1_3_5), np.array(wychyly_serw_2_4_6)

# ============ FUNKCJE DLA MARSZU ============
def funkcja_ruchu_nogi(r, h, y_punktu):
    """Funkcja ruchu nogi"""
    return (-4 * h * (y_punktu ** 2)) / (r ** 2) + (4 * h * y_punktu) / r

def dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek):
    """Funkcja liczy długość funkcji na przedziale między miejscami zerowymi"""
    suma = 0
    for i in range(1, ilosc_probek):
        y_0 = funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
        y_1 = funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
        dlugosc = np.sqrt((y_1 - y_0) ** 2 + (r/ilosc_probek) ** 2)
        suma += dlugosc
    return suma

def znajdz_punkty_rowno_odlegle_na_paraboli(r, h, ilosc_punktow_na_krzywej, ilosc_probek, bufor_y):
    """Znajdowanie punktów równo odległych na paraboli"""
    L = dlugosc_funkcji_ruchu_nogi(r, h, ilosc_probek)
    dlugosc_kroku = L/ilosc_punktow_na_krzywej
    suma = 0
    punkty = []
    for i in range(1, ilosc_probek):
        z_0 = funkcja_ruchu_nogi(r, h, (i-1)/ilosc_probek * r)
        z_1 = funkcja_ruchu_nogi(r, h, i/ilosc_probek * r)
        dlugosc = np.sqrt((z_1 - z_0) ** 2 + (r/ilosc_probek) ** 2)
        suma += dlugosc
        if suma > dlugosc_kroku:
            suma = suma - dlugosc_kroku
            punkty.append([0, i/ilosc_probek * r + bufor_y, z_1])
        if len(punkty) == ilosc_punktow_na_krzywej - 1:
            break
    punkty.append([0, bufor_y + r, 0])
    return punkty

def generate_walking_sequence(zadana_odleglosc):
    """Generowanie sekwencji marszu"""
    # Parametry nogi - obliczenie pozycji spoczynkowej
    alfa_1 = 0
    alfa_2 = np.radians(0)
    alfa_3 = np.radians(60)

    P0 = np.array([0, 0, 0])
    P1 = P0 + np.array([l1 * np.cos(alfa_1), l1 * np.sin(alfa_1), 0])
    P2 = P1 + np.array([np.cos(alfa_1)*np.cos(alfa_2)*l2, np.sin(alfa_1)*np.cos(alfa_2)*l2, np.sin(alfa_2) * l2])
    P3 = P2 + np.array([np.cos(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_2 - alfa_3) * l3])

    stopa_spoczynkowa = P3

    przyczepy_nog_do_tulowia = np.array([
        [0.073922, 0.055095, 0.003148],
        [0.0978, -0.00545, 0.003148],
        [0.067301, -0.063754, 0.003148],
        [-0.067301, -0.063754, 0.003148],
        [-0.0978, -0.00545, 0.003148],
        [-0.073922, 0.055095, 0.003148],
    ])

    nachylenia_nog_do_bokow_platformy_pajaka = np.array([
        np.deg2rad(37.169), 0, np.deg2rad(-37.169), 
        np.deg2rad(180 + 37.169), np.deg2rad(180), np.deg2rad(180 - 37.169)
    ])

    # Parametry chodu
    h = l3 / 4
    r = h
    ilosc_punktow_na_krzywych = 20
    dlugosc_pelnego_kroku = 2 * r

    print(f"Zadana odległość: {zadana_odleglosc}m")
    print(f"Długość pełnego kroku: {dlugosc_pelnego_kroku:.3f}m")

    # Oblicz liczbę pełnych cykli i pozostałą odległość
    pelne_cykle = int(zadana_odleglosc // dlugosc_pelnego_kroku)
    pozostala_odleglosc = zadana_odleglosc % dlugosc_pelnego_kroku

    print(f"Liczba pełnych cykli: {pelne_cykle}")
    print(f"Pozostała odległość: {pozostala_odleglosc:.3f}m")

    # Jeśli jest pozostała odległość, oblicz skrócony krok
    ostatni_krok_potrzebny = pozostala_odleglosc > 0.01
    if ostatni_krok_potrzebny:
        r_ostatni = pozostala_odleglosc / 2
        print(f"Ostatni krok: r = {r_ostatni:.3f}m")

    punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
    punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
    punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
    punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, ilosc_punktow_na_krzywych)
    punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
    punkty_etap4_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r, h, 2 * ilosc_punktow_na_krzywych, 20000, -r)
    punkty_etap5_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, -r)
    
    cykl_ogolny_nog_1_3_5 = punkty_etap1_ruchu.copy()
    cykl_ogolny_nog_2_4_6 = punkty_etap3_ruchu.copy()

    # Generuj pełne cykle
    for _ in range(pelne_cykle):
        cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap4_ruchu
        cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu + punkty_etap3_ruchu

    # Jeśli potrzebny jest ostatni skrócony krok
    if ostatni_krok_potrzebny:
        punkty_etap1_ostatni = znajdz_punkty_rowno_odlegle_na_paraboli(r_ostatni, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
        punkty_etap2_ostatni_y = np.linspace(r_ostatni * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
        punkty_etap2_ostatni = [[0, punkty_etap2_ostatni_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
        punkty_etap3_ostatni_y = np.linspace(-r_ostatni / ilosc_punktow_na_krzywych, -r_ostatni, ilosc_punktow_na_krzywych)
        punkty_etap3_ostatni = [[0, punkty_etap3_ostatni_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
        punkty_etap4_ostatni = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r_ostatni, h, 2 * ilosc_punktow_na_krzywych, 20000, -r_ostatni)
        punkty_etap5_ostatni = znajdz_punkty_rowno_odlegle_na_paraboli(r_ostatni, h / 2, ilosc_punktow_na_krzywych, 10000, -r_ostatni)
        
        cykl_ogolny_nog_1_3_5 += punkty_etap2_ostatni + punkty_etap3_ostatni + punkty_etap4_ostatni
        cykl_ogolny_nog_2_4_6 += punkty_etap4_ostatni + punkty_etap2_ostatni + punkty_etap3_ostatni
        
        cykl_ogolny_nog_1_3_5 += punkty_etap2_ostatni + punkty_etap3_ostatni + punkty_etap5_ostatni
        cykl_ogolny_nog_2_4_6 += punkty_etap4_ostatni + punkty_etap2_ostatni
    else:
        cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap5_ruchu
        cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu

    cykl_ogolny_nog_1_3_5 = np.array(cykl_ogolny_nog_1_3_5)
    cykl_ogolny_nog_2_4_6 = np.array(cykl_ogolny_nog_2_4_6)

    # Tworzenie cykli dla wszystkich nóg
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

    polozenia_stop_podczas_cyklu = np.array([
        [[
            stopa_spoczynkowa[0] + cykle_nog[j][i][0],
            stopa_spoczynkowa[1] + cykle_nog[j][i][1],
            stopa_spoczynkowa[2] + cykle_nog[j][i][2]
        ]
        for i in range(len(cykl_ogolny_nog_1_3_5))]
        for j in range(6)
    ])

    # Wychyły podawane odpowiednio dla 1, 2 i 3 przegubu w radianach
    wychyly_serw_podczas_ruchu = np.array([
        [katy_serw(polozenia_stop_podczas_cyklu[j][i], l1, l2, l3)
         for i in range(len(cykl_ogolny_nog_1_3_5))]
        for j in range(6)
    ])

    return wychyly_serw_podczas_ruchu

# ============ KLASA GŁÓWNA ============
class CombinedHexapodController(Node):
    def __init__(self):
        super().__init__('combined_hexapod_controller')
        self.get_logger().info('Inicjalizacja połączonego kontrolera hexapoda')
        
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

    def send_rotation_trajectory(self, wychyly_1_3_5, wychyly_2_4_6, step_index, duration_sec=0.05):
        """Wysyła trajektorię obrotu"""
        self.get_logger().info(f'Wysyłam trajektorię obrotu dla kroku {step_index}')

        if step_index >= len(wychyly_1_3_5) or step_index >= len(wychyly_2_4_6):
            self.get_logger().error(f'Indeks kroku {step_index} jest poza zakresem!')
            return False

        duration = Duration()
        duration.sec = int(duration_sec)
        duration.nanosec = int((duration_sec - int(duration_sec)) * 1e9)

        for leg_num in range(1, 7):
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names[leg_num]

            point = JointTrajectoryPoint()

            if leg_num in [1, 3, 5]:
                joint_values = wychyly_1_3_5[step_index]
            elif leg_num in [2, 4, 6]:
                joint_values = wychyly_2_4_6[step_index]
            else:
                self.get_logger().error(f'Nieprawidłowy numer nogi: {leg_num}')
                continue

            point.positions = list(map(float, joint_values))
            point.velocities = [0.0] * 3
            point.accelerations = [0.0] * 3
            point.time_from_start = duration

            trajectory.points.append(point)
            self.trajectory_publishers[leg_num].publish(trajectory)

        return True

    def send_walking_trajectory(self, wychyly_serw_podczas_ruchu, step_index, duration_sec=0.02):
        """Wysyła trajektorię marszu"""
        self.get_logger().info(f'Wysyłam trajektorię marszu dla kroku {step_index}')
        
        if step_index >= len(wychyly_serw_podczas_ruchu[0]):
            self.get_logger().error(f'Indeks kroku {step_index} jest poza zakresem!')
            return False
        
        duration = Duration()
        duration.sec = int(duration_sec)
        duration.nanosec = int((duration_sec - int(duration_sec)) * 1e9)
        
        for leg_num in range(1, 7):
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names[leg_num]
            
            point = JointTrajectoryPoint()
            joint_values = wychyly_serw_podczas_ruchu[leg_num-1][step_index]
            
            point.positions = [
                float(joint_values[0]),
                float(joint_values[1]),
                float(joint_values[2])
            ]
            point.velocities = [0.0] * 3
            point.accelerations = [0.0] * 3
            point.time_from_start = duration
            
            trajectory.points.append(point)
            self.trajectory_publishers[leg_num].publish(trajectory)
        
        return True

    def execute_rotation_sequence(self, wychyly_1_3_5, wychyly_2_4_6, step_duration=0.05):
        """Wykonanie sekwencji obrotu - ORYGINALNA LOGIKA"""
        self.get_logger().info('Rozpoczynam sekwencję obrotu')
        
        # Zakładamy, że tablice mają tę samą długość
        max_steps = min(len(wychyly_1_3_5), len(wychyly_2_4_6))

        # Przejście do pozycji początkowej (pierwszy punkt)
        self.send_rotation_trajectory(wychyly_1_3_5, wychyly_2_4_6, 0, duration_sec=step_duration)
        self.get_logger().info('Oczekiwanie na wykonanie początkowego ruchu...')
        self.wait_sim_time(step_duration + 0.05)

        # Wykonanie sekwencji
        for step in range(1, max_steps):
            self.send_rotation_trajectory(wychyly_1_3_5, wychyly_2_4_6, step, duration_sec=step_duration)
            self.get_logger().info(f'Wykonano krok obrotu {step}, oczekiwanie {step_duration}s...')
            self.wait_sim_time(step_duration + 0.05)

        self.get_logger().info('Sekwencja obrotu zakończona')

    def execute_walking_sequence(self, wychyly_serw_podczas_ruchu, step_duration=0.02):
        """Wykonanie sekwencji marszu"""
        self.get_logger().info('Rozpoczynam sekwencję marszu')
        
        # Przejście do pozycji początkowej
        self.send_walking_trajectory(wychyly_serw_podczas_ruchu, 0, duration_sec=0.15)
        self.wait_sim_time(0.15)
        
        # Wykonanie sekwencji ruchów
        for step in range(1, len(wychyly_serw_podczas_ruchu[0])):
            self.send_walking_trajectory(wychyly_serw_podczas_ruchu, step, duration_sec=step_duration)
            self.get_logger().info(f'Wykonano krok marszu {step}, oczekiwanie {step_duration}s...')
            self.wait_sim_time(step_duration)
        
        self.get_logger().info('Sekwencja marszu zakończona')

    def execute_complete_sequence(self):
        """Wykonanie pełnej sekwencji: obrót 90° → marsz 0.25m → obrót 90°"""
        self.get_logger().info('=== ROZPOCZYNAM PEŁNĄ SEKWENCJĘ ===')
        
        # Czekanie na inicjalizację czasu symulacji
        self.get_logger().info('Czekam na czas symulacji...')
        while self.sim_time is None:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        # Krótka pauza na inicjalizację
        self.get_logger().info('Inicjalizacja...')
        self.wait_sim_time(2.0)
        
        # ETAP 1: Pierwszy obrót o 90 stopni
        self.get_logger().info('=== ETAP 1: OBRÓT O 90 STOPNI ===')
        wychyly_rot1_1_3_5, wychyly_rot1_2_4_6 = generate_rotation_sequence(90)
        self.execute_rotation_sequence(wychyly_rot1_1_3_5, wychyly_rot1_2_4_6)
        
        # Pauza między etapami
        self.get_logger().info('Pauza między etapami...')
        self.wait_sim_time(1.0)
        
        # ETAP 2: Marsz do przodu o 0.25m
        self.get_logger().info('=== ETAP 2: MARSZ DO PRZODU O 0.25m ===')
        wychyly_marsz = generate_walking_sequence(0.25)
        self.execute_walking_sequence(wychyly_marsz)
        
        # Pauza między etapami
        self.get_logger().info('Pauza między etapami...')
        self.wait_sim_time(1.0)
        
        # ETAP 3: Drugi obrót o 90 stopni
        self.get_logger().info('=== ETAP 3: OBRÓT O 90 STOPNI ===')
        wychyly_rot2_1_3_5, wychyly_rot2_2_4_6 = generate_rotation_sequence(90)
        self.execute_rotation_sequence(wychyly_rot2_1_3_5, wychyly_rot2_2_4_6)
        
        # Zakończenie
        self.get_logger().info('=== PEŁNA SEKWENCJA ZAKOŃCZONA ===')
        self.wait_sim_time(2.0)


def main(args=None):
    rclpy.init(args=args)
    
    # Utworzenie węzła
    node = CombinedHexapodController()
    
    try:
        print("=== HEXAPOD COMBINED SEQUENCE ===")
        print("Sekwencja: OBRÓT 90° → MARSZ 0.25m → OBRÓT 90°")
        print("Rozpoczynam wykonanie...")
        
        # Wykonanie pełnej sekwencji
        node.execute_complete_sequence()
        
        print("Wszystkie sekwencje zakończone!")
        
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
    
    # Sprzątanie
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()