
import pygame
import numpy as np
import math

pygame.init()

# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1200
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ACCRETION DISK // SINGULARITY")

clock = pygame.time.Clock()

CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

PARTICLE_COUNT = 3200

INNER_RADIUS = 75
OUTER_RADIUS = 430

DISK_TILT = 0.38

# ============================================================
# COLORS
# ============================================================

BLACK = (1, 1, 6)
WHITE = (245, 245, 255)

# ============================================================
# RANDOM GENERATOR
# ============================================================

rng = np.random.default_rng()

# ============================================================
# PARTICLE DATA
# ============================================================

angles = rng.uniform(
    0,
    math.pi * 2,
    PARTICLE_COUNT
)

radius = (
    rng.random(PARTICLE_COUNT) ** 1.7
    * (OUTER_RADIUS - INNER_RADIUS)
    + INNER_RADIUS
)

height = rng.normal(
    0,
    5,
    PARTICLE_COUNT
)

sizes = rng.uniform(
    0.7,
    2.8,
    PARTICLE_COUNT
)

brightness = rng.uniform(
    0.65,
    1.0,
    PARTICLE_COUNT
)

# Inner particles orbit faster
angular_speed = (
    0.004
    + 0.045
    / np.power(radius / INNER_RADIUS, 1.5)
)

angular_speed *= rng.uniform(
    0.75,
    1.25,
    PARTICLE_COUNT
)

# ============================================================
# PARTICLE TRAILS
# ============================================================

TRAIL_LENGTH = 7

previous_positions = np.zeros(
    (TRAIL_LENGTH, PARTICLE_COUNT, 2)
)

previous_positions[:] = -9999

# ============================================================
# SHOCKWAVE
# ============================================================

shockwave_radius = 0
shockwave_strength = 0

# ============================================================
# CAMERA
# ============================================================

camera_x = 0
camera_y = 0

# ============================================================
# ANIMATION
# ============================================================

global_rotation = 0
elapsed = 0

# ============================================================
# FONTS
# ============================================================

font = pygame.font.SysFont(
    "consolas",
    17
)

title_font = pygame.font.SysFont(
    "consolas",
    28
)

# ============================================================
# SURFACES
# ============================================================

glow_surface = pygame.Surface(
    (WIDTH, HEIGHT),
    pygame.SRCALPHA
)

particle_surface = pygame.Surface(
    (WIDTH, HEIGHT),
    pygame.SRCALPHA
)


# ============================================================
# FUNCTIONS
# ============================================================

def particle_color(r):
    """
    Determines particle color based
    on its distance from the black hole.
    """

    ratio = (
        (r - INNER_RADIUS)
        / (OUTER_RADIUS - INNER_RADIUS)
    )

    ratio = max(
        0,
        min(1, ratio)
    )

    # Very hot inner region
    if ratio < 0.25:

        t = ratio / 0.25

        return (
            255,
            int(240 - 80 * t),
            int(160 - 100 * t)
        )

    # Orange middle region
    elif ratio < 0.65:

        t = (
            ratio - 0.25
        ) / 0.40

        return (
            255,
            int(160 - 100 * t),
            int(45 + 80 * t)
        )

    # Purple outer region
    else:

        t = (
            ratio - 0.65
        ) / 0.35

        return (
            int(180 - 80 * t),
            int(60 + 70 * t),
            int(160 + 90 * t)
        )


