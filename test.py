
import math
import random
import pygame

WIDTH, HEIGHT = 2000, 1200
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60
SCALE = 20

WORDS = ["love coding", "Love Coding", "LOVE Coding"]
CENTER_TEXT = " Love You "

COLORS = [
    (70, 130, 180),
    (30, 144, 255),
    (0, 191, 255),
    (100, 149, 237),
    (65, 105, 225)
]


class Particle:

    def __init__(self, x, y, order, kind):
        self.x = x
        self.y = y
        self.order = order
        self.kind = kind
        self.word = random.choice(WORDS)
        self.color = random.choice(COLORS)
        self.alpha = 0
        self.flicker = random.uniform(0, math.pi * 2)
        self.font = None
        self.delay = 0
        self.size_mult = random.uniform(0.85, 1.15)


def heart_xy(t):
    x = 16 * (math.sin(t) ** 3)

    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )

    return x, -y


def to_screen(x, y):
    screen_x = x * SCALE + WIDTH / 2
    screen_y = y * SCALE + HEIGHT / 2

    return screen_x, screen_y


def build_outline_particles(n_outline, min_gap=30):
    particles = []
    placed = []

    for i in range(n_outline):

        t = (i / n_outline) * 2 * math.pi

        bx, by = heart_xy(t)
        sx, sy = to_screen(bx, by)

        if any(
            math.hypot(sx - px, sy - py) < min_gap
            for px, py in placed
        ):
            continue

        placed.append((sx, sy))

        particles.append(
            Particle(sx, sy, i, "outline")
        )

    return particles


def build_fill_particles(n_fill, min_gap=46):
    particles = []
    placed = []

    attempts = 0
    max_attempts = n_fill * 80

    while len(particles) < n_fill and attempts < max_attempts:

        attempts += 1

        t = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.0, 0.86)

        bx, by = heart_xy(t)

        px = bx * r
        py = by * r

        sx, sy = to_screen(px, py)

        if any(
            math.hypot(sx - qx, sy - qy) < min_gap
            for qx, qy in placed
        ):
            continue

        placed.append((sx, sy))

        particles.append(
            Particle(
                sx,
                sy,
                random.randint(0, 320),
                "fill"
            )
        )

    return particles


