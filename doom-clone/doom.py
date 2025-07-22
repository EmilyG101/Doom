import pygame
import math

WIDTH, HEIGHT = 640, 480
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = 3 * DIST * 40
SCALE = WIDTH // NUM_RAYS

MAP = [
    "########",
    "#......#",
    "#..##..#",
    "#......#",
    "#......#",
    "#..#...#",
    "#......#",
    "########",
]

TILE = 64
MAP_WIDTH = len(MAP[0]) * TILE
MAP_HEIGHT = len(MAP) * TILE

def mapping(x, y):
    return int(x // TILE), int(y // TILE)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player_x, player_y = TILE + TILE//2, TILE + TILE//2
player_angle = 0

# Create a simple humanoid enemy sprite on transparent surface
enemy_img = pygame.Surface((40, 60), pygame.SRCALPHA)
# Draw head
pygame.draw.circle(enemy_img, (255, 220, 177), (20, 12), 10)
# Draw body
pygame.draw.rect(enemy_img, (0, 0, 255), (10, 22, 20, 30))
# Draw legs
pygame.draw.rect(enemy_img, (0, 0, 180), (10, 52, 8, 8))
pygame.draw.rect(enemy_img, (0, 0, 180), (22, 52, 8, 8))

enemy_pos = [5.5 * TILE, 5.5 * TILE]
enemy_alive = True

bullet_cooldown = 0

gun_img = pygame.Surface((100, 50))
gun_img.fill((100, 100, 100))  # Gray rectangle for placeholder weapon

# List of bullets: each bullet is a dict with x, y, angle
bullets = []

def draw_rays():
    cur_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        sin_a = math.sin(cur_angle)
        cos_a = math.cos(cur_angle)
        for depth in range(MAX_DEPTH):
            target_x = player_x + depth * cos_a
            target_y = player_y + depth * sin_a
            i, j = mapping(target_x, target_y)
            if MAP[j][i] == '#':
                depth *= math.cos(player_angle - cur_angle)
                proj_height = PROJ_COEFF / (depth + 0.0001)
                color = 255 / (1 + depth * depth * 0.0001)
                pygame.draw.rect(screen, (color, color, color), (ray * SCALE, HEIGHT // 2 - proj_height // 2, SCALE, proj_height))
                break
        cur_angle += DELTA_ANGLE

def movement():
    global player_x, player_y, player_angle
    keys = pygame.key.get_pressed()
    speed = 3
    angle_speed = 0.03
    if keys[pygame.K_w]:
        player_x += speed * math.cos(player_angle)
        player_y += speed * math.sin(player_angle)
    if keys[pygame.K_s]:
        player_x -= speed * math.cos(player_angle)
        player_y -= speed * math.sin(player_angle)
    if keys[pygame.K_a]:
        player_angle -= angle_speed
    if keys[pygame.K_d]:
        player_angle += angle_speed

def draw_enemy():
    global enemy_alive
    if not enemy_alive:
        return

    dx = enemy_pos[0] - player_x
    dy = enemy_pos[1] - player_y
    distance = math.hypot(dx, dy)

    angle_to_enemy = math.atan2(dy, dx)
    angle_diff = angle_to_enemy - player_angle

    if -HALF_FOV < angle_diff < HALF_FOV and distance > 30:
        proj_height = PROJ_COEFF / (distance + 0.0001)
        x = WIDTH // 2 + math.tan(angle_diff) * DIST - enemy_img.get_width() // 2
        y = HEIGHT // 2 - proj_height // 2
        scaled_enemy = pygame.transform.scale(enemy_img, (enemy_img.get_width(), int(proj_height)))
        screen.blit(scaled_enemy, (x, y))

def check_bullet_hit(bullet):
    global enemy_alive
    if not enemy_alive:
        return False
    dx = enemy_pos[0] - bullet['x']
    dy = enemy_pos[1] - bullet['y']
    distance = math.hypot(dx, dy)
    if distance < 20:  # hit radius
        enemy_alive = False
        print("Enemy hit by bullet!")
        return True
    return False

def update_bullets():
    # Move bullets forward and draw them
    speed = 10
    for bullet in bullets[:]:
        bullet['x'] += speed * math.cos(bullet['angle'])
        bullet['y'] += speed * math.sin(bullet['angle'])
        # Draw bullet as small circle
        pygame.draw.circle(screen, (255, 255, 0), (int(bullet['x']), int(bullet['y'])), 5)
        # Check collision with enemy
        if check_bullet_hit(bullet):
            bullets.remove(bullet)
        # Remove bullets outside map bounds
        elif bullet['x'] < 0 or bullet['x'] > MAP_WIDTH or bullet['y'] < 0 or bullet['y'] > MAP_HEIGHT:
            bullets.remove(bullet)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    screen.fill((0, 0, 0))
    movement()
    draw_rays()
    draw_enemy()

    keys = pygame.key.get_pressed()
    if bullet_cooldown > 0:
        bullet_cooldown -= 1
    if keys[pygame.K_SPACE] and bullet_cooldown == 0:
        # Spawn a bullet at player pos with player angle
        bullets.append({'x': player_x, 'y': player_y, 'angle': player_angle})
        bullet_cooldown = 20  # cooldown frames

    update_bullets()

    screen.blit(gun_img, (WIDTH // 2 - 50, HEIGHT - 60))
    pygame.display.flip()
    clock.tick(60)
