from gradient import *
import pyopencl as cl
import pygame
from pygame.locals import *

from os import environ
environ['PYOPENCL_COMPILER_OUTPUT'] = '0'

cl_context = cl.create_some_context(answers=[1, 1])

pygame.display.init()
pygame.font.init()


def get_iterations(context, complex_values, iterations):

    command_queue = cl.CommandQueue(context)

    output_array = np.empty(complex_values.shape, np.uint32)

    flags = cl.mem_flags
    gradient_array_buffer = cl.Buffer(context, flags.READ_ONLY | flags.COPY_HOST_PTR, hostbuf=gradient)
    complex_values_buffer = cl.Buffer(context, flags.READ_ONLY | flags.COPY_HOST_PTR, hostbuf=complex_values)
    output_array_buffer = cl.Buffer(context, flags.WRITE_ONLY, output_array.nbytes)

    program = cl.Program(context, '''
    #pragma OPENCL EXTENSION cl_khr_fp64 : enable
    __kernel void mandelbrot(global double2 *complex_values,
                             global uint *output_array,
                             global uint *gradient,
                             ushort const iterations)
    {
        uint id = get_global_id(0);

        double zx = 0;
        double zy = 0;
        double cx = complex_values[id].x;
        double cy = complex_values[id].y;
        double inv_log_2 = 1/log(2.0f);

        output_array[id] = 0;

        for(uint i = 0; i <= iterations; i++){
            double zx2 = zx*zx;
            double zy2 = zy*zy;
            double zx2_plus_zy2 = zx2 + zy2;

            double temp_zx = zx2 - zy2 + cx;
            zy = 2*zx*zy + cy;
            zx = temp_zx;
            if (zx2_plus_zy2 > 4.0f){
                double grad = log(log(sqrt(zx2_plus_zy2)) * inv_log_2) * inv_log_2;
                ushort colour = (int)(sqrt(i + 1 - grad) * 256) % 2048;
                output_array[id] = gradient[colour];
                return;
            }
        }
    }
    ''').build()

    program.mandelbrot(command_queue,
                       complex_values.shape,
                       None,  # Local memory size not specified
                       complex_values_buffer,
                       output_array_buffer,
                       gradient_array_buffer,
                       np.ushort(iterations))

    cl.enqueue_read_buffer(command_queue, output_array_buffer, output_array).wait()
    return output_array


def calculate_mandelbrot(context, x_minimum, x_maximum, y_minimum, y_maximum, iterations, screen_width, screen_height):
    real_values = np.linspace(x_minimum, x_maximum, screen_width, dtype=np.float64)
    imaginary_values = np.linspace(y_minimum, y_maximum, screen_height, dtype=np.float64)
    complex_values = real_values + imaginary_values[:, None]*1j
    complex_values = np.ravel(complex_values)
    colour_values = get_iterations(context, complex_values, iterations)
    colour_values = colour_values.reshape((screen_height, screen_width))
    return colour_values


def draw_mandelbrot(value_array):
    image_surface = pygame.Surface(value_array.shape, HWSURFACE)
    pygame.surfarray.blit_array(image_surface, value_array)
    image_surface = pygame.transform.rotate(image_surface, 90)
    return image_surface


width = 1000
height = 1000

max_iterations = 2000
x_max = 2.3
x_min = -2.3
y_max = x_max*(height/width)
y_min = x_min*(height/width)

pygame.display.set_caption('Mandelbrot Explorer')

coordinate_text = pygame.font.SysFont('Courier New', 14, bold=True)

main_surface = pygame.display.set_mode((width, height), HWSURFACE)
mandelbrot = calculate_mandelbrot(cl_context, x_min, x_max, y_min, y_max, max_iterations, width, height)
rendered_set = draw_mandelbrot(mandelbrot)
main_surface.blit(rendered_set, (0, 0))

text_rect_1 = pygame.Rect((20, height - 50), (0, 15))
text_rect_2 = pygame.Rect((20, height - 30), (0, 15))

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
    coordinate_surface_x = coordinate_text.render('%s<x<%s' % (x_min, x_max), True, text_colour)
    coordinate_surface_y = coordinate_text.render('%s<y<%s' % (y_min, y_max), True, text_colour)
    main_surface.blit(rendered_set, (0, 0))

    text_rect_1.width = coordinate_surface_x.get_rect().width
    text_rect_2.width = coordinate_surface_y.get_rect().width
    pygame.draw.rect(main_surface, (0, 0, 0), text_rect_1)
    pygame.draw.rect(main_surface, (0, 0, 0), text_rect_2)
    main_surface.blit(coordinate_surface_x, (20, height - 50))
    main_surface.blit(coordinate_surface_y, (20, height - 30))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if mouse_pos_1 is None:
                mouse_pos_1 = mouse_pos
            elif mouse_pos_1 is not None:
                if mouse_pos_2 is None:
                    mouse_pos_2 = True

    if mouse_pos_1 is not None:
        highlight_rect.x = mouse_pos_1[0]
        highlight_rect.y = mouse_pos_1[1]

        height_multiplier = 1
        highlight_rect.width = mouse_pos[0] - mouse_pos_1[0]
        if mouse_pos_1[1] - mouse_pos[1] > 0:
            height_multiplier = -1
        highlight_rect.height = height_multiplier * abs(highlight_rect.width) * (height/width)
        pygame.draw.rect(main_surface, (255, 0, 0), highlight_rect, 2)

    if mouse_pos_1 and mouse_pos_2 is not None:
        mouse_pos_1 = None
        mouse_pos_2 = None

        x_min = real_array[highlight_rect.left]
        x_max = real_array[highlight_rect.right]
        y_min = imaginary_array[height-highlight_rect.bottom]
        y_max = imaginary_array[height-highlight_rect.top]

        real_array = np.linspace(x_min, x_max, width, dtype=np.float64)
        imaginary_array = np.linspace(y_min, y_max, height, dtype=np.float64)

        complex_array = real_array + imaginary_array[:, None]*1j
        complex_array = np.ravel(complex_array)
        colour_array = get_iterations(cl_context, complex_array, max_iterations)
        colour_array = colour_array.reshape((height, width))

        rendered_set = draw_mandelbrot(colour_array)

    pygame.display.update()

pygame.quit()
