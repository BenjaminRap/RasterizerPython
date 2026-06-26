from math import sin

import pygame
import numpy as np

from parseSimpleObjFile import parse_simple_obj_file
from rasterizer import GameObject, Object3D, Transform, rasterize

screen_size = (400, 400)

def run_rasterizer(objectFilePath : str):
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    screen_buffer = np.empty((screen_size[0], screen_size[1], 3), np.uint8)
    clock = pygame.time.Clock()

    object_3d : Object3D = parse_simple_obj_file(objectFilePath)
    transform = Transform(
            np.array([0, 0, 1], np.float32), # position
            np.array([0.5, 0.5, 0.5], np.float32), # scale
            np.array([0, 0, 0], np.float32)) # rotation
    game_object = GameObject(object_3d, transform)

    running = True
    while running:
        clock.tick()
        print(f"fps : {int(clock.get_fps())}")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        transform.rotation[1] = sin(pygame.time.get_ticks() / 1000)
        transform.position[0] = sin(pygame.time.get_ticks() / 1000) / 7
        screen_buffer.fill(0)
        rasterize([game_object], screen_buffer)
        pygame.surfarray.blit_array(screen, screen_buffer)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    run_rasterizer("./objects/triangle.simpleObj")
