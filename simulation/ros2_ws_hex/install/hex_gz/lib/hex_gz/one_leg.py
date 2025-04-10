#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

def katy_serw(x_docelowy, y_docelowy, z_docelowy, L1, L2, L3):
    r = np.sqrt(x_docelowy ** 2 + y_docelowy ** 2)
    d = np.sqrt(z_docelowy ** 2 + (r - L1) ** 2)

    # wyznaczenie katow potrzebnych do osiagniecia przez stope punktu docelowego
    alfa_1 = np.arctan2(y_docelowy, x_docelowy)
    alfa_2 = np.arccos((L2 ** 2 + d ** 2 - L3 ** 2) / (2 * L2 * d)) + np.arctan2(z_docelowy, (r - L1))
    alfa_3 = np.arccos((L2 ** 2 + L3 ** 2 - d ** 2) / (2 * L2 * L3))
    return [alfa_1, alfa_2, alfa_3+np.radians(45)-np.radians(180)]


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

def parabola_w_przestrzeni_z_punktow(w1, w2, w3, liczba_punktow):
#rozwiązanie układu parametrycznego równania kwadratowego dla 1 punktu w t = 0, drugiego w t = 1 i trzeciego dla t = 2
    a = []
    b = []
    c = []
    dokladnosc = 1000
    for i in range (3):
        a.append(w1[i] / 2 - w2[i] + w3[i] / 2)
        b.append(-w1[i] * 3 / 2 + 2 * w2[i] - w3[i] / 2)
        c.append(w1[i])

    t = np.linspace(0, 2, dokladnosc)
    p = np.array([a[0] * t**2 + b[0] * t + c[0],
                 a[1] * t**2 + b[1] * t + c[1],
                 a[2] * t**2 + b[2] * t + c[2]]).T

    dlugosci_segmentow = np.sqrt(np.sum(np.diff(p, axis=0)**2, axis=1))
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

# Długosci segmentow nog
L1 = 0.0338968
L2 = 0.090175
L3 = 0.18278

alfa_1 = 0
alfa_2 = 0.31655
alfa_3 = -1.0929


# tor pokonywany przez nogi w ukladzie wspolrzednych srodka robota

ilosc_punktow_na_krzywych = 20
 
r = 0.05
punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], -0.1] for i in range(ilosc_punktow_na_krzywych)]
punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, ilosc_punktow_na_krzywych)
punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], -0.1] for i in range(ilosc_punktow_na_krzywych)]
punkty_etap4_ruchu = parabola_w_przestrzeni_z_punktow([0.25, -0.05, -0.1], [0.25, 0, -0.02], [0.25, 0.05, -0.1], ilosc_punktow_na_krzywych*2)
cykl_ogolny_nog_1_3_5 = punkty_etap3_ruchu.copy()

ilosc_cykli = 3 # jak dlugo pajak idzie

for _ in range(ilosc_cykli):
    cykl_ogolny_nog_1_3_5 = np.concatenate([cykl_ogolny_nog_1_3_5, punkty_etap4_ruchu, punkty_etap2_ruchu, punkty_etap3_ruchu])

cykl_ogolny_nog_1_3_5 = np.concatenate([cykl_ogolny_nog_1_3_5, punkty_etap4_ruchu, punkty_etap2_ruchu])
cykl_ogolny_nog_1_3_5 = np.array(cykl_ogolny_nog_1_3_5)


# tablica cykli, gdzie jest zapisana kazda z nog, kazdy punkt w cylku i jego wspolrzedne, kazda z nog musi miec swoj wlasny
# cykl poruszania ze wzgledu na katy pod jakimi sa ustawione wzgledem srodka robota

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Rozdzielenie współrzędnych X, Y, Z
x = punkty_etap4_ruchu[:, 0]
y = punkty_etap4_ruchu[:, 1]
z = punkty_etap4_ruchu[:, 2]

# Wyświetlenie punktów
ax.scatter(x, y, z)

# Etykiety osi (opcjonalnie)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()


