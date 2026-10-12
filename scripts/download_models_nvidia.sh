#!/usr/bin/env bash
# N 卡（RTX 4090 / 5090 等）模型下载
# 用法:
#   bash scripts/download_models_nvidia.sh                 # fp8 精简版（默认）
#   W6A8=1        bash scripts/download_models_nvidia.sh   # 再加 w6a8（更省显存）
#   NVFP4_TE=1    bash scripts/download_models_nvidia.sh   # 50 系 Blackwell 专用 nvfp4 文本编码器
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COMFY_HOME="${COMFY_HOME:-$HOME/ComfyUI}"
export MODE=nvidia
echo "=== N 卡模式，模型下载到: $COMFY_HOME/models"
echo "详见 docs/NVIDIA显卡部署指南.md"
python3 "$REPO_DIR/scripts/dl_models.py"
