import pyopencl as cl
import numpy as np
from PIL import Image
import pygame
from pygame.locals import *

from os import environ
environ['PYOPENCL_COMPILER_OUTPUT'] = '0'

cl_context = cl.create_some_context(answers=[1, 0])


def get_iterations(context, complex_array, iterations):

    command_queue = cl.CommandQueue(context)

    output_array = np.empty(complex_array.shape, np.uint8)

    flags = cl.mem_flags
    complex_array_buffer = cl.Buffer(context, flags.READ_ONLY | flags.COPY_HOST_PTR, hostbuf=complex_array)
    output_array_buffer = cl.Buffer(context, flags.WRITE_ONLY, output_array.nbytes)

    program = cl.Program(context, '''
    __kernel void mandelbrot(__global double2 *complex_array, __global uchar *output_array, ushort const iterations)
    {
        int n = get_global_id(0);

        float zx = 0;
        float zy = 0;
        float cx = complex_array[n].x;
        float cy = complex_array[n].y;

        output_array[n] = 0;

        for(int i = 1; i <= iterations; i++){
            float temp_zx = zx*zx - (zy*zy) + cx;
            zy = 2*zx*zy + cy;
            zx = temp_zx;
            if (zx*zx + zy*zy > 4.0f){
                output_array[n] = 255*i/iterations;
                return;
            }
        }
    }
    ''').build()

    program.mandelbrot(command_queue,
                       complex_array.shape,
                       None,  # Local memory size not specified
                       complex_array_buffer,
                       output_array_buffer,
                       np.ushort(iterations))

    cl.enqueue_read_buffer(command_queue, output_array_buffer, output_array).wait()
    return output_array


def calculate_mandelbrot(context, x_min, x_max, y_min, y_max, iterations, screen_width, screen_height):
    real_array = np.linspace(x_min, x_max, screen_width, dtype=np.float64)
    imaginary_array = np.linspace(y_min, y_max, screen_height, dtype=np.float64)
    complex_array = real_array + imaginary_array[:, None]*1j
    complex_array = np.ravel(complex_array)
    colour_array = get_iterations(context, complex_array, iterations)
    colour_array = colour_array.reshape((screen_height, screen_width))
    return colour_array


def draw_mandelbrot(colour_array):
    image_surface = pygame.Surface(colour_array.shape, HWSURFACE)
    pygame.surfarray.blit_array(image_surface, np.array(colour_array).astype(int))
    image_surface = pygame.transform.rotate(image_surface, 90)
    return image_surface


def render_mandelbrot(colour_array):
    image = Image.fromarray(colour_array)
    image.save('mandelbrot. jpeg', 'JPEG')

width = 1280
height = 720

max_iterations = 50
x_max = 3
x_min = -3
y_max = x_max*(height/width)
y_min = x_min*(height/width)

main_surface = pygame.display.set_mode((width, height), HWSURFACE)
mandelbrot = calculate_mandelbrot(cl_context, x_min, x_max, y_min, y_max, max_iterations, width, height)
rendered_set = draw_mandelbrot(mandelbrot)
main_surface.blit(rendered_set, (0, 0))

mouse_pos_1 = None
mouse_pos_2 = None
highlight_rect = pygame.Rect((0, 0), (0, 0))

real_array = np.linspace(x_min, x_max, width, dtype=np.float64)
imaginary_array = np.linspace(y_min, y_max, height, dtype=np.float64)

running = True
clock = pygame.time.Clock()
while running:

    clock.tick(60)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if mouse_pos_1 is None:
                mouse_pos_1 = mouse_pos
            elif mouse_pos_1 is not None:
                if mouse_pos_2 is None:
                    mouse_pos_2 = True

    main_surface.blit(rendered_set, (0, 0))

    if mouse_pos_1 is not None:
        highlight_rect.x = mouse_pos_1[0]
        highlight_rect.y = mouse_pos_1[1]

        height_multiplier = 1
        highlight_rect.width = mouse_pos[0] - mouse_pos_1[0]
        if mouse_pos_1[1] - mouse_pos[1] > 0:
            height_multiplier = -1
        highlight_rect.height = height_multiplier * abs(highlight_rect.width) * (height/width)
        pygame.draw.rect(main_surface, (255, 0, 0), highlight_rect, 2)
        highlight_rect.normalize()

    if mouse_pos_1 and mouse_pos_2 is not None:
        mouse_pos_1 = None
        mouse_pos_2 = None

        x_min = real_array[highlight_rect.left]
        x_max = real_array[highlight_rect.right]
        y_min = imaginary_array[height-highlight_rect.bottom]
        y_max = imaginary_array[height-highlight_rect.top]

        real_array = np.linspace(x_min, x_max, width, dtype=np.float64)
        imaginary_array = np.linspace(y_min, y_max, height, dtype=np.float64)

        print(x_min, x_max)

        complex_array = real_array + imaginary_array[:, None]*1j
        complex_array = np.ravel(complex_array)
        colour_array = get_iterations(cl_context, complex_array, max_iterations)
        colour_array = colour_array.reshape((height, width))


        # mandelbrot = calculate_mandelbrot(cl_context, x_min, x_max, y_min, y_max, max_iterations, width, height)
        rendered_set = draw_mandelbrot(colour_array)

    pygame.display.update()

pygame.quit()
