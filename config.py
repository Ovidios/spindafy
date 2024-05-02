from numba import cuda

USE_GPU = cuda.is_available()
