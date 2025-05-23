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


h = l3 / 3
r = h / 2.5
ilosc_punktow_na_krzywych = 20
punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, int(ilosc_punktow_na_krzywych*2.5))
punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(int(ilosc_punktow_na_krzywych*2.5))]
punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, int(ilosc_punktow_na_krzywych*2.5))
punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], 0] for i in range(int(ilosc_punktow_na_krzywych*2.5))]
punkty_etap4_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r, h, ilosc_punktow_na_krzywych, 20000, -r)
punkty_etap5_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, -r)


cały_cykl = np.concatenate([punkty_etap2_ruchu, punkty_etap3_ruchu, punkty_etap4_ruchu])

fragmenty = np.array_split(cały_cykl, 6)
print(len(fragmenty[0]))

tył_1 = fragmenty[0]
tył_2 = fragmenty[1]
tył_3 = fragmenty[2]
tył_4 = fragmenty[3]
tył_5 = fragmenty[4]
czesc_z_parabola = fragmenty[5]

odleglosc_srodek_tyl1 = np.linalg.norm(tył_1[-1] - punkty_etap1_ruchu[0])
odleglosc_srodek_tyl2 = np.linalg.norm(tył_2[-1] - punkty_etap1_ruchu[0])
odleglosc_srodek_tyl3 = np.linalg.norm(tył_3[-1] - punkty_etap1_ruchu[0])
odleglosc_srodek_tyl4 = np.linalg.norm(tył_4[-1] - punkty_etap1_ruchu[0])
odleglosc_srodek_tyl5 = np.linalg.norm(tył_5[-1] - punkty_etap1_ruchu[0])


dlugośc_malego_kroku = 10

pierwszy_krok_1_nogi = znajdz_punkty_rowno_odlegle_na_paraboli(odleglosc_srodek_tyl2, h/2, dlugośc_malego_kroku, 10000, 0)
template = np.array([punkty_etap1_ruchu[0] for _ in range(dlugośc_malego_kroku)]) # utrzymanie się w 0
pierwszy_krok_2_nogi = template.copy()
pierwszy_krok_3_nogi = template.copy()
pierwszy_krok_4_nogi = template.copy()
pierwszy_krok_5_nogi = template.copy()
pierwszy_krok_6_nogi = template.copy()


drugi_krok_1_nogi = np.array([tył_2[-1] for _ in range(dlugośc_malego_kroku)])
drugi_krok_2_nogi = znajdz_punkty_rowno_odlegle_na_paraboli(odleglosc_srodek_tyl1, h/2, dlugośc_malego_kroku, 10000, 0)
drugi_krok_3_nogi = template.copy()
drugi_krok_4_nogi = template.copy()
drugi_krok_5_nogi = template.copy()
drugi_krok_6_nogi = template.copy()


trzeci_krok_1_nogi = np.array([tył_2[-1] for _ in range(dlugośc_malego_kroku)])
trzeci_krok_2_nogi = np.array([tył_1[-1] for _ in range(dlugośc_malego_kroku)])
trzeci_krok_3_nogi = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, dlugośc_malego_kroku, 10000, 0)
trzeci_krok_4_nogi = template.copy()
trzeci_krok_5_nogi = template.copy()
trzeci_krok_6_nogi = template.copy()


czwarty_krok_1_nogi = np.array([tył_2[-1] for _ in range(dlugośc_malego_kroku)])
czwarty_krok_2_nogi = np.array([tył_1[-1] for _ in range(dlugośc_malego_kroku)])
czwarty_krok_3_nogi = np.array([punkty_etap4_ruchu[-1] for _ in range(dlugośc_malego_kroku)])
czwarty_krok_4_nogi = znajdz_punkty_rowno_odlegle_na_paraboli(-r, h/2, dlugośc_malego_kroku, 1000, 0)
czwarty_krok_5_nogi = template.copy()
czwarty_krok_6_nogi = template.copy()


