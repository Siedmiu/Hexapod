import numpy as np
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
odleglosci_przegubow_od_srodka_hexapoda = np.array([3, 2, 3, 3, 2, 3])
alfa = np.radians(30)
kat_fi_dla_kazdej_nogi = np.array([np.radians(60), 0, np.radians(-60), np.radians(60), 0, np.radians(-60)])
kat_beta_dla_kazdej_nogi = np.array([np.radians(20), 0, np.radians(-20), np.radians(20), 0, np.radians(-20)])
x_start = 4
z_start = 0
punkt_P1_dla_kazdej_nogi = np.array([push_counterclockwise(odleglosci_przegubow_od_srodka_hexapoda[i], alfa, kat_fi_dla_kazdej_nogi[i], kat_beta_dla_kazdej_nogi[i], x_start, z_start) for i in range(6)])
punkt_P2_dla_kazdej_nogi = np.array([push_clockwise(odleglosci_przegubow_od_srodka_hexapoda[i], alfa, kat_fi_dla_kazdej_nogi[i], kat_beta_dla_kazdej_nogi[i], x_start, z_start) for i in range(6)])
print(punkt_P1_dla_kazdej_nogi)
print(punkt_P2_dla_kazdej_nogi)
#todo znając punkty P1 i P2 stworzyć tor przebiegu każdego etapu cyklu dla każdej z kończyn a następnie cały cykl dla każdej z kończyn razem
#todo wykorzystać do tego 3D_points_of_movement.py

