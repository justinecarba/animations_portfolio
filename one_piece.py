
"""
GEAR 5 ENERGY EFFECT
=====================
A rare, amazing Gear-5-inspired energy animation built entirely with
procedural graphics (particles, glowing rings, shockwaves, lightning
arcs, and screen-flash effects) — no external images required.

Controls:
  SPACE - trigger a huge "Awakening" burst
  ESC   - quit

Requires: pygame  ->  pip install pygame
Run:      python gear5_energy_effect.py
"""

import pygame
import random
import math
import sys

# ----------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------
pygame.init()
WIDTH, HEIGHT = 900, 700
CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gear 5 Energy Effect")
clock = pygame.time.Clock()

# Glow surface uses per-pixel alpha and additive blending for that
# "radiant white sun-god energy" look.
glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

WHITE = (255, 255, 255)
GOLD = (255, 230, 150)
SKY = (200, 230, 255)
CYAN = (110, 220, 255)
ORANGE = (255, 160, 80)
RED = (255, 70, 70)
CRIMSON = (190, 25, 40)
MAGENTA = (255, 100, 200)

# ----------------------------------------------------------------------
# PARTICLE SYSTEMS
# ----------------------------------------------------------------------
class Particle:
    """Floating energy motes that drift outward and fade."""
    def __init__(self):
        self.reset()

    def reset(self):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.5, 3.0)
        self.x = CENTER[0] + random.uniform(-30, 30)
        self.y = CENTER[1] + random.uniform(-30, 30)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.uniform(1.5, 4)
        self.life = random.uniform(60, 160)
        self.age = 0
        self.color = random.choice([WHITE, GOLD, SKY])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.01  # slight upward drift, like embers of light
        self.age += 1
        if self.age > self.life or not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
            self.reset()

    def draw(self, surf):
        t = 1 - (self.age / self.life)
        alpha = max(0, min(255, int(255 * t)))
        r = max(1, int(self.radius * t * 2))
        pygame.draw.circle(surf, (*self.color, alpha), (int(self.x), int(self.y)), r)


class Ring:
    """Expanding shockwave rings, like bursts of Haki/Awakening energy."""
    def __init__(self, delay=0, thick=3, max_r=380, color=WHITE):
        self.delay = delay
        self.timer = 0
        self.radius = 0
        self.thick = thick
        self.max_r = max_r
        self.color = color
        self.active = False

    def update(self):
        self.timer += 1
        if self.timer > self.delay:
            self.active = True
            self.radius += 4.5
            if self.radius > self.max_r:
                self.radius = 0
                self.timer = 0
                self.delay = random.randint(0, 20)
                self.active = False

    def draw(self, surf):
        if not self.active:
            return
        t = self.radius / self.max_r
        alpha = max(0, int(255 * (1 - t)))
        pygame.draw.circle(surf, (*self.color, alpha), CENTER, int(self.radius), self.thick)


class Bolt:
    """Jagged lightning-like energy arcs radiating from the core."""
    def __init__(self, color=WHITE, min_len=60, max_len=220):
        self.color = color
        self.min_len = min_len
        self.max_len = max_len
        self.reset()

    def reset(self):
        self.angle = random.uniform(0, math.tau)
        self.length = random.uniform(self.min_len, self.max_len)
        self.segments = random.randint(4, 7)
        self.life = random.randint(6, 14)
        self.age = 0
        self.width = random.randint(1, 3)

    def points(self):
        pts = [CENTER]
        step = self.length / self.segments
        cur_angle = self.angle
        x, y = CENTER
        for i in range(self.segments):
            cur_angle += random.uniform(-0.4, 0.4)
            x += math.cos(cur_angle) * step
            y += math.sin(cur_angle) * step
            pts.append((x, y))
        return pts

    def update(self):
        self.age += 1
        if self.age > self.life:
            self.reset()

    def draw(self, surf):
        t = 1 - (self.age / self.life)
        alpha = max(0, int(255 * t))
        pts = self.points()
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, (*self.color, alpha), pts[i], pts[i + 1], self.width)


# ----------------------------------------------------------------------
# INSTANTIATE EFFECTS
# ----------------------------------------------------------------------
particles = [Particle() for _ in range(180)]
rings = [Ring(delay=i * 15, thick=random.choice([2, 3, 4]),
              max_r=random.randint(200, 420),
              color=random.choice([WHITE, GOLD, SKY])) for i in range(6)]
bolts = [Bolt(color=random.choice([WHITE, GOLD, CYAN, ORANGE, MAGENTA])) for _ in range(14)]
haki_bolts = [Bolt(color=random.choice([RED, CRIMSON, ORANGE, MAGENTA]), min_len=90, max_len=260) for _ in range(18)]

