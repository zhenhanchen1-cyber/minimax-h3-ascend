# -*- coding: utf-8 -*-
"""九宫格剧情 → 1 分钟连续视频：5 段 × 12 秒，尾帧接首帧，1.0MP 4:3"""
import json, os, re, subprocess, time, glob
import requests

BASE = "http://127.0.0.1:8188"
WF = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora_int8_2npu.json"
INPUT = "/mnt/workspace/ComfyUI/input"
OUT = "/mnt/workspace/ComfyUI/output/video"
SRC_PROMPT = "/mnt/workspace/grid_prompt.txt"

# ---- 拆分用户原始提示词 ----
raw = open(SRC_PROMPT, encoding="utf-8").read()
parts = re.split(r"镜头(\d)：", raw)
header = parts[0]
shots = {}
tail = ""
for i in range(1, len(parts) - 1, 2):
    idx = int(parts[i])
    body = parts[i + 1]
    if idx == 9:
        # 第 9 格之后的内容属于通用要求
        m = re.search(r"(整体摄影要求：[\s\S]*)", body)
        if m:
            tail = m.group(1)
            body = body[: m.start()]
    shots[idx] = "镜头" + str(idx) + "：" + body
print("提取镜头数:", sorted(shots), "| 通用要求长度:", len(tail))

SEGMENTS = [[1, 2], [3, 4], [5, 6], [7, 8], [9]]
MEGAPIXELS, DURATION = 1.0, 12

def build_prompt(idx_list):
    seg_intro = "本段视频请依次演绎以下分镜（其余风格、人物一致性、禁止项要求完全不变）：\n"
    return (header + "\n" + seg_intro + "\n".join(shots[i] for i in idx_list) + "\n" + tail)

def set_workflow(prompt_text, image_name, prefix):
    d = json.load(open(WF))
    for n in d["nodes"]:
        t = n["type"]
        wv = n.get("widgets_values")
        if t == "ResolutionSelector" and isinstance(wv, list):
            wv[0], wv[1], wv[2] = "4:3 (Standard)", MEGAPIXELS, 32
        elif t == "PrimitiveFloat" and isinstance(wv, list):
            wv[0] = DURATION
        elif t == "PrimitiveStringMultiline" and isinstance(wv, list):
            wv[0] = prompt_text
        elif t == "LoadImage" and isinstance(wv, list) and wv[0] in ("red_superboy_on_city_roof.png", "grid_storyboard.png"):
            wv[0] = image_name
        elif t == "SaveVideo" and isinstance(wv, list):
            wv[0] = "video/" + prefix
    json.dump(d, open(WF, "w"), ensure_ascii=False, indent=2)

def to_api(prefix):
    subprocess.run(["python3", "/mnt/workspace/convert_wf.py"], check=True,
                   stdout=subprocess.DEVNULL)
    d = json.load(open("/mnt/workspace/api_prompt.json"))["prompt"]
    d["136"]["inputs"].pop("last_frame", None)
    d.pop("139", None)
    d["92"]["inputs"]["filename_prefix"] = "video/" + prefix
    return {"prompt": d}

def wait_output(prefix, timeout=1800):
    pattern = os.path.join(OUT, prefix + "_*.mp4")
    t0 = time.time()
    while time.time() - t0 < timeout:
        fs = glob.glob(pattern)
        if fs:
            time.sleep(2)
            return sorted(fs, key=os.path.getmtime)[-1]
        time.sleep(10)
    return None

def last_frame(video_path, out_png):
    import av
    from PIL import Image
    c = av.open(video_path)
    stream = c.streams.video[0]
    frames = []
    for f in c.decode(stream):
        frames.append(f)
    img = frames[-1].to_image()
    img.convert("RGB").save(out_png)
    c.close()
    return out_png

results = []
prev_img = "grid_storyboard.png"
for i, seg in enumerate(SEGMENTS, 1):
    prefix = f"story60_{i:02d}"
    print(f"\n===== 第 {i}/5 段：镜头{seg} =====", flush=True)
    set_workflow(build_prompt(seg), prev_img, prefix)
    api = to_api(prefix)
    r = requests.post(f"{BASE}/prompt", json=api, timeout=120).json()
    if r.get("node_errors"):
        print("提交失败:", r["node_errors"])
        break
    print("已提交:", r["prompt_id"], flush=True)
    f = wait_output(prefix)
    if not f:
        print("生成超时，中止")
        break
    print("完成:", f, flush=True)
    results.append(f)
    if i < len(SEGMENTS):
        prev_img = f"story60_{i}_last.png"
        last_frame(f, os.path.join(INPUT, prev_img))
        print("已抽出尾帧 ->", prev_img, flush=True)

print("\n全部段完成:", results)
json.dump(results, open("/mnt/workspace/segments.json", "w"))
