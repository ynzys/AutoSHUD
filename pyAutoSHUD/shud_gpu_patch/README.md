# SHUD GPU Acceleration Patch

这是SHUD水文模型的GPU加速补丁包，使用NVIDIA CUDA实现核心计算的GPU并行化。

## 📦 包含内容

```
shud_gpu_patch/
├── INSTALL.sh              # 自动安装脚本
├── README.md               # 本文件
├── Makefile.gpu            # GPU版本Makefile
├── main_gpu.cpp            # GPU版本主程序
├── GPU_README.md           # 完整文档
├── GPU_QUICKSTART.md       # 快速入门指南
└── gpu/                    # GPU源代码目录
    ├── README.md           # GPU代码文档
    ├── gpu_types.hpp       # GPU数据类型
    ├── gpu_memory.hpp/cu   # GPU内存管理
    ├── gpu_kernels.cuh/cu  # CUDA计算核心
    └── Model_Data_GPU.hpp/cpp  # GPU模型接口
```

## 🚀 快速安装

### 方法1: 自动安装（推荐）

```bash
cd pyAutoSHUD/shud_gpu_patch
chmod +x INSTALL.sh
./INSTALL.sh ../../shud_src
```

### 方法2: 手动安装

```bash
# 假设SHUD源代码在 ~/shud 或 ../../shud_src

# 1. 复制GPU源文件
cp -r gpu /path/to/shud_src/src/

# 2. 复制主程序
cp main_gpu.cpp /path/to/shud_src/src/

# 3. 复制Makefile
cp Makefile.gpu /path/to/shud_src/

# 4. 复制文档
cp GPU_*.md /path/to/shud_src/

# 5. 编译
cd /path/to/shud_src
make -f Makefile.gpu
```

## 📋 系统要求

### 硬件要求
- **NVIDIA GPU**: Compute Capability 7.0+ (RTX 20/30/40系列, V100, A100等)
- **GPU内存**: 最低4GB，推荐8GB+

### 软件要求
- **CUDA Toolkit**: 11.0+ (推荐11.8或12.x)
- **SUNDIALS**: 6.0+ (必须编译CUDA支持)
- **GCC**: 7.0+
- **NVIDIA Driver**: 470+

### 检查系统

```bash
# 检查GPU
nvidia-smi

# 检查CUDA
nvcc --version

# 检查SUNDIALS CUDA支持
ls ~/sundials/lib/libsundials_nveccuda.*
```

## 🔧 编译SUNDIALS with CUDA

如果还没有安装支持CUDA的SUNDIALS，按以下步骤操作：

```bash
# 1. 下载SUNDIALS
cd ~/
wget https://github.com/LLNL/sundials/releases/download/v6.6.0/sundials-6.6.0.tar.gz
tar xzf sundials-6.6.0.tar.gz
cd sundials-6.6.0

# 2. 配置和编译（启用CUDA）
mkdir build && cd build
cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/sundials \
    -DENABLE_CUDA=ON \
    -DCUDA_ARCH=sm_86 \
    -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda
make -j8
make install

# 3. 验证
ls $HOME/sundials/lib/libsundials_nveccuda.*
```

**注意**: 根据你的GPU修改`-DCUDA_ARCH`:
- RTX 4090/4080: `sm_89`
- RTX 3090/3080: `sm_86`
- RTX 2080 Ti: `sm_75`
- V100: `sm_70`

查看GPU架构：
```bash
nvidia-smi --query-gpu=name,compute_cap --format=csv
```

## 📚 使用文档

安装后，参考以下文档：

1. **GPU_QUICKSTART.md**: 10分钟快速入门
2. **GPU_README.md**: 完整使用手册
3. **gpu/README.md**: GPU代码技术文档

## ⚡ 性能预期

根据GPU可行性分析报告（`../GPU_FEASIBILITY_ANALYSIS.md`）：

| 网格规模 | CPU (OpenMP) | GPU预期 | 加速比 |
|---------|-------------|---------|-------|
| 1,000 元素 | 2 秒/步 | 0.5 秒/步 | 4x |
| 5,000 元素 | 10 秒/步 | 1.2 秒/步 | 8x |
| 10,000 元素 | 25 秒/步 | 2.0 秒/步 | 12x |
| 18,000 元素 | 50 秒/步 | 3.0 秒/步 | 17x |

**综合预期**: 5-20倍加速（取决于网格规模）

## 🔍 验证安装

```bash
cd /path/to/shud_src

# 1. 编译
make -f Makefile.gpu

# 2. 查看GPU版本信息
./shud_gpu

# 3. 运行测试（如果有示例数据）
./shud_gpu ./input/test ./output/test_gpu
```

## 🐛 故障排除

### 问题1: CUDA Toolkit未找到

```bash
# 安装CUDA Toolkit
# Ubuntu/Debian:
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run

# 添加到环境变量
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

### 问题2: SUNDIALS CUDA支持未找到

重新编译SUNDIALS，确保使用`-DENABLE_CUDA=ON`选项（见上文）。

### 问题3: 编译错误 - 不支持的GPU架构

修改`Makefile.gpu`中的`CUDA_ARCH`以匹配你的GPU。

### 问题4: 运行时GPU内存不足

- 减少网格规模
- 使用更大的GPU
- 关闭其他GPU应用

## 📖 技术细节

### GPU实现特性

✅ **已实现**:
- CUDA核函数：元素更新、下渗、补给、溢出流
- CUDA核函数：地表流和地下流侧向通量
- GPU内存管理（Structure of Arrays布局）
- SUNDIALS CVODE GPU集成框架
- 完整的水量平衡计算

⚠️ **部分实现**:
- 河流计算（基础GPU化）
- ET蒸散发计算（待优化）

🔲 **待实现** (未来版本):
- 多GPU支持
- 湖泊模块GPU化
- 混合精度计算
- CUDA图优化

### 代码架构

```
GPU计算流程:
1. 初始化GPU内存 (GPUMemoryManager)
2. 复制数据到GPU (CPU → GPU)
3. 每个时间步:
   a. 更新元素状态 (kernel_update_elements)
   b. 计算垂直通量 (kernel_infiltration, kernel_recharge, etc.)
   c. 计算侧向通量 (kernel_surface_flux, kernel_subsurface_flux)
   d. 应用导数 (kernel_apply_derivatives)
4. 复制结果回CPU (GPU → CPU)
5. 清理GPU内存
```

### 性能优化

- **Structure of Arrays (SoA)**: 优化内存合并访问
- **256线程/块**: 高效的GPU线程配置
- **批量操作**: 最小化CPU-GPU传输
- **异步内核**: 重叠计算和数据传输

## 🤝 贡献

欢迎改进GPU实现！

重点方向：
- 性能优化
- 支持更多GPU架构
- Bug修复
- 文档改进

## 📧 联系方式

- **问题反馈**: GitHub Issues
- **技术讨论**: lele.shu@gmail.com
- **项目主页**: https://www.shud.xyz/

## 📄 许可证

继承原SHUD项目许可证。

## 🙏 致谢

- SUNDIALS团队 (Lawrence Livermore National Laboratory)
- NVIDIA CUDA团队
- SHUD社区贡献者

---

**版本**: 1.0 (Alpha)
**更新日期**: 2025-10-22
**基于**: SHUD v2.0
