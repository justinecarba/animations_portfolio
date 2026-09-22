
import pygame 
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Electric Plasma Ring")

clock = pygame.time.Clock()

cx, cy = WIDTH // 2, HEIGHT // 2

angle = 0


def draw_lightning_bolt(surface, bolt_angle):
    """Draw one short, flickering, branching bolt from the ring outward."""
    points = []
    segments = 7

    for segment in range(segments + 1):
        distance = 168 + segment * 12
        jitter = 0 if segment in (0, segments) else random.uniform(-14, 14)
        point_angle = bolt_angle + random.uniform(-0.025, 0.025)
        points.append((
            int(cx + math.cos(point_angle) * (distance + jitter)),
            int(cy + math.sin(point_angle) * (distance + jitter))
        ))

    for start, end in zip(points, points[1:]):
        pygame.draw.line(surface, (30, 110, 220), start, end, 7)
        pygame.draw.line(surface, (190, 245, 255), start, end, 2)

    branch_start = points[segments // 2]
    branch_angle = bolt_angle + random.choice((-1, 1)) * random.uniform(0.35, 0.7)
    branch_length = random.randint(25, 48)
    branch_end = (
        int(branch_start[0] + math.cos(branch_angle) * branch_length),
        int(branch_start[1] + math.sin(branch_angle) * branch_length)
    )
    pygame.draw.line(surface, (30, 110, 220), branch_start, branch_end, 5)
    pygame.draw.line(surface, (190, 245, 255), branch_start, branch_end, 2)

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    angle += 0.02

    for i in range(180):
        a = math.radians(i * 2) + angle
        r = 170 + 12*math.sin(i*0.3 + angle * 6)
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r

        color = (
            0,
            180 + int(75 * math.sin(i * 0.2 + angle * 3)),
            255
        )

        pygame.draw.circle(screen, color, (int(x), int(y)), 4)

    for i in range(40):
        a = i * 0.6 + angle * 4
        r1 = 120 + 25 * math.sin(angle * 5 + i)
        r2 = 175 + 20 * math.cos(angle * 4 * i)
        x1 = cx + math.cos(a) * r1
        y1 = cy + math.sin(a) * r1
        x2 = cx + math.cos(a + 0.25) * r2
        y2 = cy + math.sin(a + 0.25) * r2

        pygame.draw.line(
            screen,
            (100, 255, 255),
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            2
        )

    for i in range(8):
        if random.random() < 0.7:
            bolt_angle = angle * 1.5 + i * (math.pi / 4)
            draw_lightning_bolt(screen, bolt_angle)

    pulse = 55 + 8 * math.sin(angle * 6)
    pygame.draw.circle(
        screen,
        (0, 255, 255),
        (cx, cy),
        int(pulse / 2),
        2
    )

    for i in range(12):
        a = angle * 2 + i * (math.pi / 6)
        x = cx + math.cos(a) * 230
        y = cy + math.sin(a) * 230
        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (int(x), int(y)),
            5
        )

    pygame.display.flip()
pygame.quit()