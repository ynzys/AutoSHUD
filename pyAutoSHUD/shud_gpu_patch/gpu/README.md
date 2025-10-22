# SHUD GPU Implementation

This directory contains the GPU-accelerated implementation of SHUD using NVIDIA CUDA.

## Directory Structure

```
gpu/
├── README.md                  # This file
├── gpu_types.hpp              # GPU data structures (SoA layout)
├── gpu_memory.hpp/cu          # GPU memory management
├── gpu_kernels.cuh/cu         # CUDA computation kernels
└── Model_Data_GPU.hpp/cpp     # GPU-enabled Model_Data class
```

## Files Overview

### gpu_types.hpp
Defines GPU-compatible data structures using Structure of Arrays (SoA) layout for optimal memory coalescing.

**Key structures**:
- `GPUElementArrays`: Element properties and state variables
- `GPURiverArrays`: River properties and fluxes
- `GPUMemoryStats`: Memory usage statistics

### gpu_memory.hpp/cu
Manages GPU memory allocation, deallocation, and CPU-GPU data transfer.

**Key class**:
- `GPUMemoryManager`: Handles all GPU memory operations
  - `allocateAll()`: Allocate GPU arrays
  - `copyElementsToDevice()`: Transfer data to GPU
  - `copyElementsToHost()`: Transfer results back
  - `getMemoryStats()`: Query memory usage

### gpu_kernels.cuh/cu
Implements hydrological computations as CUDA kernels.

**Device functions** (hydrological equations):
- `d_avgY_sf()`: Average surface water depth
- `d_avgY_gw()`: Average groundwater depth
- `d_effKV()`: Effective vertical hydraulic conductivity
- `d_effKH()`: Effective horizontal hydraulic conductivity
- `d_satKfun()`: Saturation function (van Genuchten)
- `d_GreenAmpt()`: Green-Ampt infiltration

**Kernel functions**:
- `kernel_update_elements()`: Update element states
- `kernel_infiltration()`: Compute infiltration rates
- `kernel_recharge()`: Compute groundwater recharge
- `kernel_exfiltration()`: Compute exfiltration
- `kernel_surface_flux()`: Compute surface lateral fluxes
- `kernel_subsurface_flux()`: Compute subsurface lateral fluxes
- `kernel_apply_derivatives()`: Compute ODE right-hand side

**Host functions**:
- `gpu_update_all()`: Launch element update kernels
- `gpu_compute_fluxes()`: Launch all flux kernels
- `gpu_apply_dy()`: Launch derivative kernel

### Model_Data_GPU.hpp/cpp
Extends `Model_Data` class with GPU acceleration capabilities.

**Key methods**:
- `initializeGPU()`: Initialize GPU memory and kernels
- `finalizeGPU()`: Cleanup GPU resources
- `f_gpu()`: Main GPU computation entry point
- `copyStateToGPU()`: Sync state to GPU
- `copyStateFromGPU()`: Sync state from GPU

## Implementation Details

### Memory Layout

Uses **Structure of Arrays (SoA)** instead of **Array of Structures (AoS)** for GPU efficiency:

```cpp
// CPU (AoS) - Poor GPU performance
struct Element {
    double area, zmax, KsatV;
} elements[N];

// GPU (SoA) - Good GPU performance
struct {
    double *area;    // [N]
    double *zmax;    // [N]
    double *KsatV;   // [N]
} gpu_elements;
```

**Benefit**: Coalesced memory access, higher bandwidth utilization.

### Kernel Launch Configuration

```cpp
int blockSize = 256;  // Threads per block
int gridSize = (NumEle + 255) / 256;  // Number of blocks
kernel<<<gridSize, blockSize>>>(args);
```

**Tuning**: Adjust `blockSize` in `gpu_kernels.cu` based on GPU architecture.

### Computation Pipeline

