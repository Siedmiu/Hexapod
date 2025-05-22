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
#dane z modelu i potrzeby obrotu o kat alfa

def push_leg(alfa, P_start, przyczep, noga):

    x_prim = przyczep[0] * np.cos(alfa) - przyczep[1] * np.sin(alfa)
    y_prim = przyczep[0] * np.sin(alfa) + przyczep[1] * np.cos(alfa)

    delta_x = x_prim - przyczep[0]
    delta_y = y_prim - przyczep[0]

    if noga % 2 == 0:
        P_new = P_start - [delta_x, delta_y, 0]
    else:
        P_new = P_start + [delta_x, delta_y, 0]

    return P_new

def parabola_w_przestrzeni_z_punktow(w1, w2, w3, liczba_punktow, noga):
# rozwiązanie układu parametrycznego równania kwadratowego dla 1 punktu w t = 0, drugiego w t = 1 i trzeciego dla t = 2
    a = []
    b = []
    c = []
    dokladnosc = 1000
    for i in range (3):
        a.append(w1[i] / 2 - w2[i] + w3[i] / 2)
        b.append(-w1[i] * 3 / 2 + 2 * w2[i] - w3[i] / 2)
        c.append(w1[i])

    t = np.linspace(0, 2, dokladnosc)
    p = np.array([a[i] * t ** 2 + b[i] * t + c[i] for i in range(3)]).T

    dlugosci_segmentow = np.sqrt(np.sum(np.diff(p, axis=0) ** 2, axis=1))
    dlugosci_luku = np.concatenate(([0], np.cumsum(dlugosci_segmentow)))

    # Równomierne rozmieszczenie punktów
    dlugosc_calkowita = dlugosci_luku[-1]
    dlugosci_celowe = np.linspace(0, dlugosc_calkowita, liczba_punktow + 1)

    # Interpolacja punktów dla równych odstępów
    punkty_rowne = np.array([
        np.interp(dlugosci_celowe, dlugosci_luku, p[:, i]) for i in range(3)
    ]).T

    if noga % 2 == 0:
        punkty_rowne = punkty_rowne[::-1]

    punkty_rowne = punkty_rowne[1:]

    return punkty_rowne

def prosta_w_cyklu(P_start, P2, noga, liczba_punktow):

    linia = np.linspace(P_start, P2,liczba_punktow + 1)

    if noga % 2 == 1:
        linia = linia[::-1]

    linia = linia[1:]

    return linia

def katy_serw(P3, l1, h1, l2, h2, l3):

    # wyznaczenie katow potrzebnych do osiagniecia przez stope punktu docelowego
    alfa_1 = np.arctan2(P3[1], P3[0])

    P1 = np.array([l1 * np.cos(alfa_1), l1 * np.sin(alfa_1), h1])

    d = np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2 + (P3[2] - P1[2]) ** 2)
    r = np.sqrt(l2 ** 2 + h2 ** 2)

    staly_kat_przy_P1 = np.arctan2(h2, l2)

    cos_fi = (r ** 2 + l3 ** 2 - d ** 2) / (2 * r * l3)
    fi = np.arccos(cos_fi)
    alfa_3 = np.deg2rad(180) - fi - staly_kat_przy_P1

    epsilon = np.arcsin(np.sin(fi) * l3 / d)
    tau = np.arctan2(P3[2] - P1[2], np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2))

    alfa_2 = -(epsilon + tau - staly_kat_przy_P1)
    return [alfa_1, alfa_2, alfa_3]

# Długosci segmentow nog
h1 = -0.016854 - 0.003148
l1 = 0.12886 - 0.0978
l2 = 0.2188-0.12886
h2 = -0.011804 + 0.016854
l3 = 0.38709 - 0.2188

staly_kat_przy_P1 = np.arctan2(h2, l2)

# zalozone katy spoczynkowe przegubow
alfa_1 = 0
alfa_2 = np.radians(0)
alfa_3 = np.radians(60)

P0 = np.array([0, 0, 0])
P0_pod = P0 + np.array([0, 0, h1])
P1 = P0_pod + np.array([l1 * np.cos(alfa_1), l1 *np.sin(alfa_1), 0])
P2 = P1 + np.array([np.cos(alfa_1)*np.cos(alfa_2)*l2,np.sin(alfa_1)*np.cos(alfa_2)*l2, np.sin(alfa_2) * l2])
P3 = P1 + np.array([np.cos(alfa_1)*np.cos(staly_kat_przy_P1 + alfa_2)*np.sqrt(h2**2 + l2**2),np.sin(alfa_1)*np.cos(staly_kat_przy_P1 + alfa_2)*np.sqrt(h2**2 + l2**2), np.sin(staly_kat_przy_P1 + alfa_2)*np.sqrt(h2**2 + l2**2)])
P4 = P3 + np.array([np.cos(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_1)*np.cos(alfa_2 - alfa_3)*l3, np.sin(alfa_2 - alfa_3) * l3])

