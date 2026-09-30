
import pygame
import math

pygame.init()

# Window
WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Energy Ball")

clock = pygame.time.Clock()

# Ball
x = WIDTH // 2
y = HEIGHT // 2

speed_x = 5
speed_y = 4

radius = 30

# Trail
trail = []

running = True

while running:

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

    # Update position
    x += speed_x
    y += speed_y

    # Bounce from walls
    if x - radius <= 0 or x + radius >= WIDTH:
        speed_x *= -1

    if y - radius <= 0 or y + radius >= HEIGHT:
        speed_y *= -1

    # Add current position to trail
    trail.append((x, y))

    # Limit trail length
    if len(trail) > 30:
        trail.pop(0)

    # Background
    screen.fill((5, 5, 20))

    # Draw trail
    for i, position in enumerate(trail):

        trail_x, trail_y = position

        size = int(
            radius * (i / len(trail))
        )

        if size < 2:
            size = 2

        pygame.draw.circle(
            screen,
            (50, 100, 255),
            (trail_x, trail_y),
            size
        )

    # Pulsating effect
    pulse = math.sin(
        pygame.time.get_ticks() * 0.01
    )

    glow_radius = int(
        radius + pulse * 8
    )

    # Glow
    pygame.draw.circle(
        screen,
        (30, 80, 180),
        (x, y),
        glow_radius + 15
    )

    pygame.draw.circle(
        screen,
        (50, 150, 255),
        (x, y),
        glow_radius
    )

    # Ball
    pygame.draw.circle(
        screen,
        (220, 240, 255),
        (x, y),
        radius
    )

    # Update display
    pygame.display.flip()

    # FPS
    clock.tick(60)


pygame.quit()