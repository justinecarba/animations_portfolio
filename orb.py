

import pygame
import random
import math

pygame.init()

# =========================
# WINDOW
# =========================
WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Particle Animation")

clock = pygame.time.Clock()

# =========================
# COLORS
# =========================
BLACK = (5, 5, 15)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
CYAN = (0, 255, 255)
PURPLE = (180, 80, 255)

# =========================
# PARTICLE CLASS
# =========================
class Particle:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.size = random.randint(2, 5)
        self.life = random.randint(40, 120)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vx *= 1.01
        self.vy *= 1.01

        self.life -= 1

    def draw(self):
        if self.life > 0:
            alpha = min(255, self.life * 4)

            particle_surface = pygame.Surface(
                (self.size * 4, self.size * 4),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                particle_surface,
                (*CYAN, alpha),
                (self.size * 2, self.size * 2),
                self.size
            )

            screen.blit(
                particle_surface,
                (
                    self.x - self.size * 2,
                    self.y - self.size * 2
                )
            )


# =========================
# PARTICLE LIST
# =========================
particles = []

for _ in range(250):
    particles.append(Particle())


# =========================
# MAIN LOOP
# =========================
running = True

time = 0

while running:

    # -------------------------
    # EVENTS
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Create explosion when SPACE is pressed
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                for _ in range(150):
                    particles.append(Particle())


    # -------------------------
    # BACKGROUND
    # -------------------------
    screen.fill(BLACK)

    time += 0.03


    # =========================
    # MOVING ORB
    # =========================

    orb_x = WIDTH // 2 + math.sin(time) * 250
    orb_y = HEIGHT // 2 + math.cos(time * 1.5) * 120


    # =========================
    # ORB GLOW
    # =========================

    glow = pygame.Surface((300, 300), pygame.SRCALPHA)

    for radius in range(100, 10, -8):

        alpha = int(2 + (100 - radius) * 0.3)

        pygame.draw.circle(
            glow,
            (50, 150, 255, alpha),
            (150, 150),
            radius
        )

    screen.blit(
        glow,
        (orb_x - 150, orb_y - 150)
    )


    # =========================
    # ORB
    # =========================

    pygame.draw.circle(
        screen,
        BLUE,
        (int(orb_x), int(orb_y)),
        30
    )

    pygame.draw.circle(
        screen,
        CYAN,
        (int(orb_x), int(orb_y)),
        20
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (int(orb_x - 7), int(orb_y - 7)),
        7
    )


    # =========================
    # PARTICLES
    # =========================

    for particle in particles[:]:

        particle.update()
        particle.draw()

        if (
            particle.life <= 0
            or particle.x < 0
            or particle.x > WIDTH
            or particle.y < 0
            or particle.y > HEIGHT
        ):
            particles.remove(particle)


    # =========================
    # RANDOM NEW PARTICLES
    # =========================

    if len(particles) < 250:

        particles.append(Particle())


    # =========================
    # TITLE
    # =========================

    font = pygame.font.SysFont("Arial", 28, bold=True)

    title = font.render(
        "PYTHON PARTICLE ANIMATION",
        True,
        WHITE
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            30
        )
    )


    # =========================
    # INSTRUCTION
    # =========================

    small_font = pygame.font.SysFont("Arial", 18)

    text = small_font.render(
        "Press SPACE to create an explosion",
        True,
        (180, 180, 200)
    )

    screen.blit(
        text,
        (
            WIDTH // 2 - text.get_width() // 2,
            HEIGHT - 40
        )
    )


    # =========================
    # UPDATE SCREEN
    # =========================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()