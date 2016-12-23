#pragma OPENCL EXTENSION cl_khr_fp64 : enable
__kernel void mandelbrot(global double2 *complex_values,
                         global ushort4 *output_array,
                         global float4 const *gradient
                         //uint const iterations
                         ) {

	uint id = get_global_id(0);

    uint iterations = 5000;

	double zx = 0.0f;
    double zx_temp;
	double zy = 0.0f;

	double cx = complex_values[id].x;
	double cy = complex_values[id].y;

	output_array[id] = 0;

	uint bailout_radius = 1 << 16;
	double current_iter = 0.0f;

    double nu;
    double log_zn;

    float4 colour_1;
    float4 colour_2;
    ushort4 colour;

	while ((zx*zx + zy*zy < (bailout_radius)) && (current_iter < iterations)) {

        zx_temp = zx*zx - zy*zy + cx;
        zy = 2.0f*zx*zy + cy;
        zx = zx_temp;

        current_iter = current_iter + 1.0f;
    }

    if (current_iter < iterations) {
        log_zn = log(zx*zx + zy*zy) / 2.0f;
        nu = log(log_zn / log(2.0f)) / log(2.0f);
        current_iter = current_iter + 1.0f - nu;
    }

    colour_1 = gradient[(int)current_iter];
    colour_2 = gradient[(int)(current_iter) + (int)1];
    colour = convert_ushort4(mix(colour_1, colour_2, fmod((float)current_iter, 1.0f)));

    output_array[id] = colour;
    return;
}
