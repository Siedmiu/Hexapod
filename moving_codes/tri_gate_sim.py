import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.animation import FuncAnimation
from numpy.ma.core import zeros_like

matplotlib.use('TkAgg')


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

def znajdz_punkty_rowno_odlegle(r, h, ilosc_punktow_na_krzywej, ilosc_probek):
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
            punkty.append([0, i/ilosc_probek * r, z_1])
        if(len(punkty) == ilosc_punktow_na_krzywej - 1):
            break
    punkty.append([0, r, 0])
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
alfa_2 = np.radians(30)
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

# Obliczanie pozycji nog (przyczep, przeguby, stopa)
polozenie_nog = [
    [
        przyczepy_nog_do_tulowia[i],
        polozenie_przegub_1(L1, alfa_1 + nachylenia_nog_do_bokow_platformy_pajaka[i], przyczepy_nog_do_tulowia[i]),
        polozenie_przegub_2(L1, L2, alfa_1 + nachylenia_nog_do_bokow_platformy_pajaka[i], alfa_2, przyczepy_nog_do_tulowia[i]),
        polozenie_spoczynkowe_stop[i]
    ] for i in range(6)
]

# tor pokonywany przez nogi w ukladzie wspolrzednych srodka robota
h = 4
r = 5
ilosc_punktow_na_krzywych = 20
punkty_etap1_ruchu = znajdz_punkty_rowno_odlegle(r, h, ilosc_punktow_na_krzywych, 10000)
punkty_etap2_ruchu_y = np.linspace(r * (ilosc_punktow_na_krzywych - 1) / ilosc_punktow_na_krzywych, 0, ilosc_punktow_na_krzywych)
punkty_etap2_ruchu = [[0, punkty_etap2_ruchu_y[i], 0] for i in range(ilosc_punktow_na_krzywych)]
cykl_ogolny = punkty_etap1_ruchu + punkty_etap2_ruchu
cykl_ogolny = np.array(cykl_ogolny)

# tablica cykli, gdzie jest zapisana kazda z nog, kazdy punkt w cylku i jego wspolrzedne, kazda z nog musi miec swoj wlasny
# cykl poruszania ze wzgledu na katy pod jakimi sa ustawione wzgledem srodka robota

cykle_nog = np.array([
    [[cykl_ogolny[i][1] * np.sin(nachylenia_nog_do_bokow_platformy_pajaka[j]),
      cykl_ogolny[i][1] * np.cos(nachylenia_nog_do_bokow_platformy_pajaka[j]),
      cykl_ogolny[i][2]]
     for i in range(len(cykl_ogolny))]
    for j in range(6)
])
# Tworzenie figury 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Rysowanie cyklu nogi 1
ax.plot(cykle_nog[0,:, 0], cykle_nog[0, :, 1], cykle_nog[0, :, 2], label='Leg 1', color='r', marker='x')
ax.plot(cykle_nog[1,:, 0], cykle_nog[1, :, 1], cykle_nog[1, :, 2], label='Leg 2', color='g', marker='x')
ax.plot(cykle_nog[2,:, 0], cykle_nog[2, :, 1], cykle_nog[2, :, 2], label='Leg 3', color='b', marker='x')
ax.plot(cykle_nog[3,:, 0], cykle_nog[3, :, 1], cykle_nog[3, :, 2], label='Leg 4', color='y', marker='x')
ax.plot(cykle_nog[4,:, 0], cykle_nog[4, :, 1], cykle_nog[4, :, 2], label='Leg 5', color='orange', marker='x')
ax.plot(cykle_nog[5,:, 0], cykle_nog[5, :, 1], cykle_nog[5, :, 2], label='Leg 6', color='black', marker='x')

# Etykiety osi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Points that each leg has to step on to move hexapod forward')
ax.legend()

plt.show()
# Wizualizacja w 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
fig.canvas.draw_idle()

# Rysowanie tulowia
ax.plot(tulow[:, 0], tulow[:, 1], tulow[:, 2], 'bo-')
ax.plot([tulow[0, 0], tulow[7, 0]], [tulow[0, 1], tulow[7, 1]], [tulow[0, 2], tulow[7, 2]], c='b', lw=2)


# Rysowanie nog
for i in range(6):
    noga = polozenie_nog[i]

    # Rysowanie linii nog
    ax.plot([noga[j][0] for j in range(4)],
            [noga[j][1] for j in range(4)],
            [noga[j][2] for j in range(4)], 'ro-')

    # Rysowanie punktow przegubow i stop
    colors = ['g', 'y', 'r', 'b']  # Kolory: przyczep, przegub1, przegub2, stopa
    for j in range(4):
        ax.scatter(noga[j][0], noga[j][1], noga[j][2], s=50, c=colors[j])

# Oznaczenia osi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("Model hexapoda 3D")
ax.legend()

# Wyskalowanie wykresu
x_vals = [noga[i][0] for noga in polozenie_nog for i in range(4)]
y_vals = [noga[i][1] for noga in polozenie_nog for i in range(4)]
z_vals = [noga[i][2] for noga in polozenie_nog for i in range(4)]

x_min, x_max = min(x_vals), max(x_vals)
y_min, y_max = min(y_vals), max(y_vals)
z_min, z_max = min(z_vals), max(z_vals)

max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

x_mid = (x_max + x_min) / 2
y_mid = (y_max + y_min) / 2
z_mid = (z_max + z_min) / 2

ax.set_xlim(x_mid - max_range, x_mid + max_range)
ax.set_ylim(y_mid - max_range, y_mid + max_range)
ax.set_zlim(z_mid - max_range, z_mid + max_range)

plt.show()
#todo znalezc punkty w ktore noga ma trafiac aby robot poruszal sie do przodu
#todo podawac na bierzaco obrot kazdego z serw podczas chodzenia
