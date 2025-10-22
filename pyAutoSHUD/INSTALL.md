# pyAutoSHUD 安装指南

## 系统要求

### 操作系统
- Linux (推荐 Ubuntu 20.04+, CentOS 8+)
- macOS (10.14+)
- Windows 10/11 (通过 WSL2)

### Python 版本
- Python 3.8 或更高版本

### 依赖软件
- GDAL >= 3.0
- GCC 或 Clang 编译器（用于编译 SHUD）
- Git

## 安装步骤

### 1. 安装系统依赖

#### Ubuntu/Debian

```bash
# 更新包列表
sudo apt-get update

# 安装 GDAL
sudo apt-get install -y gdal-bin libgdal-dev

# 安装编译工具
sudo apt-get install -y build-essential gfortran

# 安装 Git
sudo apt-get install -y git

# 安装 Python 开发包
sudo apt-get install -y python3-dev python3-pip python3-venv
```

#### CentOS/RHEL

```bash
# 安装 EPEL 仓库
sudo yum install -y epel-release

# 安装 GDAL
sudo yum install -y gdal gdal-devel

# 安装编译工具
sudo yum groupinstall -y "Development Tools"
sudo yum install -y gcc-gfortran

# 安装 Git 和 Python
sudo yum install -y git python3-devel python3-pip
```

#### macOS

```bash
# 使用 Homebrew 安装
brew install gdal
brew install gcc
brew install git
brew install python@3.9
```

### 2. 克隆代码库

```bash
git clone https://github.com/SHUD-System/pyAutoSHUD.git
cd pyAutoSHUD
```

### 3. 创建 Python 虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 4. 安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip setuptools wheel

# 安装核心依赖
pip install -r requirements.txt

# 可选：安装开发依赖
pip install -r requirements-dev.txt

# 可选：安装率定算法依赖
pip install deap spotpy
```

### 5. 安装 pyAutoSHUD

```bash
# 开发模式安装（推荐用于开发）
pip install -e .

# 或正式安装
pip install .
```

### 6. 验证安装

```bash
# 检查命令行工具
pyautoshud --version

# 检查 Python 包
python -c "import pyautoshud; print(pyautoshud.__version__)"
```

## 安装 SHUD 核心程序

pyAutoSHUD 需要 SHUD 核心程序来运行水文模拟。

### 自动安装（推荐）

```bash
# pyAutoSHUD 会在第一次运行时自动下载和编译 SHUD
pyautoshud simulate project.yaml
```

### 手动安装

```bash
# 克隆 SHUD 源代码
git clone https://github.com/SHUD-System/SHUD.git
cd SHUD

# 安装 SUNDIALS（SHUD 依赖）
./configure

# 编译 SHUD
make clean
make shud

# 测试安装
./shud ccw  # 运行示例
```

## 可选组件

### 安装 WhiteboxTools（用于流域划分）

```bash
pip install whitebox
python -c "import whitebox; whitebox.download_wbt()"
```

### 安装高级可视化工具

```bash
# Cartopy（地图绘制）
pip install cartopy

# Plotly（交互式图表）
pip install plotly
```

### 安装率定优化算法

```bash
# DEAP（遗传算法）
pip install deap

# SPOTPY（多种率定算法）
pip install spotpy
```

## Docker 安装（推荐用于生产环境）

### 使用 Docker（未来支持）

```bash
# 拉取 Docker 镜像
docker pull shud/pyautoshud:latest

# 运行容器
docker run -v $(pwd):/workspace -it shud/pyautoshud bash

# 在容器中运行
pyautoshud run /workspace/project.yaml
```

## 常见问题

### 1. GDAL 安装失败

**问题**: `pip install GDAL` 失败

**解决方案**:
```bash
# 查找 GDAL 版本
gdal-config --version

# 安装对应版本
pip install GDAL==$(gdal-config --version)

# 或使用 conda
conda install -c conda-forge gdal
```

### 2. triangle 编译失败

**问题**: `triangle` 包编译错误

**解决方案**:
```bash
# 安装编译依赖
sudo apt-get install build-essential  # Ubuntu/Debian
# 或
sudo yum groupinstall "Development Tools"  # CentOS

# 重新安装
pip install triangle
```

### 3. numpy/scipy 版本冲突

**问题**: 依赖包版本不兼容

**解决方案**:
```bash
# 清理环境
pip uninstall numpy scipy pandas

# 重新安装
pip install numpy scipy pandas
```

### 4. SHUD 编译失败

**问题**: SUNDIALS 未找到

**解决方案**:
```bash
cd SHUD
./configure  # 这会自动下载并安装 SUNDIALS
make clean
make shud
```

### 5. 权限问题

**问题**: `Permission denied`

**解决方案**:
```bash
# 使用虚拟环境（不需要 sudo）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 数据下载

### 全球数据集

pyAutoSHUD 可以自动下载以下数据：

1. **ASTER GDEM** - DEM 数据（自动下载）
2. **ISRIC SoilGrids** - 土壤数据（需要手动下载）
3. **GLDAS** - 气象数据（需要注册 NASA EarthData）

### GLDAS 数据下载

```bash
# 1. 注册账号
# 访问: https://urs.earthdata.nasa.gov/users/new

# 2. 配置凭证
echo "machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD" > ~/.netrc
chmod 0600 ~/.netrc

# 3. pyAutoSHUD 会自动下载需要的数据
```

### ISRIC SoilGrids 数据

```bash
# 下载全球数据（需要大量存储空间）
# 或使用 pyAutoSHUD 的在线提取功能
```

## 性能优化

### 启用多核处理

```bash
# 设置 OpenMP 线程数
export OMP_NUM_THREADS=8

# 运行 pyAutoSHUD
pyautoshud run project.yaml
```

### 使用 SSD 存储

建议将工作目录放在 SSD 上以提高 I/O 性能。

## 卸载

```bash
# 卸载 pyAutoSHUD
pip uninstall pyautoshud

# 删除虚拟环境
deactivate
rm -rf venv

# 删除项目文件
cd ..
rm -rf pyAutoSHUD
```

## 升级

```bash
# 更新代码
git pull

# 升级依赖
pip install --upgrade -r requirements.txt

# 重新安装
pip install -e .
```

## 技术支持

- GitHub Issues: https://github.com/SHUD-System/pyAutoSHUD/issues
- 邮件: shulele@lzb.ac.cn
- SHUD 官网: https://www.shud.xyz

## 许可证

MIT License - 详见 LICENSE 文件
