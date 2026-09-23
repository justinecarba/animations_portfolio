
"""
Animated Waves and Particles
-----------------------------
Run this with:  python waves_particles.py

It will always save an output file "waves_particles.gif" you can open and
view. Uncomment the plt.show() line at the bottom to also see a live
window if your environment has a GUI display.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ---------------------------------------------------------
# 1. SET UP THE SCENE
# ---------------------------------------------------------
FRAMES = 150
FIG_W, FIG_H = 10, 6

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("#020314")
ax.set_facecolor("#020314")
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

rng = np.random.default_rng(7)

# ---------------------------------------------------------
# 2. LAYERED WAVES (several sine curves, filled, at different depths)
# ---------------------------------------------------------
X = np.linspace(0, 100, 400)

WAVE_LAYERS = [
    # (base height, amplitude, wavelength-factor, speed, color, alpha)
    (14, 3.0, 1.6, 0.9, "#3a2a6d", 0.55),
    (20, 4.0, 1.2, 1.3, "#5b3aa0", 0.55),
    (27, 5.5, 0.9, 1.8, "#8a4fd1", 0.60),
    (35, 7.0, 0.7, 2.4, "#c86fe0", 0.65),
]

wave_fills = [ax.fill_between(X, 0, 0, color=c, alpha=a, zorder=i)
              for i, (_, _, _, _, c, a) in enumerate(WAVE_LAYERS)]

def wave_y(base, amp, wl, speed, frame):
    phase = frame * 0.05 * speed
    return (base
            + amp * np.sin(X * wl / 10 + phase)
            + amp * 0.35 * np.sin(X * wl / 4 - phase * 1.7))

# ---------------------------------------------------------
# 3. FLOATING PARTICLES (rise up, drift sideways, twinkle, loop)
# ---------------------------------------------------------
N_PARTICLES = 140
p_x0 = rng.uniform(0, 100, N_PARTICLES)
p_y0 = rng.uniform(0, 60, N_PARTICLES)
p_speed = rng.uniform(0.15, 0.55, N_PARTICLES)
p_drift = rng.uniform(-0.25, 0.25, N_PARTICLES)
p_size = rng.uniform(4, 26, N_PARTICLES)
p_phase = rng.uniform(0, 2 * np.pi, N_PARTICLES)

# color range: cool cyan -> warm pink particles
p_hue = rng.uniform(0, 1, N_PARTICLES)
p_colors = np.zeros((N_PARTICLES, 4))
p_colors[:, 0] = 0.5 + 0.5 * p_hue           # R
p_colors[:, 1] = 0.7 - 0.3 * p_hue           # G
p_colors[:, 2] = 1.0                         # B
p_colors[:, 3] = 0.85                        # alpha (updated per-frame)

particles = ax.scatter(p_x0, p_y0, s=p_size, c=p_colors, zorder=10,
                        edgecolors="none")

# a few larger "glow" particles for extra sparkle
N_GLOW = 18
g_x0 = rng.uniform(0, 100, N_GLOW)
g_y0 = rng.uniform(0, 60, N_GLOW)
g_speed = rng.uniform(0.1, 0.3, N_GLOW)
g_phase = rng.uniform(0, 2 * np.pi, N_GLOW)
glow = ax.scatter(g_x0, g_y0, s=180, c="white", alpha=0.12, zorder=9)


# ---------------------------------------------------------
# 4. ANIMATION UPDATE FUNCTION
# ---------------------------------------------------------
def update(frame):
    # --- waves ---
    for i, (fill, (base, amp, wl, speed, color, alpha)) in enumerate(zip(wave_fills, WAVE_LAYERS)):
        y = wave_y(base, amp, wl, speed, frame)
        wave_fills[i].remove()
        wave_fills[i] = ax.fill_between(X, 0, y, color=color, alpha=alpha, zorder=i)

    # --- particles: rise, drift, wrap around, twinkle ---
    t = frame
    py = (p_y0 + t * p_speed) % 64 - 2
    px = (p_x0 + t * p_drift) % 100
    twinkle = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(t * 0.1 + p_phase))
    particles.set_offsets(np.column_stack([px, py]))
    particles.set_sizes(p_size * (0.6 + 0.4 * twinkle))
    colors = p_colors.copy()
    colors[:, 3] = 0.3 + 0.6 * twinkle
    color_values: list[tuple[float, float, float, float]] = [
        (float(red), float(green), float(blue), float(alpha))
        for red, green, blue, alpha in colors
    ]
    particles.set_color(color_values)  # type: ignore[arg-type]

    # --- glow orbs: slow float + pulse ---
    gy = (g_y0 + t * g_speed) % 64 - 2
    gx = g_x0 + 3 * np.sin(t * 0.03 + g_phase)
    pulse = 0.5 + 0.5 * np.sin(t * 0.08 + g_phase)
    glow.set_offsets(np.column_stack([gx, gy]))
    glow.set_sizes(120 + 140 * pulse)
    glow.set_alpha(0.10 + 0.12 * pulse)

    return wave_fills + [particles, glow]


# ---------------------------------------------------------
# 5. BUILD + SAVE THE ANIMATION
# ---------------------------------------------------------
anim = animation.FuncAnimation(fig, update, frames=FRAMES, interval=40, blit=False)

output_path = "waves_particles.gif"
anim.save(output_path, writer=animation.PillowWriter(fps=25))
print(f"Saved animation to {output_path}")

# Uncomment to also show a live window when running locally with a display:
# plt.show()