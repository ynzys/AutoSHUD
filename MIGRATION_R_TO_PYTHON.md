# Migration Guide: R Version → Python Version (pyAutoSHUD)

This guide helps you migrate from the legacy R-based AutoSHUD to the modern Python implementation.

---

## 📋 Quick Comparison

| Feature | R Version | Python Version |
|---------|-----------|----------------|
| **Language** | R | Python 3.8+ |
| **Interface** | R scripts | CLI + Python API |
| **Dependencies** | raster, sp, rgdal, rgeos | geopandas, rasterio, xarray |
| **Performance** | ~1x | ~1x (CPU), 5-20x (GPU) |
| **GPU Support** | ❌ No | ✅ Yes (CUDA) |
| **Documentation** | Basic | Comprehensive |
| **Configuration** | R variables | YAML files |
| **Maintenance** | Deprecated | Active |

---

## 🚀 Migration Steps

### Step 1: Install Python Version

```bash
cd pyAutoSHUD

# Install dependencies
pip install -r requirements.txt

# Verify installation
pyautoshud --version
```

### Step 2: Convert Your Workflow

#### R Workflow (Old)

```r
# Step 0: Delineation
source("Setp0.1_Delineation.R")

# Step 2: Data Subset
source("Step2_DataSubset.R")
source("Step2.1_Soil.R")
source("Step2.3_Forcing.R")

# Step 3: Build Model
source("Step3_BuidModel.R")

# Step 4: Run SHUD
system("./shud input output")

# Step 5: Visualization
source("Step5.1_FloodAnimation.R")
```

#### Python Workflow (New)

```bash
# Initialize project
pyautoshud init myproject

# Edit configuration
nano myproject/config.yaml

# Run complete workflow (all steps)
pyautoshud run myproject/config.yaml

# Or run step by step
pyautoshud preprocess myproject/config.yaml
pyautoshud build myproject/config.yaml
pyautoshud simulate myproject/config.yaml
pyautoshud analyze myproject/config.yaml
```

### Step 3: Convert Configuration

#### R Configuration (Old)

```r
# In your R script
project_name <- "MyProject"
start_year <- 2010
end_year <- 2015
dem_path <- "data/dem.tif"
outlet_point <- c(-76.5, 40.8)
```

#### Python Configuration (New)

```yaml
# myproject/config.yaml
name: MyProject
start_year: 2010
end_year: 2015
output_dir: output/myproject

input_data:
  dem: data/dem.tif
  outlet:
    lon: -76.5
    lat: 40.8

data_sources:
  soil: ISRIC_SoilGrids
  landcover: NLCD
  forcing: NLDAS

mesh:
  max_area: 1000000  # m²
  min_angle: 30

model:
  dt: 60  # minutes
  spinup_days: 365
```

### Step 4: Update Data Paths

Python version uses more standard paths:

```bash
# Old R structure
project/
├── DEM/
├── Soil/
├── Landcover/
└── Forcing/

# New Python structure
project/
├── config.yaml
├── input/
│   ├── spatial/     # DEM, soil, landcover
│   ├── forcing/     # Climate data
│   └── mesh/        # Generated mesh
├── output/
│   ├── raw/         # SHUD outputs
│   └── processed/   # Analysis results
└── logs/
```

---

## 📖 Command Equivalency Table

| R Script | Python Command | Description |
|----------|----------------|-------------|
| `Setp0.1_Delineation.R` | `pyautoshud preprocess --delineate` | Watershed delineation |
| `Step2_DataSubset.R` | `pyautoshud preprocess --extract-data` | Extract spatial data |
| `Step2.1_Soil.R` | `pyautoshud preprocess --soil` | Process soil data |
| `Step2.3_Forcing.R` | `pyautoshud preprocess --forcing` | Process climate data |
| `Step3_BuidModel.R` | `pyautoshud build` | Build SHUD model |
| `shud` command | `pyautoshud simulate` | Run simulation |
| `Step5.1_FloodAnimation.R` | `pyautoshud visualize` | Create animations |
| Manual analysis | `pyautoshud analyze` | Water balance analysis |
| Manual calibration | `pyautoshud calibrate` | Parameter calibration |

---

## 💻 Code Examples

### Example 1: Data Preprocessing

#### R Version (Old)

```r
library(raster)
library(sp)

# Load DEM
dem <- raster("data/dem.tif")

# Delineate watershed
outlet <- SpatialPoints(data.frame(x=-76.5, y=40.8))
watershed <- delineateWatershed(dem, outlet)

# Extract soil data
soil <- extractSoilData(watershed, source="SoilGrids")
```

#### Python Version (New)

```python
from pyautoshud.data import DEM, Soil
from pyautoshud.mesh import MeshGenerator

# Load DEM
dem = DEM.from_file("data/dem.tif")

# Delineate watershed
watershed = dem.delineate_watershed(
    outlet=(-76.5, 40.8),
    threshold=1000
)

# Extract soil data
soil = Soil.from_source(
    "ISRIC_SoilGrids",
    boundary=watershed.boundary
)
```

Or simply use CLI:

```bash
pyautoshud preprocess config.yaml
```

### Example 2: Model Building

#### R Version (Old)

```r
source("Rfunction/mesh_generation.R")
source("Rfunction/attribute_attachment.R")

# Generate mesh
mesh <- generateMesh(watershed, maxarea=1e6)

# Attach attributes
model <- attachAttributes(mesh, soil, lc, forcing)

# Write SHUD files
writeSHUDFiles(model, "output/")
```

#### Python Version (New)

