# pyAutoSHUD 使用指南

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone <repository_url>
cd pyAutoSHUD

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

### 2. 创建配置文件

```bash
# 生成模板配置文件
pyautoshud init project.yaml

# 编辑配置文件，更新数据路径
nano project.yaml
```

### 3. 运行完整工作流

```bash
# 运行完整工作流（从数据预处理到模型运行）
pyautoshud run project.yaml

# 或分步执行
pyautoshud preprocess project.yaml
pyautoshud build project.yaml
pyautoshud simulate project.yaml
pyautoshud analyze project.yaml
```

## 详细使用说明

### 配置文件格式

pyAutoSHUD 支持两种配置文件格式：

1. **YAML 格式**（推荐）- 更现代、更易读
2. **文本格式** - 与 R 版本 AutoSHUD 兼容

#### YAML 配置示例

```yaml
project:
  name: "MyProject"
  start_year: 2017
  end_year: 2018
  output_dir: "./output"

data:
  dem: "data/elevation.tif"
  watershed_boundary: "data/wbd.shp"
  stream_network: "data/stm.shp"

  soil:
    source: "isric"
    data_dir: "/path/to/soil"

  landcover:
    source: "glc"
    file: "/path/to/landcover.tif"

  forcing:
    source: "gldas"
    data_dir: "/path/to/forcing"

model:
  num_cells: 1000
  max_area_km2: 10.0
  aquifer_depth: 20.0

simulation:
  start_day: 0
  solver_step: 2
```

### 命令行工具

#### 1. 数据预处理

```bash
# 仅运行数据预处理步骤
pyautoshud preprocess project.yaml
```

此步骤将：
- 处理 DEM 数据和流域边界
- 提取土壤数据
- 提取土地覆盖数据
- 准备气象强迫数据

#### 2. 模型构建

```bash
# 构建 SHUD 模型
pyautoshud build project.yaml
```

此步骤将：
- 生成 Delaunay 三角网格
- 提取单元属性
- 生成 SHUD 输入文件（.mesh, .riv, .att, .soil, .geol, .lc, .para, .calib等）

#### 3. 模型运行

```bash
# 编译并运行 SHUD 模型
pyautoshud simulate project.yaml

# 仅编译
pyautoshud simulate project.yaml --compile-only
```

#### 4. 结果分析

```bash
# 分析模拟结果
pyautoshud analyze project.yaml

# 可视化结果
pyautoshud visualize project.yaml
```

#### 5. 参数率定

```bash
# 使用 NSGA2 算法率定
pyautoshud calibrate project.yaml --algorithm NSGA2 --iterations 100

# 使用 PSO 算法
pyautoshud calibrate project.yaml --algorithm PSO --iterations 50

# 指定输出文件
pyautoshud calibrate project.yaml -a NSGA2 -i 100 -o results.csv
```

## 数据源配置

### 土壤数据

支持的数据源：
- `isric` - ISRIC SoilGrids（全球，250m）
- `ssurgo` - USDA SSURGO（美国）
- `local` - 本地数据

配置示例：

```yaml
soil:
  source: "isric"
  data_dir: "/data/ISRIC_SoilGrids"

  # 本地数据配置
  # source: "local"
  # file: "data/soil.tif"
  # table: "data/soil_params.csv"
```

### 土地覆盖数据

支持的数据源：
- `glc` - USGS Global Land Cover
- `nlcd` - NLCD（美国）
- `local` - 本地数据

### 气象强迫数据

支持的数据源：
- `gldas` - GLDAS（全球）
- `nldas` - NLDAS（北美）
- `cmfd` - CMFD（中国）
- `cmip6` - CMIP6 气候预估
- `fldas` - FLDAS（非洲）
- `local` - 本地数据

## 参数率定详细说明

### 率定算法

#### NSGA-II
多目标优化算法，适用于多个目标函数的同时优化。

```yaml
calibration:
  algorithm: "NSGA2"
  iterations: 100
  population_size: 50
  objectives: ["NSE", "RMSE"]
```

#### PSO (Particle Swarm Optimization)
粒子群优化算法，快速收敛。

#### SCE-UA (Shuffled Complex Evolution)
经典水文模型率定算法。

#### DDS (Dynamically Dimensioned Search)
适用于高维参数空间。

### 目标函数

支持的目标函数：
- `NSE` - Nash-Sutcliffe Efficiency
- `RMSE` - Root Mean Square Error
- `KGE` - Kling-Gupta Efficiency
- `PBIAS` - Percent Bias
- `R2` - Coefficient of Determination

