// gpu_types.hpp
// GPU data types and structures for SHUD
// Created for SHUD GPU acceleration
//
// This file defines GPU-compatible data structures

#ifndef GPU_TYPES_HPP
#define GPU_TYPES_HPP

#include <cuda_runtime.h>
#include "Macros.hpp"

// GPU-compatible element structure (Structure of Arrays for better coalescing)
struct GPUElementArrays {
    // Geometry
    double *area;
    double *zmax;
    double *zmin;
    double *AquiferDepth;
    double *depression;

    // State variables
    double *uYsf;  // Surface water depth
    double *uYus;  // Unsaturated zone storage
    double *uYgw;  // Groundwater depth

    // Soil properties
    double *ThetaS;    // Saturated water content
    double *ThetaR;    // Residual water content
    double *ThetaW;    // Wilting point
    double *ThetaF;    // Field capacity
    double *Alpha;     // van Genuchten alpha
    double *Beta;      // van Genuchten n
    double *KsatV;     // Vertical saturated hydraulic conductivity
    double *KsatH;     // Horizontal saturated hydraulic conductivity
    double *InfD;      // Infiltration depth
    double *RzD;       // Rooting zone depth
    double *MacD;      // Macropore depth
    double *MacKsatV;  // Macropore vertical conductivity
    double *Porosity;  // Porosity
    double *AreaF;     // Macropore area fraction

    // Geology properties
    double *Kmacv_geol;
    double *Kh_geol;
    double *Sy;        // Specific yield

    // Landcover properties
    double *VegFrac;   // Vegetation fraction
    double *Albedo;
    double *Rs_min;    // Minimum stomatal resistance
    double *Rgl;       // Reference radiation
    double *Hs;        // Vapor pressure deficit
    double *RzD_lc;    // Root zone depth from landcover

    // Neighbor topology (3 neighbors per element)
    int *nabr;         // [NumEle * 3] neighbor indices (0 = boundary)
    double *edge;      // [NumEle * 3] edge lengths

    // Computed fluxes
    double *qInfil;    // Infiltration rate
    double *qRecharge; // Recharge rate
    double *qExfil;    // Exfiltration rate
    double *qNetPrep;  // Net precipitation
    double *qEs;       // Evaporation from surface
    double *qEu;       // Transpiration from unsat zone
    double *qEg;       // Evaporation from groundwater
    double *qTu;       // Transpiration from unsat zone
    double *qTg;       // Transpiration from groundwater

    // Surface and subsurface lateral fluxes
    double *QeleSurf;  // [NumEle * 3] Surface lateral flux
    double *QeleSub;   // [NumEle * 3] Subsurface lateral flux

    // Derivatives for ODE solver
    double *DY_sf;     // dY/dt for surface
    double *DY_us;     // dY/dt for unsaturated
    double *DY_gw;     // dY/dt for groundwater

    // Element attributes
    int *iBC;          // Boundary condition index
    int *iSS;          // Source/sink index
    double *QBC;       // Boundary flux
    double *QSS;       // Source/sink flux
};

// GPU-compatible river structure
struct GPURiverArrays {
    // Geometry
    double *length;
    double *width;
    double *depth;
    double *rough;

    // State
    double *uYriv;     // River stage

    // Properties
    double *KsatH;     // Bed hydraulic conductivity
    double *bedThick;  // Bed thickness

    // Fluxes
    double *QrivDown;  // Downstream flux
    double *QrivUp;    // Upstream flux
    double *QrivSurf;  // Surface exchange
    double *QrivSub;   // Subsurface exchange

    // Topology
    int *down;         // Downstream river index
    int *up;           // Upstream river index

    // BC
    int *BC;           // Boundary condition
    double *qBC;       // BC flux
};

// GPU memory statistics
struct GPUMemoryStats {
    size_t element_arrays_bytes;
    size_t river_arrays_bytes;
    size_t total_allocated;
    size_t gpu_free;
    size_t gpu_total;
};

#endif // GPU_TYPES_HPP
