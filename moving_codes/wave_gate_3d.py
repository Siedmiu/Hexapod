import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation

matplotlib.use('TkAgg')

def katy_serw(x_docelowy, y_docelowy, z_docelowy, L1, L2, L3):
    r = np.sqrt(x_docelowy ** 2 + y_docelowy ** 2)
    d = np.sqrt(z_docelowy ** 2 + (r - L1) ** 2)

    # wyznaczenie katow potrzebnych do osiagniecia przez stope punktu docelowego
    alfa_1 = np.arctan2(y_docelowy, x_docelowy)
    alfa_2 = np.arccos((L2 ** 2 + d ** 2 - L3 ** 2) / (2 * L2 * d)) + np.arctan2(z_docelowy, (r - L1))
    alfa_3 = np.arccos((L2 ** 2 + L3 ** 2 - d ** 2) / (2 * L2 * L3))
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
L1 = 3
L2 = 5
L3 = 6

# Położenie punktu spoczynku od przyczepu nogi wyznaczone na bazie katow przgubow podczas spoczynku
# WAZNE !!! jest to polozenie stopy w ukladzie punktu zaczepienia stopy a nie ukladu XYZ
# w ktorym X1 to prostopadła prosta do boku platformy do ktorej noga jest zaczepiona i rosnie w kierunku od hexapoda
# Y1 to os pokrywajaca sie z bokiem platformy do ktorego jest przyczepiona noga i rosnie w kierunku przodu hexapoda
# Z1 pokrywa sie z osia Z ukladu XYZ

# zalozone katy spoczynkowe przegubow
alfa_1 = 0
alfa_2 = np.radians(15)
alfa_3 = np.radians(90)

P1 = np.array([L1 * np.cos(alfa_1), L1 * np.sin(alfa_1), 0])
P2 = P1 + np.array([
    L2 * np.cos(alfa_1) * np.cos(alfa_2),
    L2 * np.sin(alfa_1) * np.cos(alfa_2),
    L2 * np.sin(alfa_2)
])

stopa_spoczynkowa = P2 + np.array([
    L3 * np.cos(alfa_1) * np.sin(alfa_3 - (np.pi / 2 - alfa_2)),
    L3 * np.sin(alfa_1) * np.sin(alfa_3 - (np.pi / 2 - alfa_2)),
    -L3 * np.cos(alfa_3 - (np.pi / 2 - alfa_2))
])

wysokosc_start = -stopa_spoczynkowa[2]

# Punkty tulowia
tulow = np.array([
    [2, 6, wysokosc_start],
    [4, 2, wysokosc_start],
    [4, -2, wysokosc_start],
    [2, -6, wysokosc_start],
    [-2, -6, wysokosc_start],
    [-4, -2, wysokosc_start],
    [-4, 2, wysokosc_start],
    [-2, 6, wysokosc_start],
])

# Pozycje spoczynkowe nog
przyczepy_nog_do_tulowia = np.array([
    (tulow[i] + tulow[(i + 1) % 8]) / 2 for i in [0, 1, 2, 4, 5, 6]
])

nachylenia_nog_do_bokow_platformy_pajaka = np.array([
    np.atan2(tulow[i + 1][1] - tulow[i][1], tulow[i + 1][0] - tulow[i][0]) + np.pi / 2
    for i in [0, 1, 2, 4, 5, 6]
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
h = 4
r = 3
ilosc_punktow_na_krzywych = 20
punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, 0)
punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, int(ilosc_punktow_na_krzywych*2.5))
punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(int(ilosc_punktow_na_krzywych*2.5))]
punkty_etap3_ruchu_y = np.linspace(-r / ilosc_punktow_na_krzywych, -r, int(ilosc_punktow_na_krzywych*2.5))
punkty_etap3_ruchu = [[0, punkty_etap3_ruchu_y[i], 0] for i in range(int(ilosc_punktow_na_krzywych*2.5))]
punkty_etap4_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(2 * r, h, ilosc_punktow_na_krzywych, 20000, -r)
punkty_etap5_ruchu = znajdz_punkty_rowno_odlegle_na_paraboli(r, h / 2, ilosc_punktow_na_krzywych, 10000, -r)