piaty_krok_1_nogi = np.array([tył_2[-1] for _ in range(dlugośc_malego_kroku)])
piaty_krok_2_nogi = np.array([tył_1[-1] for _ in range(dlugośc_malego_kroku)])
piaty_krok_3_nogi = np.array([punkty_etap4_ruchu[-1] for _ in range(dlugośc_malego_kroku)])
piaty_krok_4_nogi = np.array([tył_5[-1] for _ in range(dlugośc_malego_kroku)])
piaty_krok_5_nogi = znajdz_punkty_rowno_odlegle_na_paraboli(-odleglosc_srodek_tyl4, h/2, dlugośc_malego_kroku, 1000, 0)
piaty_krok_6_nogi = template.copy()


szosty_krok_6_nogi = znajdz_punkty_rowno_odlegle_na_paraboli(-odleglosc_srodek_tyl3, h/2, dlugośc_malego_kroku, 1000, 0)
szosty_krok_1_nogi = np.array([tył_2[-1] for _ in range(dlugośc_malego_kroku)])
szosty_krok_2_nogi = np.array([tył_1[-1] for _ in range(dlugośc_malego_kroku)])
szosty_krok_3_nogi = np.array([punkty_etap4_ruchu[-1] for _ in range(dlugośc_malego_kroku)])
szosty_krok_4_nogi = np.array([tył_5[-1] for _ in range(dlugośc_malego_kroku)])
szosty_krok_5_nogi = np.array([tył_4[-1] for _ in range(dlugośc_malego_kroku)])


cykl_nogi_1 = np.concatenate([pierwszy_krok_1_nogi, drugi_krok_1_nogi, trzeci_krok_1_nogi, czwarty_krok_1_nogi, piaty_krok_1_nogi, szosty_krok_1_nogi])
cykl_nogi_2 = np.concatenate([pierwszy_krok_2_nogi, drugi_krok_2_nogi, trzeci_krok_2_nogi, czwarty_krok_2_nogi, piaty_krok_2_nogi, szosty_krok_2_nogi])
cykl_nogi_3 = np.concatenate([pierwszy_krok_3_nogi, drugi_krok_3_nogi, trzeci_krok_3_nogi, czwarty_krok_3_nogi, piaty_krok_3_nogi, szosty_krok_3_nogi])
cykl_nogi_4 = np.concatenate([pierwszy_krok_4_nogi, drugi_krok_4_nogi, trzeci_krok_4_nogi, czwarty_krok_4_nogi, piaty_krok_4_nogi, szosty_krok_4_nogi])
cykl_nogi_5 = np.concatenate([pierwszy_krok_5_nogi, drugi_krok_5_nogi, trzeci_krok_5_nogi, czwarty_krok_5_nogi, piaty_krok_5_nogi, szosty_krok_5_nogi])
cykl_nogi_6 = np.concatenate([pierwszy_krok_6_nogi, drugi_krok_6_nogi, trzeci_krok_6_nogi, czwarty_krok_6_nogi, piaty_krok_6_nogi, szosty_krok_6_nogi])


ilosc_cykli = 3

for _ in range(ilosc_cykli):
    cykl_nogi_1 = np.concatenate([cykl_nogi_1, tył_3, tył_4, tył_5, czesc_z_parabola, tył_1, tył_2])
    cykl_nogi_2 = np.concatenate([cykl_nogi_2, tył_2, tył_3, tył_4, tył_5, czesc_z_parabola, tył_1])
    cykl_nogi_3 = np.concatenate([cykl_nogi_3, tył_1, tył_2, tył_3, tył_4, tył_5, czesc_z_parabola])
    cykl_nogi_4 = np.concatenate([cykl_nogi_4, czesc_z_parabola, tył_1, tył_2, tył_3, tył_4, tył_5])
    cykl_nogi_5 = np.concatenate([cykl_nogi_5, tył_5, czesc_z_parabola, tył_1, tył_2, tył_3, tył_4])
    cykl_nogi_6 = np.concatenate([cykl_nogi_6, tył_4, tył_5, czesc_z_parabola, tył_1, tył_2, tył_3])


