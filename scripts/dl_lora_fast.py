import os, threading, time
from concurrent.futures import ThreadPoolExecutor
import requests

URL = "https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
PATH = "/mnt/workspace/ComfyUI/models/loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
NCHUNK, CHUNK = 16, 8 * 1024 * 1024
lock = threading.Lock()

size = int(requests.head(URL, allow_redirects=True, timeout=60).headers["Content-Length"])
print("SIZE", size / 1e6, "MB", flush=True)
if not os.path.exists(PATH):
    open(PATH, "wb").truncate(size)
os.path.getsize(PATH) != size and open(PATH, "r+b").truncate(size)

ranges, s = [], 0
while s < size:
    e = min(s + CHUNK - 1, size - 1)
    ranges.append((s, e))
    s = e + 1

def get(rg):
    a, b = rg
    pf = f"{PATH}.p{a}"
    pos = a + (os.path.getsize(pf) if os.path.exists(pf) else 0)
    while pos <= b:
        r = requests.get(URL, headers={"Range": f"bytes={pos}-{b}"}, stream=True, timeout=60)
        r.raise_for_status()
        with open(pf, "ab") as f, open(PATH, "r+b") as t:
            t.seek(pos)
            for buf in r.iter_content(1 << 20):
                if buf:
                    f.write(buf); t.write(buf)
                    pos += len(buf)
    os.path.exists(pf) and os.remove(pf)

with ThreadPoolExecutor(max_workers=NCHUNK) as ex:
    list(ex.map(get, ranges))
print("OK", os.path.getsize(PATH) == size, os.path.getsize(PATH) / 1e6, "MB", flush=True)
