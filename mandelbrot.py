import os
from math import sqrt
import pygame


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

pygame.init()

clear()
resolution = int(input('Resolution of image:\n'))
clear()
MAXIMUM_RECURSION = int(input('Maximum number of recursions:\n'))
clear()
input('Press enter to start.')
clear()
print('Progress: 0% [                    ]')

K = 3
X_INCREMENT = K/resolution
Y_INCREMENT = K/resolution

main_surface = pygame.Surface((resolution, resolution))
x = 0
y = 0


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

running = True
count = 0
while running:

    x_coordinate = (X_INCREMENT * x) - ((K/2) + K/4)
    y_coordinate = (Y_INCREMENT * y) - K/2

    recur = recur_times(x_coordinate, y_coordinate, MAXIMUM_RECURSION)
    main_surface.set_at((x, y), get_colour(recur))

    if x + 1 > resolution and not y + 1 > resolution:
        x = 0
        y += 1
    elif x + 1 <= resolution:
        x += 1

    count += 1
    if count == 10000:
        clear()
        percentage = y/resolution
        print('Progress: %s%% [%s]' % (round(percentage*100, 0), (int(percentage*20)*'#')+(int(20-percentage*20)*' ')))
        count = 0

    if y == resolution:
        running = False

clear()
print('Progress: 100% [####################]')
pygame.image.save(main_surface, 'mandelbrot.bmp')
print('Done!\nSaved as \'mandelbrot.bmp\'.')
input()
