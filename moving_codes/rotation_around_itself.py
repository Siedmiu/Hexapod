import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D

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
    ]).T[1:]

    if noga % 2 == 0:
        punkty_rowne = punkty_rowne[::-1]

    return punkty_rowne

def prosta_w_cyklu(P_start, P2, noga, liczba_punktow):

    linia = np.linspace(P_start, P2,liczba_punktow)

    if noga % 2 == 1:
        linia = linia[::-1]

    return linia

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

ilosc_punktow_na_etap = 100
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

czy_wyswietlic = True

if czy_wyswietlic:

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    for i in range(6):
        # Parabola – ruch podnoszenia nogi
        ax.plot(parabole_nog[i][:, 0], parabole_nog[i][:, 1], parabole_nog[i][:, 2], color=colors[i],
                label=f'Parabola noga {i + 1}')
        # Prosta – ruch po podłodze
        ax.plot(proste_nog[i][:, 0], proste_nog[i][:, 1], proste_nog[i][:, 2], color=colors[i], linestyle='dashed',
                label=f'Prosta noga {i + 1}')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Trajektorie ruchu nóg robota sześcionożnego')
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
    plt.tight_layout()
    plt.show()

#todo dla kazdej nogi wyznaczyc wychylenia serw
