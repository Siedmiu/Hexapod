#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
import numpy as np
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def katy_serw(x_docelowy, y_docelowy, z_docelowy, L1, L2, L3):
    r = np.sqrt(x_docelowy ** 2 + y_docelowy ** 2)
    d = np.sqrt(z_docelowy ** 2 + (r - L1) ** 2)
    alfa_1 = np.arctan2(y_docelowy, x_docelowy)
    alfa_2 = np.arccos((L2 ** 2 + d ** 2 - L3 ** 2) / (2 * L2 * d)) + np.arctan2(z_docelowy, (r - L1))
    alfa_3 = np.arccos((L2 ** 2 + L3 ** 2 - d ** 2) / (2 * L2 * L3))
    return [alfa_1, alfa_2, alfa_3 + np.radians(45) - np.radians(180)]


def parabola_w_przestrzeni_z_punktow(w1, w2, w3, liczba_punktow):
    a, b, c = [], [], []
    dokladnosc = 1000
    for i in range(3):
        a.append(w1[i] / 2 - w2[i] + w3[i] / 2)
        b.append(-w1[i] * 3 / 2 + 2 * w2[i] - w3[i] / 2)
        c.append(w1[i])

    t = np.linspace(0, 2, dokladnosc)
    p = np.array([a[0] * t**2 + b[0] * t + c[0],
                 a[1] * t**2 + b[1] * t + c[1],
                 a[2] * t**2 + b[2] * t + c[2]]).T

    dlugosci_segmentow = np.sqrt(np.sum(np.diff(p, axis=0)**2, axis=1))
    dlugosci_luku = np.concatenate(([0], np.cumsum(dlugosci_segmentow)))
    dlugosc_calkowita = dlugosci_luku[-1]
    dlugosci_celowe = np.linspace(0, dlugosc_calkowita, liczba_punktow + 1)

    punkty_rowne = np.array([
        np.interp(dlugosci_celowe, dlugosci_luku, p[:, i]) for i in range(3)
    ]).T
    return punkty_rowne[1:]


class SerialLegController(Node):
    def __init__(self):
        super().__init__('serial_leg_controller')
        self.ser = serial.Serial('/dev/ttyUSB0', 115200)  # Dostosuj port!
        self.get_logger().info("Serial port initialized")

    def send_joint_positions(self, joint_positions):
        angles_deg = {
            'servo1': np.rad2deg(joint_positions['joint1']),
            'servo2': np.rad2deg(joint_positions['joint2']),
            'servo3': np.rad2deg(joint_positions['joint3']),
        }

        for name, angle in angles_deg.items():
            angle = int(max(0, min(180, angle)))  # ograniczenie 0–180
            command = f"{name} {angle}\n"
            self.ser.write(command.encode())
            self.get_logger().info(f"Sent: {command.strip()}")


def main(args=None):
    rclpy.init(args=args)
    controller = SerialLegController()

    # Parametry nogi
    L1 = 0.0338968
    L2 = 0.090175
    L3 = 0.18278
    ilosc_punktow_na_krzywych = 20
    r = 0.05

    punkty_etap2 = [[0, y, -0.1] for y in np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)]
    punkty_etap3 = [[0, y, -0.1] for y in np.linspace(-r / ilosc_punktow_na_krzywych, -r, ilosc_punktow_na_krzywych)]
    punkty_etap4 = parabola_w_przestrzeni_z_punktow([0.25, -0.05, -0.1], [0.25, 0, -0.02], [0.25, 0.05, -0.1], ilosc_punktow_na_krzywych*2)

    cykl = np.array(punkty_etap3)
    for _ in range(3):  # liczba cykli
        cykl = np.concatenate([cykl, punkty_etap4, punkty_etap2, punkty_etap3])
    cykl = np.concatenate([cykl, punkty_etap4, punkty_etap2])
    cykl = np.array(cykl)

    wychyly = np.array([
        katy_serw(p[0], p[1], p[2], L1, L2, L3)
        for p in cykl
    ])

    home_position = {
        'joint1': wychyly[0][0],
        'joint2': wychyly[0][1],
        'joint3': wychyly[0][2] + np.deg2rad(45)
    }

    dt = 0.1  # sekundy między krokami

    try:
        controller.send_joint_positions(home_position)
        time.sleep(1.0)

        for i in range(len(wychyly)):
            current_position = {
                'joint1': wychyly[i][0],
                'joint2': wychyly[i][1],
                'joint3': wychyly[i][2] + np.deg2rad(45)
            }
            controller.send_joint_positions(current_position)
            time.sleep(dt)

        controller.send_joint_positions(home_position)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()