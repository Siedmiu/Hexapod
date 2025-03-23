import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
matplotlib.use('TkAgg')
#punkty na paraboli ruchu nogi rownoodlegle od siebie w czasie
P1 = [1, 2, 3]
P2 = [3, 4, 5]
P3 = [6, 2, 3]

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
    dlugosci_celowe = np.linspace(0, dlugosc_calkowita, liczba_punktow)

    # Interpolacja punktów dla równych odstępów
    punkty_rowne = np.array([
        np.interp(dlugosci_celowe, dlugosci_luku, p[:, i]) for i in range(3)
    ]).T


    return punkty_rowne

trajektorie = parabola_w_przestrzeni_z_punktow(P1, P2, P3, 100)

# Tworzenie wykresu 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(trajektorie[:, 0], trajektorie[:, 1], trajektorie[:, 2], label='Trajektoria 3D')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
plt.show()
