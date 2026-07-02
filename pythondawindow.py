import pygame
pygame.init()

screen = pygame.display.set_mode((600,600))

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False
    screen.fill(('yellow'))
    pygame.display.flip()
                                                                                                                                                                                        
pygame.quit()