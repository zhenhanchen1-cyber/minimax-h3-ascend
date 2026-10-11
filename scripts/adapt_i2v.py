# -*- coding: utf-8 -*-
"""把用户下载的 i2v 工作流改成昇腾适配版并保存到服务器"""
import json, os, shutil

SRC = "/mnt/workspace/i2v_src.json"
DST_DIR = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3"
DST = os.path.join(DST_DIR, "i2v_九宫格_昇腾适配.json")

d = json.load(open(SRC, encoding="utf-8"))

UNET = "minimax_h3_fl2va_int8_convrot.safetensors"
CLIP = "qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot.safetensors"

for n in d["nodes"]:
    if n["type"] == "ResolutionSelector":
        n["widgets_values"][0] = "4:3 (Standard)"
        n["widgets_values"][1] = 0.6
        print("分辨率 -> 4:3, 0.6MP")
    if n["type"] == "4c314f31-ecda-4b08-ae98-faaba1bf613f":
        wv = n["widgets_values"]
        # 索引: 0=prompt, 1=w, 2=h, 3=duration, 4=seed, 5=unet, 6=clip,
        #       7=vae, 8=audio_vae, 9=turbo_mode, 10=lora, 11=strength, 12=steps
        print("原 unet:", wv[5])
        print("原 clip:", wv[6])
        wv[3] = 12          # duration 20 -> 12 秒（模型上限 15）
        wv[5] = UNET
        wv[6] = CLIP
        wv[9] = True        # turbo_mode 打开
        wv[12] = 8          # turbo_steps
        print("新 unet:", wv[5])
        print("新 clip:", wv[6])
        print("duration =", wv[3], "| turbo =", wv[9], "| steps =", wv[12])

os.makedirs(DST_DIR, exist_ok=True)
json.dump(d, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已保存:", DST)
