import json, requests, sys

SRC = "/mnt/workspace/ComfyUI/user/default/workflows/minimax-h3/fl2va_8steps_lora_int8_2npu.json"
OUT = "/mnt/workspace/api_prompt.json"
BASE = "http://127.0.0.1:8188"

wf = json.load(open(SRC))
nodes = {n["id"]: n for n in wf["nodes"]}
links = {}
for l in wf.get("links", []):
    # [link_id, from_node, from_slot, to_node, to_slot, type]
    links[l[0]] = (l[1], l[2])

oi = requests.get(f"{BASE}/object_info", timeout=60).json()

prompt = {}
for nid, n in nodes.items():
    t = n["type"]
    if t in ("Note", "MarkdownNote") or n.get("mode") == 4:
        continue
    info = oi.get(t)
    if info is None:
        print("MISSING NODE TYPE:", t)
        sys.exit(1)
    spec = dict(info["input"].get("required", {}))
    spec.update(info["input"].get("optional", {}))
    # 输入名 -> 是否链接型
    inputs = {}
    ui_inputs = {i["name"]: i for i in n.get("inputs", []) if i.get("name")}
    widget_order = []
    for name, s in spec.items():
        ui = ui_inputs.get(name)
        lk = ui.get("link") if ui else None
        if lk is not None and lk in links:
            src = links[lk]
            inputs[name] = [str(src[0]), src[1]]
        else:
            # 其余（含 COMBO/STRING/INT 等控件，以及被转成输入的控件）都按顺序取 widgets_values
            widget_order.append(name)
    # 动态输入（如 values.a）在 spec 里没有，需从 UI inputs 补上
    for name, ui in ui_inputs.items():
        if name in inputs or name in widget_order:
            continue
        lk = ui.get("link")
        if lk is not None and lk in links:
            src = links[lk]
            inputs[name] = [str(src[0]), src[1]]
        elif "widget" not in ui:
            widget_order.append(name)
    wv = n.get("widgets_values", [])
    if isinstance(wv, dict):
        for k, v in wv.items():
            if k in spec:
                inputs[k] = v
    else:
        for name, val in zip(widget_order, wv):
            inputs[name] = val
    prompt[str(nid)] = {"class_type": t, "inputs": inputs}

json.dump({"prompt": prompt}, open(OUT, "w"), ensure_ascii=False, indent=2)
print("nodes:", len(prompt))
for nid, p in prompt.items():
    print(" ", nid, p["class_type"], list(p["inputs"].keys()))
