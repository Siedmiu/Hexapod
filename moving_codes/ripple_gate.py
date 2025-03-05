import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

"""
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
etc.
"""

# Parameters
r = 1.5  # Total step distance
r_step = r / 3  # Distance per step in ripple gait
alpha = np.radians(35)  # Angle of leg positioning
leg_length = 5  # Length of each leg
num_steps = 5  # Number of steps per movement cycle
num_frames = 100  # Total frames in the animation

# Define leg angles
angles = [
    alpha, 0, -alpha, np.pi - alpha, np.pi, np.pi + alpha
]

# Initial leg positions
foot_positions = np.array([
    (leg_length * np.cos(angle), leg_length * np.sin(angle)) for angle in angles
])

# Function to compute the center of mass
# The torso will be positioned at the average of all foot positions
def compute_center_of_mass(positions):
    return np.mean(positions[:, 0]), np.mean(positions[:, 1])

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-30, 30)
ax.set_ylim(-30, 30)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Hexapod - Ripple Gait Animation")
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)

# Plot elements
lines = [ax.plot([], [], 'bo-', linewidth=2)[0] for _ in range(6)]  # Legs
feet = [ax.add_patch(plt.Circle((0, 0), 0.5, color='blue', fill=True)) for _ in range(6)]  # Feet
body = ax.add_patch(plt.Circle((0, 0), 0.5, color='green', fill=True, zorder=10))  # Torso

# Sequence of leg movement in ripple gait
movement_order = [1, 5, 0, 4, 2, 3]  # Order in which legs move
current_step = 0  # Index tracking which leg is currently moving
step = 0  # Steps taken by the currently moving leg

def update(frame):
    global foot_positions, current_step, step
    
    # Determine which legs are moving at this frame
    moving_legs = [movement_order[(current_step + i) % 6] for i in range(3)]
    
    # Compute incremental movement for the selected legs
    delta = r_step / num_steps
    for leg in moving_legs:
        foot_positions[leg, 1] += delta
    
    # Update step counter and switch to next leg sequence
    step += 1
    if step >= num_steps:
        current_step = (current_step + 1) % 6
        step = 0
    
    # Compute new center of mass
    center_x, center_y = compute_center_of_mass(foot_positions)
    
    # Update plot elements
    for i, (x, y) in enumerate(foot_positions):
        lines[i].set_data([center_x, x], [center_y, y])
        feet[i].set_center((x, y))
    
    body.set_center((center_x, center_y))

ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=10, repeat=True)
plt.show()
