

import pygame
import math
import random

pygame.init()

# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1200
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COSMIC SINGULARITY")

clock = pygame.time.Clock()

CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

# ============================================================
# COLORS
# ============================================================

BLACK = (2, 2, 8)
WHITE = (245, 245, 255)

# ============================================================
# STAR FIELD
# ============================================================

stars = []

for _ in range(900):

    stars.append({
        "x": random.uniform(-600, 600),
        "y": random.uniform(-400, 400),
        "z": random.uniform(50, 900),

        "speed": random.uniform(0.5, 3.0),

        "size": random.uniform(0.5, 2.5)
    })


# ============================================================
# ACCRETION DISK PARTICLES
# ============================================================

disk = []

for _ in range(1600):

    angle = random.uniform(0, math.pi * 2)

    radius = random.uniform(100, 430)

    disk.append({
        "angle": angle,
        "radius": radius,

        "speed": random.uniform(
            0.002,
            0.009
        ),

        "height": random.uniform(
            -20,
            20
        ),

        "size": random.uniform(
            1,
            3
        )
    })


# ============================================================
# ENERGY PARTICLES
# ============================================================

energy_particles = []

for _ in range(450):

    angle = random.uniform(
        0,
        math.pi * 2
    )

    radius = random.uniform(
        100,
        500
    )

    energy_particles.append({
        "angle": angle,
        "radius": radius,

        "speed": random.uniform(
            0.01,
            0.04
        ),

        "size": random.randint(
            1,
            4
        ),

        "phase": random.uniform(
            0,
            math.pi * 2
        )
    })


# ============================================================
# SHOCKWAVES
# ============================================================

shockwaves = []


# ============================================================
# CAMERA
# ============================================================

camera_x = 0
camera_y = 0

target_camera_x = 0
target_camera_y = 0


# ============================================================
# ROTATION
# ============================================================

rotation = 0

# ============================================================
# TIME
# ============================================================

time = 0


# ============================================================
# FONT
# ============================================================

font = pygame.font.SysFont(
    "consolas",
    18
)

title_font = pygame.font.SysFont(
    "consolas",
    30
)


# ============================================================
# UTILITY
# ============================================================

