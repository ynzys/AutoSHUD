// gpu_memory.cu
// Implementation of GPU memory management
//

#include "gpu_memory.hpp"
#include <cuda_runtime.h>

// Constructor
GPUMemoryManager::GPUMemoryManager(int numEle, int numRiv)
    : NumEle(numEle), NumRiv(numRiv), is_allocated(false) {
    // Initialize pointers to nullptr
    memset(&d_elem, 0, sizeof(GPUElementArrays));
    memset(&d_riv, 0, sizeof(GPURiverArrays));
}

// Destructor
GPUMemoryManager::~GPUMemoryManager() {
    if (is_allocated) {
        freeAll();
    }
}

// Allocate element arrays on GPU
void GPUMemoryManager::allocateElementArrays() {
    // Geometry
    CUDA_CHECK(cudaMalloc(&d_elem.area, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.zmax, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.zmin, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.AquiferDepth, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.depression, NumEle * sizeof(double)));

    // State variables
    CUDA_CHECK(cudaMalloc(&d_elem.uYsf, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.uYus, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.uYgw, NumEle * sizeof(double)));

    // Soil properties
    CUDA_CHECK(cudaMalloc(&d_elem.ThetaS, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.ThetaR, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.ThetaW, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.ThetaF, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Alpha, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Beta, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.KsatV, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.KsatH, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.InfD, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.RzD, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.MacD, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.MacKsatV, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Porosity, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.AreaF, NumEle * sizeof(double)));

    // Geology properties
    CUDA_CHECK(cudaMalloc(&d_elem.Kmacv_geol, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Kh_geol, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Sy, NumEle * sizeof(double)));

    // Landcover properties
    CUDA_CHECK(cudaMalloc(&d_elem.VegFrac, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Albedo, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Rs_min, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Rgl, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.Hs, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.RzD_lc, NumEle * sizeof(double)));

    // Neighbor topology
    CUDA_CHECK(cudaMalloc(&d_elem.nabr, NumEle * 3 * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&d_elem.edge, NumEle * 3 * sizeof(double)));

    // Fluxes
    CUDA_CHECK(cudaMalloc(&d_elem.qInfil, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qRecharge, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qExfil, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qNetPrep, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qEs, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qEu, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qEg, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qTu, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.qTg, NumEle * sizeof(double)));

    // Lateral fluxes
    CUDA_CHECK(cudaMalloc(&d_elem.QeleSurf, NumEle * 3 * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.QeleSub, NumEle * 3 * sizeof(double)));

    // Derivatives
    CUDA_CHECK(cudaMalloc(&d_elem.DY_sf, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.DY_us, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.DY_gw, NumEle * sizeof(double)));

    // Attributes
    CUDA_CHECK(cudaMalloc(&d_elem.iBC, NumEle * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&d_elem.iSS, NumEle * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&d_elem.QBC, NumEle * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_elem.QSS, NumEle * sizeof(double)));

    printf("[GPU] Allocated element arrays for %d elements\n", NumEle);
}

// Allocate river arrays on GPU
void GPUMemoryManager::allocateRiverArrays() {
    if (NumRiv == 0) return;

    CUDA_CHECK(cudaMalloc(&d_riv.length, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.width, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.depth, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.rough, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.uYriv, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.KsatH, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.bedThick, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.QrivDown, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.QrivUp, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.QrivSurf, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.QrivSub, NumRiv * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&d_riv.down, NumRiv * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&d_riv.up, NumRiv * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&d_riv.BC, NumRiv * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&d_riv.qBC, NumRiv * sizeof(double)));

    printf("[GPU] Allocated river arrays for %d rivers\n", NumRiv);
}

// Allocate all GPU memory
void GPUMemoryManager::allocateAll() {
    allocateElementArrays();
    allocateRiverArrays();
    is_allocated = true;
    printf("[GPU] All GPU memory allocated successfully\n");
}

