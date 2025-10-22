# SHUD-GPU 快速入门

10分钟内开始使用GPU加速的SHUD模型。

## 前提条件检查

```bash
# 1. 检查NVIDIA GPU
nvidia-smi

# 2. 检查CUDA
nvcc --version

# 3. 检查GCC
gcc --version  # 需要7.0+
```

如果任何命令失败，请先安装必要软件（见GPU_README.md）。

## 3步快速安装

### 步骤1: 安装SUNDIALS with CUDA (10分钟)

```bash
cd ~/
wget https://github.com/LLNL/sundials/releases/download/v6.6.0/sundials-6.6.0.tar.gz
tar xzf sundials-6.6.0.tar.gz
cd sundials-6.6.0
mkdir build && cd build

cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/sundials \
    -DENABLE_CUDA=ON \
    -DCUDA_ARCH=sm_86 \
    -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda

make -j8 && make install
```

**重要**: 修改`-DCUDA_ARCH`以匹配你的GPU:
- RTX 4090/4080: `sm_89`
- RTX 3090/3080: `sm_86`
- RTX 2080 Ti: `sm_75`
- V100: `sm_70`

查看你的GPU架构:
```bash
nvidia-smi --query-gpu=name,compute_cap --format=csv
```

### 步骤2: 编译SHUD-GPU (2分钟)

```bash
cd ~/AutoSHUD/shud_src

# 检查环境
make -f Makefile.gpu check

# 编译
make -f Makefile.gpu
```

### 步骤3: 运行测试 (1分钟)

```bash
# 使用示例输入运行
./shud_gpu ./input/ccw ./output/ccw_gpu
```

## 完整示例

```bash
#!/bin/bash
# complete_gpu_setup.sh - 完整的GPU版本设置脚本

set -e  # 遇到错误立即退出

echo "==== SHUD-GPU 完整安装脚本 ===="
echo ""

# 1. 检查前提条件
echo "[1/5] 检查前提条件..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "错误: nvidia-smi 未找到. 请安装NVIDIA驱动."
    exit 1
fi

if ! command -v nvcc &> /dev/null; then
    echo "错误: nvcc 未找到. 请安装CUDA Toolkit."
    exit 1
fi

nvidia-smi
nvcc --version
echo ""

# 2. 安装SUNDIALS
echo "[2/5] 编译SUNDIALS with CUDA..."
cd ~/
if [ ! -d "sundials-6.6.0" ]; then
    wget -q https://github.com/LLNL/sundials/releases/download/v6.6.0/sundials-6.6.0.tar.gz
    tar xzf sundials-6.6.0.tar.gz
fi

cd sundials-6.6.0
rm -rf build
mkdir build && cd build

cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/sundials \
    -DENABLE_CUDA=ON \
    -DCUDA_ARCH=sm_86 \
    -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda \
    -DBUILD_SHARED_LIBS=ON \
    -DEXAMPLES_INSTALL=OFF \
    > /dev/null

echo "  编译中 (可能需要5-10分钟)..."
make -j8 > /dev/null
make install > /dev/null
echo "  SUNDIALS 安装完成: $HOME/sundials"
echo ""

# 3. 编译SHUD-GPU
echo "[3/5] 编译SHUD-GPU..."
cd ~/AutoSHUD/shud_src
make -f Makefile.gpu clean > /dev/null 2>&1 || true
make -f Makefile.gpu
echo "  SHUD-GPU 编译完成"
echo ""

# 4. 验证安装
echo "[4/5] 验证安装..."
if [ ! -f "./shud_gpu" ]; then
    echo "错误: shud_gpu 可执行文件未找到"
    exit 1
fi

./shud_gpu 2>&1 | head -5
echo ""

# 5. 性能测试（如果有示例数据）
echo "[5/5] 性能测试..."
if [ -d "./input/ccw" ]; then
    echo "  运行CPU版本..."
    time ./shud ./input/ccw ./output/test_cpu 2>&1 | grep -E "Total time"

    echo "  运行GPU版本..."
    time ./shud_gpu ./input/ccw ./output/test_gpu 2>&1 | grep -E "Total time"

    echo ""
    echo "✓ 安装和测试完成！"
else
    echo "  跳过（无示例数据）"
    echo "✓ 安装完成！"
fi

echo ""
echo "==== 使用方法 ===="
echo "运行GPU版本:"
echo "  ./shud_gpu <input_dir> <output_dir>"
echo ""
echo "例如:"
echo "  ./shud_gpu ./input/myproject ./output/myproject_gpu"
echo ""
```