#wychyly podawane odpowiednio dla 1 2 i 3 przegubu w radianach
wychyly_serw_podczas_ruchu = np.array([
    katy_serw(cykl_ogolny_nog_1_3_5[i][0], cykl_ogolny_nog_1_3_5[i][1], cykl_ogolny_nog_1_3_5[i][2], L1, L2, L3)
    for i in range(len(cykl_ogolny_nog_1_3_5))
])
print(len(wychyly_serw_podczas_ruchu))

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller_client')

        # Tworzenie wydawcy (publishera) dla bezpośredniego sterowania trajektorią
        self.trajectory_publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        # Tworzenie klienta akcji (jeśli chcesz korzystać z interfejsu action)
        self.action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )

        # Czekamy na nawiązanie połączenia z serwerem akcji
        self.get_logger().info("Waiting for action server...")
        if not self.action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().warn("Action server not available, using only direct trajectory publisher")
        else:
            self.get_logger().info("Action server connected!")

    def move_to_position(self, joint_positions, execution_time=3.0):
        """
        Przesuwa ramię do zadanej pozycji stawów.

        Args:
            joint_positions: dict z nazwami stawów i ich wartościami (w radianach)
            execution_time: czas wykonania ruchu (w sekundach)
        """
        # Tworzymy trajektorię
        traj = JointTrajectory()
        traj.joint_names = list(joint_positions.keys())

        # Definiujemy punkt docelowy
        point = JointTrajectoryPoint()
        point.positions = list(joint_positions.values())
        point.time_from_start.sec = int(execution_time)
        point.time_from_start.nanosec = int((execution_time % 1) * 1e9)

        traj.points.append(point)

        # Publikujemy trajektorię
        self.get_logger().info(f"Moving joints to positions: {joint_positions}")
        self.trajectory_publisher.publish(traj)

    def execute_trajectory_action(self, joint_positions, execution_time=3.0):
        """
        Wykonuje ruch używając interfejsu akcji (z informacją zwrotną)

        Args:
            joint_positions: dict z nazwami stawów i ich wartościami (w radianach)
            execution_time: czas wykonania ruchu (w sekundach)
        """
        if not self.action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().error("Action server not available!")
            return False

        # Tworzymy cel akcji (action goal)
        goal = FollowJointTrajectory.Goal()

        # Tworzymy trajektorię
        traj = JointTrajectory()
        traj.joint_names = list(joint_positions.keys())

        # Definiujemy punkt docelowy
        point = JointTrajectoryPoint()
        point.positions = list(joint_positions.values())
        point.time_from_start.sec = int(execution_time)
        point.time_from_start.nanosec = int((execution_time % 1) * 1e9)

        traj.points.append(point)
        goal.trajectory = traj

        # Wysyłamy cel i czekamy na rezultat
        self.get_logger().info(f"Sending action goal for positions: {joint_positions}")
        future = self.action_client.send_goal_async(goal)

        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Goal was rejected!")
            return False

        self.get_logger().info("Goal accepted, waiting for result...")
        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result

        self.get_logger().info(f"Action completed with result: {result}")
        return True


def main(args=None):
    rclpy.init(args=args)
    controller = ArmController()

    # Pozycje zerowe dla wszystkich stawów
    zero_positions = {
        # Leg 1 (będzie kontrolowana przez animację)
        'joint1_1': 0.0,
        'joint2_1': 0.0,
        'joint3_1': 0.0,
        
        # Leg 2
        'joint1_2': 0.0,
        'joint2_2': 0.0,
        'joint3_2': 0.0,
        
        # Leg 3
        'joint1_3': 0.0,
        'joint2_3': 0.0,
        'joint3_3': 0.0,
        
        # Leg 4
        'joint1_4': 0.0,
        'joint2_4': 0.0,
        'joint3_4': 0.0,
        
        # Leg 5
        'joint1_5': 0.0,
        'joint2_5': 0.0,
        'joint3_5': 0.0,
        
        # Leg 6
        'joint1_6': 0.0,
        'joint2_6': 0.0,
        'joint3_6': 0.0
    }

    # Początkowa pozycja
    home_position = zero_positions.copy()
    home_position.update({
        'joint1_1': wychyly_serw_podczas_ruchu[0][0],
        'joint2_1': wychyly_serw_podczas_ruchu[0][1],
        'joint3_1': wychyly_serw_podczas_ruchu[0][2] + np.deg2rad(45)
    })

    # Alternatywna pozycja (w radianach)
    alt_position = zero_positions.copy()
    alt_position.update({
        'joint1_1': wychyly_serw_podczas_ruchu[0][0],
        'joint2_1': wychyly_serw_podczas_ruchu[0][1],
        'joint3_1': wychyly_serw_podczas_ruchu[0][2] + np.deg2rad(45)
    })
    
    dt = 0.1
    try:
        # Najpierw do pozycji domowej
        controller.move_to_position(home_position)
        controller.get_logger().info("Sent command to move to home position")

        for i in range(len(wychyly_serw_podczas_ruchu)):
            # Czekamy chwilę
            import time
            time.sleep(dt)

            # Aktualizacja pozycji tylko dla pierwszej nogi, pozostałe pozostają na zero
            alt_position.update({
                'joint1_1': wychyly_serw_podczas_ruchu[i][0],
                'joint2_1': wychyly_serw_podczas_ruchu[i][1],
                'joint3_1': wychyly_serw_podczas_ruchu[i][2] + np.deg2rad(45)
            })
            
            # Wysłanie komendy do kontrolera
            controller.move_to_position(alt_position)
            controller.get_logger().info(f"Sent command to move to position {i}")
            print(i)

        # Powrót do pozycji domowej
        controller.move_to_position(home_position)

    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()