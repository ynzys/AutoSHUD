// Model_Data_GPU.cpp
// Implementation of GPU-accelerated Model_Data
//

#include "Model_Data_GPU.hpp"
#include <cuda_runtime.h>

// Constructor
Model_Data_GPU::Model_Data_GPU() : Model_Data(), gpu_mem(nullptr), gpu_initialized(false) {
    d_Y = nullptr;
    d_DY = nullptr;
}

// Destructor
Model_Data_GPU::~Model_Data_GPU() {
    if (gpu_initialized) {
        finalizeGPU();
    }
}

// Initialize GPU
void Model_Data_GPU::initializeGPU() {
    if (gpu_initialized) {
        printf("[GPU] Already initialized\n");
        return;
    }

    printf("[GPU] Initializing GPU acceleration...\n");

    // Print GPU information
    printGPUInfo();

    // Allocate GPU memory manager
    gpu_mem = new GPUMemoryManager(NumEle, NumRiv);
    gpu_mem->allocateAll();

    // Allocate state and derivative vectors on GPU
    CUDA_CHECK(cudaMalloc(&d_Y, NumY * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_DY, NumY * sizeof(double)));

    // Copy initial element and river data to GPU
    gpu_mem->copyElementsToDevice(Ele, &uYsf[0], &uYus[0], &uYgw[0]);
    if (NumRiv > 0) {
        gpu_mem->copyRiversToDevice(Riv, &uYriv[0]);
    }

    gpu_initialized = true;

    // Print memory statistics
    GPUMemoryStats stats = gpu_mem->getMemoryStats();
    printf("[GPU] Memory allocated: %.2f MB\n", stats.total_allocated / (1024.0 * 1024.0));
    printf("[GPU] GPU free memory: %.2f MB / %.2f MB\n",
           stats.gpu_free / (1024.0 * 1024.0),
           stats.gpu_total / (1024.0 * 1024.0));
    printf("[GPU] Initialization complete\n");
}

// Finalize GPU
void Model_Data_GPU::finalizeGPU() {
    if (!gpu_initialized) return;

    printf("[GPU] Finalizing GPU...\n");

    if (d_Y) cudaFree(d_Y);
    if (d_DY) cudaFree(d_DY);

    if (gpu_mem) {
        delete gpu_mem;
        gpu_mem = nullptr;
    }

    gpu_initialized = false;
    printf("[GPU] Finalization complete\n");
}

// GPU version of f_update
void Model_Data_GPU::f_update_gpu(double *Y, double *DY, double t) {
    // Copy Y to device if needed
    CUDA_CHECK(cudaMemcpy(d_Y, Y, NumY * sizeof(double), cudaMemcpyHostToDevice));

    // Zero derivatives
    gpu_zero_derivatives(d_DY, NumY);

    // Update element states on GPU
    gpu_update_all(gpu_mem->d_elem, NumEle, t);
}

// GPU version of f_loop
void Model_Data_GPU::f_loop_gpu(double *Y, double *DY, double t) {
    // Compute all fluxes on GPU
    gpu_compute_fluxes(gpu_mem->d_elem, NumEle, t);
}

// GPU version of f_applyDY
void Model_Data_GPU::f_applyDY_gpu(double *DY, double t) {
    // Apply derivatives (compute DY from fluxes)
    gpu_apply_dy(gpu_mem->d_elem, d_DY, NumEle, t);

    // Copy DY back to host
    CUDA_CHECK(cudaMemcpy(DY, d_DY, NumY * sizeof(double), cudaMemcpyDeviceToHost));
}

// Main GPU computation function
int Model_Data_GPU::f_gpu(double t, double *Y, double *DY) {
    if (!gpu_initialized) {
        fprintf(stderr, "[GPU ERROR] GPU not initialized!\n");
        return -1;
    }

    tnow = t;

    // Step 1: Update element states
    f_update_gpu(Y, DY, t);

    // Step 2: Compute fluxes
    f_loop_gpu(Y, DY, t);

    // Step 3: Compute derivatives
    f_applyDY_gpu(DY, t);

    nFCall++;

    return 0;
}

