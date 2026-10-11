import json, os, subprocess, shutil

FF = "/mnt/workspace/bin/ffmpeg"
segs = json.load(open("/mnt/workspace/segments.json"))
segs = sorted(segs)
print("待拼接:", [os.path.basename(s) for s in segs])

lst = "/mnt/workspace/concat_list.txt"
with open(lst, "w") as f:
    for s in segs:
        f.write(f"file '{s}'\n")

out = "/mnt/workspace/ComfyUI/output/video/story_60s_final.mp4"
r = subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], capture_output=True, text=True)
print("rc:", r.returncode, r.stderr[-300:] if r.returncode else "")
if os.path.exists(out):
    print("输出:", out, os.path.getsize(out) / 1e6, "MB")

import av
c = av.open(out)
print("总时长:", round(float(c.duration) / 1e6, 2), "s")
for s in c.streams:
    print(" ", s.type, s.codec_context.name, getattr(s, "width", ""), getattr(s, "height", ""))