def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(value, maximum)
    )


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000

    time += dt

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # GRAVITATIONAL PULSE
        # ----------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            shockwaves.append({
                "radius": 80,
                "alpha": 255
            })

            # Push particles outward

            for p in energy_particles:

                p["radius"] += random.uniform(
                    30,
                    100
                )


    # ========================================================
    # MOUSE CAMERA
    # ========================================================

    mouse_x, mouse_y = pygame.mouse.get_pos()

    target_camera_x = (
        mouse_x - WIDTH / 2
    ) * 0.04

    target_camera_y = (
        mouse_y - HEIGHT / 2
    ) * 0.04

    camera_x += (
        target_camera_x - camera_x
    ) * 0.05

    camera_y += (
        target_camera_y - camera_y
    ) * 0.05


    # ========================================================
    # BACKGROUND
    # ========================================================

    screen.fill(BLACK)


    # ========================================================
    # STAR FIELD
    # ========================================================

    for star in stars:

        z = star["z"]

        # Move stars toward camera

        z -= star["speed"]

        star["z"] = z

        # Reset star

        if z < 1:

            star["x"] = random.uniform(
                -600,
                600
            )

            star["y"] = random.uniform(
                -400,
                400
            )

            star["z"] = 900


        # Perspective projection

        perspective = 500 / z

        x = (
            CENTER.x
            + star["x"] * perspective
            + camera_x
        )

        y = (
            CENTER.y
            + star["y"] * perspective
            + camera_y
        )

        size = clamp(
            int(
                star["size"]
                * perspective
            ),
            1,
            5
        )


        if (
            0 <= x < WIDTH
            and
            0 <= y < HEIGHT
        ):

            brightness = clamp(
                int(
                    255
                    * (1 - z / 900)
                ),
                50,
                255
            )

            pygame.draw.circle(
                screen,
                (
                    brightness,
                    brightness,
                    brightness
                ),
                (
                    int(x),
                    int(y)
                ),
                size
            )


    # ========================================================
    # ACCRETION DISK
    # ========================================================

    rotation += 0.02

    for particle in disk:

        particle["angle"] += (
            particle["speed"]
            * (450 / particle["radius"])
        )

        angle = (
            particle["angle"]
            + rotation
        )

        radius = particle["radius"]


        # GRAVITY DISTORTION
        gravity = (
            9000
            / (radius * radius)
        )

        distorted_radius = (
            radius
            + math.sin(
                time * 3
                + angle * 5
            )
            * gravity
            * 20
        )


        # 3D ellipse projection

        vertical_scale = 0.38

        x = (
            CENTER.x
            + math.cos(angle)
            * distorted_radius
            + camera_x
        )

        y = (
            CENTER.y
            + math.sin(angle)
            * distorted_radius
            * vertical_scale
            + camera_y
            + particle["height"]
        )


        # Color based on radius

        ratio = radius / 430

        if ratio < 0.25:

            color = (
                255,
                240,
                120
            )

        elif ratio < 0.55:

            color = (
                255,
                130,
                40
            )

        else:

            color = (
                150,
                50,
                255
            )


        # Pulsating brightness

        pulse = (
            math.sin(
                time * 5
                + angle * 8
            )
            + 1
        ) / 2


        brightness = (
            0.65
            + pulse * 0.35
        )


        color = tuple(
            int(c * brightness)
            for c in color
        )


        size = int(
            particle["size"]
            * (
                1
                + gravity * 2
            )
        )


        pygame.draw.circle(
            screen,
            color,
            (
                int(x),
                int(y)
            ),
            max(1, size)
        )


    # ========================================================
    # GRAVITATIONAL LENSING RINGS
    # ========================================================

    for i in range(12):

        radius = (
            150
            + i * 13
        )

        distortion = (
            math.sin(
                time * 2
                + i
            )
            * 5
        )

        radius += distortion


        pygame.draw.ellipse(
            screen,
            (
                40 + i * 5,
                20,
                100 + i * 8
            ),
            (
                CENTER.x
                - radius
                + camera_x,

                CENTER.y
                - radius * 0.38
                + camera_y,

                radius * 2,

                radius * 0.76
            ),
            1
        )


    # ========================================================
    # ENERGY VORTEX
    # ========================================================

    for particle in energy_particles:

        particle["angle"] += (
            particle["speed"]
        )

        angle = particle["angle"]

        radius = particle["radius"]


        # Slowly pull toward singularity

        particle["radius"] -= 0.15


        if radius < 70:

            particle["radius"] = random.uniform(
                350,
                550
            )

            particle["angle"] = random.uniform(
                0,
                math.pi * 2
            )


        # Spiral distortion

        spiral = (
            math.sin(
                radius * 0.025
                - time * 4
            )
            * 20
        )


        final_radius = (
            radius
            + spiral
        )


        x = (
            CENTER.x
            + math.cos(angle)
            * final_radius
            + camera_x
        )

        y = (
            CENTER.y
            + math.sin(angle)
            * final_radius
            * 0.7
            + camera_y
        )


        pulse = (
            math.sin(
                time * 8
                + particle["phase"]
            )
            + 1
        ) / 2


        if pulse < 0.35:

            color = (
                80,
                120,
                255
            )

        else:

            color = (
                200,
                80,
                255
            )


        size = int(
            particle["size"]
            + pulse * 2
        )


        pygame.draw.circle(
            screen,
            color,
            (
                int(x),
                int(y)
            ),
            size
        )


    # ========================================================
    # JET OF ENERGY
    # ========================================================

    jet_length = 320

    for direction in [-1, 1]:

        points = []

        for i in range(35):

            distance = (
                i
                * jet_length
                / 35
            )

            wave = (
                math.sin(
                    time * 8
                    + i * 0.7
                )
                * (
                    20
                    + i * 1.2
                )
            )


            x = (
                CENTER.x
                + wave
                + camera_x
            )

            y = (
                CENTER.y
                + direction * distance
                + camera_y
            )

            points.append(
                (
                    int(x),
                    int(y)
                )
            )


        if len(points) > 1:

            pygame.draw.lines(
                screen,
                (
                    120,
                    80,
                    255
                ),
                False,
                points,
                2
            )


    # ========================================================
    # EVENT HORIZON
    # ========================================================

    horizon_radius = 105

    pulse = (
        math.sin(time * 4)
        * 5
    )


    pygame.draw.circle(
        screen,
        (
            0,
            0,
            0
        ),
        (
            int(CENTER.x + camera_x),
            int(CENTER.y + camera_y)
        ),
        int(
            horizon_radius
            + pulse
        )
    )


    # ========================================================
    # HORIZON GLOW
    # ========================================================

    for i in range(20):

        radius = (
            110
            + i * 3
        )

        alpha_factor = (
            1
            - i / 20
        )

        color = (
            int(150 * alpha_factor),
            int(30 * alpha_factor),
            int(255 * alpha_factor)
        )


        pygame.draw.circle(
            screen,
            color,
            (
                int(CENTER.x + camera_x),
                int(CENTER.y + camera_y)
            ),
            radius,
            2
        )


    # ========================================================
    # SHOCKWAVES
    # ========================================================

    for wave in shockwaves[:]:

        wave["radius"] += 12

        wave["alpha"] -= 5

        if wave["alpha"] <= 0:

            shockwaves.remove(
                wave
            )

            continue


        radius = wave["radius"]

        pygame.draw.ellipse(
            screen,
            (
                180,
                80,
                255
            ),
            (
                CENTER.x - radius,
                CENTER.y - radius * 0.35,
                radius * 2,
                radius * 0.7
            ),
            3
        )


    # ========================================================
    # UI
    # ========================================================

    title = title_font.render(
        "COSMIC SINGULARITY",
        True,
        WHITE
    )

    screen.blit(
        title,
        (30, 25)
    )


    status = font.render(
        "EVENT HORIZON: ACTIVE",
        True,
        (180, 100, 255)
    )

    screen.blit(
        status,
        (32, 65)
    )


    instruction = font.render(
        "MOVE MOUSE: DISTORT SPACE",
        True,
        WHITE
    )

    screen.blit(
        instruction,
        (30, HEIGHT - 65)
    )


    instruction2 = font.render(
        "CLICK: GRAVITATIONAL PULSE",
        True,
        WHITE
    )

    screen.blit(
        instruction2,
        (30, HEIGHT - 38)
    )


    fps_text = font.render(
        f"FPS: {int(clock.get_fps())}",
        True,
        WHITE
    )

    screen.blit(
        fps_text,
        (WIDTH - 130, 30)
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()


pygame.quit()