```python
from pyautoshud.model import ModelBuilder

# Build complete model
builder = ModelBuilder(config_file="config.yaml")
builder.generate_mesh()
builder.attach_attributes()
builder.write_shud_files()
```

Or use CLI:

```bash
pyautoshud build config.yaml
```

### Example 3: Running Simulation

#### R Version (Old)

```r
# Run SHUD
system("./shud input/ output/")

# Read results
library(ncdf4)
results <- nc_open("output/YEsurf.nc")
surf_water <- ncvar_get(results, "Y_surf")
```

#### Python Version (New)

```python
from pyautoshud.runner import SHUDRunner
from pyautoshud.analysis import ResultAnalyzer

# Run simulation
runner = SHUDRunner("config.yaml")
runner.run()

# Analyze results
analyzer = ResultAnalyzer("output/")
surf_water = analyzer.read_surface_water()
analyzer.plot_timeseries()
```

Or use CLI:

```bash
pyautoshud simulate config.yaml
pyautoshud analyze config.yaml
```

---

## 🎯 Feature Migration

### Data Sources

Both versions support the same data sources:

| Data Type | Source Options |
|-----------|----------------|
| Soil | ISRIC SoilGrids, SSURGO, Custom |
| Landcover | NLCD, GLC, MODIS |
| Forcing | NLDAS, GLDAS, FLDAS, CMFD, Custom |
| DEM | ASTER GDEM, SRTM, Custom |

### Mesh Generation

Python version uses same triangulation algorithm:
- Triangle library (Delaunay triangulation)
- Same parameters: max_area, min_angle
- Improved quality checks

### File Formats

Python version is **fully compatible** with SHUD C++ input files:
- `.mesh` - Same format
- `.att` - Same format
- `.para.*` - Same format
- `.forc` - Same format

Your existing SHUD input files can be used directly!

---

## ⚡ GPU Acceleration (New Feature)

The Python version includes GPU acceleration for SHUD core:

```bash
# Install GPU patch
cd pyAutoSHUD/shud_gpu_patch
./INSTALL.sh ../../shud_src

# Compile GPU version
cd ../../shud_src
make -f Makefile.gpu

# Run with GPU
./shud_gpu input/ output/
```

Expected speedup: **5-20x faster** (depending on mesh size)

See: [pyAutoSHUD/shud_gpu_patch/GPU_README.md](pyAutoSHUD/shud_gpu_patch/GPU_README.md)

---

## 🐛 Common Issues

### Issue 1: Python Dependencies

```bash
# Error: ModuleNotFoundError
pip install -r pyAutoSHUD/requirements.txt

# If GDAL fails
conda install -c conda-forge gdal
```

### Issue 2: Configuration Format

R uses variables, Python uses YAML:

```r
# R (Old)
project_name <- "Test"
```

```yaml
# YAML (New)
name: Test
```

Use online converters or see examples in `pyAutoSHUD/examples/`

### Issue 3: Data Paths

Update absolute paths in your workflows:

```bash
# Use relative paths
input/dem.tif  # Good
/home/user/project/data/dem.tif  # Avoid
```

### Issue 4: R Functions Not Available

Some R-specific functions need Python equivalents:

| R Function | Python Equivalent |
|------------|-------------------|
| `raster()` | `rasterio.open()` |
| `sp::SpatialPoints()` | `geopandas.GeoDataFrame()` |
| `rgdal::readOGR()` | `geopandas.read_file()` |

---

## 📚 Learning Resources

### Documentation

- **Python API**: `pyAutoSHUD/docs/API.md`
- **CLI Reference**: `pyautoshud --help`
- **Examples**: `pyAutoSHUD/examples/`
- **Tutorials**: `pyAutoSHUD/tutorials/`

### Getting Help

1. Check documentation first
2. Look at examples in `pyAutoSHUD/examples/`
3. GitHub Issues: https://github.com/ynzys/AutoSHUD/issues
4. Email: lele.shu@gmail.com

---

## ✅ Migration Checklist

- [ ] Install Python 3.8+
- [ ] Install pyAutoSHUD dependencies
- [ ] Convert R configuration to YAML
- [ ] Update data paths
- [ ] Test preprocessing step
- [ ] Test model building
- [ ] Test simulation run
- [ ] Verify results match R version
- [ ] Update documentation/workflows
- [ ] Archive R scripts

---

## 🎓 Example Migration Project

Complete example of migrating a project:

```bash
# 1. Setup
mkdir my_migrated_project
cd my_migrated_project

# 2. Initialize Python project
pyautoshud init .

# 3. Copy your data
cp -r ~/old_r_project/DEM/* input/spatial/
cp -r ~/old_r_project/Forcing/* input/forcing/

# 4. Edit config.yaml with your parameters
nano config.yaml

# 5. Run complete workflow
pyautoshud run config.yaml

# 6. Compare with R results
python compare_results.py old_r_project/output output/
```

---

## 💡 Tips for Smooth Migration

1. **Start small**: Migrate one project first
2. **Keep R scripts**: Use `legacy/r-version/` for reference
3. **Use examples**: Copy from `pyAutoSHUD/examples/`
4. **Test thoroughly**: Verify results match
5. **Ask for help**: GitHub Issues or email

---

## 📞 Support

Need help with migration?

- **Documentation**: pyAutoSHUD/README.md
- **Issues**: GitHub Issues
- **Email**: lele.shu@gmail.com

---

**Migration completed?** Delete your R scripts or archive them in `legacy/`.

**Welcome to pyAutoSHUD!** 🎉
