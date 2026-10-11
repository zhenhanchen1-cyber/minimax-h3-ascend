#!/usr/bin/env bash
# =============================================================
# MiniMax-H3 on Ascend 一键部署脚本
# 适用: CANNLab / 昇腾 910B / 910C 容器与环境
# 用法: bash setup.sh
# =============================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMFY_HOME="${COMFY_HOME:-/mnt/workspace/ComfyUI}"
COMFY_COMMIT="bd34f338ac505ea79e43968753968a464060e609"
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"

echo "=== [1/6] 环境检查 ==="

# --- 定位 CANN ---
ASCEND_HOME=""
for p in /usr/local/Ascend/ascend-toolkit "$HOME/Ascend/ascend-toolkit" /home/*/Ascend/ascend-toolkit; do
    if [ -f "$p/set_env.sh" ]; then ASCEND_HOME="$p"; break; fi
done
if [ -z "$ASCEND_HOME" ]; then
    echo "!! 未找到 CANN (ascend-toolkit/set_env.sh)。请先安装 CANN >= 9.0.0"; exit 1
fi
echo "CANN: $ASCEND_HOME"
# shellcheck disable=SC1091
set +u; source "$ASCEND_HOME/set_env.sh"; set -u

# --- 检查 NPU ---
NPU_COUNT=$(ls -d /dev/davinci[0-9]* 2>/dev/null | wc -l)
[ "$NPU_COUNT" -eq 0 ] && { echo "!! 未发现 NPU 设备 (/dev/davinci*)"; exit 1; }
# npu_count 仅支持 1/2/4，取最接近的合法值
if [ "$NPU_COUNT" -ge 4 ]; then NPU_COUNT=4; elif [ "$NPU_COUNT" -ge 2 ]; then NPU_COUNT=2; else NPU_COUNT=1; fi
echo "NPU 数量(用于 npu_count): $NPU_COUNT"

# --- 检查 torch_npu ---
python3 - <<'PY'
import torch, torch_npu
print(f"torch {torch.__version__} / torch_npu {torch_npu.__version__} / npu_available={torch.npu.is_available()}")
assert torch.npu.is_available(), "torch_npu 不可用，请检查 CANN 与 torch_npu 版本配套"
PY

echo "=== [2/6] 克隆 ComfyUI (锁定 commit) ==="
if [ ! -d "$COMFY_HOME/.git" ]; then
    git clone https://github.com/Comfy-Org/ComfyUI.git "$COMFY_HOME"
fi
cd "$COMFY_HOME"
git fetch --depth 1 origin "$COMFY_COMMIT" || { echo "网络问题，重试..."; sleep 3; git fetch --depth 1 origin "$COMFY_COMMIT"; }
git checkout --detach FETCH_HEAD
git log --oneline -1

echo "=== [3/6] 应用昇腾适配补丁 ==="
git apply --check "$REPO_DIR/assets/comfy-ui-changes.patch" && git apply "$REPO_DIR/assets/comfy-ui-changes.patch"
echo "补丁已应用 (来源: Ascend-SACT/MiniMax-H3-Comfy-NPU, Apache-2.0)"

echo "=== [4/6] 安装 Python 依赖 ==="
# ComfyUI 核心依赖（跳过需要 py3.12 的模板包）
grep -v -E 'comfyui-workflow-templates|comfyui-embedded-docs' requirements.txt > /tmp/req_core.txt
python3 -m pip install -q -i "$PIP_MIRROR" -r /tmp/req_core.txt
python3 -m pip install -q --no-deps -i "$PIP_MIRROR" comfyui-workflow-templates comfyui-embedded-docs
# 关键: torchaudio 必须与 torch 同版本
TORCH_VER=$(python3 -c "import torch; print(torch.__version__.split('+')[0])")
python3 -m pip install -q -i "$PIP_MIRROR" "torchaudio==${TORCH_VER}" || \
    python3 -m pip install -q --index-url https://download.pytorch.org/whl/cpu "torchaudio==${TORCH_VER}"
# 昇腾验证版依赖
python3 -m pip install -q -i "$PIP_MIRROR" comfy-kitchen==0.2.30 comfy-aimdo==0.4.13 imageio-ffmpeg hf_transfer

echo "=== [5/6] 安装验证版 Turbo 节点 ==="
mkdir -p "$COMFY_HOME/custom_nodes"
tar xzf "$REPO_DIR/assets/ComfyUI-MiniMax-H3-Turbo-verified.tgz" -C /tmp/
rm -rf "$COMFY_HOME/custom_nodes/ComfyUI-MiniMax-H3-Turbo"
cp -r /tmp/additional_files/custom_nodes/ComfyUI-MiniMax-H3-Turbo "$COMFY_HOME/custom_nodes/"

echo "=== [6/6] 安装工作流 ==="
mkdir -p "$COMFY_HOME/user/default/workflows/minimax-h3"
cp "$REPO_DIR"/workflows/*.json "$COMFY_HOME/user/default/workflows/minimax-h3/"
# i2v 工作流需要的图占位
mkdir -p "$COMFY_HOME/input"

cat <<EOF

============================================================
✅ 部署完成！

下一步：
  1) 下载模型（约 90GB，可断点续传）:
       bash scripts/download_models.sh
  2) 启动服务:
       bash scripts/start_comfyui.sh
  3) 浏览器打开: http://127.0.0.1:8188
     从 Workflows → minimax-h3 选择工作流出片

提示: 默认使用 $COMFY_HOME
============================================================
EOF
