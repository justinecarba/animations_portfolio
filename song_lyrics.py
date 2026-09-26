
import math
import random
import wave
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).resolve().parent
MUSIC_PATH = BASE_DIR / "panaginip.mp3"
FALLBACK_MUSIC_PATH = BASE_DIR / "panaginip_generated.wav"
LYRICS_PATH = BASE_DIR / "lyrics.txt"

DEFAULT_LYRICS = """0.0|Panaginip
3.5|Sa dilim ng gabi
7.0|Ako'y lumuluha
10.5|Sa bawat pag-iyak
14.0|Hinahanap ka pa rin
18.0|Nang mahinang awit
22.0|Parang bumubuhos ang ulan
26.0|At tinatawag ka ng puso
30.0|Kahit hindi kita makita
34.0|Sa panaginip, nandiyan ka
38.0|Hanggang sa umaga
42.0|Babalik ang iyong ngiti
46.0|At muling sisikat ang araw
50.0|Sa puso ko, ikaw parin
54.0|Ang huling tinitibok
58.0|Ng bawat pag-asa
62.0|Hanggang sa wakas ng gabi
"""

# ==========================================
# INITIALIZATION
# ==========================================

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Audio device unavailable; continuing without sound output.")

WIDTH = 1200
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PANAGINIP - Rainy Night")

clock = pygame.time.Clock()


def write_default_lyrics():
    if not LYRICS_PATH.exists():
        LYRICS_PATH.write_text(DEFAULT_LYRICS, encoding="utf-8")


def generate_fallback_track(path: Path):
    sample_rate = 22050
    total_seconds = 70
    total_samples = sample_rate * total_seconds
    melody = [220.0, 246.94, 293.66, 329.63, 293.66, 246.94, 196.0, 220.0]
    frames = bytearray()

    for i in range(total_samples):
        t = i / sample_rate
        note_index = int(t * 2) % len(melody)
        base_freq = melody[note_index]
        envelope = 0.8 if (i % 2205) < 1102 else 0.35
        tone = math.sin(2 * math.pi * base_freq * t)
        tone += 0.45 * math.sin(2 * math.pi * (base_freq * 0.5) * t)
        sample = int(max(-1.0, min(1.0, tone * envelope)) * 32767)
        frames.extend(sample.to_bytes(2, byteorder="little", signed=True))

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


def resolve_music_file():
    if MUSIC_PATH.exists():
        return MUSIC_PATH

    if not FALLBACK_MUSIC_PATH.exists():
        generate_fallback_track(FALLBACK_MUSIC_PATH)

    return FALLBACK_MUSIC_PATH


write_default_lyrics()

# ==========================================
# MUSIC
# ==========================================

music_file = resolve_music_file()
try:
    pygame.mixer.music.load(str(music_file))
    pygame.mixer.music.play(-1)
except pygame.error:
    if not FALLBACK_MUSIC_PATH.exists():
        generate_fallback_track(FALLBACK_MUSIC_PATH)
    pygame.mixer.music.load(str(FALLBACK_MUSIC_PATH))
    pygame.mixer.music.play(-1)

# ==========================================
# FONTS
# ==========================================

try:
    title_font = pygame.font.SysFont("arial", 36, bold=True)
    lyrics_font = pygame.font.SysFont("arial", 42, bold=True)
    small_font = pygame.font.SysFont("arial", 18)
except Exception:
    title_font = pygame.font.Font(None, 36)
    lyrics_font = pygame.font.Font(None, 42)
    small_font = pygame.font.Font(None, 18)

# ==========================================
# RAIN
# ==========================================

rain = []

for i in range(500):

    rain.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(-HEIGHT, HEIGHT),
        "speed": random.uniform(8, 15),
        "length": random.randint(12, 28)
    })

# ==========================================
# BACKGROUND STARS / LIGHTS
# ==========================================

lights = []

for i in range(80):

    lights.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(100, HEIGHT - 150),
        "size": random.randint(2, 5),
        "brightness": random.randint(50, 150)
    })

# ==========================================
# BUILDINGS
# ==========================================

buildings = []

x = 0

while x < WIDTH:

    width = random.randint(80, 160)
    height = random.randint(180, 400)

    buildings.append({
        "x": x,
        "width": width,
        "height": height
    })

    x += width + random.randint(10, 25)

# ==========================================
# BUILDING WINDOWS
# ==========================================

windows = []

for building in buildings:

    start_x = building["x"]
    start_y = HEIGHT - building["height"]

    for wx in range(
        start_x + 20,
        start_x + building["width"] - 10,
        30
    ):

        for wy in range(
            start_y + 30,
            HEIGHT - 140,
            40
        ):

            if random.random() < 0.30:

                windows.append({
                    "x": wx,
                    "y": wy,
                    "brightness": random.randint(80, 180)
                })

# ==========================================
# LYRICS
# ==========================================

def read_lyrics():
    lyrics = []

    try:
        with LYRICS_PATH.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if "|" not in line:
                    continue
                timestamp, text = line.split("|", 1)
                try:
                    lyrics.append((float(timestamp), text.strip()))
                except ValueError:
                    continue
    except FileNotFoundError:
        write_default_lyrics()
        return read_lyrics()

    return lyrics


lyrics = read_lyrics()

# ==========================================
# GET CURRENT LYRIC
# ==========================================

def get_current_lyric(current_time):

    current = ""

    for timestamp, text in lyrics:

        if current_time >= timestamp:

            current = text

        else:

            break

    return current


# ==========================================
# BACKGROUND
# ==========================================

def draw_background():

    # Gradient night sky

    for y in range(HEIGHT):

        ratio = y / HEIGHT

        r = int(4 + ratio * 8)
        g = int(7 + ratio * 12)
        b = int(18 + ratio * 25)

        pygame.draw.line(
            screen,
            (r, g, b),
            (0, y),
            (WIDTH, y)
        )


