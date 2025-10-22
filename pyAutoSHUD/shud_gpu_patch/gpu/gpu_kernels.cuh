// gpu_kernels.cuh
// CUDA kernel declarations for SHUD hydrological computations
//

#ifndef GPU_KERNELS_CUH
#define GPU_KERNELS_CUH

#include <cuda_runtime.h>
#include "gpu_types.hpp"

// Device functions (inline, callable from kernels)
__device__ inline double d_avgY_sf(double z1, double y1, double z2, double y2, double threshold);
__device__ inline double d_avgY_gw(double z1, double y1, double z2, double y2, double threshold);
__device__ inline double d_effKV(double ksatFunc, double gradY, double macKV, double KV, double areaF);
__device__ inline double d_effKH(double Ygw, double aqDepth, double MacD, double Kmac, double AF, double Kmx);
__device__ inline double d_satKfun(double elemSatn, double n);
__device__ inline double d_GreenAmpt(double k, double ti, double ts, double phi, double hf, double h0, double Sy);

// Kernel declarations

// Element update kernels
__global__ void kernel_update_elements(
    GPUElementArrays elem,
    int NumEle,
    double t
);

__global__ void kernel_infiltration(
    GPUElementArrays elem,
    int NumEle,
    double t
);

__global__ void kernel_recharge(
    GPUElementArrays elem,
    int NumEle,
    double t
);

__global__ void kernel_exfiltration(
    GPUElementArrays elem,
    int NumEle,
    double t
);

// Lateral flux kernels
__global__ void kernel_surface_flux(
    GPUElementArrays elem,
    int NumEle,
    double t
);

__global__ void kernel_subsurface_flux(
    GPUElementArrays elem,
    int NumEle,
    double t
);

// ODE derivative computation
__global__ void kernel_apply_derivatives(
    GPUElementArrays elem,
    double *DY,  // Global derivative array [NumY]
    int NumEle,
    double t
);

// Initialize flux arrays
__global__ void kernel_zero_fluxes(
    GPUElementArrays elem,
    int NumEle
);

// River kernels
__global__ void kernel_update_rivers(
    GPURiverArrays riv,
    int NumRiv,
    double t
);

__global__ void kernel_river_flux(
    GPURiverArrays riv,
    GPUElementArrays elem,
    int NumRiv,
    double t
);

// Host function declarations (callable from C++)
extern "C" {
    // Launch configuration helpers
    void get_launch_config(int N, int *gridSize, int *blockSize);

    // Main computation functions
    void gpu_update_all(GPUElementArrays& d_elem, int NumEle, double t);
    void gpu_compute_fluxes(GPUElementArrays& d_elem, int NumEle, double t);
    void gpu_apply_dy(GPUElementArrays& d_elem, double *d_DY, int NumEle, double t);

    // Utility functions
    void gpu_zero_derivatives(double *d_DY, int NumY);
    void gpu_synchronize();
}

#endif // GPU_KERNELS_CUH
