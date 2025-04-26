import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

"""This code presents an idea how the hexapod would follow the path of points"""

# Parametry
r = 1.5  # Całkowity dystans
r_step = r / 3  # Dystans na krok w Ripple gait
alpha = np.radians(35)  # Kąt ustawienia nóg
leg_length = 5  # Długość nogi
num_steps = 5  # Liczba kroków
num_frames = 100  # Liczba klatek w animacji
angle = 0
previous_angle = 0
oriented = False
orientationReached = False

rotAngle = np.radians(0.2)

# Definicje kątów nóg
angles = [
    alpha, 0, -alpha, np.pi - alpha, np.pi, np.pi + alpha
]

# Początkowe pozycje nóg
foot_positions = np.array([
    (leg_length * np.cos(angle), leg_length * np.sin(angle)) for angle in angles
])

# Funkcja obliczania środka masy
def compute_center_of_mass(positions):
    return np.mean(positions[:, 0]), np.mean(positions[:, 1])

# Ścieżka robota (zestaw punktów)
path = [(-1, -3), (5, 3), (10, 10), (15, 5), (20, 0), (25, -5)]
current_target = 0  # Indeks aktualnego celu na ścieżce
arrived = False  # Flaga sprawdzająca, czy robot dotarł do celu

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-30, 30)
ax.set_ylim(-30, 30)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Hexapod - Podążanie za ścieżką")
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)

# Elementy do rysowania
lines = [ax.plot([], [], 'bo-', linewidth=2)[0] for _ in range(6)]  # Nogi
feet = [ax.add_patch(plt.Circle((0, 0), 0.5, color='blue', fill=True)) for _ in range(6)]  # Stopy
body = ax.add_patch(plt.Circle((0, 0), 0.5, color='green', fill=True, zorder=10))  # Ciało
goal_points = [ax.add_patch(plt.Circle((x, y), 0.5, color='red', fill=True)) for (x, y) in path]

# Kolejność ruchu nóg w Ripple gait
movement_order = [1, 5, 0, 4, 2, 3]  # Kolejność, w jakiej poruszają się nogi
current_step = 0  # Indeks obecnie poruszającej się nogi
step = 0  # Liczba wykonanych kroków przez aktualnie poruszającą się nogę

# Funkcja do obliczania kąta między aktualną pozycją a celem
def angle_to_target(curr_pos, target_pos):
    dx = target_pos[0] - curr_pos[0]
    dy = target_pos[1] - curr_pos[1]
    return np.atan2(dy,dx)

# Funkcja do obliczania przesunięcia nóg robota
def move_legs_relative_to_body(foot_positions, body_angle, center_x, center_y):
    # Przesuwamy nogi w taki sposób, aby obrót był wokół środka robota
    foot_positions = foot_positions - np.array([center_x, center_y])
    rotation_matrix = np.array([
        [np.cos(body_angle), -np.sin(body_angle)],
        [np.sin(body_angle), np.cos(body_angle)]
    ])
    foot_positions = np.dot(foot_positions, rotation_matrix)
    foot_positions += np.array([center_x, center_y])
    return foot_positions

# Funkcja aktualizująca animację
def update(frame):
    global foot_positions, current_step, step, current_target, arrived, oriented, targetAngle, previous_angle, orientationReached

    moving_legs = [movement_order[(current_step + i) % 6] for i in range(3)]
    
    # Obliczanie kąta do celu
    center_x, center_y = compute_center_of_mass(foot_positions)
    target_x, target_y = path[current_target]

    hexAngle = np.atan2((foot_positions[1, 1] - foot_positions[4,1]), (foot_positions[1, 0] - foot_positions[4, 0]))
    # print(hexAngle)
    
    # Sprawdzanie, czy robot dotarł do celu
    distance_to_target = np.sqrt((target_x - center_x) ** 2 + (target_y - center_y) ** 2)
    
    if distance_to_target < 0.1:
        arrived = True
        oriented = False
        orientationReached = False
    else:
        arrived = False
    
    # Jeśli robot dotarł do celu, przejdź do następnego punktu
    if arrived:
        current_target = (current_target + 1) % len(path)
        target_x, target_y = path[current_target]
        arrived = False
        previous_angle = targetAngle
    # Obliczanie kąta, pod jakim robot powinien się obrócić w kierunku celu
    targetAngle = angle_to_target((center_x, center_y), (target_x, target_y))

    print("rot: ", hexAngle, "target: ", targetAngle )

    xAngle = targetAngle - previous_angle


    if abs( (hexAngle)-(targetAngle)  - 3.14/2)< 0.2 or abs( (targetAngle)-(hexAngle) - 3.14/2) < 0.2:
        orientationReached = True
    
    # Przemieszczanie ciała robota w kierunku celu
    move_ratio = 0.1 / distance_to_target
    center_x += (target_x - center_x) * move_ratio
    center_y += (target_y - center_y) * move_ratio

    delta = r_step / num_steps

    for leg in moving_legs:
        if orientationReached:
            foot_positions[leg, 1] += delta*np.sin(targetAngle)
            foot_positions[leg, 0] += delta*np.cos(targetAngle)
            # foot_positions = move_legs_relative_to_body(foot_positions, rotAngle, center_x, center_y)
        else:
            foot_positions = move_legs_relative_to_body(foot_positions, rotAngle, center_x, center_y)
            #TODO make rotations how it should work based on inversed kinemtaics, not the rotation matrix
            # furthermore instead of rotating only when standing in points it could rotating simultaneously when moving

    step += 1
    if step >= num_steps:
        current_step = (current_step + 1) % 6
        step = 0
    
    # Zaktualizuj pozycje nóg w odniesieniu do nowego położenia ciała
    for i, (x, y) in enumerate(foot_positions):
        lines[i].set_data([center_x, x], [center_y, y])
        feet[i].set_center((x, y))
    
    body.set_center((center_x, center_y))

ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=50, repeat=True)
plt.show()
