import numpy as np
import matplotlib.pyplot as plt

L1 = 1
L2 = 4
L3 = 3

print('Podaj po kolei wspolrzedne punktu docelowego P(x, y, z)')
x = int(input())
y = int(input())
z = int(input())

r = np.sqrt(x**2 + y**2)
d = np.sqrt(z**2 + (r - L1) ** 2)

alfa_1 = np.arctan2(y, x)
alfa_2 = np.arccos((L2 ** 2 + d ** 2 - L3 ** 2) / (2 * L2 * d)) + np.arctan2(z, (r - L1))
alfa_3 = np.arccos((L2**2+ L3**2 - d**2)/(2*L2*L3))

print(np.arctan2(z, (r - L1)) * 180 / np.pi)

P1_X = L1 * np.cos(alfa_1)
P1_Y = L1 * np.sin(alfa_1)
P1_Z = 0

P2_X = P1_X + L2 * np.cos(alfa_1) * np.cos(alfa_2)
P2_Y = P1_Y + L2 * np.sin(alfa_1) * np.cos(alfa_2)
P2_Z = L2 * np.sin(alfa_2)

P3_X = P2_X + L3 * np.cos(alfa_1) * np.sin(alfa_3 - (np.pi / 2 - alfa_2))
P3_Y = P2_Y + L3 * np.sin(alfa_1) * np.sin(alfa_3 - (np.pi / 2 - alfa_2))
P3_Z = P2_Z - L3 * np.cos(alfa_3 - (np.pi / 2 - alfa_2))

print(alfa_1 * 180 / np.pi , alfa_2 * 180 / np.pi, alfa_3 * 180 / np.pi)
print(P1_X, P1_Y, P1_Z)
print(P2_X, P2_Y, P2_Z)
print(P3_X, P3_Y, P3_Z)

points = np.array([
    [0,0,0],
    [P1_X, P1_Y, P1_Z],
    [P2_X, P2_Y, P2_Z],
    [P3_X, P3_Y, P3_Z],
])

x_min, x_max = points[:, 0].min(), points[:, 0].max()
y_min, y_max = points[:, 1].min(), points[:, 1].max()
z_min, z_max = points[:, 2].min(), points[:, 2].max()

axis_min = min(x_min, y_min, z_min) - 1
axis_max = max(x_max, y_max, z_max) + 1

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# XY
axes[0].plot(points[:2, 0], points[:2, 1], color='red', linewidth=2)
axes[0].plot(points[1:3, 0], points[1:3, 1], color='blue', linewidth=2)
axes[0].plot(points[2:, 0], points[2:, 1], color='green', linewidth=2)
axes[0].scatter(points[:, 0], points[:, 1], color='black', s=50)
axes[0].set_xlabel('X')
axes[0].set_ylabel('Y')
axes[0].set_title('Rzut na płaszczyznę XY')
axes[0].set_xlim(axis_min, axis_max)
axes[0].set_ylim(axis_min, axis_max)

# XZ
axes[1].plot(points[:2, 0], points[:2, 2], color='red', linewidth=2)
axes[1].plot(points[1:3, 0], points[1:3, 2], color='blue', linewidth=2)
axes[1].plot(points[2:, 0], points[2:, 2], color='green', linewidth=2)
axes[1].scatter(points[:, 0], points[:, 2], color='black', s=50)
axes[1].set_xlabel('X')
axes[1].set_ylabel('Z')
axes[1].set_title('Rzut na płaszczyznę XZ')
axes[1].set_xlim(axis_min, axis_max)
axes[1].set_ylim(axis_min, axis_max)

# YZ
axes[2].plot(points[:2, 1], points[:2, 2], color='red', linewidth=2)
axes[2].plot(points[1:3, 1], points[1:3, 2], color='blue', linewidth=2)
axes[2].plot(points[2:, 1], points[2:, 2], color='green', linewidth=2)
axes[2].scatter(points[:, 1], points[:, 2], color='black', s=50)
axes[2].set_xlabel('Y')
axes[2].set_ylabel('Z')
axes[2].set_title('Rzut na płaszczyznę YZ')
axes[2].set_xlim(axis_min, axis_max)
axes[2].set_ylim(axis_min, axis_max)

plt.tight_layout()
plt.show()
