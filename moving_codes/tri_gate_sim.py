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
print(polozenia_stop_podczas_cyklu[1])

#wychyly podawane odpowiednio dla 1 2 i 3 przegubu w radianach
wychyly_serw_podczas_ruchu = np.array([
[katy_serw(polozenia_stop_podczas_cyklu[j][i], l1, h1, l2, h2, l3)
    for i in range(len(cykl_ogolny_nog_1_3_5))]
    for j in range(6)
])

#print(wychyly_serw_podczas_ruchu[0])
#obliczanie polozenia przegubow i stop z wyliczonymi wychyleniami serw

def calculate_positions():
    #rownania zastosowane z kinematyki odwrotnej, nachylenia nog do bokow platformy pajaka sa dodana TYLKO DO SYMULACJI!!!
    #w rzeczywistości nie trzeba tego uwzgledniać gdyż noga bedzie fizycznie obrocona

    polozenie_punktow_P1_w_ruchu = np.array([
    [[
        przyczepy_nog_do_tulowia[j][0] + l1 * np.cos(wychyly_serw_podczas_ruchu[j][i][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]),
        przyczepy_nog_do_tulowia[j][1] + l1 * np.sin(wychyly_serw_podczas_ruchu[j][i][0] + nachylenia_nog_do_bokow_platformy_pajaka[j]),
        przyczepy_nog_do_tulowia[j][2] + h1
    ]
        for i in range(len(cykl_ogolny_nog_1_3_5))]
        for j in range(6)
    ])

    polozenie_punktow_P2_w_ruchu = polozenie_punktow_P1_w_ruchu + np.array([

    [[
        np.cos(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-wychyly_serw_podczas_ruchu[j][i][1]) * l2,
        np.sin(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j]) * np.cos(-wychyly_serw_podczas_ruchu[j][i][1]) * l2,
        l2 * np.sin(-wychyly_serw_podczas_ruchu[j][i][1])
    ]
        for i in range(len(cykl_ogolny_nog_1_3_5))]
        for j in range(6)
    ])

    polozenie_punktow_P3_w_ruchu = polozenie_punktow_P1_w_ruchu + np.array([

        [[
            np.cos(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j])*np.cos(staly_kat_przy_P1 - wychyly_serw_podczas_ruchu[j][i][1])*np.sqrt(h2**2 + l2**2),
            np.sin(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j])*np.cos(staly_kat_przy_P1 - wychyly_serw_podczas_ruchu[j][i][1])*np.sqrt(h2**2 + l2**2),
            np.sin(staly_kat_przy_P1 - wychyly_serw_podczas_ruchu[j][i][1])*np.sqrt(h2**2 + l2**2)
        ]
            for i in range(len(cykl_ogolny_nog_1_3_5))]
        for j in range(6)
    ])

    obliczone_z_serw_polozenie_stop = polozenie_punktow_P3_w_ruchu + np.array([
        [[
            np.cos(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j])*np.cos( -wychyly_serw_podczas_ruchu[j][i][1] - wychyly_serw_podczas_ruchu[j][i][2])*l3,
            np.sin(wychyly_serw_podczas_ruchu[j][i][0]+ nachylenia_nog_do_bokow_platformy_pajaka[j])*np.cos( -wychyly_serw_podczas_ruchu[j][i][1] - wychyly_serw_podczas_ruchu[j][i][2])*l3,
            np.sin( -wychyly_serw_podczas_ruchu[j][i][1] - wychyly_serw_podczas_ruchu[j][i][2]) * l3
        ]
            for i in range(len(cykl_ogolny_nog_1_3_5))]
        for j in range(6)
    ])

    return polozenie_punktow_P1_w_ruchu, polozenie_punktow_P2_w_ruchu, polozenie_punktow_P3_w_ruchu, obliczone_z_serw_polozenie_stop

P0_pod_tab = przyczepy_nog_do_tulowia + np.array([0, 0, h1])

#funkcja odpowiada za rysowanie symulacji
def update(frame, lines, positions):
    P1, P2, P3, foot = positions
    for j in range(6):
        # 0. Przyczep -> P0_pod
        lines[j][0].set_data([przyczepy_nog_do_tulowia[j][0], P0_pod_tab[j][0]],
                             [przyczepy_nog_do_tulowia[j][1], P0_pod_tab[j][1]])
        lines[j][0].set_3d_properties([przyczepy_nog_do_tulowia[j][2], P0_pod_tab[j][2]])

        # 1. P0_pod -> P1
        lines[j][1].set_data([P0_pod_tab[j][0], P1[j][frame][0]],
                             [P0_pod_tab[j][1], P1[j][frame][1]])
        lines[j][1].set_3d_properties([P0_pod_tab[j][2], P1[j][frame][2]])

        # 2. P1 -> P2
        lines[j][2].set_data([P1[j][frame][0], P2[j][frame][0]],
                             [P1[j][frame][1], P2[j][frame][1]])
        lines[j][2].set_3d_properties([P1[j][frame][2], P2[j][frame][2]])

        # 3. P2 -> P3
        lines[j][3].set_data([P2[j][frame][0], P3[j][frame][0]],
                             [P2[j][frame][1], P3[j][frame][1]])
        lines[j][3].set_3d_properties([P2[j][frame][2], P3[j][frame][2]])

        # 4. P3 -> koniec stopy
        lines[j][4].set_data([P3[j][frame][0], foot[j][frame][0]],
                             [P3[j][frame][1], foot[j][frame][1]])
        lines[j][4].set_3d_properties([P3[j][frame][2], foot[j][frame][2]])

    return [segment for leg in lines for segment in leg]  # spłaszczona lista


# Ustawienia wykresu i animacji
positions = calculate_positions()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-0.5, 0.5])
ax.set_ylim([-0.5, 0.5])
ax.set_zlim([-0.5, 0.5])

segment_colors = ['purple','r','b', 'orange', 'g']
lines = [[ax.plot([], [], [], color=segment_colors[i], marker='o')[0] for i in range(5)] for _ in range(6)]

ani = animation.FuncAnimation(fig, update, frames=len(positions[0][0]), fargs=(lines, positions),
                              interval=50, blit=False)
plt.show()
