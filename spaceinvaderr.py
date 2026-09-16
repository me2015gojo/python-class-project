import pygame
import math
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

background = pygame.image.load("back.png")

playerImg = pygame.image.load("rocketggs.png")
playerX = 370
playerY = 480
playerX_change = 0
PLAYER_START_Y = 480

num_of_enemies = 6
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
ENEMY_START_Y_MIN = 50
ENEMY_START_Y_MAX = 150

for i in range(num_of_enemies):
    img = pygame.image.load("invader2.png")
    enemyImg.append(img)
    enemyX.append(random.randint(0, SCREEN_WIDTH - 64))
    enemyY.append(random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX))
    enemyX_change.append(4)
    enemyY_change.append(40)

bulletImg = pygame.image.load("bullet1.png")
bulletX = 0
bulletY = PLAYER_START_Y
bulletY_change = 10
bullet_state = "ready"

score_value = 0
textX = 10
textY = 10
font = pygame.font.SysFont("comicsansms", 32)
over_font = pygame.font.SysFont("comicsansms", 64)

def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
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
    bullet_offset_x = (playerImg.get_width() // 2) - (bulletImg.get_width() // 2)
    screen.blit(bulletImg, (x + bullet_offset_x, y + 10))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((enemyX - bulletX) ** 2 + (enemyY - bulletY) ** 2)
    return distance < 27

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bulletX = playerX
                fire_bullet(bulletX, bulletY)
                
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                playerX_change = 0

    playerX += playerX_change
    playerX = max(0, min(playerX, SCREEN_WIDTH - playerImg.get_width()))
    
    for i in range(num_of_enemies):
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break
            
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= SCREEN_WIDTH - enemyImg[i].get_width():
            enemyX_change[i] *= -1
            enemyY[i] += enemyY_change[i]
            
        if bullet_state == "fire" and isCollision(enemyX[i], enemyY[i], bulletX, bulletY):
            bulletY = PLAYER_START_Y
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, SCREEN_WIDTH - enemyImg[i].get_width())
            enemyY[i] = random.randint(ENEMY_START_Y_MIN, ENEMY_START_Y_MAX)
            
        enemy(enemyX[i], enemyY[i], i)

    if bulletY <= 0:
        bulletY = PLAYER_START_Y
        bullet_state = "ready"
        
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change   
        
    player(playerX, playerY)
    show_score(textX, textY)
    
    pygame.display.update()

pygame.quit()
 