import numpy as np
import matplotlib.pyplot as plt

#stałe hexapoda
h1 = -0.016854 - 0.003148
l1 = 0.12886 - 0.0978
l2 = 0.2188-0.12886
h2 = -0.011804 + 0.016854
l3 = 0.38709 - 0.2188

#kinematyka odwrotna
P3 = np.array([0.34709 - 0.0978, 0.14, -0.011804 - 0.003148])

print(P3)

alfa_1 = np.arctan2(P3[1], P3[0])

P1 = np.array([l1 * np.cos(alfa_1), l1 *np.sin(alfa_1), h1])

d = np.sqrt((P3[0] - P1[0]) ** 2 + (P3[1] - P1[1]) ** 2 + (P3[2] - P1[2]) ** 2)
r = np.sqrt(l2**2 + h2**2)

#wynika ten kat z l2 i h2

staly_kat_przy_P1 = np.arctan2(h2, l2)

cos_fi = (r**2 + l3**2 - d ** 2) / (2 * r * l3)
fi = np.arccos(cos_fi)
alfa_3 = np.deg2rad(180) - fi - staly_kat_przy_P1

epsilon = np.arcsin(np.sin(fi) * l3 / d)
tau = np.arctan2(P3[2] - P1[2], np.sqrt((P3[0] - P1[0])**2 + (P3[1] - P1[1])**2))

alfa_2 = - (epsilon + tau - staly_kat_przy_P1)

print(np.rad2deg(alfa_1), np.rad2deg(alfa_2), np.rad2deg(alfa_3))

#kinematyka prosta

#komentarze do znajdywania katów z podanej pozycji
#alfa_1, alfa_2, alfa_3 = 0, 0, np.deg2rad(0)
#y, x, z = 0, 0.38709 - 0.0978, -0.011804 - 0.003148

#p1, p3, p4 to jointy nogi, reszta punktów do podglądu na elementy nogi
P0 = np.array([0, 0, 0])
P0_pod = P0 + np.array([0, 0, h1])
P1 = P0_pod + np.array([l1 * np.cos(alfa_1), l1 *np.sin(alfa_1), 0])
P2 = P1 + np.array([np.cos(alfa_1)*np.cos(-alfa_2)*l2,np.sin(alfa_1)*np.cos(-alfa_2)*l2, np.sin(-alfa_2) * l2])
P3 = P1 + np.array([np.cos(alfa_1)*np.cos(staly_kat_przy_P1 - alfa_2)*np.sqrt(h2**2 + l2**2),np.sin(alfa_1)*np.cos(staly_kat_przy_P1 - alfa_2)*np.sqrt(h2**2 + l2**2), np.sin(staly_kat_przy_P1 - alfa_2)*np.sqrt(h2**2 + l2**2)])
P4 = P3 + np.array([np.cos(alfa_1)*np.cos(-alfa_2 - alfa_3)*l3, np.sin(alfa_1)*np.cos(-alfa_2 - alfa_3)*l3, np.sin(-alfa_2 - alfa_3) * l3])

print(P4)

# Lista punktów
points = np.array([
    [P0[0], P0[1], P0[2]],
    [P0_pod[0], P0_pod[1], P0_pod[2]],
    [P1[0], P1[1], P1[2]],
    [P2[0], P2[1], P2[2]],
    [P3[0], P3[1], P3[2]],
    [P4[0], P4[1], P4[2]]
])

x_min, x_max = points[:, 0].min(), points[:, 0].max()
y_min, y_max = points[:, 1].min(), points[:, 1].max()
z_min, z_max = points[:, 2].min(), points[:, 2].max()

axis_min = min(x_min, y_min, z_min) - 0.05
axis_max = max(x_max, y_max, z_max) + 0.05

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Lista połączeń (indeksy punktów + kolor)
segments = [
    (0, 1, 'red'),
    (1, 2, 'red'),
    (2, 3, 'blue'),
    (3, 4, 'blue'),
    (4, 5, 'green')
]

# XY
for i, j, color in segments:
    axes[0].plot([points[i, 0], points[j, 0]], [points[i, 1], points[j, 1]], color=color, linewidth=2)
axes[0].scatter(points[:, 0], points[:, 1], color='black', s=50)
axes[0].set_xlabel('X')
axes[0].set_ylabel('Y')
axes[0].set_title('Rzut na płaszczyznę XY')
axes[0].set_xlim(axis_min, axis_max)
axes[0].set_ylim(axis_min, axis_max)

# XZ
for i, j, color in segments:
    axes[1].plot([points[i, 0], points[j, 0]], [points[i, 2], points[j, 2]], color=color, linewidth=2)
axes[1].scatter(points[:, 0], points[:, 2], color='black', s=50)
axes[1].set_xlabel('X')
axes[1].set_ylabel('Z')
axes[1].set_title('Rzut na płaszczyznę XZ')
axes[1].set_xlim(axis_min, axis_max)
axes[1].set_ylim(axis_min, axis_max)

# YZ
for i, j, color in segments:
    axes[2].plot([points[i, 1], points[j, 1]], [points[i, 2], points[j, 2]], color=color, linewidth=2)
axes[2].scatter(points[:, 1], points[:, 2], color='black', s=50)
axes[2].set_xlabel('Y')
axes[2].set_ylabel('Z')
axes[2].set_title('Rzut na płaszczyznę YZ')
axes[2].set_xlim(axis_min, axis_max)
axes[2].set_ylim(axis_min, axis_max)

plt.tight_layout()
plt.show()
