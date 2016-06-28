from math import sqrt

from random import shuffle
import pygame
from pygame.locals import *

WINDOW_SIZE = 400
COLOURFUL = False
RANDOM = False
K = 3
X_INCREMENT = K/WINDOW_SIZE
Y_INCREMENT = K/WINDOW_SIZE
MAXIMUM_RECURSION = 40

colours = [(255, 0, 0),
           (255, 64, 0),
           (255, 128, 0),
           (255, 191, 0),
           (255, 255, 0),
           (191, 255, 0),
           (128, 255, 0),
           (64, 255, 0),
           (0, 255, 0),
           (0, 255, 64),
           (0, 255, 128),
           (0, 255, 191),
           (0, 255, 255),
           (0, 191, 255),
           (0, 128, 255),
           (0, 64, 255),
           (0, 0, 255),
           (64, 0, 255),
           (128, 0, 255),
           (191, 0, 255),
           (255, 0, 255),
           (255, 0, 191),
           (255, 0, 128),
           (255, 0, 64),
           (255, 0, 0)]
if RANDOM:
    shuffle(colours)


def recur_x(zx, zy, c):
    return zx**2 - zy**2 + c


def recur_y(zx, zy, c):
    return 2*zx*zy + c


def recur_times(cx, cy, limit):
    zx = 0
    zy = 0
    for i in range(0, limit + 1):
        temp_x = recur_x(zx, zy, cx)
        temp_y = recur_y(zx, zy, cy)
        zx = temp_x
        zy = temp_y
        if not 2 > sqrt(zx**2 + zy**2) > -1:
            return i
    return limit


def get_colour(recursions):
    colour = (recursions/MAXIMUM_RECURSION) * 255
    return colour, colour, colour

main_surface = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

x = 0
y = 0

update = True
running = True
while running:
    if update:

        x_coordinate = (X_INCREMENT * x) - ((K/2) + K/4)
        y_coordinate = (Y_INCREMENT * y) - K/2

        recur = recur_times(x_coordinate, y_coordinate, MAXIMUM_RECURSION)
        if COLOURFUL:
            main_surface.set_at((x, y), colours[recur % 25])
        else:
            main_surface.set_at((x, y), get_colour(recur))

        if x + 1 > WINDOW_SIZE:
            x = 0
            y += 1
        elif y == WINDOW_SIZE:
            update = False
        else:
            x += 1

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                pygame.image.save(main_surface, 'mandelbrot.bmp')

    pygame.display.update()
