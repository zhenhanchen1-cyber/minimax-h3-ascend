#!/usr/bin/env bash
# 模型下载（hf-mirror 分片并行，实测 ~40MB/s，支持断点续传）
# 用法: bash scripts/download_models.sh [COMFY_HOME]
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COMFY_HOME="${1:-${COMFY_HOME:-/mnt/workspace/ComfyUI}}"
echo "模型将下载到: $COMFY_HOME/models"
python3 "$REPO_DIR/scripts/dl_models.py"