# Modify the cycle generation to make all legs move simultaneously
cykl_ogolny_nog = punkty_etap1_ruchu.copy()

cały_cykl = np.concatenate([punkty_etap2_ruchu, punkty_etap3_ruchu, punkty_etap4_ruchu])

fragmenty = np.array_split(cały_cykl, 6)
print(len(fragmenty[0]))

tył_1 = fragmenty[0]
tył_2 = fragmenty[1]
tył_3 = fragmenty[2]
tył_4 = fragmenty[3]
tył_5 = fragmenty[4]
czesc_z_parabola = fragmenty[5]

pierwszy_krok_1_nogi = punkty_etap1_ruchu
pierwszy_krok_2_nogi = np.linspace(punkty_etap1_ruchu[0], tył_1[-1], ilosc_punktow_na_krzywych)
pierwszy_krok_3_nogi = np.linspace(punkty_etap1_ruchu[0], tył_2[-1], ilosc_punktow_na_krzywych)
pierwszy_krok_4_nogi = np.linspace(punkty_etap1_ruchu[0], tył_3[-1], ilosc_punktow_na_krzywych)
pierwszy_krok_5_nogi = np.linspace(punkty_etap1_ruchu[0], tył_4[-1], ilosc_punktow_na_krzywych)
pierwszy_krok_6_nogi = np.linspace(punkty_etap1_ruchu[0], tył_5[-1], ilosc_punktow_na_krzywych)

#ustawianie nóg w odpowiednich miejscach na pierwszy ruch

cykl_nogi_1 = pierwszy_krok_1_nogi.copy()
cykl_nogi_2 = pierwszy_krok_2_nogi.copy()
cykl_nogi_3 = pierwszy_krok_3_nogi.copy()
cykl_nogi_4 = pierwszy_krok_4_nogi.copy()
cykl_nogi_5 = pierwszy_krok_5_nogi.copy()
cykl_nogi_6 = pierwszy_krok_6_nogi.copy()

ilosc_cykli = 10 # jak dlugo pajak idzie

for _ in range(ilosc_cykli):
    cykl_nogi_1 = np.concatenate([cykl_nogi_1, tył_1, tył_2, tył_3, tył_4, tył_5, czesc_z_parabola])
    cykl_nogi_2 = np.concatenate([cykl_nogi_2, tył_2, tył_3, tył_4, tył_5, czesc_z_parabola, tył_1])
    cykl_nogi_3 = np.concatenate([cykl_nogi_3, tył_3, tył_4, tył_5, czesc_z_parabola, tył_1, tył_2])
    cykl_nogi_4 = np.concatenate([cykl_nogi_4, tył_4, tył_5, czesc_z_parabola, tył_1, tył_2, tył_3])
    cykl_nogi_5 = np.concatenate([cykl_nogi_5, tył_5, czesc_z_parabola, tył_1, tył_2, tył_3, tył_4])
    cykl_nogi_6 = np.concatenate([cykl_nogi_6, czesc_z_parabola, tył_1, tył_2, tył_3, tył_4, tył_5])