// Copy state from host to GPU
void Model_Data_GPU::copyStateToGPU(double *h_Y) {
    if (!gpu_initialized) return;

    CUDA_CHECK(cudaMemcpy(d_Y, h_Y, NumY * sizeof(double), cudaMemcpyHostToDevice));

    // Update element arrays
    CUDA_CHECK(cudaMemcpy(gpu_mem->d_elem.uYsf, &h_Y[0], NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(gpu_mem->d_elem.uYus, &h_Y[NumEle], NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(gpu_mem->d_elem.uYgw, &h_Y[2*NumEle], NumEle * sizeof(double), cudaMemcpyHostToDevice));
}

// Copy state from GPU to host
void Model_Data_GPU::copyStateFromGPU(double *h_Y) {
    if (!gpu_initialized) return;

    CUDA_CHECK(cudaMemcpy(h_Y, d_Y, NumY * sizeof(double), cudaMemcpyDeviceToHost));
}

// Copy derivatives from GPU to host
void Model_Data_GPU::copyDerivativesFromGPU(double *h_DY) {
    if (!gpu_initialized) return;

    CUDA_CHECK(cudaMemcpy(h_DY, d_DY, NumY * sizeof(double), cudaMemcpyDeviceToHost));
}

// Get GPU memory statistics
GPUMemoryStats Model_Data_GPU::getGPUMemoryStats() {
    if (gpu_mem) {
        return gpu_mem->getMemoryStats();
    }
    return GPUMemoryStats{0, 0, 0, 0, 0};
}

// Print GPU information
void Model_Data_GPU::printGPUInfo() {
    int deviceCount;
    cudaGetDeviceCount(&deviceCount);

    printf("[GPU] Found %d CUDA device(s)\n", deviceCount);

    if (deviceCount == 0) {
        fprintf(stderr, "[GPU ERROR] No CUDA-capable devices found!\n");
        exit(EXIT_FAILURE);
    }

    for (int dev = 0; dev < deviceCount; dev++) {
        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, dev);

        printf("[GPU %d] %s\n", dev, prop.name);
        printf("  Compute Capability: %d.%d\n", prop.major, prop.minor);
        printf("  Total Global Memory: %.2f GB\n", prop.totalGlobalMem / (1024.0 * 1024.0 * 1024.0));
        printf("  Multiprocessors: %d\n", prop.multiProcessorCount);
        printf("  Max Threads per Block: %d\n", prop.maxThreadsPerBlock);
        printf("  Max Grid Size: %d x %d x %d\n", prop.maxGridSize[0], prop.maxGridSize[1], prop.maxGridSize[2]);
    }

    // Set default device
    cudaSetDevice(0);
    printf("[GPU] Using device 0\n");
}

// Check for GPU errors
void Model_Data_GPU::checkGPUErrors() {
    cudaError_t error = cudaGetLastError();
    if (error != cudaSuccess) {
        fprintf(stderr, "[GPU ERROR] %s\n", cudaGetErrorString(error));
    }
}

// ============================================================================
// GPU wrapper for CVODE
// ============================================================================

int f_gpu_wrapper(double t, N_Vector CV_Y, N_Vector CV_Ydot, void *user_data) {
    Model_Data_GPU *MD = (Model_Data_GPU *)user_data;

    // Get pointers to vector data
    #ifdef _CUDA_NVECTOR
        // If using CUDA N_Vector, get device pointers
        double *Y = N_VGetDeviceArrayPointer_Cuda(CV_Y);
        double *DY = N_VGetDeviceArrayPointer_Cuda(CV_Ydot);
    #else
        // If using serial N_Vector, get host pointers
        double *Y = NV_DATA_S(CV_Y);
        double *DY = NV_DATA_S(CV_Ydot);
    #endif

    // Call GPU computation
    int status = MD->f_gpu(t, Y, DY);

    return status;
}