def draw_glow_text(
    glow_layer,
    screen_layer,
    font,
    word,
    color,
    x,
    y,
    alpha,
    size_mult=1.0
):

    if alpha <= 0:
        return

    if size_mult != 1.0:

        scaled_font = pygame.font.Font(
            None,
            int(font.get_height() * size_mult)
        )

        text = scaled_font.render(
            word,
            True,
            color
        )

    else:

        text = font.render(
            word,
            True,
            color
        )

    text.set_alpha(alpha)

    text_rect = text.get_rect(
        center=(x, y)
    )

    if alpha > 10:

        glow_big = pygame.transform.smoothscale(
            text,
            (
                int(text.get_width() * 2.4),
                int(text.get_height() * 2.4)
            )
        )

        glow_big.set_alpha(
            max(0, alpha // 7)
        )

        glow_rect = glow_big.get_rect(
            center=(x, y)
        )

        glow_layer.blit(
            glow_big,
            glow_rect
        )

        glow_small = pygame.transform.smoothscale(
            text,
            (
                int(text.get_width() * 1.6),
                int(text.get_height() * 1.6)
            )
        )

        glow_small.set_alpha(
            max(0, alpha // 3)
        )

        glow_rect = glow_small.get_rect(
            center=(x, y)
        )

        glow_layer.blit(
            glow_small,
            glow_rect
        )

    screen_layer.blit(
        text,
        text_rect
    )


def main():

    pygame.init()

    try:
        pygame.mixer.init()

        pygame.mixer.music.load(
            "Love_you.mp3"
        )

        pygame.mixer.music.play()

    except pygame.error:
        print("Music could not be loaded.")

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.DOUBLEBUF
    )

    pygame.display.set_caption(
        "Love Coding ❤"
    )

    clock = pygame.time.Clock()

    font_outline = pygame.font.SysFont(
        "arial",
        20,
        bold=True
    )

    font_fill = pygame.font.SysFont(
        "arial",
        17,
        bold=True
    )

    font_center = pygame.font.SysFont(
        "georgia",
        54,
        bold=True
    )

    background = pygame.Surface(
        (WIDTH, HEIGHT)
    )

    background.fill(
        BACKGROUND_COLOR
    )

    outline = build_outline_particles(
        n_outline=160
    )

    fill = build_fill_particles(
        n_fill=130
    )

    outline_span = max(
        (p.order for p in outline),
        default=0
    )

    frames_per_step = 1.6

    fill_start_frame = (
        int(outline_span * frames_per_step)
        + 30
    )

    for particle in outline:

        particle.delay = int(
            particle.order * frames_per_step
        )

    for particle in fill:

        particle.delay = (
            fill_start_frame
            + particle.order
        )

    particles = outline + fill

    for particle in particles:

        if particle.kind == "outline":
            particle.font = font_outline

        else:
            particle.font = font_fill

    glow_layer = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    text_layer = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    running = True
    frame = 0

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                running = False

        screen.blit(
            background,
            (0, 0)
        )

        glow_layer.fill(
            (0, 0, 0, 0)
        )

        text_layer.fill(
            (0, 0, 0, 0)
        )

        frame += 1

        for particle in particles:

            if (
                frame > particle.delay
                and particle.alpha < 255
            ):

                particle.alpha = min(
                    255,
                    particle.alpha
                    + 14
                    + random.randint(0, 4)
                )

            if particle.alpha >= 255:

                flick = (
                    0.75
                    + 0.25
                    * math.sin(
                        frame * 0.04
                        + particle.flicker
                    )
                )

            else:

                flick = 1.0

            alpha = int(
                particle.alpha * flick
            )

            if alpha <= 0:
                continue

            draw_glow_text(
                glow_layer,
                text_layer,
                particle.font,
                particle.word,
                particle.color,
                particle.x,
                particle.y,
                alpha,
                particle.size_mult
            )

        screen.blit(
            glow_layer,
            (0, 0)
        )

        screen.blit(
            text_layer,
            (0, 0)
        )

        center_start = (
            fill_start_frame + 200
        )

        if frame > center_start:

            progress = min(
                1.0,
                (frame - center_start) / 60
            )

            center_alpha = int(
                255
                * (
                    1
                    - math.exp(
                        -progress * 8
                    )
                )
            )

            pulse = (
                1.0
                + 0.025
                * math.sin(frame * 0.05)
            )

            center_surf = font_center.render(
                CENTER_TEXT,
                True,
                (255, 250, 245)
            )

            new_width = int(
                center_surf.get_width()
                * pulse
            )

            new_height = int(
                center_surf.get_height()
                * pulse
            )

            if (
                new_width > 0
                and new_height > 0
            ):

                center_surf = (
                    pygame.transform.smoothscale(
                        center_surf,
                        (
                            new_width,
                            new_height
                        )
                    )
                )

            center_surf.set_alpha(
                center_alpha
            )

            if center_alpha > 10:
                glow_center = (
                    pygame.transform.smoothscale(
                        center_surf,
                        (
                            int(
                                center_surf.get_width()
                                * 1.4
                            ),
                            int(
                                center_surf.get_height()
                                * 1.4
                            )
                        )
                    )
                )

                glow_center.set_alpha(
                    center_alpha // 5
                )

                glow_rect = (
                    glow_center.get_rect(
                        center=(
                            WIDTH / 2,
                            HEIGHT / 2
                        )
                    )
                )

                screen.blit(
                    glow_center,
                    glow_rect
                )

                text_rect = center_surf.get_rect(
                    center=(
                        WIDTH / 2,
                        HEIGHT / 2
                    )
                )

                screen.blit(
                    center_surf,
                    text_rect
                )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":

    try:
        main()

    except Exception as e:

        print(
            "OCURRIO UN ERROR:",
            e
        )

        import traceback

        traceback.print_exc()