frame = 0
flash_timer = 0
shake_timer = 0
haki_timer = 0


def draw_core(surf, t, haki_strength=0):
    """Pulsing radiant core, like a small sun — the heart of the effect."""
    pulse = 40 + 14 * math.sin(t * 0.08)
    core_colors = [WHITE, GOLD, CYAN, MAGENTA, ORANGE]
    for i in range(9, 0, -1):
        r = int(pulse + i * 12)
        alpha = int(35 - i * 3 + haki_strength * 1.6)
        color = core_colors[(i + t // 15) % len(core_colors)]
        pygame.draw.circle(surf, (*color, max(alpha, 0)), CENTER, r)
    pygame.draw.circle(surf, WHITE, CENTER, int(pulse * 0.5))
    pygame.draw.circle(surf, GOLD, CENTER, int(pulse * 0.5), 3)
    if haki_strength > 0:
        for i in range(3):
            radius = int(40 + i * 22 + haki_strength * 1.8)
            alpha = int(50 + haki_strength * 2)
            pygame.draw.circle(surf, (*RED, max(alpha, 0)), CENTER, radius, 2)


def draw_clouds(surf, t):
    """Soft drifting cloud-like puffs, evoking the character's iconic look."""
    for i in range(6):
        ang = t * 0.01 + i * (math.tau / 6)
        cx = CENTER[0] + math.cos(ang) * 250
        cy = CENTER[1] + math.sin(ang) * 160
        r = 46 + 12 * math.sin(t * 0.05 + i)
        color = random.choice([SKY, CYAN, MAGENTA, GOLD, ORANGE])
        pygame.draw.circle(surf, (*color, 46), (int(cx), int(cy)), int(r))


def draw_haki_lightning(surf, t, strength):
    """Add a red Haki lightning overlay during transformations."""
    if strength <= 0:
        return
    for i in range(18):
        angle = t * 0.09 + i * (math.tau / 18)
        x1 = CENTER[0] + math.cos(angle) * (80 + strength * 1.8)
        y1 = CENTER[1] + math.sin(angle) * (55 + strength * 1.3)
        x2 = CENTER[0] + math.cos(angle + random.uniform(-0.9, 0.9)) * (150 + strength * 4)
        y2 = CENTER[1] + math.sin(angle + random.uniform(-0.9, 0.9)) * (130 + strength * 3)
        color = random.choice([RED, CRIMSON, ORANGE, MAGENTA])
        alpha = int(100 + strength * 4)
        pygame.draw.line(surf, (*color, max(0, min(255, alpha))), (int(x1), int(y1)), (int(x2), int(y2)), 2 + int(strength * 0.2))

    for i in range(5):
        radius = 55 + i * 30 + strength * 2
        alpha = int(35 + strength * 1.6)
        pygame.draw.circle(surf, (*RED, max(0, min(255, alpha))), CENTER, int(radius), 2)


# ----------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                flash_timer = 12
                shake_timer = 18
                haki_timer = 24
                for b in bolts:
                    b.age = b.life  # force-refresh all bolts at once
                for b in haki_bolts:
                    b.age = b.life
                for r in rings:
                    r.radius = 0
                    r.timer = r.delay + 1
                    r.active = True

    frame += 1
    if haki_timer > 0:
        haki_timer -= 1

    # Screen shake offset for extra impact during bursts
    offset = (0, 0)
    if shake_timer > 0:
        offset = (random.randint(-6, 6), random.randint(-6, 6))
        shake_timer -= 1

    # Fade the background slightly each frame for smooth motion trails
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.set_alpha(35)
    fade.fill((5, 8, 20))
    screen.blit(fade, (0, 0))

    glow_surface.fill((0, 0, 0, 0))

    draw_clouds(glow_surface, frame)

    for r in rings:
        r.update()
        r.draw(glow_surface)

    for b in bolts:
        b.update()
        b.draw(glow_surface)

    if haki_timer > 0:
        for b in haki_bolts:
            b.update()
            b.draw(glow_surface)
        draw_haki_lightning(glow_surface, frame, haki_timer)

    for p in particles:
        p.update()
        p.draw(glow_surface)

    draw_core(glow_surface, frame, haki_strength=haki_timer)

    screen.blit(glow_surface, offset, special_flags=pygame.BLEND_ADD)

    # Full-screen flash effect on burst trigger
    if flash_timer > 0:
        flash = pygame.Surface((WIDTH, HEIGHT))
        flash.set_alpha(int(255 * (flash_timer / 12)))
        flash.fill(WHITE)
        screen.blit(flash, (0, 0))
        flash_timer -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()