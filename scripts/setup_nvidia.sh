#!/usr/bin/env bash
# N 卡（RTX 4090 / 5090 等）一键部署 ComfyUI（原生版，不打昇腾补丁）
# 用法: bash scripts/setup_nvidia.sh [COMFY_HOME]
# 之后: bash scripts/download_models_nvidia.sh
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT="$(dirname "$REPO_DIR")"
COMFY_HOME="${1:-${COMFY_HOME:-$HOME/ComfyUI}}"
COMFY_COMMIT="bd34f338ac505ea79e43968753968a464060e609"
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"

echo "=== [1/4] 环境检查 ==="
python3 - <<'PY'
import torch
print(f"torch {torch.__version__} | CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0),
          f"| 显存 {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB")
else:
    print("!! 未检测到 CUDA，请检查驱动与 torch 版本")
PY

echo "=== [2/4] 克隆 ComfyUI（锁定 commit，保证可复现）==="
if [ ! -d "$COMFY_HOME/.git" ]; then
    git clone https://github.com/Comfy-Org/ComfyUI.git "$COMFY_HOME"
fi
cd "$COMFY_HOME"
git fetch --depth 1 origin "$COMFY_COMMIT"
git checkout --detach FETCH_HEAD
git log --oneline -1

echo "=== [3/4] 安装依赖 ==="
python3 -m pip install -q --upgrade pip -i "$PIP_MIRROR"
python3 -m pip install -q -i "$PIP_MIRROR" torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 || \
    python3 -m pip install -q -i "$PIP_MIRROR" torch torchvision torchaudio
grep -v -E 'comfyui-workflow-templates|comfyui-embedded-docs' requirements.txt > /tmp/req_core.txt
python3 -m pip install -q -i "$PIP_MIRROR" -r /tmp/req_core.txt
python3 -m pip install -q --no-deps -i "$PIP_MIRROR" comfyui-workflow-templates comfyui-embedded-docs

# 可选加速（失败不影响主流程）
python3 -m pip install -q -i "$PIP_MIRROR" sageattention 2>/dev/null && echo "SageAttention 已安装" || echo "SageAttention 跳过（可选）"

echo "=== [4/4] 安装 Turbo 节点（官方版）==="
mkdir -p "$COMFY_HOME/custom_nodes"
if [ ! -d "$COMFY_HOME/custom_nodes/ComfyUI-MiniMax-H3-Turbo" ]; then
    git clone https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo.git \
        "$COMFY_HOME/custom_nodes/ComfyUI-MiniMax-H3-Turbo"
fi

cat <<EOF

============================================================
✅ N 卡环境部署完成

下一步：
  1) 下载 N 卡专用权重:
       bash scripts/download_models_nvidia.sh
       # 50 系 Blackwell: NVFP4_TE=1 bash scripts/download_models_nvidia.sh
       # 显存吃紧:        W6A8=1    bash scripts/download_models_nvidia.sh
  2) 启动（24GB 卡建议带 --lowvram）:
       cd $COMFY_HOME && python main.py --listen --lowvram
  3) 浏览器打开 http://127.0.0.1:8188

详细说明见 docs/NVIDIA显卡部署指南.md
============================================================
EOF
