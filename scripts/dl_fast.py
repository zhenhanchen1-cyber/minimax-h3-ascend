import os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = "/mnt/workspace/ComfyUI/models"
FILES = [
    ("https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors",
     BASE + "/diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors"),
    ("https://hf-mirror.com/ethanfel/Qwen3-VL-32B-Ultra-Heretic-H3-ComfyUI-INT8-ConvRot/resolve/main/qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot.safetensors",
     BASE + "/text_encoders/qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot.safetensors"),
    ("https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
     BASE + "/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors"),
]
NCHUNK = int(os.environ.get("NCHUNK", "11"))
CHUNK = 64 * 1024 * 1024

lock = threading.Lock()
total_bytes = [0]

def head_size(url):
    r = requests.head(url, allow_redirects=True, timeout=60)
    return int(r.headers["Content-Length"])

def get_chunk(url, path, start, end):
    for attempt in range(5):
        try:
            downloaded = os.path.getsize(path) if os.path.exists(path) else 0
            # 分片进度文件
            pf = f"{path}.p{start}"
            pos = start
            if os.path.exists(pf):
                pos = start + os.path.getsize(pf)
            if pos > end:
                return end - start + 1
            headers = {"Range": f"bytes={pos}-{end}"}
            r = requests.get(url, headers=headers, stream=True, timeout=60)
            r.raise_for_status()
            with open(pf, "ab") as f, open(path, "r+b") as tgt:
                tgt.seek(pos)
                for buf in r.iter_content(1 << 20):
                    if not buf:
                        continue
                    f.write(buf)
                    tgt.write(buf)
                    with lock:
                        total_bytes[0] += len(buf)
            if os.path.getsize(pf) != end - start + 1:
                raise RuntimeError("size mismatch")
            return end - start + 1
        except Exception as e:
            print("retry", path, start, repr(e)[:80], flush=True)
            time.sleep(3)
    return 0

def download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    size = head_size(url)
    print("SIZE", os.path.basename(path), size / 1e9, "GB", flush=True)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.truncate(size)
    elif os.path.getsize(path) != size:
        with open(path, "r+b") as f:
            f.truncate(size)
    ranges = []
    s = 0
    while s < size:
        e = min(s + CHUNK - 1, size - 1)
        ranges.append((s, e))
        s = e + 1
    # 按已完成的分片过滤
    todo = []
    for a, b in ranges:
        pf = f"{path}.p{a}"
        if os.path.exists(pf) and os.path.getsize(pf) == b - a + 1:
            continue
        todo.append((a, b))
    print("chunks todo:", len(todo), "of", len(ranges), flush=True)
    with ThreadPoolExecutor(max_workers=NCHUNK) as ex:
        list(ex.map(lambda rg: get_chunk(url, path, rg[0], rg[1]), todo))
    # 清理分片标记
    for a, b in ranges:
        pf = f"{path}.p{a}"
        if os.path.exists(pf):
            os.remove(pf)
    got = os.path.getsize(path)
    print(("OK " if got == size else "INCOMPLETE ") + path, got / 1e9, "GB", flush=True)

def reporter():
    last = [0]
    while not done[0]:
        time.sleep(30)
        d = (total_bytes[0] - last[0]) / 30 / 1e6
        last[0] = total_bytes[0]
        print(f"[speed] {d:.1f} MB/s  transferred={total_bytes[0]/1e9:.2f} GB", flush=True)

done = [False]
threading.Thread(target=reporter, daemon=True).start()
with ThreadPoolExecutor(max_workers=len(FILES)) as ex:
    list(ex.map(lambda item: download(item[0], item[1]), FILES))
done[0] = True
print("ALL_DONE", flush=True)
