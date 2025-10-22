// gpu_kernels.cu
// CUDA kernel implementations for SHUD hydrological computations
//

#include "gpu_kernels.cuh"
#include <cuda_runtime.h>
#include <math.h>

#define EPSILON 1e-10
#define ZERO 1e-10

// ============================================================================
// Device utility functions (hydrological equations on GPU)
// ============================================================================

__device__ inline double d_avgY_sf(double z1, double y1, double z2, double y2, double threshold) {
    double h1 = z1 + y1;
    double h2 = z2 + y2;

    if (h1 > h2) {
        return (y1 > threshold) ? y1 : 0.0;
    } else {
        return (y2 > threshold) ? y2 : 0.0;
    }
}

__device__ inline double d_avgY_gw(double z1, double y1, double z2, double y2, double threshold) {
    y1 = fmax(y1, 0.0);
    y2 = fmax(y2, 0.0);
    return (y1 + y2) * 0.5;
}

__device__ inline double d_effKV(double ksatFunc, double gradY, double macKV, double KV, double areaF) {
    if (ksatFunc >= 0.98) {
        return (macKV * areaF + KV * (1.0 - areaF) * ksatFunc);
    } else {
        if (fabs(gradY) * ksatFunc * KV <= KV * ksatFunc) {
            return KV * ksatFunc;
        } else {
            if (fabs(gradY) * ksatFunc * KV < (macKV * areaF + KV * (1.0 - areaF) * ksatFunc)) {
                return (macKV * areaF * ksatFunc + KV * (1.0 - areaF) * ksatFunc);
            } else {
                return (macKV * areaF + KV * (1.0 - areaF) * ksatFunc);
            }
        }
    }
}

__device__ inline double d_effKH(double Ygw, double aqDepth, double MacD, double Kmac, double AF, double Kmx) {
    double effk = 0.0;
    if (MacD <= ZERO || Ygw < aqDepth - MacD) {
        effk = Kmx;
    } else {
        if (Ygw > aqDepth) {
            effk = (Kmac * MacD * AF + Kmx * (aqDepth - MacD * AF)) / aqDepth;
        } else {
            effk = (Kmac * (Ygw - (aqDepth - MacD)) * AF +
                    Kmx * (aqDepth - MacD + (Ygw - (aqDepth - MacD)) * (1.0 - AF))) / Ygw;
        }
    }
    return effk;
}

__device__ inline double d_satKfun(double elemSatn, double n) {
    double temp = -1.0 + pow(1.0 - pow(elemSatn, n / (n - 1.0)), (n - 1.0) / n);
    return sqrt(elemSatn) * temp * temp;
}

__device__ inline double d_GreenAmpt(double k, double ti, double ts, double phi, double hf, double h0, double Sy) {
    double dTheta = ts - ti;
    double q = 0.0;

    if (h0 <= 0) {
        return 0.0;
    }

    hf = fmax(EPSILON, hf);

    if (dTheta <= 0.0) {
        q = 0.0;
    } else {
        q = k * ((h0 + hf - phi) * dTheta / hf);
    }

    if (q >= 0.0) {
        q = fmin(q, h0);
    }

    return q;
}

// ============================================================================
// Element update kernel
// ============================================================================

__global__ void kernel_update_elements(
    GPUElementArrays elem,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        // Update element state based on water depths
        double ysf = elem.uYsf[i];
        double yus = elem.uYus[i];
        double ygw = elem.uYgw[i];

        // Calculate saturation
        double deficit = fmax(elem.AquiferDepth[i] - ygw, 0.01);
        double satn = (yus > 0.0) ? (yus / deficit) : 0.0;
        satn = fmin(fmax(satn, 0.0), 1.0);

        // Calculate relative hydraulic conductivity
        double beta = elem.Beta[i];
        double satKr = d_satKfun(satn, beta);

        // Store computed values (if needed for later kernels)
        // Could add temporary storage arrays if needed
    }
}

// ============================================================================
// Infiltration kernel
// ============================================================================

__global__ void kernel_infiltration(
    GPUElementArrays elem,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        double ysf = elem.uYsf[i];
        double yus = elem.uYus[i];
        double ygw = elem.uYgw[i];

        // Green-Ampt infiltration
        if (ysf > EPSILON) {
            double deficit = fmax(elem.AquiferDepth[i] - ygw, 0.01);
            double satn = (yus > 0.0) ? (yus / deficit) : 0.0;
            satn = fmin(fmax(satn, 0.0), 1.0);

            double thetaS = elem.ThetaS[i];
            double thetaR = elem.ThetaR[i];
            double theta_curr = thetaR + (thetaS - thetaR) * satn;

            double ksatV = elem.KsatV[i];
            double macKsatV = elem.MacKsatV[i];
            double areaF = elem.AreaF[i];

            // Simplified infiltration rate
            double beta = elem.Beta[i];
            double satKr = d_satKfun(satn, beta);
            double effK = d_effKV(satKr, 1.0, macKsatV, ksatV, areaF);

            // Infiltration rate (m/day)
            double qInfil = effK * (1.0 + ysf / 0.1); // Simplified gradient
            qInfil = fmin(qInfil, ysf / (1.0 / 1440.0)); // Limit to available water

            elem.qInfil[i] = qInfil;
        } else {
            elem.qInfil[i] = 0.0;
        }
    }
}

