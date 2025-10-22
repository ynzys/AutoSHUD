/*******************************************************************************
 * File        : main_gpu.cpp                                                  *
 * Version     : GPU-accelerated SHUD (2025)                                   *
 * Function    : SHUD with CUDA GPU acceleration                               *
 * Website     : https://www.shud.xyz/                                         *
 * Maintainer  : Lele Shu (lele.shu@gmail.com)                                *
 * GPU Version : Based on SHUD v2.0 with CUDA kernels                          *
 *                                                                             *
 * Description : GPU-accelerated version of SHUD hydrological model            *
 *               Uses CUDA for element computations and SUNDIALS CVODE         *
 *               for ODE integration with GPU support                          *
 *******************************************************************************/

#include "shud.hpp"
#include "print.hpp"
#include "Model_Data_GPU.hpp"
#include <cuda_runtime.h>

void PrintGPULogo() {
    printf("\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("   SHUD-GPU: GPU-Accelerated Hydrological Modeling\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("   Simulator for Hydrologic Unstructured Domains\n");
    printf("   GPU Version powered by NVIDIA CUDA\n");
    printf("───────────────────────────────────────────────────────────────\n");
    printf("   Website: https://www.shud.xyz/\n");
    printf("   Version: SHUD v2.0 + CUDA GPU Acceleration\n");
    printf("   Maintainer: Lele Shu (lele.shu@gmail.com)\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("\n");
}

void CheckGPUAvailability() {
    int deviceCount;
    cudaError_t error = cudaGetDeviceCount(&deviceCount);

    if (error != cudaSuccess) {
        fprintf(stderr, "ERROR: CUDA initialization failed: %s\n", cudaGetErrorString(error));
        fprintf(stderr, "Please check:\n");
        fprintf(stderr, "  1. NVIDIA driver is installed\n");
        fprintf(stderr, "  2. CUDA Toolkit is installed\n");
        fprintf(stderr, "  3. GPU is properly configured\n");
        exit(EXIT_FAILURE);
    }

    if (deviceCount == 0) {
        fprintf(stderr, "ERROR: No CUDA-capable GPU found!\n");
        fprintf(stderr, "This version requires an NVIDIA GPU.\n");
        fprintf(stderr, "Use the CPU version (./shud) instead.\n");
        exit(EXIT_FAILURE);
    }

    printf("[GPU] Detected %d CUDA-capable device(s)\n", deviceCount);

    // Print info for first device
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, 0);
    printf("[GPU] Using: %s\n", prop.name);
    printf("[GPU] Compute Capability: %d.%d\n", prop.major, prop.minor);
    printf("[GPU] Global Memory: %.2f GB\n", prop.totalGlobalMem / (1024.0 * 1024.0 * 1024.0));
    printf("\n");

    // Check compute capability
    if (prop.major < 7) {
        fprintf(stderr, "WARNING: GPU Compute Capability %d.%d is below recommended (7.0+)\n",
                prop.major, prop.minor);
        fprintf(stderr, "Performance may be limited.\n");
    }
}

int SHUD_GPU(int argc, char *argv[]) {
    // Check GPU availability
    CheckGPUAvailability();

    // Create GPU-enabled model data structure
    printf("[SHUD] Initializing GPU-accelerated model...\n");
    Model_Data_GPU *MD = new Model_Data_GPU();

    // Read input files (same as CPU version)
    printf("[SHUD] Reading input files...\n");
    MD->read_alloc(argc, argv);
    MD->initialize();

    // Initialize GPU memory and kernels
    printf("[SHUD] Initializing GPU acceleration...\n");
    MD->initializeGPU();

    // Run simulation with GPU acceleration
    printf("[SHUD] Starting GPU-accelerated simulation...\n");
    printf("═══════════════════════════════════════════════════════════════\n");

    clock_t start_time = clock();

    // Main simulation loop (uses GPU kernels internally)
    MD->CVODE_Solve();

    clock_t end_time = clock();
    double elapsed = (double)(end_time - start_time) / CLOCKS_PER_SEC;

    printf("═══════════════════════════════════════════════════════════════\n");
    printf("[SHUD] Simulation complete\n");
    printf("[SHUD] Total time: %.2f seconds (%.2f minutes)\n", elapsed, elapsed / 60.0);
    printf("[SHUD] Function calls: %lu\n", MD->nFCall);
    printf("[SHUD] Average time per call: %.4f ms\n", (elapsed * 1000.0) / MD->nFCall);

    // Print GPU memory usage
    GPUMemoryStats stats = MD->getGPUMemoryStats();
    printf("[GPU] Memory used: %.2f MB\n", stats.total_allocated / (1024.0 * 1024.0));

    // Cleanup
    printf("[SHUD] Cleaning up...\n");
    MD->finalizeGPU();
    delete MD;

    printf("[SHUD] Done!\n");
    printf("═══════════════════════════════════════════════════════════════\n");

    return 0;
}

int main(int argc, char *argv[]) {
    PrintGPULogo();

    if (argc < 2) {
        printf("Usage: %s <project_directory> [output_directory]\n", argv[0]);
        printf("\n");
        printf("Example:\n");
        printf("  %s ./input ./output\n", argv[0]);
        printf("\n");
        printf("Requirements:\n");
        printf("  - NVIDIA GPU with CUDA support\n");
        printf("  - CUDA Toolkit 11.0+\n");
        printf("  - SUNDIALS 6.0+ with CUDA support\n");
        printf("\n");
        return 1;
    }

    try {
        return SHUD_GPU(argc, argv);
    } catch (const std::exception &e) {
        fprintf(stderr, "ERROR: %s\n", e.what());
        return 1;
    } catch (...) {
        fprintf(stderr, "ERROR: Unknown exception occurred\n");
        return 1;
    }
}
