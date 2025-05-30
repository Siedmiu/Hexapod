#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation

matplotlib.use('TkAgg')

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

l1 = 0.17995 - 0.12184
l2 = 0.30075 - 0.17995
l3 = 0.50975 - 0.30075

stala_naprawcza = 1.2025

odleglosc_przegubow_od_srodka_hexapoda = 0.1218
kat_obrotu_cyklu = np.radians(20)
kat_obrotu = kat_obrotu_cyklu / 2 * stala_naprawcza
kat_calkowity = np.radians(90)
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

#etap 1 z początkowej parabolą do P1
#etap 2 z P1 do początkowej po ziemi
#etap 3 z początkowej do P2 po ziemi
#etap4 ewentualna parabola z P2 do P1
#etap 5 z P2 do początkowej parabolą

etap_1 = np.array(parabola_w_przestrzeni_z_punktow(punkt_start_dla_kazdej_nogi, punkt_szczytowy_etapu_1, punkt_P1, ilosc_punktow_na_etap))
etap_2 = np.linspace(punkt_P1, punkt_start_dla_kazdej_nogi, ilosc_punktow_na_etap)[1:]
etap_3 = np.linspace(punkt_start_dla_kazdej_nogi, punkt_P2, ilosc_punktow_na_etap)[1:]
etap_5 = np.array(parabola_w_przestrzeni_z_punktow(punkt_P2, punkt_szczytowy_etapu_5, punkt_start_dla_kazdej_nogi, ilosc_punktow_na_etap))

ilosc_cykli = int(np.abs(kat_calkowity) // kat_obrotu_cyklu)
print(ilosc_cykli)
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

wychyly_serw_1_3_5 = []
wychyly_serw_2_4_6 = []

# Dla każdej nogi
for punkt in cykl_nog_1_3_5:
    kat_obrotu = katy_serw(punkt, l1, l2, l3)
    wychyly_serw_1_3_5.append(kat_obrotu)

for punkt in cykl_nog_2_4_6:
    kat_obrotu = katy_serw(punkt, l1, l2, l3)
    wychyly_serw_2_4_6.append(kat_obrotu)

wychyly_serw_1_3_5 = np.array(wychyly_serw_1_3_5)
wychyly_serw_2_4_6 = np.array(wychyly_serw_2_4_6)

czy_wyswietlic = False
if czy_wyswietlic:

    plt.figure(figsize=(14, 6))

    # Wykresy dla nóg 1, 3, 5
    plt.subplot(1, 2, 1)
    plt.plot(wychyly_serw_1_3_5[:, 0], label='alfa_1 (obrót w poziomie)')
    plt.plot(wychyly_serw_1_3_5[:, 1], label='alfa_2 (podnoszenie)')
    plt.plot(wychyly_serw_1_3_5[:, 2], label='alfa_3 (zgięcie stawu)')
    plt.title('Wychylenia serwomechanizmów nóg 1, 3, 5')
    plt.xlabel('Krok')
    plt.ylabel('Kąt (radiany)')
    plt.legend()
    plt.grid(True)

    # Wykresy dla nóg 2, 4, 6
    plt.subplot(1, 2, 2)
    plt.plot(wychyly_serw_2_4_6[:, 0], label='alfa_1 (obrót w poziomie)')
    plt.plot(wychyly_serw_2_4_6[:, 1], label='alfa_2 (podnoszenie)')
    plt.plot(wychyly_serw_2_4_6[:, 2], label='alfa_3 (zgięcie stawu)')
    plt.title('Wychylenia serwomechanizmów nóg 2, 4, 6')
    plt.xlabel('Krok')
    plt.ylabel('Kąt (radiany)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

class LegSequencePlayer(Node):
    def __init__(self):
        super().__init__('leg_sequence_player')
        self.get_logger().info('Inicjalizacja węzła do sekwencji ruchów')
        
        # Przechowaj tablicę z wychyłami serw
        
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
        

    def send_trajectory_to_all_legs_at_step(self, step_index, duration_sec=2.0):
        self.get_logger().info(f'Wysyłam trajektorię dla kroku {step_index}')

        if step_index >= len(wychyly_serw_1_3_5) or step_index >= len(wychyly_serw_2_4_6):
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
                joint_values = wychyly_serw_1_3_5[step_index]
            elif leg_num in [2, 4, 6]:
                joint_values = wychyly_serw_2_4_6[step_index]
            else:
                self.get_logger().error(f'Nieprawidłowy numer nogi: {leg_num}')
                continue

            point.positions = list(map(float, joint_values))
            point.velocities = [0.0] * 3
            point.accelerations = [0.0] * 3
            point.time_from_start = duration

            trajectory.points.append(point)

            self.trajectory_publishers[leg_num].publish(trajectory)

        self.get_logger().info('Wysłano trajektorie dla wszystkich nóg')
        return True

    
    def execute_sequence(self, start_step=0, end_step=None, step_duration=0.1):
        """
        Wykonanie sekwencji ruchów dla wszystkich nóg równocześnie
        używając wychyłów z osobnych tablic: wychyly_serw_1_3_5 i wychyly_serw_2_4_6
        """
        self.get_logger().info('Rozpoczynam sekwencję ruchów dla wszystkich nóg')
        
        # Zakładamy, że tablice mają tę samą długość
        max_steps = min(len(wychyly_serw_1_3_5), len(wychyly_serw_2_4_6))

        if end_step is None or end_step > max_steps:
            end_step = max_steps

        # Przejście do pozycji początkowej (pierwszy punkt)
        self.send_trajectory_to_all_legs_at_step(start_step, duration_sec=0.1)

        self.get_logger().info('Oczekiwanie na wykonanie początkowego ruchu...')
        time.sleep(0.1)

        for step in range(start_step + 1, end_step):
            self.send_trajectory_to_all_legs_at_step(step, duration_sec=step_duration)
            self.get_logger().info(f'Wykonano krok {step}, oczekiwanie {step_duration}s...')
            time.sleep(step_duration)

        self.get_logger().info('Sekwencja zakończona')



def main(args=None):
    rclpy.init(args=args)
    
    # Utworzenie węzła
    node = LegSequencePlayer()
    
    try:
        # Krótkie oczekiwanie na inicjalizację
        print("Inicjalizacja... Poczekaj 2 sekundy.")
        time.sleep(2.0)
        
        # Wykonanie sekwencji
        print("Rozpoczynam sekwencję")
        node.execute_sequence()
        
        # Utrzymanie węzła aktywnego przez chwilę
        time.sleep(2.0)
        
    except KeyboardInterrupt:
        pass
    
    # Sprzątanie
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
