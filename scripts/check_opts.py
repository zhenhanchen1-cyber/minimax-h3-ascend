import requests, json

for t, key in [("UNETLoader", "unet_name"), ("LoraLoaderModelOnly", "lora_name"),
               ("CLIPLoader", "clip_name"), ("VAELoader", "vae_name")]:
    try:
        d = requests.get(f"http://127.0.0.1:8188/object_info/{t}", timeout=20).json()[t]
        opts = d["input"]["required"][key][0]
        print(f"{t} 可选：")
        for o in opts:
            print("   -", o)
    except Exception as e:
        print(t, "ERR", repr(e)[:80])
