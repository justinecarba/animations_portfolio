import os
import random
import sys

import pygame

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Arcade")

BLACK = (10, 10, 16)
DARK = (20, 28, 20)
GRID = (36, 36, 36)
GREEN = (86, 227, 117)
DARK_GREEN = (35, 150, 65)
RED = (255, 85, 85)
WHITE = (255, 255, 255)
GOLD = (255, 220, 90)
GRAY = (180, 180, 180)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 22)

SAVE_PATH = os.path.join(os.path.dirname(__file__), "snake_best_score.txt")


def load_best_score():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as file:
            return max(0, int(file.read().strip() or 0))
    except (FileNotFoundError, ValueError):
        return 0


def save_best_score(score):
    with open(SAVE_PATH, "w", encoding="utf-8") as file:
        file.write(str(score))


def create_food(snake):
    """Create food in a position that is not occupied by the snake."""
    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        if (x, y) not in snake:
            return (x, y)


def reset_game():
    """Reset the game state."""
    snake = [
        (WIDTH // 2, HEIGHT // 2),
        (WIDTH // 2 - CELL_SIZE, HEIGHT // 2),
        (WIDTH // 2 - CELL_SIZE * 2, HEIGHT // 2),
    ]
    direction = (CELL_SIZE, 0)
    food = create_food(snake)
    score = 0
    speed = 7
    return snake, direction, food, score, speed


def draw_grid():
    """Draw a background grid."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, HEIGHT), 2)


def draw_snake(snake):
    """Draw the snake body."""
    for index, segment in enumerate(snake):
        color = GREEN if index == 0 else DARK_GREEN
        rect = pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=6)

        if index == 0:
            eye_offset_x = 5
            eye_offset_y = 5
            eye_color = BLACK

            pygame.draw.circle(screen, eye_color, (segment[0] + 6, segment[1] + 7), 2)
            pygame.draw.circle(screen, eye_color, (segment[0] + 14, segment[1] + 7), 2)

            if direction[0] == 0:
                eye_offset_x = 6
                eye_offset_y = 4

            if direction[0] > 0:
                pygame.draw.circle(screen, eye_color, (segment[0] + 14, segment[1] + 7), 2)
            elif direction[0] < 0:
                pygame.draw.circle(screen, eye_color, (segment[0] + 6, segment[1] + 7), 2)
            elif direction[1] > 0:
                pygame.draw.circle(screen, eye_color, (segment[0] + 8, segment[1] + 13), 2)
                pygame.draw.circle(screen, eye_color, (segment[0] + 12, segment[1] + 13), 2)
            elif direction[1] < 0:
                pygame.draw.circle(screen, eye_color, (segment[0] + 8, segment[1] + 3), 2)
                pygame.draw.circle(screen, eye_color, (segment[0] + 12, segment[1] + 3), 2)


def draw_food(food):
    """Draw the food with a pulsing look."""
    center_x = food[0] + CELL_SIZE // 2
    center_y = food[1] + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - 3
    pygame.draw.circle(screen, RED, (center_x, center_y), radius)
    pygame.draw.circle(screen, WHITE, (center_x - 3, center_y - 4), 3)


def draw_hud(score, best_score, speed):
    """Show score and best score."""
    score_text = font.render(f"Score: {score}", True, WHITE)
    best_text = font.render(f"Best: {best_score}", True, GOLD)
    speed_text = small_font.render(f"Speed {speed}", True, GRAY)

    screen.blit(score_text, (14, 10))
    screen.blit(best_text, (WIDTH - best_text.get_width() - 14, 10))
    screen.blit(speed_text, (WIDTH // 2 - speed_text.get_width() // 2, 10))


def draw_menu(best_score):
    screen.fill(BLACK)
    draw_grid()

    title = big_font.render("SNAKE", True, GREEN)
    subtitle = font.render("ARCADE", True, WHITE)
    hint = font.render("Press any arrow key to start", True, WHITE)
    best = font.render(f"Best Score: {best_score}", True, GOLD)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 220))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 320))
    screen.blit(best, (WIDTH // 2 - best.get_width() // 2, 370))

    pygame.display.flip()


def game_over_screen(score, best_score):
    """Display the game-over screen."""
    screen.fill(BLACK)
    draw_grid()

    game_over_text = big_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    best_text = font.render(f"Best: {best_score}", True, GOLD)
    restart_text = font.render("Press R to restart • Q to quit • P to pause", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 140))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 240))
    screen.blit(best_text, (WIDTH // 2 - best_text.get_width() // 2, 280))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 350))
    pygame.display.flip()


best_score = load_best_score()
snake, direction, food, score, speed = reset_game()
state = "playing"
paused = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                if state == "menu":
                    state = "playing"

                move_map = {
                    pygame.K_UP: (0, -CELL_SIZE),
                    pygame.K_DOWN: (0, CELL_SIZE),
                    pygame.K_LEFT: (-CELL_SIZE, 0),
                    pygame.K_RIGHT: (CELL_SIZE, 0),
                }
                next_direction = move_map[event.key]

                if not (
                    next_direction[0] == -direction[0] and next_direction[1] == -direction[1]
                ):
                    direction = next_direction

            elif event.key == pygame.K_p:
                if state == "playing":
                    paused = not paused

            elif event.key == pygame.K_r:
                if state == "game_over":
                    snake, direction, food, score, speed = reset_game()
                    state = "playing"
                    paused = False

            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    if state == "playing" and not paused:
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        wall_hit = (
            new_head[0] < 0
            or new_head[0] >= WIDTH
            or new_head[1] < 0
            or new_head[1] >= HEIGHT
        )
        body_hit = new_head in snake[:-1]

        if wall_hit or body_hit:
            state = "game_over"
            best_score = max(best_score, score)
            save_best_score(best_score)
        else:
            snake.insert(0, new_head)
            if new_head == food:
                score += 1
                best_score = max(best_score, score)
                save_best_score(best_score)
                speed = min(14, 7 + score // 3)
                food = create_food(snake)
            else:
                snake.pop()

    screen.fill(BLACK)
    draw_grid()

    if state == "menu":
        draw_menu(best_score)
    elif state == "playing":
        draw_snake(snake)
        draw_food(food)
        draw_hud(score, best_score, speed)
        if paused:
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 20))
    elif state == "game_over":
        draw_snake(snake)
        draw_food(food)
        draw_hud(score, best_score, speed)
        game_over_screen(score, best_score)

    pygame.display.flip()
    clock.tick(60)