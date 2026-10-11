import json, os

src = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora.json"
dst = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora_int8_2npu.json"

UNET = "minimax_h3_fl2va_int8_convrot.safetensors"
CLIP = "qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot.safetensors"

d = json.load(open(src))
changed = []
for n in d.get("nodes", []):
    t = n.get("type", "")
    wv = n.get("widgets_values")
    if isinstance(wv, list) and wv:
        if t == "UNETLoader" and isinstance(wv[0], str):
            changed.append(("UNET", wv[0], UNET)); wv[0] = UNET
        elif t == "CLIPLoader" and isinstance(wv[0], str):
            changed.append(("CLIP", wv[0], CLIP)); wv[0] = CLIP
        elif t == "MultiNPUParallelConfig" and isinstance(wv[0], str):
            changed.append(("NPU", wv[0], "2")); wv[0] = "2"
        elif t == "LoadImage" and isinstance(wv[0], str):
            changed.append(("IMG", wv[0], wv[0]))
    if t == "MiniMaxH3ImageToVideo" and isinstance(wv, list) and len(wv) >= 4:
        # 降低首测负载：1344x768 -> 832x480，124 帧 -> 82 帧
        wv[1], wv[2], wv[3] = 832, 480, 82
        changed.append(("RES", "1344x768x124", "832x480x82"))

json.dump(d, open(dst, "w"), ensure_ascii=False, indent=2)
for c in changed:
    print("SET", c[0], ":", c[1], "->", c[2])
print("WROTE", dst)
