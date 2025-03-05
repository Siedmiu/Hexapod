import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

"""
Bi-gate explanation:
The Hexapod moves pairs of legs simultaneously.
Leg pairs: (0,5), (1,4), (2,3)
They move in sequence.
"""

# Parameters
r = 1.5  # Length of leg movement
alpha = np.radians(35)  
leg_length = 5  
num_steps = 5  # Number of steps for each leg movement
num_frames = 100  # Total number of animation frames

# Define leg angles relative to the body
angles = [
    alpha, 0, -alpha, np.pi - alpha, np.pi, np.pi + alpha
]

# Legs initial positions
foot_positions = np.array([
    (leg_length * np.cos(angle), leg_length * np.sin(angle)) for angle in angles
])

# Define leg pairs for bi-gate
leg_pairs = [(0, 5), (1, 4), (2, 3)]
current_pair = 0  # Index of the moving pair
step = 0  # Step counter for the current movement

# Compute center of mass
def compute_center_of_mass(positions):
    return np.mean(positions[:, 0]), np.mean(positions[:, 1])

# Initialize figure
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-30, 30)
ax.set_ylim(-30, 30)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Hexapod - Bi-Gate Animacja")
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)

# Initialize plot elements
lines = [ax.plot([], [], 'bo-', linewidth=2)[0] for _ in range(6)]
feet = [ax.add_patch(plt.Circle((0, 0), 0.5, color='blue', fill=True)) for _ in range(6)]
body = ax.add_patch(plt.Circle((0, 0), 0.5, color='green', fill=True, zorder=10))

def update(frame):
    """Update function for animation."""
    global foot_positions, current_pair, step
    
    # Move the current leg pair progressively
    if step < num_steps:
        t = step / num_steps  # Normalized progress of the step
        for leg in leg_pairs[current_pair]:
            foot_positions[leg, 1] += (r / num_steps)  # Increment leg position gradually
        step += 1
    else:
        # Switch to the next leg pair after completing the movement
        current_pair = (current_pair + 1) % len(leg_pairs)
        step = 0
    
    # Compute center of mass of legs
    center_x, center_y = compute_center_of_mass(foot_positions)
    
    # Update positions of legs and body
    for i, (x, y) in enumerate(foot_positions):
        lines[i].set_data([center_x, x], [center_y, y])  # Update leg lines
        feet[i].set_center((x, y))  # Update foot positions
    
    body.set_center((center_x, center_y))  # Update body position

# Run animation
ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=10, repeat=True)
plt.show()