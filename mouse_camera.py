
import pygame
import random
import math

pygame.init()

# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1200
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOUSE CONTROLLED COSMIC CAMERA")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (2, 2, 10)
WHITE = (255, 255, 255)
BLUE = (80, 170, 255)
PURPLE = (180, 80, 255)

# ============================================================
# CAMERA
# ============================================================

camera_x = 0
camera_y = 0

target_camera_x = 0
target_camera_y = 0

# ============================================================
# STARS
# ============================================================

stars = []

for i in range(700):

    stars.append({
        "x": random.uniform(-1000, 1000),
        "y": random.uniform(-700, 700),
        "depth": random.uniform(0.2, 1.5),
        "size": random.randint(1, 3)
    })

# ============================================================
# PLANETS
# ============================================================

planets = [
    {
        "x": -350,
        "y": -120,
        "radius": 80,
        "depth": 0.35
    },
    {
        "x": 300,
        "y": 180,
        "radius": 120,
        "depth": 0.55
    },
    {
        "x": 550,
        "y": -250,
        "radius": 55,
        "depth": 0.8
    }
]

# ============================================================
# CAMERA SMOOTHING
# ============================================================

SMOOTHING = 0.06

# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ========================================================
    # GET MOUSE POSITION
    # ========================================================

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Convert mouse position to range -1 to 1

    mouse_normal_x = (
        mouse_x - WIDTH / 2
    ) / (WIDTH / 2)

    mouse_normal_y = (
        mouse_y - HEIGHT / 2
    ) / (HEIGHT / 2)

    # ========================================================
    # CAMERA TARGET
    # ========================================================

    target_camera_x = (
        mouse_normal_x * 180
    )

    target_camera_y = (
        mouse_normal_y * 120
    )

    # ========================================================
    # SMOOTH CAMERA MOVEMENT
    # ========================================================

    camera_x += (
        target_camera_x - camera_x
    ) * SMOOTHING

    camera_y += (
        target_camera_y - camera_y
    ) * SMOOTHING

    # ========================================================
    # BACKGROUND
    # ========================================================

    screen.fill(BLACK)

    # ========================================================
    # DRAW STARS
    # ========================================================

    for star in stars:

        x = star["x"]
        y = star["y"]
        depth = star["depth"]

        # Farther stars move less
        screen_x = (
            WIDTH / 2
            + x
            - camera_x * depth
        )

        screen_y = (
            HEIGHT / 2
            + y
            - camera_y * depth
        )

        # Twinkle effect

        twinkle = random.random()

        size = star["size"]

        if twinkle > 0.97:
            size += 1

        # Draw only visible stars

        if (
            0 <= screen_x < WIDTH
            and
            0 <= screen_y < HEIGHT
        ):

            brightness = int(
                100
                + 120 * depth
            )

            brightness = min(
                brightness,
                255
            )

            pygame.draw.circle(
                screen,
                (
                    brightness,
                    brightness,
                    255
                ),
                (
                    int(screen_x),
                    int(screen_y)
                ),
                size
            )

    # ========================================================
    # DRAW PLANETS
    # ========================================================

    for planet in planets:

        x = planet["x"]
        y = planet["y"]
        radius = planet["radius"]
        depth = planet["depth"]

        screen_x = (
            WIDTH / 2
            + x
            - camera_x * depth
        )

        screen_y = (
            HEIGHT / 2
            + y
            - camera_y * depth
        )

        # Planet glow

        for glow in range(5):

            glow_radius = (
                radius
                + glow * 12
            )

            pygame.draw.circle(
                screen,
                (
                    30,
                    30,
                    100
                ),
                (
                    int(screen_x),
                    int(screen_y)
                ),
                glow_radius,
                2
            )

        # Planet

        pygame.draw.circle(
            screen,
            (
                70,
                100,
                220
            ),
            (
                int(screen_x),
                int(screen_y)
            ),
            radius
        )

        # Highlight

        pygame.draw.circle(
            screen,
            (
                150,
                180,
                255
            ),
            (
                int(screen_x - radius * 0.3),
                int(screen_y - radius * 0.3)
            ),
            int(radius * 0.25)
        )

    # ========================================================
    # CENTER OBJECT
    # ========================================================

    center_x = (
        WIDTH / 2
        - camera_x * 0.15
    )

    center_y = (
        HEIGHT / 2
        - camera_y * 0.15
    )

    # Glow

    for glow in range(8):

        radius = (
            70
            + glow * 10
        )

        pygame.draw.circle(
            screen,
            (
                40,
                80,
                180
            ),
            (
                int(center_x),
                int(center_y)
            ),
            radius,
            2
        )

    # Main object

    pygame.draw.circle(
        screen,
        (
            20,
            30,
            80
        ),
        (
            int(center_x),
            int(center_y)
        ),
        65
    )

    # ========================================================
    # CAMERA CROSSHAIR
    # ========================================================

    pygame.draw.line(
        screen,
        BLUE,
        (
            int(center_x - 100),
            int(center_y)
        ),
        (
            int(center_x + 100),
            int(center_y)
        ),
        1
    )

    pygame.draw.line(
        screen,
        BLUE,
        (
            int(center_x),
            int(center_y - 100)
        ),
        (
            int(center_x),
            int(center_y + 100)
        ),
        1
    )

    # ========================================================
    # UI
    # ========================================================

    font = pygame.font.SysFont(
        "consolas",
        18
    )

    title = font.render(
        "MOUSE CONTROLLED CAMERA",
        True,
        WHITE
    )

    screen.blit(
        title,
        (30, 30)
    )

    instruction = font.render(
        "MOVE YOUR MOUSE TO CONTROL THE CAMERA",
        True,
        BLUE
    )

    screen.blit(
        instruction,
        (30, 60)
    )

    camera_text = font.render(
        f"CAMERA X: {camera_x:7.2f}",
        True,
        WHITE
    )

    screen.blit(
        camera_text,
        (30, 100)
    )

    camera_text_y = font.render(
        f"CAMERA Y: {camera_y:7.2f}",
        True,
        WHITE
    )

    screen.blit(
        camera_text_y,
        (30, 125)
    )

    fps = font.render(
        f"FPS: {int(clock.get_fps())}",
        True,
        WHITE
    )

    screen.blit(
        fps,
        (WIDTH - 110, 30)
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

pygame.quit()