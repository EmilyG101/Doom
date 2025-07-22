# doom.py
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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    
    screen.fill((0, 0, 0))
    movement()
    draw_rays()
    pygame.display.flip()
    clock.tick(60)

