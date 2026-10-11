# -*- coding: utf-8 -*-
"""配置九宫格剧情视频工作流：4:3 匹配分镜图、8 秒、用户提示词、首帧=九宫格图"""
import json

SRC = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora_int8_2npu.json"
PROMPT_FILE = "/mnt/workspace/grid_prompt.txt"

d = json.load(open(SRC))

prompt_text = open(PROMPT_FILE, encoding="utf-8").read().strip()
print("prompt length:", len(prompt_text))

for n in d["nodes"]:
    t = n["type"]
    wv = n.get("widgets_values")
    if t == "ResolutionSelector" and isinstance(wv, list):
        wv[0], wv[1], wv[2] = "4:3 (Standard)", 0.6, 32
        print("分辨率 -> 4:3, 0.6MP")
    elif t == "PrimitiveFloat" and isinstance(wv, list):
        wv[0] = 8
        print("时长 -> 8 秒")
    elif t == "PrimitiveStringMultiline" and isinstance(wv, list):
        wv[0] = prompt_text
        print("提示词已写入")
    elif t == "LoadImage" and isinstance(wv, list) and wv[0] == "red_superboy_on_city_roof.png":
        wv[0] = "grid_storyboard.png"
        print("首帧 -> grid_storyboard.png")

json.dump(d, open(SRC, "w"), ensure_ascii=False, indent=2)
print("SAVED")