pierwszy_od_konca_krok_1_nogi = pierwszy_krok_1_nogi[::-1]
pierwszy_od_konca_krok_2_nogi = np.array([tył_1[-1] for _ in range(dlugośc_malego_kroku)])
pierwszy_od_konca_krok_3_nogi = np.array([punkty_etap4_ruchu[-1] for _ in range(dlugośc_malego_kroku)])
pierwszy_od_konca_krok_4_nogi = np.array([tył_5[-1] for _ in range(dlugośc_malego_kroku)])
pierwszy_od_konca_krok_5_nogi = np.array([tył_4[-1] for _ in range(dlugośc_malego_kroku)])
pierwszy_od_konca_krok_6_nogi = np.array([tył_3[-1] for _ in range(dlugośc_malego_kroku)])

drugi_od_konca_krok_1_nogi = template.copy()
drugi_od_konca_krok_2_nogi = drugi_krok_2_nogi[::-1]
drugi_od_konca_krok_3_nogi = np.array([punkty_etap4_ruchu[-1] for _ in range(dlugośc_malego_kroku)])
drugi_od_konca_krok_4_nogi = np.array([tył_5[-1] for _ in range(dlugośc_malego_kroku)])
drugi_od_konca_krok_5_nogi = np.array([tył_4[-1] for _ in range(dlugośc_malego_kroku)])
drugi_od_konca_krok_6_nogi = np.array([tył_3[-1] for _ in range(dlugośc_malego_kroku)])


trzeci_od_konca_krok_1_nogi = template.copy()
trzeci_od_konca_krok_2_nogi = template.copy()
trzeci_od_konca_krok_3_nogi = trzeci_krok_3_nogi[::-1]
trzeci_od_konca_krok_4_nogi = np.array([tył_5[-1] for _ in range(dlugośc_malego_kroku)])
trzeci_od_konca_krok_5_nogi = np.array([tył_4[-1] for _ in range(dlugośc_malego_kroku)])
trzeci_od_konca_krok_6_nogi = np.array([tył_3[-1] for _ in range(dlugośc_malego_kroku)])

czwarty_od_konca_krok_1_nogi = template.copy()
czwarty_od_konca_krok_2_nogi = template.copy()
czwarty_od_konca_krok_3_nogi = template.copy()
czwarty_od_konca_krok_4_nogi = czwarty_krok_4_nogi[::-1]
czwarty_od_konca_krok_5_nogi = np.array([tył_4[-1] for _ in range(dlugośc_malego_kroku)])
czwarty_od_konca_krok_6_nogi = np.array([tył_3[-1] for _ in range(dlugośc_malego_kroku)])


piaty_od_konca_krok_1_nogi = template.copy()
piaty_od_konca_krok_2_nogi = template.copy()
piaty_od_konca_krok_3_nogi = template.copy()
piaty_od_konca_krok_4_nogi = template.copy()
piaty_od_konca_krok_5_nogi = piaty_krok_5_nogi[::-1]
piaty_od_konca_krok_6_nogi = np.array([tył_3[-1] for _ in range(dlugośc_malego_kroku)])


szosty_od_konca_krok_1_nogi = template.copy()
szosty_od_konca_krok_2_nogi = template.copy()
szosty_od_konca_krok_3_nogi = template.copy()
szosty_od_konca_krok_4_nogi = template.copy()
szosty_od_konca_krok_5_nogi = template.copy()
szosty_od_konca_krok_6_nogi = szosty_krok_6_nogi[::-1]


