#!/usr/bin/env bash
# MiniMax-H3 on Ascend —— ComfyUI 启动脚本（自适应 910B/910C，卡数自动识别）
# 用法: bash scripts/start_comfyui.sh
# 环境变量: COMFY_HOME(默认 /mnt/workspace/ComfyUI)  COMFYUI_PORT(默认 8188)  NPU_DEVICES(可手动指定)
set -euo pipefail

COMFY_HOME="${COMFY_HOME:-/mnt/workspace/ComfyUI}"
PORT="${COMFYUI_PORT:-8188}"
RUNTIME="/mnt/workspace/runtime"
PID_FILE="$RUNTIME/comfyui-$PORT.pid"
LOG_FILE="$RUNTIME/comfyui-$PORT.log"
mkdir -p "$RUNTIME"

# --- 已在运行则先停 ---
if [ -s "$PID_FILE" ]; then
    old=$(cat "$PID_FILE")
    kill -0 "$old" 2>/dev/null && { echo "停止旧服务 PID=$old"; kill "$old"; sleep 3; }
    rm -f "$PID_FILE"
fi

# --- CANN ---
ASCEND_HOME=""
for p in /usr/local/Ascend/ascend-toolkit "$HOME/Ascend/ascend-toolkit" /home/*/Ascend/ascend-toolkit; do
    [ -f "$p/set_env.sh" ] && ASCEND_HOME="$p" && break
done
[ -z "$ASCEND_HOME" ] && { echo "!! 未找到 CANN"; exit 1; }
set +u; source "$ASCEND_HOME/set_env.sh"; set -u

# --- 卡数自适应 ---
if [ -z "${NPU_DEVICES:-}" ]; then
    n=$(ls -d /dev/davinci[0-9]* 2>/dev/null | wc -l)
    [ "$n" -ge 4 ] && n=4 || true
    [ "$n" -ge 8 ] && n=8 || true
    NPU_DEVICES=$(seq -s, 0 $(( (n>0?n:1) - 1 )))
fi
export ASCEND_RT_VISIBLE_DEVICES="$NPU_DEVICES"
echo "使用 NPU: $NPU_DEVICES"

# --- aarch64 关键修复：预先加载 libgomp，避免 torchaudio TLS 报错 ---
[ -f /lib/aarch64-linux-gnu/libgomp.so.1 ] && export LD_PRELOAD=/lib/aarch64-linux-gnu/libgomp.so.1

export HCCL_OP_EXPANSION_MODE="${HCCL_OP_EXPANSION_MODE:-AIV}"
export COMFYUI_MULTI_DEVICE_BACKEND="${COMFYUI_MULTI_DEVICE_BACKEND:-auto}"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy || true

# --- 同步工作流里的 npu_count（避免校验失败）---
python3 "$(dirname "$0")/set_npu_count.py" "$NPU_DEVICES" 2>/dev/null || true

# --- 显存模式 ---
ARGS="--listen 0.0.0.0 --port $PORT --disable-auto-launch --cache-classic"
if [ "${LOWVRAM:-0}" = "1" ]; then
    echo "低显存模式 (--lowvram)：模型逐层卸载到内存，慢但 32GB 卡也能跑"
    ARGS="$ARGS --lowvram"
fi
if [ "${NORMALVRAM:-0}" = "1" ]; then
    ARGS="$ARGS --normalvram"
fi

echo "$$" > "$PID_FILE"
cd "$COMFY_HOME"
exec python3 main.py $ARGS >> "$LOG_FILE" 2>&1
