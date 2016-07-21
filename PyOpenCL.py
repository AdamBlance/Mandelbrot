import pyopencl as cl
import numpy as np

from os import environ
environ['PYOPENCL_COMPILER_OUTPUT'] = '0'


def get_iterations(context, complex_array, iterations):

    command_queue = cl.CommandQueue(context)

    output_array = np.empty(complex_array.shape, np.ushort)

    flags = cl.mem_flags
    complex_array_buffer = cl.Buffer(context, flags.READ_ONLY | flags.COPY_HOST_PTR, hostbuf=complex_array)
    output_array_buffer = cl.Buffer(context, flags.WRITE_ONLY, output_array.nbytes)

    program = cl.Program(context, '''
    __kernel void mandelbrot(__global float2 *complex_array, __global ushort *output_array, ushort const iterations)
    {
        int n = get_global_id(0);

        float zx = 0;
        float zy = 0;
        float cx = complex_array[n].x;
        float cy = complex_array[n].y;

        for(int i = 1; i <= iterations; i++){
            float temp_zx = zx*zx - (zy*zy) + cx;
            zy = 2*zx*zy + cy;
            zx = temp_zx;
            if (zx*zx + zy*zy > 4.0f){
                output_array[n] = i;
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
    real_array = np.linspace(x_min, x_max, screen_width, dtype=np.float32)
    imaginary_array = np.linspace(y_min, y_max, screen_height, dtype=np.float32)
    complex_array = real_array + imaginary_array[:, None]*1j
    complex_array = np.ravel(complex_array)
    colour_array = get_iterations(context, complex_array, iterations)
    colour_array = (colour_array.reshape((screen_width, screen_height)) /
                    float(colour_array.max()) * 255).astype(np.uint8)
    return colour_array

cl_context = cl.create_some_context(answers=[1, 0])
max_iterations = 1

print(calculate_mandelbrot(cl_context, -2, 2, -2, 2, max_iterations, 10, 10))

