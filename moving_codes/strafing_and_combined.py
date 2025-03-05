import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.widgets import Button
import matplotlib
matplotlib.use("TkAgg")


"""
GAITS EXPLANATION:

Wave gate explanation:
The Hexapod only moves one leg at a time.
He successively moves: front right, middle right, back right, front left, middle left, back left, etc.

--------------------------------------------

Bi-gate explanation:
The Hexapod moves pairs of legs simultaneously.
Leg pairs: (0,5), (1,4), (2,3)
They move in sequence.

--------------------------------------------

Tri-gate explanation:
The Hexapod moves groups of three legs simultaneously.
Leg groups: (0,3,5), (1,4,2)
They move in sequence.

--------------------------------------------

Ripple-gate explanation:
It's basically tri-gate, but non od the legs are in sync.
There only 3 legs moving at a time, and they move in a wave-like pattern.

Order of movement: 
[1,5,0,4,2,3]
The cycle looks as follows:
1) covering distance r/3 - legs 1,5,0 - leg 1 stops after this, legs 5 and 0 continue to move. Leg 4 also starts to move
2) covering distance r/3 - legs 5,0,4 - leg 5 stops after this, legs 0 and 4 continue to move. Leg 2 also starts to move...
3) distance r/3 - legs 0,4,2
4) distance r/3 - legs 4,2,3
5) distance run r/3 - legs 2,3,1
6. distance r/3 - legs 3,1,5

In total in such a cycle each leg covers distance r.
Each leg spends 50% of the cycle in motion.

Leg 0 does the movement from 0 to 1/2 the cycle time,
Leg 4 from 1/6 time to 4/6 time
Leg 2 from 2/6 time to 5/6 time

"""

# Movement parameters
r = 1.5  # Step length
alpha = np.radians(35)  # Angle of leg positioning
leg_length = 5  # Length of each leg
num_steps = 5  # Number of steps per movement cycle
num_frames = 100  # Total frames in the animation
direction_x = 1  # 1 for right, -1 for left
direction_y = 0  # 1 for up, -1 for down

# Define leg angles
angles = [
    alpha, 0, -alpha, np.pi - alpha, np.pi, np.pi + alpha
]

# Initial foot positions
initial_positions = np.array([
    (leg_length * np.cos(angle), leg_length * np.sin(angle)) for angle in angles
])
foot_positions = initial_positions.copy()

# Function to compute the center of mass
def compute_center_of_mass(positions):
    return np.mean(positions[:, 0]), np.mean(positions[:, 1])

# Define movement sequences for different gaits
wave_sequence = [0, 1, 2, 3, 4, 5]
bi_sequence = [(0, 5), (1, 4), (2, 3)]
tri_sequence = [(0, 2, 4), (1, 3, 5)]
ripple_sequence = [1, 5, 0, 4, 2, 3]

# Default gait and control parameters
current_gait = 'wave'
moving_leg = 0
step = 0
resetting = False
pending_gait = None
target_position = foot_positions.copy()

# Initialize the plot
fig, ax = plt.subplots(figsize=(6, 6))
plt.subplots_adjust(bottom=0.2)
ax.set_xlim(-30, 30)
ax.set_ylim(-30, 30)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Hexapod Gait Simulation")
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)

# Visual elements for animation
lines = [ax.plot([], [], 'bo-', linewidth=2)[0] for _ in range(6)]
feet = [ax.add_patch(plt.Circle((0, 0), 0.5, color='blue', fill=True)) for _ in range(6)]
body = ax.add_patch(plt.Circle((0, 0), 0.5, color='green', fill=True, zorder=10))

