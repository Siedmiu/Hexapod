import numpy as np

# dlugosci segmentow nog
L1 = 1
L2 = 5
L3 = 6

#położenie punktu spoczynku stopy od przyczepu nogi w układzie wspolrzednych danej nogi a nie srodka pajaka!!!
alfa_1 = 0
alfa_2 = np.pi / 180 * 30
alfa_3 = np.pi / 180 * 90

P1_X = L1 * np.cos(alfa_1)
P1_Y = L1 * np.sin(alfa_1)
P1_Z = 0

P2_X = P1_X + L2 * np.cos(alfa_1) * np.cos(alfa_2)
P2_Y = P1_Y + L2 * np.sin(alfa_1) * np.cos(alfa_2)
P2_Z = L2 * np.sin(alfa_2)

x_spocz = P2_X + L3 * np.cos(alfa_1) * np.sin(alfa_3 - (np.pi / 2 - alfa_2))
y_spocz = P2_Y + L3 * np.sin(alfa_1) * np.sin(alfa_3 - (np.pi / 2 - alfa_2))
z_spocz = P2_Z - L3 * np.cos(alfa_3 - (np.pi / 2 - alfa_2))

print(x_spocz, y_spocz, z_spocz)

wysokosc_start = -z_spocz
z_spocz = 0

# definicja punktow na platformie pajaka
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

#pozycje w przestrzeni przyczepow nog do tulowia

przyczepy_nog_do_tulowia= np.array([
    #noga 1
    [(tulow[0][0] + tulow[1][0]) / 2, (tulow[0][1] + tulow[1][1]) / 2, wysokosc_start],
    #noga 2
    [(tulow[1][0] + tulow[2][0]) / 2, (tulow[1][1] + tulow[2][1]) / 2, wysokosc_start],
    #noga 3
    [(tulow[2][0] + tulow[3][0]) / 2, (tulow[2][1] + tulow[3][1]) / 2, wysokosc_start],
    #noga 4
    [(tulow[4][0] + tulow[5][0]) / 2, (tulow[4][1] + tulow[5][1]) / 2, wysokosc_start],
    #noga 5
    [(tulow[5][0] + tulow[6][0]) / 2, (tulow[5][1] + tulow[6][1]) / 2, wysokosc_start],
    #noga 6
    [(tulow[6][0] + tulow[7][0]) / 2, (tulow[6][1] + tulow[7][1]) / 2, wysokosc_start],
])

#todo polozenie przegubow i stop podczas pozycji spoczynkowej pajaka

# cos z tym popgrzebac --> np.tan((np.abs(tulow[0][0] - tulow[1][0])) / np.abs((tulow[0][1] - tulow[1][1]))))
