#pragma OPENCL EXTENSION cl_khr_fp64 : enable
__kernel void mandelbrot(global double2 *complex_values,
                         global uint *output_array,
                         global uint *gradient,
                         ushort const iterations) {

	uint id = get_global_id(0);

	double zx = 0;
	double zy = 0;
	double cx = complex_values[id].x;
	double cy = complex_values[id].y;
	double inv_log_2 = 1/log(2.0f);

	output_array[id] = 0;

	for(uint i = 0; i <= iterations; i++) {
		double zx2 = zx*zx;
		double zy2 = zy*zy;
		double zx2_plus_zy2 = zx2 + zy2;

		double temp_zx = zx2 - zy2 + cx;
		zy = 2*zx*zy + cy;
		zx = temp_zx;
		if (zx2_plus_zy2 > 4){
			double grad = log(log(sqrt(zx2_plus_zy2)) * inv_log_2) * inv_log_2;
			ushort colour = (uint)(sqrt(i + 1 - grad) * 256) % 2048;
			output_array[id] = gradient[colour];
			return;
		}
	}
}