stopa_spoczynkowa = P4

wysokosc_start = -stopa_spoczynkowa[2]

przyczepy_nog_do_tulowia = np.array([
    [ 0.073922, 0.055095 ,0.003148],
    [ 0.0978, -0.00545, 0.003148],
    [ 0.067301, -0.063754, 0.003148],
    [ -0.067301, -0.063754 , 0.003148],
    [ -0.0978 , -0.00545,0.003148],
    [ -0.073922, 0.055095,0.003148],
])

punkt_start_dla_kazdej_nogi = P4

ilosc_punktow_na_etap = 10
kat_obrotu = np.deg2rad(20)
h = l3 / 2

punkt_po_obrocie_dla_kazdej_nogi = np.array([
    push_leg(kat_obrotu, punkt_start_dla_kazdej_nogi, przyczepy_nog_do_tulowia[i], i)
    for i in range(6)
])

#ruch każdej nogi dzieli się na parabolę i ruch po podłodze

punkt_szczytowy_dla_kazdej_nogi = np.array([
    (punkt_po_obrocie_dla_kazdej_nogi[i] + punkt_start_dla_kazdej_nogi) / 2 + np.array([0, 0, h])
    for i in range(6)
])
#nogi 1 3 5 najpierw pchają a 2 4 6 parabola
#funkcja parabola w przestrzeni uwzglednia rodzaj nogi (1 3 5 lub 2 4 6) bo ich parabole sie liczy tak samo ale punkty w tablicy są w odwrotnej kolejności

parabole_nog = np.array([parabola_w_przestrzeni_z_punktow(punkt_start_dla_kazdej_nogi, punkt_szczytowy_dla_kazdej_nogi[i], punkt_po_obrocie_dla_kazdej_nogi[i], ilosc_punktow_na_etap, i) for i in range(6)])
proste_nog = np.array([prosta_w_cyklu(punkt_start_dla_kazdej_nogi, punkt_po_obrocie_dla_kazdej_nogi[i], i, ilosc_punktow_na_etap) for i in range (6)])

cykle_nog = []
ilosc_cykli = 10
for i in range(6):  # Dla każdej nogi
    cykl = []
    for c in range(ilosc_cykli):
        if i in [0, 2, 4]:
            cykl.append(proste_nog[i])
            cykl.append(parabole_nog[i])
        else:
            cykl.append(parabole_nog[i])
            cykl.append(proste_nog[i])
    cykle_nog.append(np.concatenate(cykl))  # Połącz punkty w jeden cykl

cykle_nog = np.array(cykle_nog)

wychyly_serw_podczas_ruchu = np.array([
[katy_serw(cykle_nog[j][i], l1, h1, l2, h2, l3)
    for i in range(len(cykle_nog[j]))]
    for j in range(6)
])

czy_wyswietlic = False

if czy_wyswietlic:

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    for i in range(6):
        # Parabola – ruch podnoszenia nogi
        ax.scatter(parabole_nog[i][:, 0], parabole_nog[i][:, 1], parabole_nog[i][:, 2], color=colors[i],
                label=f'Parabola noga {i + 1}')
        # Prosta – ruch po podłodze
        ax.scatter(proste_nog[i][:, 0], proste_nog[i][:, 1], proste_nog[i][:, 2], color=colors[i], linestyle='dashed',
                label=f'Prosta noga {i + 1}')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Trajektorie ruchu nóg robota sześcionożnego')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
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
    
    def execute_sequence(self, start_step=0, end_step=None, step_duration=0.1):
        """
        Wykonanie sekwencji ruchów dla wszystkich nóg równocześnie
        używając wartości z tablicy wychyly_serw_podczas_ruchu
        """
        self.get_logger().info('Rozpoczynam sekwencję ruchów dla wszystkich nóg')
        
        # Jeśli nie podano end_step, użyj całej tablicy
        if end_step is None:
            end_step = len(wychyly_serw_podczas_ruchu[0])
        
        # Przejście do pozycji początkowej (pierwszy punkt w tablicy)
        self.send_trajectory_to_all_legs_at_step(start_step, duration_sec=3.0)
        self.get_logger().info('Oczekiwanie na wykonanie początkowego ruchu...')
        time.sleep(3.0)
        
        # Wykonanie sekwencji ruchów
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
