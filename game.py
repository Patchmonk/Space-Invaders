import math
import random
import pygame
from pygame import mixer

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 4
ENEMY_DROP = 40
NUM_ENEMIES = 6
MAX_BULLETS = 5  # Maximum number of bullets allowed on the screen

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader")

# Load assets from the "assets" folder
try:
    # Images
    background = pygame.image.load('assets/images/background.png')
    icon = pygame.image.load('assets/images/ufo.png')
    playerImg = pygame.image.load('assets/images/player.png')
    enemyImg = pygame.image.load('assets/images/enemy.png')
    bulletImg = pygame.image.load('assets/images/bullet.png')

    # Validate image sizes
    if enemyImg.get_width() == 0 or enemyImg.get_height() == 0:
        raise ValueError("Enemy image is invalid or empty.")

    # Music
    mixer.music.load("assets/music/background.wav")
except Exception as e:
    print(f"Error loading assets: {e}")
    pygame.quit()
    exit()

mixer.music.play(-1)  # Loop background music
pygame.display.set_icon(icon)

# Fonts
font = pygame.font.Font('assets/fonts/SuperSense.ttf', 32)
over_font = pygame.font.Font('assets/fonts/SuperSense.ttf', 64)

# Game State
class GameState:
    def __init__(self):
        self.score_value = 0
        self.playerX = 370
        self.playerY = 480
        self.playerX_change = 0
        self.bullets = []  # List to track active bullets
        self.enemies = []
        self.game_over = False

    def reset(self):
        self.score_value = 0
        self.playerX = 370
        self.playerY = 480
        self.playerX_change = 0
        self.bullets.clear()  # Clear bullets
        self.enemies.clear()  # Clear enemies
        for _ in range(NUM_ENEMIES):  # Repopulate enemies
            self.enemies.append({
                'x': random.randint(0, 735),
                'y': random.randint(50, 150),
                'x_change': ENEMY_SPEED,
                'y_change': ENEMY_DROP
            })
        self.game_over = False

# Initialize game state
game_state = GameState()
game_state.reset()  # Populate enemies at the start

# Functions
def show_score(x, y):
    score = font.render(f"Score : {game_state.score_value}", True, WHITE)
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, WHITE)
    screen.blit(over_text, (200, 250))

def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    button_text = font.render(text, True, WHITE)
    text_rect = button_text.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(button_text, text_rect)

def restart_game():
    game_state.reset()

def quit_game():
    pygame.quit()
    exit()

def player(x, y):
    screen.blit(playerImg, (x, y))

def draw_enemy(x, y):
    screen.blit(enemyImg, (x, y))

def fire_bullet(x, y):
    screen.blit(bulletImg, (x + 16, y + 10))

def is_collision(enemyX, enemyY, bulletX, bulletY):
    distance = math.hypot(enemyX - bulletX, enemyY - bulletY)
    return distance < 27

# Key State Tracking
key_states = {
    pygame.K_LEFT: False,
    pygame.K_RIGHT: False
}

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)  # Clear screen
    screen.blit(background, (0, 0))  # Draw background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in key_states:
                key_states[event.key] = True
            if event.key == pygame.K_SPACE:
                # Fire a new bullet if the maximum number of bullets hasn't been reached
                if len(game_state.bullets) < MAX_BULLETS:
                    game_state.bullets.append({'x': game_state.playerX, 'y': game_state.playerY})
        if event.type == pygame.KEYUP:
            if event.key in key_states:
                key_states[event.key] = False

    # Update player movement based on key states
    game_state.playerX_change = 0
    if key_states[pygame.K_LEFT]:
        game_state.playerX_change -= PLAYER_SPEED
    if key_states[pygame.K_RIGHT]:
        game_state.playerX_change += PLAYER_SPEED

    # Player movement
    game_state.playerX += game_state.playerX_change
    game_state.playerX = max(0, min(game_state.playerX, SCREEN_WIDTH - 64))  # Boundary check

    # Bullet movement
    for bullet in game_state.bullets[:]:  # Iterate over a copy of the list
        bullet['y'] -= BULLET_SPEED
        if bullet['y'] <= 0:
            game_state.bullets.remove(bullet)  # Remove bullet if it goes off-screen
        else:
            fire_bullet(bullet['x'], bullet['y'])

    # Enemy movement and collision
    for enemy_data in game_state.enemies[:]:  # Iterate over a copy of the list
        if game_state.game_over:
            break

        # Move the enemy horizontally
        enemy_data['x'] += enemy_data['x_change']

        # Reverse direction and move down when hitting boundaries
        if enemy_data['x'] <= 0 or enemy_data['x'] >= SCREEN_WIDTH - 64:
            enemy_data['x_change'] *= -1
            enemy_data['y'] += enemy_data['y_change']

        # Check collisions with bullets
        for bullet in game_state.bullets[:]:
            if is_collision(enemy_data['x'], enemy_data['y'], bullet['x'], bullet['y']):
                game_state.score_value += 1
                game_state.bullets.remove(bullet)  # Remove the bullet
                enemy_data['x'] = random.randint(0, 735)
                enemy_data['y'] = random.randint(50, 150)
                break

        # Draw the enemy
        draw_enemy(enemy_data['x'], enemy_data['y'])

        # Game over condition
        if enemy_data['y'] > 440:
            game_state.game_over = True
            break

    if game_state.game_over:
        game_over_text()
        draw_button("Restart", 300, 400, 200, 50, (0, 255, 0), (0, 200, 0), restart_game)
        draw_button("Quit", 300, 470, 200, 50, (255, 0, 0), (200, 0, 0), quit_game)
    else:
        # Draw player and score
        player(game_state.playerX, game_state.playerY)
        show_score(10, 10)

    pygame.display.update()
    clock.tick(60)  # Limit frame rate to 60 FPS

pygame.quit()