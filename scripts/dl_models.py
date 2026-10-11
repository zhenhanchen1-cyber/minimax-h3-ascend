# -*- coding: utf-8 -*-
"""
MiniMax-H3 on Ascend —— 模型下载脚本
特点：分片并行（16 连接/文件，实测聚合 ~40MB/s）、断点续传、走 hf-mirror
用法：COMFY_HOME=/mnt/workspace/ComfyUI python3 dl_models.py
可选：INCLUDE_HERETIC_TE=1 额外下载无审查文本编码器（26GB）
      INCLUDE_REF2VA=0    跳过 Ref2VA 主模型（21GB）
"""
import os, threading, requests
from concurrent.futures import ThreadPoolExecutor

M = os.environ.get("COMFY_HOME", "/mnt/workspace/ComfyUI") + "/models"
BASE = "https://hf-mirror.com"
INC_HERETIC = os.environ.get("INCLUDE_HERETIC_TE", "1") != "0"
INC_REF2VA = os.environ.get("INCLUDE_REF2VA", "1") != "0"
NCHUNK, CHUNK = 16, 64 * 1024 * 1024

# (repo, 仓库内路径, 本地目录)
FILES = [
    ("Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors", "diffusion_models"),
    ("Comfy-Org/MiniMax-H3", "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors", "text_encoders"),
    ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_fp16.safetensors", "vae"),
    ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors", "vae"),
    ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_int8_convrot.safetensors", "vae"),
    ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", "loras"),
    ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "loras"),
]
if INC_REF2VA:
    FILES.append(("Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors", "diffusion_models"))
if INC_HERETIC:
    FILES.append(("ethanfel/Qwen3-VL-32B-Ultra-Heretic-H3-ComfyUI-INT8-ConvRot",
                  "qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot.safetensors", "text_encoders"))

lock = threading.Lock()
total = [0]


def dl(repo, rpath, subdir):
    url = f"{BASE}/{repo}/resolve/main/{rpath}"
    path = os.path.join(M, subdir, os.path.basename(rpath))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    size = int(requests.head(url, allow_redirects=True, timeout=60).headers["Content-Length"])
    fname = os.path.basename(path)
    if os.path.exists(path) and os.path.getsize(path) == size:
        print(f"[跳过] {fname} ({size/1e9:.2f}GB 已存在)")
        return
    print(f"[下载] {fname} ({size/1e9:.2f}GB)", flush=True)
    if not os.path.exists(path):
        open(path, "wb").truncate(size)
    elif os.path.getsize(path) != size:
        open(path, "r+b").truncate(size)

    ranges, s = [], 0
    while s < size:
        e = min(s + CHUNK - 1, size - 1)
        ranges.append((s, e)); s = e + 1

    def get(rg):
        a, b = rg
        pf = f"{path}.p{a}"
        pos = a + (os.path.getsize(pf) if os.path.exists(pf) else 0)
        for _ in range(6):
            try:
                while pos <= b:
                    r = requests.get(url, headers={"Range": f"bytes={pos}-{b}"}, stream=True, timeout=90)
                    r.raise_for_status()
                    with open(pf, "ab") as f, open(path, "r+b") as t:
                        t.seek(pos)
                        for buf in r.iter_content(1 << 20):
                            if buf:
                                f.write(buf); t.write(buf); pos += len(buf)
                                with lock: total[0] += len(buf)
                break
            except Exception as e:
                print(f"  [重试] {fname} @{a}: {repr(e)[:60]}", flush=True)
        if os.path.exists(pf):
            os.remove(pf)

    with ThreadPoolExecutor(max_workers=NCHUNK) as ex:
        list(ex.map(get, ranges))
    ok = os.path.getsize(path) == size
    print(f"[{'完成' if ok else '未完成'}] {fname}", flush=True)


def reporter():
    import time
    last = [0]
    while not done[0]:
        time.sleep(30)
        d = (total[0] - last[0]) / 30 / 1e6
        last[0] = total[0]
        print(f"  --- 速度 {d:.1f} MB/s，本次累计 {total[0]/1e9:.2f} GB", flush=True)


done = [False]
threading.Thread(target=reporter, daemon=True).start()
for f in FILES:
    dl(*f)
done[0] = True
print("\n全部模型下载完成。若工作流里选不到新模型，重启 ComfyUI 即可。")
