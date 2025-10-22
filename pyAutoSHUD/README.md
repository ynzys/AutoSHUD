# pyAutoSHUD - Python版水文模型自动化部署工具

## 项目简介

**pyAutoSHUD** 是 AutoSHUD (R语言版本) 的 Python 重构版本，用于自动化部署 SHUD 水文模型。相比 R 语言版本，Python 版本具有以下优势：

- 更友好的依赖管理和环境配置
- 更强大的并行处理能力
- 更丰富的科学计算生态
- 更现代化的命令行界面
- 更高效的数据处理性能

## 主要功能

1. **数据预处理**
   - DEM 数据下载和处理
   - 流域划分和河网提取
   - 土壤数据处理（ISRIC SoilGrids、SSURGO等）
   - 土地覆盖数据处理（GLC、NLCD等）
   - 气象强迫数据处理（GLDAS、NLDAS、CMFD、CMIP6等）

2. **模型构建**
   - Delaunay 三角网格生成
   - 单元属性提取和分配
   - SHUD 输入文件生成

3. **模型执行**
   - SHUD 模型编译
   - 模型运行管理

4. **后处理分析**
   - 结果可视化
   - 水量平衡分析
   - 洪水动画生成
   - 参数率定（校准）

## 系统架构

```
pyAutoSHUD/
├── pyautoshud/              # 主要Python包
│   ├── __init__.py
│   ├── config/              # 配置管理
│   ├── data/                # 数据处理模块
│   │   ├── dem.py           # DEM处理
│   │   ├── soil.py          # 土壤数据
│   │   ├── landcover.py     # 土地覆盖
│   │   ├── forcing.py       # 气象数据
│   │   └── spatial.py       # 空间操作工具
│   ├── mesh/                # 网格生成
│   ├── model/               # 模型构建
│   ├── runner/              # 模型执行
│   ├── analysis/            # 结果分析
│   ├── calibration/         # 参数率定
│   ├── visualization/       # 可视化
│   └── utils/               # 工具函数
├── scripts/                 # 命令行脚本
├── tests/                   # 单元测试
├── examples/                # 示例项目
├── docs/                    # 文档
├── setup.py                 # 安装脚本
├── requirements.txt         # 依赖列表
├── pyproject.toml           # 项目配置
└── README.md
```

## 快速开始

### 安装

```bash
# 克隆代码库
git clone <repo_url>
cd pyAutoSHUD

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

### 基本使用

```bash
# 查看帮助
pyautoshud --help

# 运行完整工作流
pyautoshud run project.yaml

# 分步执行
pyautoshud preprocess project.yaml
pyautoshud build-model project.yaml
pyautoshud run-model project.yaml
pyautoshud postprocess project.yaml

# 参数率定
pyautoshud calibrate project.yaml --algorithm NSGA2
```

### 配置文件示例

```yaml
# project.yaml
project:
  name: "Example"
  start_year: 2017
  end_year: 2017
  output_dir: "./Example"

data:
  dem: "data/elevation.tif"
  watershed_boundary: "data/wbd.shp"
  stream_network: "data/stm.shp"
  lake: null  # 可选

  soil:
    source: "isric"  # isric, ssurgo, or local
    data_dir: "/path/to/soil/data"

  landcover:
    source: "glc"  # glc, nlcd, or local
    file: "/path/to/landuse.tif"

  forcing:
    source: "gldas"  # gldas, nldas, cmfd, cmip6, or local
    data_dir: "/path/to/forcing/data"

model:
  num_cells: 1000
  max_area_km2: 10.0
  min_angle: 31.0
  aquifer_depth: 20.0
  buffer_distance: 5000.0

simulation:
  start_day: 0
  end_day: 365
  solver_step: 2
  cryosphere: false

calibration:
  algorithm: "NSGA2"  # NSGA2, PSO, SCE-UA, DDS
  objective: ["NSE", "RMSE"]
  parameters:
    - name: "Ksat"
      min: 0.001
      max: 10.0
    - name: "RoughnessManning"
      min: 0.01
      max: 0.5
```

## 主要依赖

- Python >= 3.8
- geopandas >= 0.10
- rasterio >= 1.2
- xarray >= 0.19
- netCDF4 >= 1.5
- scipy >= 1.7
- numpy >= 1.20
- matplotlib >= 3.4
- click >= 8.0
- pyyaml >= 5.4
- triangle >= 20200424

## 对比 R 版本的改进

| 特性 | R 版本 | Python 版本 |
|------|--------|-------------|
| 配置文件 | 自定义格式 | YAML/TOML 标准格式 |
| 命令行 | Rscript | Click 现代CLI |
| 依赖管理 | 手动安装 | pip/conda 自动化 |
| 并行处理 | 有限 | multiprocessing/dask |
| 数据格式 | RDS | HDF5/NetCDF/Parquet |
| 测试 | 无 | pytest 单元测试 |
| 文档 | README | Sphinx 文档 |
| 类型检查 | 无 | Type hints |
| 代码风格 | 无 | Black/flake8 |

## 开发路线图

- [x] 项目架构设计
- [x] 核心模块实现
- [ ] 参数率定算法集成
- [ ] 性能优化（并行化）
- [ ] 完整的单元测试
- [ ] 文档和教程
- [ ] Docker 容器化
- [ ] Web 界面（可选）

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 许可证

与原 AutoSHUD 项目保持一致

## 联系方式

项目地址：[GitHub链接]

## 致谢

感谢原 AutoSHUD (R语言版本) 的作者提供的设计思路和实现参考。
