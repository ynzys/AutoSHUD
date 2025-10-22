# AutoSHUD - Automatic and Reproducible Hydrological Model Deployment

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![SHUD](https://img.shields.io/badge/SHUD-v2.0-orange.svg)](https://www.shud.xyz/)

**AutoSHUD** is an automatic and reproducible deployment tool for the SHUD (Simulator for Hydrologic Unstructured Domains) hydrological model.

🎉 **Now with Python implementation (pyAutoSHUD) and GPU acceleration!**

---

## 🚀 Quick Start

```bash
# Install
cd pyAutoSHUD
pip install -r requirements.txt

# Initialize project
pyautoshud init myproject

# Edit configuration
nano myproject/config.yaml

# Run complete workflow
pyautoshud run myproject/config.yaml
```

---

## 📦 Current Version: pyAutoSHUD (Python)

**pyAutoSHUD** is the modern Python implementation with:

- ✅ **Modern CLI interface** - Easy-to-use command-line tools
- ✅ **Better performance** - Optimized with pandas/numpy
- ✅ **GPU acceleration** - 5-20x faster with CUDA support
- ✅ **Comprehensive documentation** - User guides and API docs
- ✅ **Active development** - Regular updates and improvements
- ✅ **Full SHUD compatibility** - Works with SHUD v2.0

**Location**: [`pyAutoSHUD/`](pyAutoSHUD/)

**Documentation**: [`pyAutoSHUD/README.md`](pyAutoSHUD/README.md)

---

## ⚡ GPU Acceleration (NEW!)

SHUD-GPU provides CUDA acceleration for the SHUD core model:

- **5-20x speedup** (depending on mesh size)
- NVIDIA GPU support (Compute Capability 7.0+)
- Fully compatible with existing SHUD inputs

**Location**: [`pyAutoSHUD/shud_gpu_patch/`](pyAutoSHUD/shud_gpu_patch/)

**Quick Start**:
```bash
cd pyAutoSHUD/shud_gpu_patch
./INSTALL.sh ../../shud_src
cd ../../shud_src && make -f Makefile.gpu
./shud_gpu input/ output/
```

**Documentation**:
- [GPU Quick Start](pyAutoSHUD/shud_gpu_patch/GPU_QUICKSTART.md)
- [GPU User Guide](pyAutoSHUD/shud_gpu_patch/GPU_README.md)
- [GPU Feasibility Analysis](pyAutoSHUD/GPU_FEASIBILITY_ANALYSIS.md)

---

## 🗂️ Repository Structure

```
AutoSHUD/
├── pyAutoSHUD/              # Python implementation (CURRENT)
│   ├── pyautoshud/         # Main Python package
│   ├── examples/           # Example projects
│   ├── docs/               # Documentation
│   └── shud_gpu_patch/     # GPU acceleration patch
│
├── legacy/                 # Archived versions
│   └── r-version/          # R version (DEPRECATED)
│
├── MIGRATION_R_TO_PYTHON.md  # Migration guide
└── README.md               # This file
```

---

## 📋 Workflow

AutoSHUD automates the complete SHUD deployment:

1. **Data Preparation** - Download and process spatial data
2. **Model Building** - Generate mesh and attach attributes
3. **Simulation** - Run SHUD (CPU or GPU)
4. **Analysis** - Water balance and visualization
5. **Calibration** - Parameter optimization (optional)

---

## 📖 Documentation

### User Guides
- [pyAutoSHUD README](pyAutoSHUD/README.md) - Main documentation
- [GPU Quick Start](pyAutoSHUD/shud_gpu_patch/GPU_QUICKSTART.md)
- [Migration Guide](MIGRATION_R_TO_PYTHON.md) - For R users

### Data Sources
- Elevation: ASTER GDEM, SRTM
- Soil: ISRIC SoilGrids, SSURGO
- Land Cover: NLCD, GLC, MODIS
- Climate: NLDAS, GLDAS, FLDAS, CMFD

---

## ⚠️ Legacy R Version

The original R-based implementation has been **deprecated**:

**Location**: [`legacy/r-version/`](legacy/r-version/)

**Status**: No longer maintained (archived 2025-10-22)

**Migration**: See [MIGRATION_R_TO_PYTHON.md](MIGRATION_R_TO_PYTHON.md)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ynzys/AutoSHUD/issues)
- **Email**: lele.shu@gmail.com
- **Website**: https://www.shud.xyz/

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**pyAutoSHUD v2.0** with GPU acceleration

[Documentation](pyAutoSHUD/README.md) • [GPU Guide](pyAutoSHUD/shud_gpu_patch/GPU_README.md) • [Migration](MIGRATION_R_TO_PYTHON.md)

</div>
