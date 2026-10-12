#!/usr/bin/env bash
# 模型下载（hf-mirror 分片并行，实测 ~40MB/s，支持断点续传）
# 用法:
#   bash scripts/download_models.sh              # 全量（约 90GB，双卡 64GB 推荐）
#   bash scripts/download_models.sh --lowvram    # 低配档（约 57GB，32GB 单卡可用）
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COMFY_HOME="${COMFY_HOME:-/mnt/workspace/ComfyUI}"

if [ "${1:-}" = "--lowvram" ]; then
    echo "=== 低配档：精简版主模型（21GB），跳过完整版（34GB）==="
    export SKIP_FULL_FL2VA=1
    export INCLUDE_PRUNED=1
else
    export SKIP_FULL_FL2VA=0
    export INCLUDE_PRUNED=0
fi

echo "模型将下载到: $COMFY_HOME/models"
python3 "$REPO_DIR/scripts/dl_models.py"
