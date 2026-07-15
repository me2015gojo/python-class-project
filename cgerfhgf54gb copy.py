import pygame
pygame.init()
window.fill(('black'))
GREEN=(0,255,0)
pygame.draw.circle(window,GREEN,(300,300),50)
pygame.draw.circle(window,GREEN,(100,100),50,3)
pygame.draw.Rect(window,GREEN,(0,0,225),pygame.Rect(200,30,80,100))
pygame.display.update()
running =True
while running:
    for event in pygame.event.get():
        if event.type == pygame.Quit:
            running=False
pygame.quit()