import pygame
import math
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_device = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill((10, 10, 30)) 

playerImg = pygame.Surface((64, 64))
playerImg.fill((0, 255, 0))
playerX = 370
playerY = 480
playerX_change = 0

num_of_enemies = 6
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []

for i in range(num_of_enemies):
    img = pygame.Surface((64, 64))
    img.fill((255, 0, 0))
    enemyImg.append(img)
    enemyX.append(random.randint(0, SCREEN_WIDTH - 64))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(4)
    enemyY_change.append(40)

ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150

bulletImg = pygame.Surface((16, 16))
bulletImg.fill((255, 255, 0))
bulletX = 0
PLAYER_START_Y = 480
bulletY = PLAYER_START_Y
bulletY_change = 10
bullet_state = "ready"

COLLISION_DISTANCE = 27
score_value = 0
textX = 10
textY = 10

font = pygame.font.SysFont("comicsansms", 32)
over_font = pygame.font.SysFont("comicsansms", 64)

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((enemyX - bulletX) ** 2 + (enemyY - bulletY) ** 2)
    return distance < COLLISION_DISTANCE

running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.event.QUIT:
            running = False
        if event.type == pygame.event.KEYDOWN:
            if event.key == pygame.event.K_LEFT:
                playerX_change = -5
            if event.key == pygame.event.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.event.K_SPACE and bullet_state == "ready":
                bulletX = playerX
                bulletY = playerY
                fire_bullet(bulletX, bulletY)
        if event.type == pygame.event.KEYUP and event.key in [pygame.event.K_LEFT, pygame.event.K_RIGHT]:
            playerX_change = 0

    playerX += playerX_change
    playerX = max(0, min(playerX, SCREEN_WIDTH - 64))

    for i in range(num_of_enemies):
        if enemyY[i] > 340:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break

        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= SCREEN_WIDTH - 64:
            enemyX_change[i] *= -1
            enemyY[i] += enemyY_change[i]

        if isCollision(enemyX[i], enemyY[i], bulletX, bulletY):
            bulletY = PLAYER_START_Y
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, SCREEN_WIDTH - 64)
            enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)

        enemy(enemyX[i], enemyY[i], i)

    if bulletY <= 0:
        bulletY = PLAYER_START_Y
        bullet_state = "ready"
    elif bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    player(playerX, playerY)
    show_score(textX, textY)
    pygame.display.update()

pygame.quit()