// Free element arrays
void GPUMemoryManager::freeElementArrays() {
    // Free all element arrays
    if (d_elem.area) cudaFree(d_elem.area);
    if (d_elem.zmax) cudaFree(d_elem.zmax);
    if (d_elem.zmin) cudaFree(d_elem.zmin);
    if (d_elem.AquiferDepth) cudaFree(d_elem.AquiferDepth);
    if (d_elem.depression) cudaFree(d_elem.depression);

    if (d_elem.uYsf) cudaFree(d_elem.uYsf);
    if (d_elem.uYus) cudaFree(d_elem.uYus);
    if (d_elem.uYgw) cudaFree(d_elem.uYgw);

    if (d_elem.ThetaS) cudaFree(d_elem.ThetaS);
    if (d_elem.ThetaR) cudaFree(d_elem.ThetaR);
    if (d_elem.ThetaW) cudaFree(d_elem.ThetaW);
    if (d_elem.ThetaF) cudaFree(d_elem.ThetaF);
    if (d_elem.Alpha) cudaFree(d_elem.Alpha);
    if (d_elem.Beta) cudaFree(d_elem.Beta);
    if (d_elem.KsatV) cudaFree(d_elem.KsatV);
    if (d_elem.KsatH) cudaFree(d_elem.KsatH);
    if (d_elem.InfD) cudaFree(d_elem.InfD);
    if (d_elem.RzD) cudaFree(d_elem.RzD);
    if (d_elem.MacD) cudaFree(d_elem.MacD);
    if (d_elem.MacKsatV) cudaFree(d_elem.MacKsatV);
    if (d_elem.Porosity) cudaFree(d_elem.Porosity);
    if (d_elem.AreaF) cudaFree(d_elem.AreaF);

    if (d_elem.Kmacv_geol) cudaFree(d_elem.Kmacv_geol);
    if (d_elem.Kh_geol) cudaFree(d_elem.Kh_geol);
    if (d_elem.Sy) cudaFree(d_elem.Sy);

    if (d_elem.VegFrac) cudaFree(d_elem.VegFrac);
    if (d_elem.Albedo) cudaFree(d_elem.Albedo);
    if (d_elem.Rs_min) cudaFree(d_elem.Rs_min);
    if (d_elem.Rgl) cudaFree(d_elem.Rgl);
    if (d_elem.Hs) cudaFree(d_elem.Hs);
    if (d_elem.RzD_lc) cudaFree(d_elem.RzD_lc);

    if (d_elem.nabr) cudaFree(d_elem.nabr);
    if (d_elem.edge) cudaFree(d_elem.edge);

    if (d_elem.qInfil) cudaFree(d_elem.qInfil);
    if (d_elem.qRecharge) cudaFree(d_elem.qRecharge);
    if (d_elem.qExfil) cudaFree(d_elem.qExfil);
    if (d_elem.qNetPrep) cudaFree(d_elem.qNetPrep);
    if (d_elem.qEs) cudaFree(d_elem.qEs);
    if (d_elem.qEu) cudaFree(d_elem.qEu);
    if (d_elem.qEg) cudaFree(d_elem.qEg);
    if (d_elem.qTu) cudaFree(d_elem.qTu);
    if (d_elem.qTg) cudaFree(d_elem.qTg);

    if (d_elem.QeleSurf) cudaFree(d_elem.QeleSurf);
    if (d_elem.QeleSub) cudaFree(d_elem.QeleSub);

    if (d_elem.DY_sf) cudaFree(d_elem.DY_sf);
    if (d_elem.DY_us) cudaFree(d_elem.DY_us);
    if (d_elem.DY_gw) cudaFree(d_elem.DY_gw);

    if (d_elem.iBC) cudaFree(d_elem.iBC);
    if (d_elem.iSS) cudaFree(d_elem.iSS);
    if (d_elem.QBC) cudaFree(d_elem.QBC);
    if (d_elem.QSS) cudaFree(d_elem.QSS);
}

// Free river arrays
void GPUMemoryManager::freeRiverArrays() {
    if (d_riv.length) cudaFree(d_riv.length);
    if (d_riv.width) cudaFree(d_riv.width);
    if (d_riv.depth) cudaFree(d_riv.depth);
    if (d_riv.rough) cudaFree(d_riv.rough);
    if (d_riv.uYriv) cudaFree(d_riv.uYriv);
    if (d_riv.KsatH) cudaFree(d_riv.KsatH);
    if (d_riv.bedThick) cudaFree(d_riv.bedThick);
    if (d_riv.QrivDown) cudaFree(d_riv.QrivDown);
    if (d_riv.QrivUp) cudaFree(d_riv.QrivUp);
    if (d_riv.QrivSurf) cudaFree(d_riv.QrivSurf);
    if (d_riv.QrivSub) cudaFree(d_riv.QrivSub);
    if (d_riv.down) cudaFree(d_riv.down);
    if (d_riv.up) cudaFree(d_riv.up);
    if (d_riv.BC) cudaFree(d_riv.BC);
    if (d_riv.qBC) cudaFree(d_riv.qBC);
}

// Free all GPU memory
void GPUMemoryManager::freeAll() {
    freeElementArrays();
    freeRiverArrays();
    is_allocated = false;
    printf("[GPU] All GPU memory freed\n");
}

