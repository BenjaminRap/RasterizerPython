from math import inf

import pygame
import numpy as np

from parseSimpleObjFile import Object3D, parse_simple_obj_file
from rasterizer import rasterize

size = (400, 400)

def run_rasterizer(objectFilePath : str):
    pygame.init()
    screen = pygame.display.set_mode(size)
    depth_buffer = np.full(size, inf, np.float32)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill("black")
        object3D : Object3D = parse_simple_obj_file(objectFilePath)
        rasterize(object3D, screen, depth_buffer)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    run_rasterizer("./objects/triangle.simpleObj")
