import json

p = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora_int8_2npu.json"
d = json.load(open(p))
names = ["red_superboy_on_city_roof.png", "mecha_dragon_lightning.png"]
i = 0
for n in d.get("nodes", []):
    if n.get("type") == "LoadImage" and isinstance(n.get("widgets_values"), list):
        n["widgets_values"][0] = names[min(i, len(names) - 1)]
        i += 1
json.dump(d, open(p, "w"), ensure_ascii=False, indent=2)
print("images set:", names[:i])
