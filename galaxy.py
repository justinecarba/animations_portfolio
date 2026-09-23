

"""
Spaceship Flying Through an Animated Galaxy
--------------------------------------------
Run this with:  python galaxy_ship.py

It will pop up a live animated window (if your environment supports a GUI),
AND it will always save an output file "spaceship_galaxy.gif" you can open
and view even without a GUI.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon

# ---------------------------------------------------------
# 1. SET UP THE SCENE
# ---------------------------------------------------------
FRAMES = 150
FIG_W, FIG_H = 10, 7.5

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
ax.set_xlim(0, 100)
ax.set_ylim(0, 75)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

rng = np.random.default_rng(42)

# ---------------------------------------------------------
# 2. BACKGROUND STARFIELD (twinkling)
# ---------------------------------------------------------
N_STARS = 220
star_x = rng.uniform(0, 100, N_STARS)
star_y = rng.uniform(0, 75, N_STARS)
star_base_size = rng.uniform(1, 10, N_STARS)
star_phase = rng.uniform(0, 2 * np.pi, N_STARS)

stars = ax.scatter(star_x, star_y, s=star_base_size, c="white", alpha=0.8)

# ---------------------------------------------------------
# 3. SPIRAL GALAXY (rotating)
# ---------------------------------------------------------
N_ARMS = 3
POINTS_PER_ARM = 260
t = np.linspace(0, 1, POINTS_PER_ARM)

# radius grows outward, angle spirals around, jittered for a "dusty" look
base_r = t * 34
base_theta = t * 3.2 * np.pi

galaxy_x_list, galaxy_y_list, galaxy_c_list = [], [], []
for arm in range(N_ARMS):
    offset = arm * (2 * np.pi / N_ARMS)
    jitter_r = rng.normal(0, 1.4, POINTS_PER_ARM) * (0.3 + t)
    jitter_a = rng.normal(0, 0.12, POINTS_PER_ARM)
    galaxy_x_list.append(base_r + jitter_r)
    galaxy_y_list.append(base_theta + offset + jitter_a)
    galaxy_c_list.append(t)

gal_r = np.concatenate(galaxy_x_list)
gal_theta0 = np.concatenate(galaxy_y_list)
gal_t = np.concatenate(galaxy_c_list)

GAL_CX, GAL_CY = 58, 40  # galaxy center on screen

# color: hot white/blue core fading to purple/orange edges
colors = np.zeros((len(gal_t), 4))
colors[:, 0] = 0.55 + 0.45 * gal_t          # R
colors[:, 1] = 0.25 + 0.35 * (1 - gal_t)    # G
colors[:, 2] = 0.85                         # B
colors[:, 3] = 0.85 * (1 - 0.5 * gal_t)     # alpha

galaxy_scatter = ax.scatter(gal_r * 0 + GAL_CX, gal_r * 0 + GAL_CY,
                             s=(1 - gal_t) * 18 + 3, c=colors)

# bright galactic core glow
core = ax.scatter([GAL_CX], [GAL_CY], s=900, c="white", alpha=0.35)
core2 = ax.scatter([GAL_CX], [GAL_CY], s=350, c="white", alpha=0.6)

# ---------------------------------------------------------
# 4. SPACESHIP (a simple triangular ship + flame)
# ---------------------------------------------------------
def ship_shape(cx, cy, angle_deg, scale=3.2):
    """Return polygon vertices for a little ship at (cx, cy) rotated by angle."""
    pts = np.array([
        [1.6, 0.0],    # nose
        [-1.0, 0.7],   # back-top
        [-0.5, 0.0],   # back-notch
        [-1.0, -0.7],  # back-bottom
    ]) * scale
    a = np.radians(angle_deg)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    pts = pts @ rot.T
    pts[:, 0] += cx
    pts[:, 1] += cy
    return pts

ship_patch = Polygon(ship_shape(0, 0, 0), closed=True,
                      facecolor="#e8e8ff", edgecolor="#7fd8ff", linewidth=1.5, zorder=5)
ax.add_patch(ship_patch)

flame_patch = Polygon(np.zeros((3, 2)), closed=True,
                       facecolor="#ff9933", edgecolor="none", alpha=0.85, zorder=4)
ax.add_patch(flame_patch)

# ship trail (fading dots behind it)
TRAIL_LEN = 18
trail_scatter = ax.scatter([], [], s=[], c=[], zorder=3)
trail_x, trail_y = [], []

# flight path: a swooping curve across the screen, past the galaxy
def ship_position(frame):
    p = frame / FRAMES
    x = 5 + 92 * p
    y = 18 + 30 * np.sin(p * 2.4 * np.pi) * np.exp(-1.2 * p) + 14 * p
    # heading = derivative direction
    p2 = min(p + 0.01, 1.0)
    x2 = 5 + 92 * p2
    y2 = 18 + 30 * np.sin(p2 * 2.4 * np.pi) * np.exp(-1.2 * p2) + 14 * p2
    angle = np.degrees(np.arctan2(y2 - y, x2 - x))
    return x, y, angle


# ---------------------------------------------------------
# 5. ANIMATION UPDATE FUNCTION
# ---------------------------------------------------------
def update(frame):
    # twinkle stars
    tw = 0.5 + 0.5 * np.sin(frame * 0.15 + star_phase)
    stars.set_sizes(star_base_size * (0.5 + tw))
    stars.set_alpha(0.5)

    # rotate galaxy slowly
    rot_speed = 0.01
    theta = gal_theta0 + frame * rot_speed
    gx = GAL_CX + gal_r * np.cos(theta)
    gy = GAL_CY + gal_r * 0.55 * np.sin(theta)  # squashed for a "tilted disk" look
    galaxy_scatter.set_offsets(np.column_stack([gx, gy]))

    pulse = 1 + 0.15 * np.sin(frame * 0.2)
    core.set_sizes([900 * pulse])
    core2.set_sizes([350 * pulse])

    # move ship
    sx, sy, sangle = ship_position(frame)
    ship_patch.set_xy(ship_shape(sx, sy, sangle))

    # flame behind ship
    a = np.radians(sangle)
    back = np.array([-1.0, 0.0]) * 3.2
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    back_pt = back @ rot.T + [sx, sy]
    flick = 1 + 0.4 * np.sin(frame * 1.3)
    flame_pts = np.array([
        [-0.4, 0.5], [-2.2 * flick, 0.0], [-0.4, -0.5]
    ]) * 1.0
    flame_pts = (flame_pts @ rot.T) + back_pt
    flame_patch.set_xy(flame_pts)

    # trail
    trail_x.append(sx)
    trail_y.append(sy)
    if len(trail_x) > TRAIL_LEN:
        trail_x.pop(0)
        trail_y.pop(0)
    n = len(trail_x)
    sizes = np.linspace(2, 22, n)
    alphas = np.linspace(0.05, 0.7, n)
    trail_colors = np.zeros((n, 4))
    trail_colors[:, 0] = 0.5
    trail_colors[:, 1] = 0.85
    trail_colors[:, 2] = 1.0
    trail_colors[:, 3] = alphas
    trail_scatter.set_offsets(np.column_stack([trail_x, trail_y]))
    trail_scatter.set_sizes(sizes)
    trail_rgba = [
        (float(color[0]), float(color[1]), float(color[2]), float(color[3]))
        for color in trail_colors
    ]
    trail_scatter.set_color(trail_rgba)

    return stars, galaxy_scatter, core, core2, ship_patch, flame_patch, trail_scatter


# ---------------------------------------------------------
# 6. BUILD + SAVE THE ANIMATION
# ---------------------------------------------------------
anim = animation.FuncAnimation(fig, update, frames=FRAMES, interval=40, blit=False)

output_path = "spaceship_galaxy.gif"
anim.save(output_path, writer=animation.PillowWriter(fps=25))
print(f"Saved animation to {output_path}")

# Keep the window open so the animation can be watched after the GIF is saved.
plt.show()