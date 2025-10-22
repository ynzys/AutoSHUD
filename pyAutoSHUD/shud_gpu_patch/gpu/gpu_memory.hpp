// gpu_memory.hpp
// GPU memory management for SHUD
//
// Handles allocation, deallocation, and transfer of data between CPU and GPU

#ifndef GPU_MEMORY_HPP
#define GPU_MEMORY_HPP

#include <cuda_runtime.h>
#include <stdio.h>
#include <stdlib.h>
#include "gpu_types.hpp"
#include "Element.hpp"
#include "River.hpp"
#include "Model_Data.hpp"

// CUDA error checking macro
#define CUDA_CHECK(call) \
    do { \
        cudaError_t error = call; \
        if (error != cudaSuccess) { \
            fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__, \
                    cudaGetErrorString(error)); \
            exit(EXIT_FAILURE); \
        } \
    } while(0)

class GPUMemoryManager {
private:
    int NumEle;
    int NumRiv;
    bool is_allocated;

public:
    GPUElementArrays d_elem;  // Device element arrays
    GPURiverArrays d_riv;     // Device river arrays

    // Constructor
    GPUMemoryManager(int numEle, int numRiv);

    // Destructor
    ~GPUMemoryManager();

    // Allocate GPU memory
    void allocateElementArrays();
    void allocateRiverArrays();
    void allocateAll();

    // Free GPU memory
    void freeElementArrays();
    void freeRiverArrays();
    void freeAll();

    // Copy data from CPU to GPU
    void copyElementsToDevice(_Element *h_Ele, double *h_uYsf, double *h_uYus, double *h_uYgw);
    void copyRiversToDevice(_River *h_Riv, double *h_uYriv);

    // Copy data from GPU to CPU
    void copyElementsToHost(double *h_uYsf, double *h_uYus, double *h_uYgw);
    void copyFluxesToHost(double *h_qInfil, double *h_qRecharge, double *h_qExfil);
    void copyRiversToHost(double *h_uYriv);

    // Get memory statistics
    GPUMemoryStats getMemoryStats();

    // Check if allocated
    bool isAllocated() const { return is_allocated; }
};

// Helper functions for CUDA memory operations
namespace GPUMemHelper {
    // Allocate and initialize device array
    template<typename T>
    void allocateDeviceArray(T** d_ptr, size_t count, const char* name = nullptr);

    // Free device array
    template<typename T>
    void freeDeviceArray(T* d_ptr);

    // Copy host to device
    template<typename T>
    void copyHostToDevice(T* d_ptr, const T* h_ptr, size_t count);

    // Copy device to host
    template<typename T>
    void copyDeviceToHost(T* h_ptr, const T* d_ptr, size_t count);

    // Set device array to zero
    template<typename T>
    void zeroDeviceArray(T* d_ptr, size_t count);
}

#endif // GPU_MEMORY_HPP