def project_disk(angle, radius_value, particle_height):
    """
    Converts the disk into a
    3D-looking perspective.
    """

    # Gravitational bending
    bend = 14000 / (radius_value * radius_value)

    distorted_angle = (
        angle + bend
    )

    # Spiral distortion
    spiral = (
        math.sin(
            radius_value * 0.045
            - elapsed * 2.5
        )
        * (
            3
            + 20 / max(radius_value, 1)
        )
    )

    r = radius_value + spiral

    x = (
        math.cos(distorted_angle)
        * r
    )

    y = (
        math.sin(distorted_angle)
        * r
        * DISK_TILT
    )

    # Turbulence
    turbulence = (
        math.sin(
            angle * 5
            + elapsed * 3
        )
        * 3
    )

    y += (
        particle_height
        + turbulence
    )

    return (
        CENTER_X + x + camera_x,
        CENTER_Y + y + camera_y
    )


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000

    elapsed += dt

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Click = gravitational pulse
        if event.type == pygame.MOUSEBUTTONDOWN:

            shockwave_radius = 100
            shockwave_strength = 1.0

    # ========================================================
    # MOUSE CAMERA
    # ========================================================

    mouse_x, mouse_y = pygame.mouse.get_pos()

    target_camera_x = (
        mouse_x - WIDTH / 2
    ) * 0.035

    target_camera_y = (
        mouse_y - HEIGHT / 2
    ) * 0.02

    camera_x += (
        target_camera_x - camera_x
    ) * 0.04

    camera_y += (
        target_camera_y - camera_y
    ) * 0.04

    # ========================================================
    # ROTATE DISK
    # ========================================================

    global_rotation += 0.0025

    angles += angular_speed

    angles += global_rotation * 0.001

    # ========================================================
    # SHOCKWAVE
    # ========================================================

    if shockwave_strength > 0:

        shockwave_radius += 8

        shockwave_strength *= 0.965

        distance_from_wave = np.abs(
            radius - shockwave_radius
        )

        disturbance = np.exp(
            -distance_from_wave / 35
        )

        radius[:] += (
            disturbance
            * shockwave_strength
            * 5
        )

        if shockwave_strength < 0.01:
            shockwave_strength = 0

    # ========================================================
    # BACKGROUND
    # ========================================================

    screen.fill(BLACK)

    # ========================================================
    # BACKGROUND STARS
    # ========================================================

    for i in range(180):

        angle = i * 2.399

        distance = (
            450
            + (i * 73) % 450
        )

        star_x = (
            CENTER_X
            + math.cos(angle)
            * distance
        )

        star_y = (
            CENTER_Y
            + math.sin(angle)
            * distance
            * 0.55
        )

        pulse = (
            math.sin(
                elapsed * 2 + i
            ) + 1
        ) / 2

        size = 1 if i % 3 else 2

        brightness_value = int(
            70 + pulse * 100
        )

        pygame.draw.circle(
            screen,
            (
                brightness_value,
                brightness_value,
                min(
                    255,
                    brightness_value + 30
                )
            ),
            (
                int(star_x),
                int(star_y)
            ),
            size
        )

    # ========================================================
    # CLEAR SURFACES
    # ========================================================

    particle_surface.fill(
        (0, 0, 0, 0)
    )

    glow_surface.fill(
        (0, 0, 0, 0)
    )

    # ========================================================
    # CALCULATE PARTICLE POSITIONS
    # ========================================================

    positions = np.zeros(
        (PARTICLE_COUNT, 2)
    )

    for i in range(PARTICLE_COUNT):

        x, y = project_disk(
            angles[i],
            radius[i],
            height[i]
        )

        positions[i] = (
            x,
            y
        )

    # ========================================================
    # PARTICLE TRAILS
    # ========================================================

    previous_positions[1:] = (
        previous_positions[:-1]
    )

    previous_positions[0] = positions

    for trail in range(
        TRAIL_LENGTH - 1,
        0,
        -1
    ):

        alpha = int(
            35
            * (
                1
                - trail / TRAIL_LENGTH
            )
        )

        if alpha <= 0:
            continue

        old_positions = previous_positions[trail]

        for i in range(
            0,
            PARTICLE_COUNT,
            5
        ):

            x1, y1 = old_positions[i]
            x2, y2 = positions[i]

            if x1 < 0:
                continue

            color = particle_color(
                radius[i]
            )

            trail_color = (
                color[0],
                color[1],
                color[2],
                alpha
            )

            pygame.draw.line(
                particle_surface,
                trail_color,
                (
                    int(x1),
                    int(y1)
                ),
                (
                    int(x2),
                    int(y2)
                ),
                1
            )

    # ========================================================
    # MAIN PARTICLES
    # ========================================================

    for i in range(PARTICLE_COUNT):

        x, y = positions[i]

        if (
            x < 0
            or x >= WIDTH
            or y < 0
            or y >= HEIGHT
        ):
            continue

        r = radius[i]

        color = particle_color(r)

        # Energy pulse
        pulse = (
            math.sin(
                elapsed * 5
                + angles[i] * 8
            ) + 1
        ) / 2

        brightness_factor = (
            brightness[i]
            * (
                0.75
                + pulse * 0.45
            )
        )

        color = tuple(
            max(
                0,
                min(
                    255,
                    int(
                        c * brightness_factor
                    )
                )
            )
            for c in color
        )

        size = max(
            1,
            int(
                sizes[i]
                * (
                    1
                    + 40 / max(r, 40)
                )
            )
        )

        pygame.draw.circle(
            particle_surface,
            (
                color[0],
                color[1],
                color[2],
                220
            ),
            (
                int(x),
                int(y)
            ),
            size
        )

        # Particle glow
        if i % 4 == 0:

            glow_size = size * 5

            pygame.draw.circle(
                glow_surface,
                (
                    color[0],
                    color[1],
                    color[2],
                    18
                ),
                (
                    int(x),
                    int(y)
                ),
                glow_size
            )

    # ========================================================
    # RENDER GLOW
    # ========================================================

    screen.blit(
        glow_surface,
        (0, 0),
        special_flags=pygame.BLEND_ADD
    )

    screen.blit(
        particle_surface,
        (0, 0),
        special_flags=pygame.BLEND_ADD
    )

    # ========================================================
    # INNER RING
    # ========================================================

    inner_pulse = (
        math.sin(elapsed * 6)
        * 5
    )

    inner_radius = (
        115 + inner_pulse
    )

    for layer in range(12):

        radius_layer = (
            inner_radius
            + layer * 3
        )

        intensity = int(
            150
            * (
                1 - layer / 12
            )
        )

        pygame.draw.ellipse(
            screen,
            (
                intensity,
                int(intensity * 0.3),
                255
            ),
            (
                CENTER_X - radius_layer,
                CENTER_Y
                - radius_layer * DISK_TILT,
                radius_layer * 2,
                radius_layer
                * DISK_TILT
                * 2
            ),
            2
        )

    # ========================================================
    # BLACK HOLE
    # ========================================================

    black_hole_radius = 88

    pygame.draw.circle(
        screen,
        (0, 0, 0),
        (
            int(CENTER_X + camera_x),
            int(CENTER_Y + camera_y)
        ),
        black_hole_radius
    )

    # ========================================================
    # EVENT HORIZON
    # ========================================================

    for layer in range(10):

        radius_layer = (
            black_hole_radius
            + 3
            + layer * 3
        )

        alpha = int(
            120
            * (
                1 - layer / 10
            )
        )

        horizon_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            horizon_surface,
            (
                255,
                120,
                30,
                alpha
            ),
            (
                CENTER_X - radius_layer,
                CENTER_Y
                - radius_layer * DISK_TILT,
                radius_layer * 2,
                radius_layer
                * DISK_TILT * 2
            ),
            2
        )

        screen.blit(
            horizon_surface,
            (0, 0),
            special_flags=pygame.BLEND_ADD
        )

    # ========================================================
    # SHOCKWAVE
    # ========================================================

    if shockwave_strength > 0:

        pygame.draw.ellipse(
            screen,
            (
                180,
                80,
                255
            ),
            (
                CENTER_X - shockwave_radius,
                CENTER_Y
                - shockwave_radius * DISK_TILT,
                shockwave_radius * 2,
                shockwave_radius
                * DISK_TILT * 2
            ),
            3
        )

    # ========================================================
    # TITLE
    # ========================================================

    title = title_font.render(
        "ACCRETION DISK",
        True,
        WHITE
    )

    screen.blit(
        title,
        (30, 25)
    )

    subtitle = font.render(
        "PROCEDURAL SINGULARITY // 3200 PARTICLES",
        True,
        (
            160,
            100,
            255
        )
    )

    screen.blit(
        subtitle,
        (32, 62)
    )

    # ========================================================
    # CONTROLS
    # ========================================================

    controls = font.render(
        "MOVE MOUSE  :  CAMERA DISTORTION",
        True,
        WHITE
    )

    screen.blit(
        controls,
        (30, HEIGHT - 65)
    )

    controls2 = font.render(
        "LEFT CLICK   :  GRAVITATIONAL PULSE",
        True,
        WHITE
    )

    screen.blit(
        controls2,
        (30, HEIGHT - 40)
    )

    # ========================================================
    # FPS
    # ========================================================

    fps_text = font.render(
        f"FPS : {int(clock.get_fps())}",
        True,
        WHITE
    )

    screen.blit(
        fps_text,
        (WIDTH - 120, 30)
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()


pygame.quit()