```
1. Update element states (parallel across elements)
   ├── Calculate saturation
   ├── Compute effective conductivities
   └── Update auxiliary variables

2. Compute vertical fluxes (parallel across elements)
   ├── Infiltration (Green-Ampt)
   ├── Recharge (unsaturated → groundwater)
   └── Exfiltration (overflow)

3. Compute lateral fluxes (parallel across elements)
   ├── Surface flow (Manning's equation)
   └── Subsurface flow (Darcy's law)

4. Apply derivatives (parallel across elements)
   ├── Surface water balance: dY_sf/dt
   ├── Unsaturated zone balance: dY_us/dt
   └── Groundwater balance: dY_gw/dt
```

### Data Dependencies

**Independent computations** (ideal for GPU):
- Element state updates
- Infiltration/recharge/exfiltration
- Local water balance

**Dependent computations** (managed via neighbor arrays):
- Lateral fluxes (read neighbor states)
- Resolved via read-only access patterns

## Performance Optimization

### Current Optimizations

1. **Coalesced Memory Access**: SoA layout
2. **Thread Parallelism**: 256 threads per block
3. **Minimize Host-Device Transfer**: Batch operations
4. **Asynchronous Kernels**: Sequential kernel launches with sync points

### Future Optimizations

1. **Shared Memory**: Cache neighbor data
2. **Texture Memory**: Read-only neighbor access
3. **CUDA Streams**: Overlap computation and transfer
4. **Dynamic Parallelism**: Adaptive kernel launches
5. **Multi-GPU**: Domain decomposition
6. **Mixed Precision**: FP16/FP32 hybrid

## Debugging

### Enable Debug Output

```cpp
// In gpu_kernels.cu, add:
#define GPU_DEBUG

__global__ void kernel_infiltration(...) {
    #ifdef GPU_DEBUG
    if (i == 0) {  // Print only first element
        printf("[GPU] Element %d: ysf=%.4f, qInfil=%.4f\n", i, ysf, qInfil);
    }
    #endif
}
```

### CUDA Error Checking

```bash
# Enable CUDA error checking
export CUDA_LAUNCH_BLOCKING=1

# Run with CUDA memcheck
cuda-memcheck ./shud_gpu ./input ./output
```

### Profiling

```bash
# NVIDIA Nsight Systems
nsys profile --stats=true ./shud_gpu ./input ./output

# NVIDIA Nsight Compute
ncu --set full ./shud_gpu ./input ./output
```

## Testing

### Unit Tests (Future)

```bash
# Compile test suite
make -f Makefile.gpu test

# Run tests
./test_gpu_kernels
```

### Validation

Compare GPU vs CPU results:

```bash
./shud ./input ./output_cpu
./shud_gpu ./input ./output_gpu

# Compare outputs (should be nearly identical)
python compare_results.py output_cpu output_gpu
```

## Known Limitations

1. **River computations**: Partially GPU-accelerated
2. **Evapotranspiration**: Not yet GPU-accelerated
3. **Lake module**: Not yet GPU-accelerated
4. **Small grids (<1000 elements)**: GPU overhead may dominate

## Contributing

When adding new GPU features:

1. **Follow SoA pattern**: Add new arrays to `GPUElementArrays`
2. **Add kernel**: Implement as `__global__ void kernel_newfeature(...)`
3. **Update memory manager**: Add allocation/deallocation
4. **Test**: Verify against CPU version
5. **Document**: Update this README

### Code Style

```cpp
// Device functions: d_ prefix
__device__ double d_myFunction(...);

// Kernels: kernel_ prefix
__global__ void kernel_myComputation(...);

// Host functions: gpu_ prefix
extern "C" void gpu_myLauncher(...);
```

## References

- **CUDA Programming Guide**: https://docs.nvidia.com/cuda/
- **SUNDIALS Documentation**: https://sundials.readthedocs.io/
- **SHUD Model**: https://www.shud.xyz/

## Contact

For GPU-specific questions:
- GitHub Issues: https://github.com/SHUD-System/SHUD/issues
- Email: lele.shu@gmail.com

---

**Last Updated**: 2025-10-22
**GPU Version**: 1.0 (Alpha)