// Copy elements from CPU to GPU
void GPUMemoryManager::copyElementsToDevice(_Element *h_Ele, double *h_uYsf, double *h_uYus, double *h_uYgw) {
    // Temporary host arrays for Structure of Arrays conversion
    double *h_area = new double[NumEle];
    double *h_zmax = new double[NumEle];
    double *h_KsatV = new double[NumEle];
    double *h_ThetaS = new double[NumEle];
    double *h_Sy = new double[NumEle];
    int *h_nabr = new int[NumEle * 3];

    // Convert from Array of Structures to Structure of Arrays
    for (int i = 0; i < NumEle; i++) {
        h_area[i] = h_Ele[i].area;
        h_zmax[i] = h_Ele[i].zmax;
        h_KsatV[i] = h_Ele[i].KsatV;
        h_ThetaS[i] = h_Ele[i].ThetaS;
        h_Sy[i] = h_Ele[i].Sy;

        // Copy neighbor indices
        for (int j = 0; j < 3; j++) {
            h_nabr[i * 3 + j] = h_Ele[i].nabr[j];
        }
    }

    // Copy to device
    CUDA_CHECK(cudaMemcpy(d_elem.area, h_area, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.zmax, h_zmax, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.KsatV, h_KsatV, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.ThetaS, h_ThetaS, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.Sy, h_Sy, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.nabr, h_nabr, NumEle * 3 * sizeof(int), cudaMemcpyHostToDevice));

    // Copy state variables
    CUDA_CHECK(cudaMemcpy(d_elem.uYsf, h_uYsf, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.uYus, h_uYus, NumEle * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_elem.uYgw, h_uYgw, NumEle * sizeof(double), cudaMemcpyHostToDevice));

    // Clean up
    delete[] h_area;
    delete[] h_zmax;
    delete[] h_KsatV;
    delete[] h_ThetaS;
    delete[] h_Sy;
    delete[] h_nabr;

    printf("[GPU] Copied element data to device\n");
}

// Copy elements from GPU to CPU
void GPUMemoryManager::copyElementsToHost(double *h_uYsf, double *h_uYus, double *h_uYgw) {
    CUDA_CHECK(cudaMemcpy(h_uYsf, d_elem.uYsf, NumEle * sizeof(double), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_uYus, d_elem.uYus, NumEle * sizeof(double), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_uYgw, d_elem.uYgw, NumEle * sizeof(double), cudaMemcpyDeviceToHost));
}

// Get memory statistics
GPUMemoryStats GPUMemoryManager::getMemoryStats() {
    GPUMemoryStats stats;

    // Calculate allocated memory
    size_t elem_scalars = 30; // Number of scalar double arrays
    size_t elem_vectors = 2;  // Number of 3-element arrays
    size_t elem_int = 2;      // Number of integer arrays

    stats.element_arrays_bytes = NumEle * elem_scalars * sizeof(double) +
                                 NumEle * elem_vectors * 3 * sizeof(double) +
                                 NumEle * elem_int * sizeof(int);

    stats.river_arrays_bytes = NumRiv * 15 * sizeof(double) + NumRiv * 3 * sizeof(int);
    stats.total_allocated = stats.element_arrays_bytes + stats.river_arrays_bytes;

    // Get GPU memory info
    size_t free, total;
    CUDA_CHECK(cudaMemGetInfo(&free, &total));
    stats.gpu_free = free;
    stats.gpu_total = total;

    return stats;
}

// Helper template implementations
namespace GPUMemHelper {
    template<typename T>
    void allocateDeviceArray(T** d_ptr, size_t count, const char* name) {
        CUDA_CHECK(cudaMalloc(d_ptr, count * sizeof(T)));
        if (name) {
            printf("[GPU] Allocated %s: %zu elements\n", name, count);
        }
    }

    template<typename T>
    void freeDeviceArray(T* d_ptr) {
        if (d_ptr) {
            cudaFree(d_ptr);
        }
    }

    template<typename T>
    void copyHostToDevice(T* d_ptr, const T* h_ptr, size_t count) {
        CUDA_CHECK(cudaMemcpy(d_ptr, h_ptr, count * sizeof(T), cudaMemcpyHostToDevice));
    }

    template<typename T>
    void copyDeviceToHost(T* h_ptr, const T* d_ptr, size_t count) {
        CUDA_CHECK(cudaMemcpy(h_ptr, d_ptr, count * sizeof(T), cudaMemcpyDeviceToHost));
    }

    template<typename T>
    void zeroDeviceArray(T* d_ptr, size_t count) {
        CUDA_CHECK(cudaMemset(d_ptr, 0, count * sizeof(T)));
    }
}