# ==========================================
# CITY
# ==========================================

def draw_city():

    # Buildings

    for building in buildings:

        pygame.draw.rect(
            screen,
            (10, 15, 25),
            (
                building["x"],
                HEIGHT - building["height"],
                building["width"],
                building["height"]
            )
        )

    # Windows

    for window in windows:

        color = (
            window["brightness"],
            window["brightness"] - 20,
            70
        )

        pygame.draw.rect(
            screen,
            color,
            (
                window["x"],
                window["y"],
                8,
                12
            )
        )


# ==========================================
# CITY LIGHTS
# ==========================================

def draw_lights():

    for light in lights:

        brightness = light["brightness"]

        color = (
            brightness,
            brightness,
            brightness + 20
        )

        pygame.draw.circle(
            screen,
            color,
            (
                light["x"],
                light["y"]
            ),
            light["size"]
        )


# ==========================================
# RAIN
# ==========================================

def draw_rain():

    for drop in rain:

        # Move rain

        drop["y"] += drop["speed"]

        # Reset when rain reaches bottom

        if drop["y"] > HEIGHT:

            drop["y"] = random.randint(
                -100,
                -20
            )

            drop["x"] = random.randint(
                0,
                WIDTH
            )

        # Draw rain

        pygame.draw.line(
            screen,
            (110, 150, 190),
            (
                drop["x"],
                drop["y"]
            ),
            (
                drop["x"] - 2,
                drop["y"] + drop["length"]
            ),
            1
        )


# ==========================================
# PUDDLE
# ==========================================

def draw_puddle():

    pygame.draw.rect(
        screen,
        (8, 12, 20),
        (
            0,
            HEIGHT - 120,
            WIDTH,
            120
        )
    )

    # Horizontal reflections

    for i in range(20):

        y = HEIGHT - 110 + i * 5

        pygame.draw.line(
            screen,
            (25, 35, 50),
            (0, y),
            (WIDTH, y),
            1
        )


# ==========================================
# STREET LIGHT
# ==========================================

def draw_street_light():

    lamp_x = 950
    lamp_y = 300

    # Glow

    for radius in range(
        180,
        20,
        -10
    ):

        alpha = int(
            3 + (180 - radius) * 0.25
        )

        glow = pygame.Surface(
            (
                radius * 2,
                radius * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (255, 220, 100, alpha),
            (
                radius,
                radius
            ),
            radius
        )

        screen.blit(
            glow,
            (
                lamp_x - radius,
                lamp_y - radius
            )
        )

    # Pole

    pygame.draw.line(
        screen,
        (35, 35, 40),
        (
            lamp_x,
            lamp_y
        ),
        (
            lamp_x,
            HEIGHT
        ),
        7
    )

    # Lamp

    pygame.draw.circle(
        screen,
        (255, 220, 100),
        (
            lamp_x,
            lamp_y
        ),
        12
    )


# ==========================================
# LYRICS
# ==========================================

def draw_lyrics(current_time):

    lyric = get_current_lyric(
        current_time
    )

    if lyric == "":
        return

    # Shadow

    shadow = lyrics_font.render(
        lyric,
        True,
        (0, 0, 0)
    )

    shadow_rect = shadow.get_rect(
        center=(
            WIDTH // 2 + 3,
            HEIGHT - 180 + 3
        )
    )

    screen.blit(
        shadow,
        shadow_rect
    )

    # Main lyric

    text = lyrics_font.render(
        lyric,
        True,
        (235, 240, 255)
    )

    text_rect = text.get_rect(
        center=(
            WIDTH // 2,
            HEIGHT - 180
        )
    )

    screen.blit(
        text,
        text_rect
    )


# ==========================================
# MAIN LOOP
# ==========================================

running = True

while running:

    clock.tick(60)

    # ======================================
    # EVENTS
    # ======================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # ESC = exit

            if event.key == pygame.K_ESCAPE:

                running = False

            # SPACE = pause / resume

            if event.key == pygame.K_SPACE:

                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():

                    pygame.mixer.music.pause()

                elif pygame.mixer.get_init():

                    pygame.mixer.music.unpause()

    # ======================================
    # SONG TIME
    # ======================================

    if pygame.mixer.get_init():
        song_time = pygame.mixer.music.get_pos() / 1000.0
    else:
        song_time = 0.0

    # ======================================
    # DRAW EVERYTHING
    # ======================================

    draw_background()

    draw_city()

    draw_lights()

    draw_puddle()

    draw_street_light()

    draw_rain()

    draw_lyrics(song_time)

    # ======================================
    # TITLE
    # ======================================

    title = title_font.render(
        "PANAGINIP",
        True,
        (180, 210, 255)
    )

    screen.blit(
        title,
        (35, 30)
    )

    artist = small_font.render(
        "nicole",
        True,
        (150, 170, 190)
    )

    screen.blit(
        artist,
        (38, 72)
    )

    # ======================================
    # MUSIC TIME
    # ======================================

    timer = small_font.render(
        f"{song_time:.1f}s",
        True,
        (150, 160, 175)
    )

    screen.blit(
        timer,
        (WIDTH - 90, 30)
    )

    # ======================================
    # CONTROLS
    # ======================================

    controls = small_font.render(
        "SPACE = Pause / Resume    ESC = Exit",
        True,
        (130, 140, 155)
    )

    screen.blit(
        controls,
        (
            35,
            HEIGHT - 35
        )
    )

    # ======================================
    # UPDATE SCREEN
    # ======================================

    pygame.display.flip()


# ==========================================
# EXIT
# ==========================================

if pygame.mixer.get_init():
    pygame.mixer.music.stop()

pygame.quit()