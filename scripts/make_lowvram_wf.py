# -*- coding: utf-8 -*-
"""生成 32GB 单卡低显存档工作流：精简版主模型 + 480P + 5秒 + 4步 + npu_count=1
用法（本机，仓库内）：python scripts/make_lowvram_wf.py
用法（服务器）：COMFY_HOME=/mnt/workspace/ComfyUI python scripts/make_lowvram_wf.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SERVER_MODE = bool(os.environ.get("COMFY_HOME"))

if SERVER_MODE:
    WF_DIR = os.environ["COMFY_HOME"] + "/user/default/workflows/minimax-h3"
    SRC = os.path.join(WF_DIR, "fl2va_8steps_lora_int8_2npu.json")
else:
    WF_DIR = os.path.join(REPO, "workflows")
    SRC = os.path.join(WF_DIR, "fl2va_8steps_lora_int8_2npu.json")
DST = os.path.join(WF_DIR, "fl2va_4step_480P低显存.json")

d = json.load(open(SRC, encoding="utf-8"))
for n in d["nodes"]:
    t = n["type"]
    wv = n.get("widgets_values")
    if t == "UNETLoader" and isinstance(wv, list):
        wv[0] = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"   # 21GB 精简版
        print("主模型 -> 精简版 pruned_int8 (21GB)")
    elif t == "MiniMaxH3TurboLoRA" and isinstance(wv, list):
        wv[0] = "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors"
        print("LoRA -> 4 步版")
    elif t == "BasicScheduler" and isinstance(wv, list):
        wv[1] = 4
        print("步数 -> 4")
    elif t == "ResolutionSelector" and isinstance(wv, list):
        wv[0], wv[1] = "16:9 (Widescreen)", 0.4      # 864x480
        print("分辨率 -> 16:9 0.4MP (864x480)")
    elif t == "VAELoader" and isinstance(wv, list) and wv[0] == "minimax_h3_video_vae_fp16.safetensors":
        wv[0] = "minimax_h3_video_vae_int8_convrot.safetensors"       # 2.8GB，省显存
        print("视频VAE -> int8_convrot (2.8GB)")
    elif t == "PrimitiveFloat" and isinstance(wv, list):
        wv[0] = 5
        print("时长 -> 5 秒")
    elif t == "MultiNPUParallelConfig" and isinstance(wv, list):
        wv[0] = "1"
        print("npu_count -> 1（单卡）")

json.dump(d, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已保存:", DST)