// ============================================================================
// Recharge kernel
// ============================================================================

__global__ void kernel_recharge(
    GPUElementArrays elem,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        double yus = elem.uYus[i];
        double ygw = elem.uYgw[i];

        if (yus > EPSILON) {
            double deficit = fmax(elem.AquiferDepth[i] - ygw, 0.01);
            double ksatV = elem.KsatV[i];
            double macKsatV = elem.MacKsatV[i];
            double areaF = elem.AreaF[i];

            // Simplified recharge calculation
            double effK = (areaF <= 0.0) ? ksatV : (ksatV * (1.0 - areaF) + macKsatV * areaF);
            double qRecharge = effK * (1.0 + yus / (deficit * 0.5));

            elem.qRecharge[i] = qRecharge;
        } else {
            elem.qRecharge[i] = 0.0;
        }
    }
}

// ============================================================================
// Exfiltration kernel
// ============================================================================

__global__ void kernel_exfiltration(
    GPUElementArrays elem,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        double ygw = elem.uYgw[i];
        double aqDepth = elem.AquiferDepth[i];

        // Exfiltration occurs when groundwater exceeds aquifer depth
        if (ygw > aqDepth + EPSILON) {
            double excess = ygw - aqDepth;
            elem.qExfil[i] = excess * elem.Sy[i] * 1440.0; // Convert to daily rate
        } else {
            elem.qExfil[i] = 0.0;
        }
    }
}

// ============================================================================
// Surface lateral flux kernel
// ============================================================================

__global__ void kernel_surface_flux(
    GPUElementArrays elem,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        double ysf_i = elem.uYsf[i];
        double z_i = elem.zmax[i];
        double area_i = elem.area[i];

        // Calculate flux to each of 3 neighbors
        for (int j = 0; j < 3; j++) {
            int nabr_idx = elem.nabr[i * 3 + j];

            if (nabr_idx > 0) {  // Valid neighbor (not boundary)
                int n = nabr_idx - 1;  // Convert to 0-indexed

                double ysf_n = elem.uYsf[n];
                double z_n = elem.zmax[n];
                double edge_len = elem.edge[i * 3 + j];

                // Average water depth for flux calculation
                double avg_y = d_avgY_sf(z_i, ysf_i, z_n, ysf_n, elem.depression[i]);

                if (avg_y > EPSILON) {
                    // Manning's equation (simplified)
                    double h1 = z_i + ysf_i;
                    double h2 = z_n + ysf_n;
                    double grad = fabs(h1 - h2) / fmax(1.0, sqrt(area_i));
                    double rough = 0.05;  // Simplified roughness

                    // Overland flow (Manning)
                    double Q = edge_len * pow(avg_y, 2.0/3.0) * sqrt(grad) / rough;

                    // Direction of flow
                    if (h1 > h2) {
                        elem.QeleSurf[i * 3 + j] = -Q;  // Outflow
                    } else {
                        elem.QeleSurf[i * 3 + j] = Q;   // Inflow
                    }
                } else {
                    elem.QeleSurf[i * 3 + j] = 0.0;
                }
            } else {
                elem.QeleSurf[i * 3 + j] = 0.0;  // No flux at boundary
            }
        }
    }
}

// ============================================================================
// Subsurface lateral flux kernel
// ============================================================================

__global__ void kernel_subsurface_flux(
    GPUElementArrays elem,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        double ygw_i = elem.uYgw[i];
        double zmin_i = elem.zmin[i];
        double area_i = elem.area[i];
        double kh_i = elem.Kh_geol[i];

        // Calculate flux to each of 3 neighbors
        for (int j = 0; j < 3; j++) {
            int nabr_idx = elem.nabr[i * 3 + j];

            if (nabr_idx > 0) {
                int n = nabr_idx - 1;

                double ygw_n = elem.uYgw[n];
                double zmin_n = elem.zmin[n];
                double kh_n = elem.Kh_geol[n];
                double edge_len = elem.edge[i * 3 + j];

                // Average depth and hydraulic conductivity
                double avg_ygw = d_avgY_gw(zmin_i, ygw_i, zmin_n, ygw_n, EPSILON);

                if (avg_ygw > EPSILON) {
                    // Darcy's law for groundwater flow
                    double h1 = zmin_i + ygw_i;
                    double h2 = zmin_n + ygw_n;
                    double grad = (h1 - h2) / fmax(1.0, sqrt(area_i));

                    // Harmonic mean of conductivities
                    double kh_avg = (kh_i > ZERO && kh_n > ZERO) ?
                                    (2.0 * kh_i * kh_n / (kh_i + kh_n)) : 0.0;

                    // Darcy flux
                    double Q = kh_avg * edge_len * avg_ygw * grad;

                    elem.QeleSub[i * 3 + j] = -Q;  // Sign convention: negative = outflow
                } else {
                    elem.QeleSub[i * 3 + j] = 0.0;
                }
            } else {
                elem.QeleSub[i * 3 + j] = 0.0;
            }
        }
    }
}

