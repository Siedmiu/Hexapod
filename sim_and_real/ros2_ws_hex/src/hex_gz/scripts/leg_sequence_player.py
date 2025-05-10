#!/usr/bin/env python3

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

# Długosci segmentow nog
h1 = -0.016854 - 0.003148
l1 = 0.12886 - 0.0978
l2 = 0.2188-0.12886
h2 = -0.011804 + 0.016854
l3 = 0.38709 - 0.2188
staly_kat_przy_P1 = np.arctan2(h2, l2)
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

# tor pokonywany przez nogi w ukladzie wspolrzednych srodka robota
h = l3 / 4
r = h
ilosc_punktow_na_krzywych = 20
punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, ilosc_punktow_na_krzywych)
punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
punkty_etap4_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r, h, 2 * ilosc_punktow_na_krzywych, 20000, -r)
punkty_etap5_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, -r)
cykl_ogolny_nog_1_3_5 = punkty_etap1_ruchu.copy()
cykl_ogolny_nog_2_4_6 = punkty_etap3_ruchu.copy()

ilosc_cykli = 10 # jak dlugo pajak idzie

for _ in range(ilosc_cykli):
    cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap4_ruchu
    cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu + punkty_etap3_ruchu

cykl_ogolny_nog_1_3_5 += punkty_etap2_ruchu + punkty_etap3_ruchu + punkty_etap5_ruchu
cykl_ogolny_nog_2_4_6 += punkty_etap4_ruchu + punkty_etap2_ruchu
cykl_ogolny_nog_1_3_5 = np.array(cykl_ogolny_nog_1_3_5)
cykl_ogolny_nog_2_4_6 = np.array(cykl_ogolny_nog_2_4_6)

# tablica cykli, gdzie jest zapisana kazda z nog, kazdy punkt w cylku i jego wspolrzedne, kazda z nog musi miec swoj wlasny
# cykl poruszania ze wzgledu na katy pod jakimi sa ustawione wzgledem srodka robota

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
np.set_printoptions(threshold=np.inf)
print(polozenia_stop_podczas_cyklu[2])

#wychyly podawane odpowiednio dla 1 2 i 3 przegubu w radianach
wychyly_serw_podczas_ruchu = np.array([
[katy_serw(polozenia_stop_podczas_cyklu[j][i], l1, h1, l2, h2, l3)
    for i in range(len(cykl_ogolny_nog_1_3_5))]
    for j in range(6)
])

#print(wychyly_serw_podczas_ruchu[0])
#obliczanie polozenia przegubow i stop z wyliczonymi wychyleniami serw

