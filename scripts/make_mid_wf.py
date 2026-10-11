# -*- coding: utf-8 -*-
"""中间档工作流：4 步 LoRA + 0.6MP + 8 秒 + INT8 视频 VAE"""
import json

SRC = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora_int8_2npu.json"
DST = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_4step_0.6MP中间档.json"

d = json.load(open(SRC))
for n in d["nodes"]:
    t = n["type"]
    wv = n.get("widgets_values")
    if t == "MiniMaxH3TurboLoRA" and isinstance(wv, list):
        wv[0] = "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors"
        print("LoRA -> 4步版")
    elif t == "BasicScheduler" and isinstance(wv, list):
        wv[1] = 4
        print("步数 -> 4")
    elif t == "ResolutionSelector" and isinstance(wv, list):
        wv[0], wv[1] = "16:9 (Widescreen)", 0.6
        print("分辨率 -> 16:9 0.6MP (约 1024x576)")
    elif t == "VAELoader" and isinstance(wv, list) and wv[0] == "minimax_h3_video_vae_fp16.safetensors":
        wv[0] = "minimax_h3_video_vae_int8_convrot.safetensors"
        print("视频VAE -> int8_convrot")
    elif t == "PrimitiveFloat" and isinstance(wv, list):
        wv[0] = 8
        print("时长 -> 8 秒")

json.dump(d, open(DST, "w"), ensure_ascii=False, indent=2)
print("已保存:", DST)