// ============================================================================
// Apply derivatives kernel (ODE right-hand side)
// ============================================================================

__global__ void kernel_apply_derivatives(
    GPUElementArrays elem,
    double *DY,
    int NumEle,
    double t
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        double area = elem.area[i];

        // Sum lateral fluxes
        double QeleSurfTot = 0.0;
        double QeleSubTot = 0.0;
        for (int j = 0; j < 3; j++) {
            QeleSurfTot += elem.QeleSurf[i * 3 + j];
            QeleSubTot += elem.QeleSub[i * 3 + j];
        }

        // Surface water balance: dY_sf/dt
        int isf = i;
        DY[isf] = elem.qNetPrep[i] - elem.qInfil[i] + elem.qExfil[i]
                  - QeleSurfTot / area - elem.qEs[i];

        // Unsaturated zone balance: dY_us/dt
        int ius = NumEle + i;
        DY[ius] = elem.qInfil[i] - elem.qRecharge[i] - elem.qEu[i] - elem.qTu[i];
        DY[ius] /= elem.Sy[i];

        // Groundwater balance: dY_gw/dt
        int igw = 2 * NumEle + i;
        DY[igw] = elem.qRecharge[i] - elem.qExfil[i] - QeleSubTot / area
                  - elem.qEg[i] - elem.qTg[i];

        // Boundary conditions
        if (elem.iBC[i] > 0) {
            DY[igw] = 0.0;  // Fixed head
        } else if (elem.iBC[i] < 0) {
            DY[igw] += elem.QBC[i] / area;  // Fixed flux
        }

        // Source/sink terms
        if (elem.iSS[i] > 0) {
            DY[isf] += elem.QSS[i] / area;
        } else if (elem.iSS[i] < 0) {
            DY[igw] += elem.QSS[i] / area;
        }

        // Convert with specific yield
        DY[igw] /= elem.Sy[i];
    }
}

// ============================================================================
// Zero fluxes kernel
// ============================================================================

__global__ void kernel_zero_fluxes(GPUElementArrays elem, int NumEle) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < NumEle) {
        elem.qInfil[i] = 0.0;
        elem.qRecharge[i] = 0.0;
        elem.qExfil[i] = 0.0;
        elem.qEs[i] = 0.0;
        elem.qEu[i] = 0.0;
        elem.qEg[i] = 0.0;
        elem.qTu[i] = 0.0;
        elem.qTg[i] = 0.0;

        for (int j = 0; j < 3; j++) {
            elem.QeleSurf[i * 3 + j] = 0.0;
            elem.QeleSub[i * 3 + j] = 0.0;
        }
    }
}

// ============================================================================
// Host functions (C++ callable)
// ============================================================================

extern "C" {

void get_launch_config(int N, int *gridSize, int *blockSize) {
    *blockSize = 256;  // Typical block size
    *gridSize = (N + *blockSize - 1) / *blockSize;
}

void gpu_update_all(GPUElementArrays& d_elem, int NumEle, double t) {
    int gridSize, blockSize;
    get_launch_config(NumEle, &gridSize, &blockSize);

    kernel_update_elements<<<gridSize, blockSize>>>(d_elem, NumEle, t);
    cudaDeviceSynchronize();
}

void gpu_compute_fluxes(GPUElementArrays& d_elem, int NumEle, double t) {
    int gridSize, blockSize;
    get_launch_config(NumEle, &gridSize, &blockSize);

    // Run all flux kernels sequentially
    kernel_infiltration<<<gridSize, blockSize>>>(d_elem, NumEle, t);
    kernel_recharge<<<gridSize, blockSize>>>(d_elem, NumEle, t);
    kernel_exfiltration<<<gridSize, blockSize>>>(d_elem, NumEle, t);
    kernel_surface_flux<<<gridSize, blockSize>>>(d_elem, NumEle, t);
    kernel_subsurface_flux<<<gridSize, blockSize>>>(d_elem, NumEle, t);

    cudaDeviceSynchronize();
}

void gpu_apply_dy(GPUElementArrays& d_elem, double *d_DY, int NumEle, double t) {
    int gridSize, blockSize;
    get_launch_config(NumEle, &gridSize, &blockSize);

    kernel_apply_derivatives<<<gridSize, blockSize>>>(d_elem, d_DY, NumEle, t);
    cudaDeviceSynchronize();
}

void gpu_zero_derivatives(double *d_DY, int NumY) {
    cudaMemset(d_DY, 0, NumY * sizeof(double));
}

void gpu_synchronize() {
    cudaDeviceSynchronize();
}

} // extern "C"