cykl_nogi_1 = np.concatenate([cykl_nogi_1, pierwszy_od_konca_krok_1_nogi, drugi_od_konca_krok_1_nogi, trzeci_od_konca_krok_1_nogi, czwarty_od_konca_krok_1_nogi, piaty_od_konca_krok_1_nogi, szosty_od_konca_krok_1_nogi])
cykl_nogi_2 = np.concatenate([cykl_nogi_2, pierwszy_od_konca_krok_2_nogi, drugi_od_konca_krok_2_nogi, trzeci_od_konca_krok_2_nogi, czwarty_od_konca_krok_2_nogi, piaty_od_konca_krok_2_nogi, szosty_od_konca_krok_2_nogi])
cykl_nogi_3 = np.concatenate([cykl_nogi_3, pierwszy_od_konca_krok_3_nogi, drugi_od_konca_krok_3_nogi, trzeci_od_konca_krok_3_nogi, czwarty_od_konca_krok_3_nogi, piaty_od_konca_krok_3_nogi, szosty_od_konca_krok_3_nogi])
cykl_nogi_4 = np.concatenate([cykl_nogi_4, pierwszy_od_konca_krok_4_nogi, drugi_od_konca_krok_4_nogi, trzeci_od_konca_krok_4_nogi, czwarty_od_konca_krok_4_nogi, piaty_od_konca_krok_4_nogi, szosty_od_konca_krok_4_nogi])
cykl_nogi_5 = np.concatenate([cykl_nogi_5, pierwszy_od_konca_krok_5_nogi, drugi_od_konca_krok_5_nogi, trzeci_od_konca_krok_5_nogi, czwarty_od_konca_krok_5_nogi, piaty_od_konca_krok_5_nogi, szosty_od_konca_krok_5_nogi])
cykl_nogi_6 = np.concatenate([cykl_nogi_6, pierwszy_od_konca_krok_6_nogi, drugi_od_konca_krok_6_nogi, trzeci_od_konca_krok_6_nogi, czwarty_od_konca_krok_6_nogi, piaty_od_konca_krok_6_nogi, szosty_od_konca_krok_6_nogi])


print("noga1: ", len(cykl_nogi_1))
print("noga2: ", len(cykl_nogi_2))
print("noga3: ", len(cykl_nogi_3))
print("noga4: ", len(cykl_nogi_4))
print("noga5: ", len(cykl_nogi_5))
print("noga6: ", len(cykl_nogi_6))

# Update the cycle array to use the new unified cycle
cykle_nog = np.array([
    [
        [cykl_nogi_1[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_1[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_1[i][2]]
        for i in range(len(cykl_nogi_1))
    ] if j == 0 else
    [
        [cykl_nogi_2[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_2[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_2[i][2]]
        for i in range(len(cykl_nogi_2))
    ] if j == 1 else
    [
        [cykl_nogi_3[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_3[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_3[i][2]]
        for i in range(len(cykl_nogi_3))
    ] if j == 2 else
    [
        [cykl_nogi_4[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_4[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_4[i][2]]
        for i in range(len(cykl_nogi_4))
    ] if j == 5 else
    [
        [cykl_nogi_5[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_5[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_5[i][2]]
        for i in range(len(cykl_nogi_5))
    ] if j == 4 else [
        [cykl_nogi_6[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
        cykl_nogi_6[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
        cykl_nogi_6[i][2]]
        for i in range(len(cykl_nogi_6))
    ]
    for j in range(6)
])

polozenia_stop_podczas_cyklu = np.array([ # polozenie_stop jest wzgledem ukladu nogi, gdzie przyczep do tulowia to punkt 0,0,0
    [[
        stopa_spoczynkowa[0] + cykle_nog[j][i][0],
        stopa_spoczynkowa[1] + cykle_nog[j][i][1],
        stopa_spoczynkowa[2] + cykle_nog[j][i][2]
    ]
    for i in range(len(cykl_nogi_1))]
    for j in range(6)
])
np.set_printoptions(threshold=np.inf)
print(polozenia_stop_podczas_cyklu[2])

#wychyly podawane odpowiednio dla 1 2 i 3 przegubu w radianach
wychyly_serw_podczas_ruchu = np.array([
[katy_serw(polozenia_stop_podczas_cyklu[j][i], l1, h1, l2, h2, l3)
    for i in range(len(cykl_nogi_1))]
    for j in range(6)
])


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
    
    def execute_sequence(self, start_step=0, end_step=None, step_duration=0.05):
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