import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.animation import FuncAnimation

matplotlib.use('TkAgg')

# Definicja punktów
srodek = np.array([0.0, 0.0])
nogi = np.array([
    [3.0, 4.0],
    [5.0, 0.0],
    [3.0, -4.0],
    [-3.0, -4.0],
    [-5.0, 0.0],
    [-3.0, 4.0]
])

r = 1.2
delta = 0.1
etap = 0
nastepny_srodek = r

# pogladowy przebieg chodu
def update(frame):
    global etap, srodek, nogi, nastepny_srodek
#start
    if etap == 0:
        nogi[[0, 2, 4], 1] += 2 * delta
        srodek[1] += delta
        if srodek[1] > nastepny_srodek:
            etap = 1
            nastepny_srodek += 2 * r
# ruch nog 1,3,5 w powietrzu a 2, 4, 6 na ziemi
    elif etap == 1:
        nogi[[1, 3, 5], 1] += 4 * delta
        srodek[1] += 2 * delta
        if srodek[1] > nastepny_srodek:
            etap = 2
            nastepny_srodek += 2 * r
# ruch nog 2,4,6 w powietrzu a 1,3,5 na ziemi
    
    elif etap == 2:
        nogi[[0, 2, 4], 1] += 4 * delta
        srodek[1] += 2 * delta
        if srodek[1] > nastepny_srodek:
            etap = 1
            nastepny_srodek += 2 * r

    ax.clear()
    ax.set_xlim(-30, 30)
    ax.set_ylim(-6, 54)
    ax.set_title("Animacja ruchu nóg")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Rysowanie punktów
    ax.scatter(srodek[0], srodek[1], c='red', marker='o', label='Środek')
    ax.scatter(nogi[:, 0], nogi[:, 1], c='blue', marker='o', label='Nogi')

    # Rysowanie linii do środka
    for i in range(len(nogi)):
        ax.plot([srodek[0], nogi[i, 0]], [srodek[1], nogi[i, 1]], 'k-')

    ax.legend()
    ax.grid(True)


# Tworzenie wykresu
fig, ax = plt.subplots()
ax.set_xlim(-6, 6)
ax.set_ylim(-2, 6)
ani = FuncAnimation(fig, update, frames=100, interval=100)

plt.show()