# Function to update leg positions in each animation frame
def update(frame):
    global foot_positions, moving_leg, step, current_gait, resetting, pending_gait, direction_x, direction_y, target_position
    
    center_x, center_y = compute_center_of_mass(foot_positions)
    if resetting:
        target_positions = np.array([
            (center_x + leg_length * np.cos(angle), center_y + leg_length * np.sin(angle)) for angle in angles
        ])
        diff = target_positions - foot_positions
        max_diff = np.max(np.abs(diff))
        if max_diff < 0.01:
            foot_positions = target_positions.copy()
            resetting = False
            if pending_gait:
                current_gait = pending_gait
                pending_gait = None
            step = 0
            moving_leg = 0
            return
        foot_positions += diff * 0.4
    else:
        if current_gait == 'wave':
            sequence = wave_sequence[::-1] if direction_x == -1 or direction_y == -1 else wave_sequence
            if step < num_steps:
                foot_positions[sequence[moving_leg], 0] += direction_x * r / num_steps
                foot_positions[sequence[moving_leg], 1] += direction_y * r / num_steps
                step += 1
            else:
                moving_leg = (moving_leg + 1) % 6
                step = 0
        elif current_gait == 'bi':
            sequence = bi_sequence[::-1] if direction_x == -1 or direction_y == -1 else bi_sequence
            if step == 0:
                target_position = foot_positions.copy()
                for leg in sequence[moving_leg]:
                    target_position[leg, 0] += direction_x * r
                    target_position[leg, 1] += direction_y * r
            for leg in sequence[moving_leg]:
                foot_positions[leg] += (target_position[leg] - foot_positions[leg]) * (1 / num_steps)
            step += 1
            if step >= num_steps:
                moving_leg = (moving_leg + 1) % 3
                step = 0
        elif current_gait == 'tri':
            sequence = tri_sequence[::-1] if direction_x == -1 or direction_y == -1 else tri_sequence
            if step == 0:
                target_position = foot_positions.copy()
                for leg in sequence[moving_leg]:
                    target_position[leg, 0] += direction_x * r
                    target_position[leg, 1] += direction_y * r
            for leg in sequence[moving_leg]:
                foot_positions[leg] += (target_position[leg] - foot_positions[leg]) * (1 / num_steps)
            step += 1
            if step >= num_steps:
                moving_leg = (moving_leg + 1) % 2
                step = 0
        elif current_gait == 'ripple':
            sequence = ripple_sequence[::-1] if direction_x == -1 or direction_y == -1 else ripple_sequence
            moving_legs = [sequence[(moving_leg + i) % 6] for i in range(3)]
            delta_x = (direction_x * r / 3) / num_steps
            delta_y = (direction_y * r / 3) / num_steps
            for leg in moving_legs:
                foot_positions[leg, 0] += delta_x
                foot_positions[leg, 1] += delta_y
            step += 1
            if step >= num_steps:
                moving_leg = (moving_leg + 1) % 6
                step = 0
    
    center_x, center_y = compute_center_of_mass(foot_positions)
    for i, (x, y) in enumerate(foot_positions):
        lines[i].set_data([center_x, x], [center_y, y])
        feet[i].set_center((x, y))
    body.set_center((center_x, center_y))

# Function to change gait
def change_gait(new_gait):
    global resetting, pending_gait
    if current_gait != new_gait:
        pending_gait = new_gait
        resetting = True

# Function to change direction and speed
def on_key(event):
    global direction_x, direction_y, resetting, num_steps
    if event.key == 'left':
        direction_x, direction_y = -1, 0
        resetting = True
    elif event.key == 'right':
        direction_x, direction_y = 1, 0
        resetting = True
    elif event.key == 'up':
        direction_x, direction_y = 0, 1
        resetting = True
    elif event.key == 'down':
        direction_x, direction_y = 0, -1
        resetting = True
    elif event.key == 'w':
        num_steps = max(1, num_steps - 1)  # Increase speed
    elif event.key == 'x':
        num_steps += 1  # Decrease speed

# Buttons for gait selection
ax_wave = plt.axes([0.05, 0.05, 0.175, 0.075])
ax_bi = plt.axes([0.275, 0.05, 0.175, 0.075])
ax_tri = plt.axes([0.5, 0.05, 0.175, 0.075])
ax_ripple = plt.axes([0.725, 0.05, 0.175, 0.075])

btn_wave = Button(ax_wave, 'Wave Gait')
btn_bi = Button(ax_bi, 'Bi Gait')
btn_tri = Button(ax_tri, 'Tri Gait')
btn_ripple = Button(ax_ripple, 'Ripple Gait')

btn_wave.on_clicked(lambda event: change_gait('wave'))
btn_bi.on_clicked(lambda event: change_gait('bi'))
btn_tri.on_clicked(lambda event: change_gait('tri'))
btn_ripple.on_clicked(lambda event: change_gait('ripple'))

fig.canvas.mpl_connect('key_press_event', on_key)
ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=50, repeat=True)
plt.show()
