// Model_Data_GPU.hpp
// GPU-accelerated version of Model_Data class
//

#ifndef MODEL_DATA_GPU_HPP
#define MODEL_DATA_GPU_HPP

#include "Model_Data.hpp"
#include "gpu_memory.hpp"
#include "gpu_types.hpp"
#include "gpu_kernels.cuh"
#include <nvector/nvector_cuda.h>
#include <sunlinsol/sunlinsol_spgmr.h>

class Model_Data_GPU : public Model_Data {
private:
    GPUMemoryManager *gpu_mem;
    bool gpu_initialized;

    // Device pointers for CVODE
    double *d_Y;   // State vector on device
    double *d_DY;  // Derivative vector on device

public:
    // Constructor
    Model_Data_GPU();

    // Destructor
    ~Model_Data_GPU();

    // GPU initialization
    void initializeGPU();
    void finalizeGPU();

    // Override CPU methods with GPU versions
    void f_update_gpu(double *Y, double *DY, double t);
    void f_loop_gpu(double *Y, double *DY, double t);
    void f_applyDY_gpu(double *DY, double t);

    // Main GPU computation entry point
    int f_gpu(double t, double *Y, double *DY);

    // Data synchronization
    void copyStateToGPU(double *h_Y);
    void copyStateFromGPU(double *h_Y);
    void copyDerivativesFromGPU(double *h_DY);

    // Memory management
    GPUMemoryStats getGPUMemoryStats();
    bool isGPUInitialized() const { return gpu_initialized; }

    // Utility functions
    void printGPUInfo();
    void checkGPUErrors();
};

// GPU version of the ODE right-hand side function for CVODE
int f_gpu_wrapper(double t, N_Vector CV_Y, N_Vector CV_Ydot, void *user_data);

#endif // MODEL_DATA_GPU_HPP
