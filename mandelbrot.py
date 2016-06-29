import os
from math import sqrt
from PIL import Image


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

clear()
resolution = int(input('Resolution of image:\n'))
clear()
MAXIMUM_RECURSION = int(input('Maximum number of recursions:\n'))
clear()
input('Press enter to start.')
clear()

INVERT = False

K = 3
X_INCREMENT = K/resolution
Y_INCREMENT = K/resolution
x = 0
y = 0

loaded_image = Image.new('RGB', (resolution, resolution), 'black')
main_image = loaded_image.load()


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
    colour = int((recursions/MAXIMUM_RECURSION) * 255)
    if not INVERT:
        colour = 255 - colour
    return colour, colour, colour

running = True
count = 0
while running:

    x_coordinate = (X_INCREMENT * x) - ((K/2) + K/4)
    y_coordinate = (Y_INCREMENT * y) - K/2

    recur = recur_times(x_coordinate, y_coordinate, MAXIMUM_RECURSION)
    main_image[x, y] = get_colour(recur)

    if x + 1 > resolution-1 and not y + 1 > resolution:
        x = 0
        y += 1
    elif x + 1 <= resolution:
        x += 1

    count += 1
    if count == 32359:
        clear()
        percentage = y/resolution
        area = resolution**2
        print('%i/%i lines complete.\n%i/%i pixels complete.' % (y, resolution, ((y-1)/resolution) * area + x, area))
        count = 0

    if y == resolution:
        running = False

clear()
loaded_image.save('mandelbrot.bmp')
print('Done!\nSaved as \'mandelbrot.bmp\'.')
input()