保存为`complete_gpu_setup.sh`，然后运行:

```bash
chmod +x complete_gpu_setup.sh
./complete_gpu_setup.sh
```

## 常见问题

### Q1: 如何知道GPU是否在工作？

**方法1**: 监控GPU使用率
```bash
# 另开一个终端
watch -n 1 nvidia-smi

# 运行SHUD-GPU
./shud_gpu ./input ./output
```

你应该看到GPU使用率接近100%。

**方法2**: 查看输出日志
```
[GPU] Detected 1 CUDA-capable device(s)
[GPU] Using: NVIDIA GeForce RTX 4090
[GPU] Compute Capability: 8.9
```

### Q2: GPU版本比CPU慢？

可能原因：
1. **网格太小** (<1000元素) - GPU开销大于收益
2. **数据传输** - 检查是否频繁CPU-GPU传输
3. **未优化** - 当前版本是基础实现

解决方案：使用更大的网格（>5000元素）以获得最佳性能。

### Q3: 内存不足错误？

```bash
# 检查GPU内存
nvidia-smi --query-gpu=memory.free,memory.total --format=csv

# 如果内存不足：
# 1. 减少网格规模
# 2. 使用更大GPU
# 3. 关闭其他GPU应用
```

### Q4: 如何选择GPU（多GPU系统）？

```bash
# 设置环境变量
export CUDA_VISIBLE_DEVICES=0  # 使用GPU 0
./shud_gpu ./input ./output

export CUDA_VISIBLE_DEVICES=1  # 使用GPU 1
./shud_gpu ./input ./output
```

## 性能对比示例

创建性能测试脚本:

```bash
#!/bin/bash
# benchmark.sh

PROJECT="./input/ccw"
OUTPUT_CPU="./output/bench_cpu"
OUTPUT_GPU="./output/bench_gpu"

echo "==== SHUD 性能对比测试 ===="
echo ""

echo "[CPU版本] OpenMP..."
rm -rf $OUTPUT_CPU
time ./shud $PROJECT $OUTPUT_CPU 2>&1 | tail -5

echo ""
echo "[GPU版本] CUDA..."
rm -rf $OUTPUT_GPU
time ./shud_gpu $PROJECT $OUTPUT_GPU 2>&1 | tail -5

echo ""
echo "==== 结果对比 ===="
# 对比关键输出
echo "Surface water (last step):"
echo "  CPU: $(tail -1 $OUTPUT_CPU/YEsurf.txt)"
echo "  GPU: $(tail -1 $OUTPUT_GPU/YEsurf.txt)"
```

运行:
```bash
chmod +x benchmark.sh
./benchmark.sh
```

## 下一步

1. **阅读完整文档**: [GPU_README.md](GPU_README.md)
2. **性能调优**: 调整CUDA块大小和网格规模
3. **集成pyAutoSHUD**: 使用Python工具链前后处理
4. **参与开发**: GitHub贡献代码和优化

## 获取帮助

- **文档**: GPU_README.md
- **问题**: GitHub Issues
- **邮件**: lele.shu@gmail.com

---

**快速命令参考**:

```bash
# 编译
make -f Makefile.gpu

# 运行
./shud_gpu ./input ./output

# 清理
make -f Makefile.gpu clean

# 监控GPU
nvidia-smi -l 1

# 检查环境
make -f Makefile.gpu check
```

祝使用愉快！🚀
