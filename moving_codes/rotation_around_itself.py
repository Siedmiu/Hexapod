import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
#dane z modelu i potrzeby obrotu o kat alfa
def push_counterclockwise(R, alfa, fi, beta, x_start, z):

    delta = np.radians(180) + beta - fi
    tau = np.radians(360) - delta - (np.radians(180) - alfa) / 2
    r = R * np.sqrt(2 - 2 * np.cos(alfa))

    omega = np.sqrt(r ** 2 + x_start ** 2 - 2 * np.cos(tau) * r * x_start)

    epsilon = np.arcsin(np.sin(tau) * x_start / omega)

    gamma = delta - epsilon - (np.radians(180) - alfa) / 2

    y_new = -np.sin(gamma) * omega
    x_new = np.cos(gamma) * omega

    return np.array([x_new, y_new, z])

def push_clockwise(R, alfa, fi, beta, x_start, z):
    delta = np.radians(180) + beta - fi
    tau = delta - (np.radians(180) - alfa) / 2
    r = R * np.sqrt(2 - 2 * np.cos(alfa))

    omega = np.sqrt(r ** 2 + x_start ** 2 - 2 * np.cos(tau) * r * x_start)

    epsilon = np.arcsin(np.sin(tau) * x_start / omega)

    gamma = np.radians(360) - delta - epsilon - (np.radians(180) - alfa) / 2

    y_new = np.sin(gamma) * omega
    x_new = np.cos(gamma) * omega

    return np.array([x_new, y_new, z])

def parabola_w_przestrzeni_z_punktow(w1, w2, w3, liczba_punktow):
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
    p = np.array([a[0] * t ** 2 + b[0] * t + c[0],
                 a[1] * t ** 2 + b[1] * t + c[1],
                 a[2] * t ** 2 + b[2] * t + c[2]]).T

    dlugosci_segmentow = np.sqrt(np.sum(np.diff(p, axis=0) ** 2, axis=1))
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

odleglosci_przegubow_od_srodka_hexapoda = np.array([3, 2, 3, 3, 2, 3])
alfa = np.radians(30)
kat_fi_dla_kazdej_nogi = np.array([np.radians(60), 0, np.radians(-60), np.radians(60), 0, np.radians(-60)])
kat_beta_dla_kazdej_nogi = np.array([np.radians(20), 0, np.radians(-20), np.radians(20), 0, np.radians(-20)])
x_start = 4 # poczatkowe wychylenie nogi pajaka w osi x
z_start = 0 # poczatkowy z
h = 1 # wysokosc paraboli
ilosc_punktow_na_etap = 100

punkt_start_dla_kazdej_nogi = np.array([[x_start, 0, z_start] for _ in range(6)])

punkt_P1_dla_kazdej_nogi = np.array([
    push_counterclockwise(odleglosci_przegubow_od_srodka_hexapoda[i], alfa, kat_fi_dla_kazdej_nogi[i], kat_beta_dla_kazdej_nogi[i], x_start, z_start)
    for i in range(6)
])

punkt_P2_dla_kazdej_nogi = np.array([
    push_clockwise(odleglosci_przegubow_od_srodka_hexapoda[i], alfa, kat_fi_dla_kazdej_nogi[i], kat_beta_dla_kazdej_nogi[i], x_start, z_start)
    for i in range(6)
])

punkt_szczytowy_etapu_4_dla_kazdej_nogi = np.array([
    (punkt_P1_dla_kazdej_nogi[i] + punkt_P2_dla_kazdej_nogi[i]) / 2 + np.array([0, 0, h])
    for i in range(6)
])
#punkt szczytowy etapu 1 ccw to ten sam punkt co etap 5 cw i na odwrot
punkt_szczytowy_etapu_1_ccw_dla_kazdej_nogi = np.array([
    (punkt_start_dla_kazdej_nogi[i] + punkt_P2_dla_kazdej_nogi[i]) / 2 + np.array([0, 0, h])
    for i in range(6)
])

punkt_szczytowy_etapu_5_ccw_dla_kazdej_nogi = np.array([
    (punkt_P1_dla_kazdej_nogi[i] + punkt_start_dla_kazdej_nogi[i]) / 2 + np.array([0, 0, h])
    for i in range(6)
])

# cw -> clockwise, ccw-> counter clockwise
#obrot hexapoda CCW
etap_1_dla_kazdej_nogi_ccw = np.array([parabola_w_przestrzeni_z_punktow(punkt_start_dla_kazdej_nogi[i], punkt_szczytowy_etapu_1_ccw_dla_kazdej_nogi[i], punkt_P2_dla_kazdej_nogi[i], ilosc_punktow_na_etap) for i in range(6)])
etap_2_dla_kazdej_nogi_ccw = np.array([
    np.linspace(punkt_P2_dla_kazdej_nogi[i], punkt_start_dla_kazdej_nogi[i], ilosc_punktow_na_etap)[1:]
    for i in range(6)
])
etap_3_dla_kazdej_nogi_ccw = np.array([
    np.linspace(punkt_start_dla_kazdej_nogi[i], punkt_P1_dla_kazdej_nogi[i], ilosc_punktow_na_etap)[1:]
    for i in range(6)
])
etap_4_dla_kazdej_nogi_ccw = np.array([parabola_w_przestrzeni_z_punktow(punkt_P1_dla_kazdej_nogi[i], punkt_szczytowy_etapu_4_dla_kazdej_nogi[i], punkt_P2_dla_kazdej_nogi[i], ilosc_punktow_na_etap * 2) for i in range(6)])
etap_5_dla_kazdej_nogi_ccw = np.array([parabola_w_przestrzeni_z_punktow(punkt_P1_dla_kazdej_nogi[i], punkt_szczytowy_etapu_5_ccw_dla_kazdej_nogi[i], punkt_start_dla_kazdej_nogi[i], ilosc_punktow_na_etap) for i in range(6)])

