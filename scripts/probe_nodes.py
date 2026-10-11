import json, requests

for t in ["MiniMaxH3ImageToVideo", "ResolutionSelector", "MiniMaxH3TurboSampler", "MiniMaxH3VAEDecodeParallel"]:
    d = requests.get(f"http://127.0.0.1:8188/object_info/{t}", timeout=30).json()[t]["input"]
    print("=== ", t)
    print("REQUIRED:", json.dumps(d.get("required", {}), ensure_ascii=False)[:700])
    print("OPTIONAL:", json.dumps(d.get("optional", {}), ensure_ascii=False)[:700])
