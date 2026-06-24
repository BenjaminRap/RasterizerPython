import pygame

_ = pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    _ = screen.fill("purple")
    pygame.display.flip()

pygame.quit()
