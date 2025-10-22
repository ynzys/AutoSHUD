#!/bin/bash
#
# SHUD GPU Patch Installer
# This script installs GPU acceleration for SHUD
#
# Usage: ./INSTALL.sh [shud_src_directory]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   SHUD GPU Acceleration Installer             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Determine SHUD source directory
if [ -z "$1" ]; then
    # Default: look for shud_src in parent directories
    if [ -d "../../shud_src" ]; then
        SHUD_SRC="../../shud_src"
    elif [ -d "../../../shud_src" ]; then
        SHUD_SRC="../../../shud_src"
    elif [ -d "$HOME/shud" ]; then
        SHUD_SRC="$HOME/shud"
    else
        echo -e "${RED}Error: SHUD source directory not found${NC}"
        echo "Usage: $0 <shud_src_directory>"
        echo ""
        echo "Example:"
        echo "  $0 ~/shud"
        echo "  $0 ../../shud_src"
        exit 1
    fi
else
    SHUD_SRC="$1"
fi

# Verify SHUD source directory
if [ ! -d "$SHUD_SRC" ]; then
    echo -e "${RED}Error: Directory not found: $SHUD_SRC${NC}"
    exit 1
fi

if [ ! -f "$SHUD_SRC/Makefile" ]; then
    echo -e "${RED}Error: Not a valid SHUD source directory (Makefile not found)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found SHUD source: $SHUD_SRC"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check CUDA
if ! command -v nvcc &> /dev/null; then
    echo -e "${RED}✗ CUDA Toolkit not found${NC}"
    echo "  Please install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads"
    exit 1
fi
echo -e "${GREEN}✓${NC} CUDA Toolkit found: $(nvcc --version | grep release | awk '{print $5}' | sed 's/,//')"

# Check NVIDIA driver
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}✗ NVIDIA driver not found${NC}"
    echo "  Please install NVIDIA driver"
    exit 1
fi
echo -e "${GREEN}✓${NC} NVIDIA driver found"

# Check GPU
GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader | head -1)
if [ "$GPU_COUNT" = "0" ]; then
    echo -e "${RED}✗ No NVIDIA GPU detected${NC}"
    exit 1
fi
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
echo -e "${GREEN}✓${NC} GPU detected: $GPU_NAME"

# Check SUNDIALS
SUNDIALS_DIR="${SUNDIALS_DIR:-$HOME/sundials}"
if [ ! -f "$SUNDIALS_DIR/lib/libsundials_nveccuda.so" ] && [ ! -f "$SUNDIALS_DIR/lib/libsundials_nveccuda.dylib" ]; then
    echo -e "${YELLOW}⚠${NC}  SUNDIALS with CUDA support not found at: $SUNDIALS_DIR"
    echo ""
    echo "You need to compile SUNDIALS with CUDA support first."
    echo "See GPU_QUICKSTART.md for instructions."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} SUNDIALS with CUDA found: $SUNDIALS_DIR"
fi

echo ""
echo "Installing GPU patch..."

# Backup existing files if they exist
if [ -d "$SHUD_SRC/src/gpu" ]; then
    echo "  Backing up existing GPU files..."
    mv "$SHUD_SRC/src/gpu" "$SHUD_SRC/src/gpu.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy GPU source files
echo "  Copying GPU source files..."
cp -r gpu "$SHUD_SRC/src/"
echo -e "${GREEN}    ✓${NC} GPU source files installed"

# Copy main_gpu.cpp
echo "  Copying main_gpu.cpp..."
cp main_gpu.cpp "$SHUD_SRC/src/"
echo -e "${GREEN}    ✓${NC} main_gpu.cpp installed"

# Copy Makefile.gpu
echo "  Copying Makefile.gpu..."
cp Makefile.gpu "$SHUD_SRC/"
echo -e "${GREEN}    ✓${NC} Makefile.gpu installed"

# Copy documentation
echo "  Copying documentation..."
cp GPU_README.md "$SHUD_SRC/"
cp GPU_QUICKSTART.md "$SHUD_SRC/"
echo -e "${GREEN}    ✓${NC} Documentation installed"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Compile SHUD-GPU:"
echo -e "   ${YELLOW}cd $SHUD_SRC${NC}"
echo -e "   ${YELLOW}make -f Makefile.gpu${NC}"
echo ""
echo "2. Run SHUD-GPU:"
echo -e "   ${YELLOW}./shud_gpu <input_dir> <output_dir>${NC}"
echo ""
echo "For detailed instructions, see:"
echo "  - $SHUD_SRC/GPU_README.md"
echo "  - $SHUD_SRC/GPU_QUICKSTART.md"
echo ""