#obrot hexapoda CW
etap_1_dla_kazdej_nogi_cw = np.array([parabola_w_przestrzeni_z_punktow(punkt_start_dla_kazdej_nogi[i], punkt_szczytowy_etapu_5_ccw_dla_kazdej_nogi[i], punkt_P1_dla_kazdej_nogi[i], ilosc_punktow_na_etap) for i in range(6)])
etap_2_dla_kazdej_nogi_cw = np.array([
    np.linspace(punkt_P1_dla_kazdej_nogi[i], punkt_start_dla_kazdej_nogi[i], ilosc_punktow_na_etap)[1:]
    for i in range(6)
])
etap_3_dla_kazdej_nogi_cw = np.array([
    np.linspace(punkt_start_dla_kazdej_nogi[i], punkt_P2_dla_kazdej_nogi[i], ilosc_punktow_na_etap)[1:]
    for i in range(6)
])
etap_4_dla_kazdej_nogi_cw = np.array([parabola_w_przestrzeni_z_punktow(punkt_P2_dla_kazdej_nogi[i], punkt_szczytowy_etapu_4_dla_kazdej_nogi[i], punkt_P1_dla_kazdej_nogi[i], ilosc_punktow_na_etap * 2) for i in range(6)])
etap_5_dla_kazdej_nogi_cw = np.array([parabola_w_przestrzeni_z_punktow(punkt_P2_dla_kazdej_nogi[i], punkt_szczytowy_etapu_1_ccw_dla_kazdej_nogi[i], punkt_start_dla_kazdej_nogi[i], ilosc_punktow_na_etap) for i in range(6)])

czy_wyswietlic = False

if czy_wyswietlic:
    #CCW
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), subplot_kw={'projection': '3d'})

    for idx in range(6):

        row = idx // 3
        col = idx % 3
        ax = axes[row, col]

        P_start = punkt_start_dla_kazdej_nogi[idx]
        P1 = punkt_P1_dla_kazdej_nogi[idx]
        P2 = punkt_P2_dla_kazdej_nogi[idx]

        etap_1 = etap_1_dla_kazdej_nogi_ccw[idx]
        etap_2 = etap_2_dla_kazdej_nogi_ccw[idx]
        etap_3 = etap_3_dla_kazdej_nogi_ccw[idx]
        etap_4 = etap_4_dla_kazdej_nogi_ccw[idx]
        etap_5 = etap_5_dla_kazdej_nogi_ccw[idx]

        ax.scatter(*P_start, color='cyan', label='Start')
        ax.scatter(*P1, color='brown', label='P1')
        ax.scatter(*P2, color='black', label='P2')

        if idx % 2 == 0:
            ax.plot(etap_1[:, 0], etap_1[:, 1], etap_1[:, 2], color='orange', label='Etap 1')
        ax.plot(etap_2[:, 0], etap_2[:, 1], etap_2[:, 2], color='red', label='Etap 2')
        ax.plot(etap_3[:, 0], etap_3[:, 1], etap_3[:, 2], color='green', label='Etap 3')
        ax.plot(etap_4[:, 0], etap_4[:, 1], etap_4[:, 2], color='violet', label='Etap 4')
        if idx % 2 == 1:
            ax.plot(etap_5[:, 0], etap_5[:, 1], etap_5[:, 2], color='blue', label='Etap 5')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Trajectory for leg {idx + 1}, counterclockwise movement')
        ax.legend()

    plt.tight_layout()
    plt.show()
    #CW
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), subplot_kw={'projection': '3d'})

    for idx in range(6):

        row = idx // 3
        col = idx % 3
        ax = axes[row, col]

        P_start = punkt_start_dla_kazdej_nogi[idx]
        P1 = punkt_P1_dla_kazdej_nogi[idx]
        P2 = punkt_P2_dla_kazdej_nogi[idx]

        etap_1 = etap_1_dla_kazdej_nogi_cw[idx]
        etap_2 = etap_2_dla_kazdej_nogi_cw[idx]
        etap_3 = etap_3_dla_kazdej_nogi_cw[idx]
        etap_4 = etap_4_dla_kazdej_nogi_cw[idx]
        etap_5 = etap_5_dla_kazdej_nogi_cw[idx]

        ax.scatter(*P_start, color='cyan', label='Start')
        ax.scatter(*P1, color='brown', label='P1')
        ax.scatter(*P2, color='black', label='P2')

        if idx % 2 == 0:
            ax.plot(etap_1[:, 0], etap_1[:, 1], etap_1[:, 2], color='orange', label='Etap 1')
        ax.plot(etap_2[:, 0], etap_2[:, 1], etap_2[:, 2], color='red', label='Etap 2')
        ax.plot(etap_3[:, 0], etap_3[:, 1], etap_3[:, 2], color='green', label='Etap 3')
        ax.plot(etap_4[:, 0], etap_4[:, 1], etap_4[:, 2], color='violet', label='Etap 4')
        if idx % 2 == 1:
            ax.plot(etap_5[:, 0], etap_5[:, 1], etap_5[:, 2], color='blue', label='Etap 5')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Trajectory for leg {idx + 1}, clockwise movement')
        ax.legend()

    plt.tight_layout()
    plt.show()
#todo dla kazdej nogi wyznaczyc wychylenia serw
