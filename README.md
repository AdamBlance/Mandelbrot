# Mandelbrot
A basic mandelbrot set visualiser.

To run this program, you must have the following packages installed:
  - Pygame
  - PyOpenCL
Both of these packages must be of a version that is compatible with Python 3.5. 

You must also have an OpenCL driver installed. These are often packaged with AMD/Nvidia GPU drivers, but if you don't have a discrete card, download the driver from your CPU vendor's website. To change the device the program uses, change the text on line 9 from 'answers=[1, 1]' to 'interactive=True'. This will prompt you to choose a device. 