### 率定参数

常用率定参数：

```yaml
parameters:
  # 地质参数
  - name: "GEOL_KSATH"  # 水平饱和导水率
    min: 0.1
    max: 10.0

  - name: "GEOL_KSATV"  # 垂直饱和导水率
    min: 0.1
    max: 10.0

  # 土壤参数
  - name: "SOIL_KINF"  # 入渗率
    min: 0.001
    max: 1.0

  - name: "SOIL_ALPHA"  # van Genuchten α
    min: 0.5
    max: 2.0

  - name: "SOIL_BETA"  # van Genuchten β
    min: 0.5
    max: 2.0

  # 河道参数
  - name: "RIV_ROUGH"  # 河道糙率
    min: 0.01
    max: 0.5

  - name: "RIV_KH"  # 河床导水率
    min: 0.1
    max: 10.0

  # 土地覆盖参数
  - name: "LC_ROUGH"  # 地表糙率
    min: 0.5
    max: 2.0
```

## 输出文件

### 模型输入文件

生成的 SHUD 输入文件位于 `output/<project_name>/input/<project_name>/`：

- `<name>.sp.mesh` - 网格文件
- `<name>.sp.riv` - 河流文件
- `<name>.sp.att` - 属性文件
- `<name>.sp.rivseg` - 河段文件
- `<name>.para.soil` - 土壤参数
- `<name>.para.geol` - 地质参数
- `<name>.para.lc` - 土地覆盖参数
- `<name>.cfg.para` - 模型参数
- `<name>.cfg.calib` - 率定参数
- `<name>.cfg.ic` - 初始条件
- `<name>.tsd.*` - 时间序列数据

### 模型输出文件

SHUD 输出文件位于 `output/<project_name>/output/<project_name>.out/`：

- 水文状态变量时间序列
- 通量时间序列
- 水量平衡报告

### 可视化结果

图片保存在 `output/<project_name>/Image/`：

- 网格和流域示意图
- 水文要素分布图
- 时间序列图
- 水量平衡图

## 故障排除

### 常见问题

1. **GDAL 安装问题**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install gdal-bin libgdal-dev

   # macOS
   brew install gdal

   # 然后安装 Python 绑定
   pip install GDAL==$(gdal-config --version)
   ```

2. **triangle 包编译问题**
   ```bash
   # 需要 C 编译器
   # Ubuntu/Debian
   sudo apt-get install build-essential

   # macOS
   xcode-select --install
   ```

3. **SHUD 编译失败**
   - 确保安装了 SUNDIALS v6.0+
   - 检查编译器版本（需要 gcc 或 clang）

4. **内存不足**
   - 减小 `num_cells` 参数
   - 增大 `max_area_km2` 参数
   - 使用 `quick_mode: true`

## 性能优化

### 加速数据处理

1. 使用多核处理：
   ```python
   # 在配置中启用并行
   export OMP_NUM_THREADS=8
   ```

2. 使用快速模式（测试用）：
   ```yaml
   model:
     quick_mode: true
     num_cells: 100  # 更少的单元
   ```

### 加速模型运行

1. 调整求解器步长：
   ```yaml
   simulation:
     solver_step: 10  # 更大的步长（分钟）
   ```

2. 减少输出频率：
   编辑 `.cfg.para` 文件中的 `DT_*` 参数

## Python API 使用

除了命令行工具，也可以直接在 Python 代码中使用：

```python
from pyautoshud import ProjectConfig, AutoSHUDWorkflow

# 加载配置
config = ProjectConfig.from_yaml('project.yaml')

# 创建工作流
workflow = AutoSHUDWorkflow(config)

# 运行完整工作流
workflow.run_all()

# 或分步执行
workflow.preprocess_data()
workflow.build_model()
workflow.run_simulation()
workflow.analyze_results()

# 参数率定
workflow.calibrate(algorithm='NSGA2', iterations=100)
```

## 从 R 版本迁移

如果你之前使用 R 版本的 AutoSHUD，可以直接使用现有的配置文件：

```bash
# pyAutoSHUD 兼容 R 版本的 project.txt 格式
pyautoshud run project.txt

# 或转换为 YAML 格式
python -c "
from pyautoshud.config import ProjectConfig
config = ProjectConfig.from_txt('project.txt')
config.to_yaml('project.yaml')
"
```

## 进一步帮助

- GitHub Issues: <repository_url>/issues
- 文档: https://pyautoshud.readthedocs.io
- SHUD 官网: https://www.shud.xyz
