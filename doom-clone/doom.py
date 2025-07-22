# doom.py
import pygame
import math

enemy_img = pygame.Surface((40, 60))
enemy_img.fill((255, 0, 0))  # Red enemy placeholder

bullet_cooldown = 0
enemy_pos = [5.5 * TILE, 5.5 * TILE]
enemy_alive = True


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
        
def check_shot():
    global enemy_alive
    if not enemy_alive:
        return
    dx = enemy_pos[0] - player_x
    dy = enemy_pos[1] - player_y
    angle_to_enemy = math.atan2(dy, dx)
    distance = math.hypot(dx, dy)

    if distance < 800 and abs(angle_to_enemy - player_angle) < 0.1:
        enemy_alive = False
        print("Enemy hit!")

    gun_img = pygame.Surface((100, 50))
    gun_img.fill((100, 100, 100))  # Gray rectangle for placeholder weapon


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    
    screen.fill((0, 0, 0))
    movement()
    draw_rays()
    draw_enemy()

    keys = pygame.key.get_pressed()
    global bullet_cooldown
    if bullet_cooldown > 0:
        bullet_cooldown -= 1
    if keys[pygame.K_SPACE] and bullet_cooldown == 0:
        check_shot()
        bullet_cooldown = 20  # Short cooldown between shots
        screen.blit(gun_img, (WIDTH//2 - 50, HEIGHT - 60))
    pygame.display.flip()
    clock.tick(60)