class LegSequencePlayer(Node):
    def __init__(self):
        super().__init__('leg_sequence_player')
        self.get_logger().info('Inicjalizacja węzła do sekwencji ruchów')
        
        # Wydawcy dla kontrolerów wszystkich nóg
        self.trajectory_publishers = {
            1: self.create_publisher(JointTrajectory, '/leg1_controller/joint_trajectory', 10),
            2: self.create_publisher(JointTrajectory, '/leg2_controller/joint_trajectory', 10),
            3: self.create_publisher(JointTrajectory, '/leg3_controller/joint_trajectory', 10),
            4: self.create_publisher(JointTrajectory, '/leg4_controller/joint_trajectory', 10),
            5: self.create_publisher(JointTrajectory, '/leg5_controller/joint_trajectory', 10),
            6: self.create_publisher(JointTrajectory, '/leg6_controller/joint_trajectory', 10)
        }
        
        # Definicje pozycji (możesz dostosować wartości na podstawie twoich pozycji)
        self.positions = {
            # Na podstawie twoich definicji w pliku SRDF
            'home_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][-1][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][-1][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][-1][2],
            },
            'przod_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][19][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][19][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][19][2],
            },
            'tyl_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][59][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][59][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][59][2],
            },
            'up_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][79][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][79][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][79][2],
            },
            'half_up_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][9][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][9][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][9][2],
            },
            'half_back_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][49][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][49][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][49][2],
            },
            'half_back_up_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][-11][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][-11][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][-11][2],
            },
            'half_front_1': {
                'joint1_1': wychyly_serw_podczas_ruchu[0][29][0],
                'joint2_1': wychyly_serw_podczas_ruchu[0][29][1],
                'joint3_1': wychyly_serw_podczas_ruchu[0][29][2],
            },



            'home_2': {
                'joint1_2': wychyly_serw_podczas_ruchu[1][-1][0],
                'joint2_2': wychyly_serw_podczas_ruchu[1][-1][1],
                'joint3_2': wychyly_serw_podczas_ruchu[1][-1][2],
            },
            'przod_2': {
                'joint1_2': wychyly_serw_podczas_ruchu[1][59][0],
                'joint2_2': wychyly_serw_podczas_ruchu[1][59][1],
                'joint3_2': wychyly_serw_podczas_ruchu[1][59][2],
            },
            'tyl_2': {
                'joint1_2': wychyly_serw_podczas_ruchu[1][19][0],
                'joint2_2': wychyly_serw_podczas_ruchu[1][19][1],
                'joint3_2': wychyly_serw_podczas_ruchu[1][19][2],
            },
            'up_2': {
                'joint1_2': wychyly_serw_podczas_ruchu[1][39][0],
                'joint2_2': wychyly_serw_podczas_ruchu[1][39][1],
                'joint3_2': wychyly_serw_podczas_ruchu[1][39][2],
            },
            'half_back_2': {
                'joint1_2': wychyly_serw_podczas_ruchu[1][9][0],
                'joint2_2': wychyly_serw_podczas_ruchu[1][9][1],
                'joint3_2': wychyly_serw_podczas_ruchu[1][9][2],
            },
            'half_front_2': {
                'joint1_2': wychyly_serw_podczas_ruchu[1][69][0],
                'joint2_2': wychyly_serw_podczas_ruchu[1][69][1],
                'joint3_2': wychyly_serw_podczas_ruchu[1][69][2],
            },



            'home_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][-1][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][-1][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][-1][2],
            },
            'przod_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][19][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][19][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][19][2],
            },
            'tyl_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][59][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][59][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][59][2],
            },
            'up_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][79][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][79][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][79][2],
            },
            'half_up_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][9][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][9][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][9][2],
            },
            'half_back_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][49][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][49][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][49][2],
            },
            'half_back_up_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][-11][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][-11][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][-11][2],
            },
            'half_front_3': {
                'joint1_3': wychyly_serw_podczas_ruchu[2][29][0],
                'joint2_3': wychyly_serw_podczas_ruchu[2][29][1],
                'joint3_3': wychyly_serw_podczas_ruchu[2][29][2],
            },



            'home_4': {
                'joint1_4': wychyly_serw_podczas_ruchu[3][-1][0],
                'joint2_4': wychyly_serw_podczas_ruchu[3][-1][1],
                'joint3_4': wychyly_serw_podczas_ruchu[3][-1][2],
            },
            'przod_4': {
                'joint1_4': wychyly_serw_podczas_ruchu[3][59][0],
                'joint2_4': wychyly_serw_podczas_ruchu[3][59][1],
                'joint3_4': wychyly_serw_podczas_ruchu[3][59][2],
            },
            'tyl_4': {
                'joint1_4': wychyly_serw_podczas_ruchu[3][19][0],
                'joint2_4': wychyly_serw_podczas_ruchu[3][19][1],
                'joint3_4': wychyly_serw_podczas_ruchu[3][19][2],
            },
            'up_4': {
                'joint1_4': wychyly_serw_podczas_ruchu[3][39][0],
                'joint2_4': wychyly_serw_podczas_ruchu[3][39][1],
                'joint3_4': wychyly_serw_podczas_ruchu[3][39][2],
            },
            'half_back_4': {
                'joint1_4': wychyly_serw_podczas_ruchu[3][9][0],
                'joint2_4': wychyly_serw_podczas_ruchu[3][9][1],
                'joint3_4': wychyly_serw_podczas_ruchu[3][9][2],
            },
            'half_front_4': {
                'joint1_4': wychyly_serw_podczas_ruchu[3][69][0],
                'joint2_4': wychyly_serw_podczas_ruchu[3][69][1],
                'joint3_4': wychyly_serw_podczas_ruchu[3][69][2],
            },



            'home_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][-1][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][-1][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][-1][2],
            },
            'przod_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][19][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][19][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][19][2],
            },
            'tyl_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][59][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][59][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][59][2],
            },
            'up_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][79][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][79][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][79][2],
            },
            'half_up_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][9][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][9][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][9][2],
            },
            'half_back_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][49][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][49][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][49][2],
            },
            'half_back_up_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][-11][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][-11][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][-11][2],
            },
            'half_front_5': {
                'joint1_5': wychyly_serw_podczas_ruchu[4][29][0],
                'joint2_5': wychyly_serw_podczas_ruchu[4][29][1],
                'joint3_5': wychyly_serw_podczas_ruchu[4][29][2],
            },



            'home_6': {
                'joint1_6': wychyly_serw_podczas_ruchu[5][-1][0],
                'joint2_6': wychyly_serw_podczas_ruchu[5][-1][1],
                'joint3_6': wychyly_serw_podczas_ruchu[5][-1][2],
            },
            'przod_6': {
                'joint1_6': wychyly_serw_podczas_ruchu[5][59][0],
                'joint2_6': wychyly_serw_podczas_ruchu[5][59][1],
                'joint3_6': wychyly_serw_podczas_ruchu[5][59][2],
            },
            'tyl_6': {
                'joint1_6': wychyly_serw_podczas_ruchu[5][19][0],
                'joint2_6': wychyly_serw_podczas_ruchu[5][19][1],
                'joint3_6': wychyly_serw_podczas_ruchu[5][19][2],
            },
            'up_6': {
                'joint1_6': wychyly_serw_podczas_ruchu[5][39][0],
                'joint2_6': wychyly_serw_podczas_ruchu[5][39][1],
                'joint3_6': wychyly_serw_podczas_ruchu[5][39][2],
            },
            'half_back_6': {
                'joint1_6': wychyly_serw_podczas_ruchu[5][9][0],
                'joint2_6': wychyly_serw_podczas_ruchu[5][9][1],
                'joint3_6': wychyly_serw_podczas_ruchu[5][9][2],
            },
            'half_front_6': {
                'joint1_6': wychyly_serw_podczas_ruchu[5][69][0],
                'joint2_6': wychyly_serw_podczas_ruchu[5][69][1],
                'joint3_6': wychyly_serw_podczas_ruchu[5][69][2],
            },
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
        
    def send_trajectory_to_all_legs(self, positions_dict, duration_sec=2.0):
        """
        Wysyła trajektorię do kontrolerów wszystkich nóg jednocześnie
        positions_dict to słownik z pozycjami dla wszystkich nóg, np. {"home_1", "home_2", ...}
        """
        self.get_logger().info(f'Wysyłam trajektorię do pozycji: {positions_dict}')
        
        # Sprawdź, czy wszystkie pozycje istnieją
        for leg_num, position_name in positions_dict.items():
            if position_name not in self.positions:
                self.get_logger().error(f'Pozycja {position_name} nie istnieje!')
                return False
        
        # Ustaw czas trwania ruchu
        duration = Duration()
        duration.sec = int(duration_sec)
        duration.nanosec = int((duration_sec - int(duration_sec)) * 1e9)
        
        # Dla każdej nogi przygotuj i wyślij trajektorię
        for leg_num, position_name in positions_dict.items():
            # Utwórz wiadomość trajektorii dla nogi
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names[leg_num]
            
            # Utwórz punkt trajektorii
            point = JointTrajectoryPoint()
            
            # Ustaw pozycje stawów
            position_values = []
            for joint in self.joint_names[leg_num]:
                position_values.append(self.positions[position_name][joint])
            
            point.positions = position_values
            point.velocities = [0.0] * len(self.joint_names[leg_num])
            point.accelerations = [0.0] * len(self.joint_names[leg_num])
            
            # Ustaw czas trwania ruchu
            point.time_from_start = duration
            
            # Dodaj punkt do trajektorii
            trajectory.points.append(point)
            
            # Wyślij trajektorię
            self.trajectory_publishers[leg_num].publish(trajectory)
        
        self.get_logger().info('Wysłano trajektorie dla wszystkich nóg')
        return True
    
    def execute_sequence(self):
        """Wykonanie sekwencji ruchów dla wszystkich nóg równocześnie"""
        self.get_logger().info('Rozpoczynam sekwencję ruchów dla wszystkich nóg')
        
        # Przejście do pozycji początkowej dla wszystkich nóg
        self.send_trajectory_to_all_legs({
            1: "home_1",
            2: "home_2",
            3: "home_3",
            4: "home_4",
            5: "home_5",
            6: "home_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(2.0)  # Daj czas na wykonanie ruchu

        # Przejście do pozycji początkowej sekwencji
        self.send_trajectory_to_all_legs({
            1: "half_up_1",
            2: "half_back_2",
            3: "half_up_3",
            4: "half_back_4",
            5: "half_up_5",
            6: "half_back_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(1.0)
        
        self.send_trajectory_to_all_legs({
            1: "przod_1",
            2: "tyl_2",
            3: "przod_3",
            4: "tyl_4",
            5: "przod_5",
            6: "tyl_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(2.0)  # Daj czas na wykonanie ruchu

        for i in range(3):
            self.send_trajectory_to_all_legs({
                1: "home_1",
                2: "up_2",
                3: "home_3",
                4: "up_4",
                5: "home_5",
                6: "up_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)  # Daj czas na wykonanie ruchu

            self.send_trajectory_to_all_legs({
                1: "tyl_1",
                2: "przod_2",
                3: "tyl_3",
                4: "przod_4",
                5: "tyl_5",
                6: "przod_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(2.0)  # Daj czas na wykonanie ruchu

            self.send_trajectory_to_all_legs({
                1: "up_1",
                2: "home_2",
                3: "up_3",
                4: "home_4",
                5: "up_5",
                6: "home_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(1.5)

            self.send_trajectory_to_all_legs({
                1: "przod_1",
                2: "tyl_2",
                3: "przod_3",
                4: "tyl_4",
                5: "przod_5",
                6: "tyl_6"
            })
            self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
            time.sleep(2.0)  # Daj czas na wykonanie ruchu


        self.send_trajectory_to_all_legs({
            1: "home_1",
            2: "up_2",
            3: "home_3",
            4: "up_4",
            5: "home_5",
            6: "up_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(1.0)


        self.send_trajectory_to_all_legs({
            1: "tyl_1",
            2: "przod_2",
            3: "tyl_3",
            4: "przod_4",
            5: "tyl_5",
            6: "przod_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(1.0)

        self.send_trajectory_to_all_legs({
            1: "half_back_up_1",
            2: "half_front_2",
            3: "half_back_up_3",
            4: "half_front_4",
            5: "half_back_up_5",
            6: "half_front_6"
        })
        self.get_logger().info('Oczekiwanie na wykonanie ruchu...')
        time.sleep(1.0)


        self.send_trajectory_to_all_legs({
            1: "home_1",
            2: "home_2",
            3: "home_3",
            4: "home_4",
            5: "home_5",
            6: "home_6"
        })


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
