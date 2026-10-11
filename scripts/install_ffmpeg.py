import subprocess, sys, os, glob

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-i",
                "https://pypi.tuna.tsinghua.edu.cn/simple", "imageio-ffmpeg"], check=False)
try:
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    print("FFMPEG:", exe)
    os.makedirs("/mnt/workspace/bin", exist_ok=True)
    if not os.path.exists("/mnt/workspace/bin/ffmpeg"):
        os.symlink(exe, "/mnt/workspace/bin/ffmpeg")
    print(subprocess.run(["/mnt/workspace/bin/ffmpeg", "-version"],
                         capture_output=True, text=True).stdout.splitlines()[0])
except Exception as e:
    print("ERR", repr(e)[:200])