# Update the cycle array to use the new unified cycle
cykle_nog = np.array([
    [
        [cykl_nogi_1[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_1[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_1[i][2]]
        for i in range(len(cykl_nogi_1))
    ] if j == 2 else
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
    ] if j == 0 else
    [
        [cykl_nogi_4[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_4[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
         cykl_nogi_4[i][2]]
        for i in range(len(cykl_nogi_4))
    ] if j == 3 else
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

#wychyly podawane odpowiednio dla 1 2 i 3 przegubu w radianach
wychyly_serw_podczas_ruchu = np.array([
    [katy_serw(polozenia_stop_podczas_cyklu[j][i][0], polozenia_stop_podczas_cyklu[j][i][1], polozenia_stop_podczas_cyklu[j][i][2], L1, L2, L3)
     for i in range(len(cykl_nogi_1))]
    for j in range(6)
])

#obliczanie polozenia przegubow i stop z wyliczonymi wychyleniami serw
def calculate_positions():
    #rownania zastosowane z kinematyki odwrotnej, nachylenia nog do bokow platformy pajaka sa dodana TYLKO DO SYMULACJI!!!
    #w rzeczywistości nie trzeba tego uwzgledniać gdyż noga bedzie fizycznie obrocona

    polozenie_punktow_pierwszych_przegubow_nog = np.array([
    [[
        przyczepy_nog_do_tulowia[j][0] + L1 * np.cos(wychyly_serw_podczas_ruchu[j][i][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]),
        przyczepy_nog_do_tulowia[j][1] + L1 * np.sin(wychyly_serw_podczas_ruchu[j][i][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]),
        przyczepy_nog_do_tulowia[j][2]
    ]
        for i in range(len(cykl_nogi_1))]
        for j in range(6)
    ])

    polozenie_punktow_drugich_przegubow_nog = polozenie_punktow_pierwszych_przegubow_nog + np.array([

    [[
        L2 * np.cos(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(wychyly_serw_podczas_ruchu[j][i][1]),
        L2 * np.sin(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(wychyly_serw_podczas_ruchu[j][i][1]),
        L2 * np.sin(wychyly_serw_podczas_ruchu[j][i][1])
    ]
        for i in range(len(cykl_nogi_1))]
        for j in range(6)
    ])

    obliczone_z_serw_polozenie_stop = polozenie_punktow_drugich_przegubow_nog + np.array([
    [[
        L3 * np.cos(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.sin(wychyly_serw_podczas_ruchu[j][i][2] - (np.pi / 2 - wychyly_serw_podczas_ruchu[j][i][1])),
        L3 * np.sin(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.sin(wychyly_serw_podczas_ruchu[j][i][2] - (np.pi / 2 - wychyly_serw_podczas_ruchu[j][i][1])),
        -L3 * np.cos(wychyly_serw_podczas_ruchu[j][i][2] - (np.pi / 2 - wychyly_serw_podczas_ruchu[j][i][1]))
    ]
        for i in range(len(cykl_nogi_1))]
        for j in range(6)
    ])
    return polozenie_punktow_pierwszych_przegubow_nog, polozenie_punktow_drugich_przegubow_nog, obliczone_z_serw_polozenie_stop

#funkcja odpowiada za rysowanie symulacji
def update(frame, lines, positions):
    first_joints, second_joints, feet = positions
    for j in range(6):
        lines[j][0].set_data([przyczepy_nog_do_tulowia[j][0], first_joints[j][frame][0]],
                             [przyczepy_nog_do_tulowia[j][1], first_joints[j][frame][1]])
        lines[j][0].set_3d_properties([przyczepy_nog_do_tulowia[j][2], first_joints[j][frame][2]])

        lines[j][1].set_data([first_joints[j][frame][0], second_joints[j][frame][0]],
                             [first_joints[j][frame][1], second_joints[j][frame][1]])
        lines[j][1].set_3d_properties([first_joints[j][frame][2], second_joints[j][frame][2]])

        lines[j][2].set_data([second_joints[j][frame][0], feet[j][frame][0]],
                             [second_joints[j][frame][1], feet[j][frame][1]])
        lines[j][2].set_3d_properties([second_joints[j][frame][2], feet[j][frame][2]])
    return lines

positions = calculate_positions()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-15, 15])
ax.set_ylim([-15, 15])
ax.set_zlim([-15, 15])

lines = [[ax.plot([], [], [], 'ro-')[0], ax.plot([], [], [], 'go-')[0], ax.plot([], [], [], 'bo-')[0]] for _ in range(6)]
ani = animation.FuncAnimation(fig, update, frames=len(cykl_nogi_1), fargs=(lines, positions), interval=20, blit=False)
plt.show()

#todo: poprawić początek ruchu, bo się nieprawidłowo rozpoczyna