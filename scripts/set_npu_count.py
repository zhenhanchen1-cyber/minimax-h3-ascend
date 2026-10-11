# -*- coding: utf-8 -*-
"""按实际 NPU 卡数更新所有工作流中 MultiNPUParallelConfig 的 npu_count。
用法: python3 set_npu_count.py 0,1,2,3   (或直接传卡数 4)
"""
import json, os, sys, glob

arg = sys.argv[1] if len(sys.argv) > 1 else "0,1"
count = len(arg.split(",")) if "," in arg else int(arg)
valid = min([1, 2, 4, 8], key=lambda v: abs(v - count))

root = os.environ.get("COMFY_HOME", "/mnt/workspace/ComfyUI")
wdir = os.path.join(root, "user/default/workflows/minimax-h3")
changed = 0
for f in glob.glob(os.path.join(wdir, "*.json")):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    dirty = False
    for n in d.get("nodes", []):
        if n.get("type") == "MultiNPUParallelConfig" and isinstance(n.get("widgets_values"), list) and n["widgets_values"]:
            if n["widgets_values"][0] != str(valid):
                n["widgets_values"][0] = str(valid)
                dirty = True
    if dirty:
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        changed += 1
        print(f"已更新 {os.path.basename(f)} -> npu_count={valid}")
print(f"共更新 {changed} 个工作流（npu_count={valid}）")
