# -*- coding: utf-8 -*-
"""
九宫格切图工具
用法（在本机 CMD 或 PowerShell 里运行）：
    python 切九宫格.py 九宫格图片.png
运行后在图片同目录生成 9 张小图：cell_1.png ~ cell_9.png
（顺序：从左到右、从上到下，即 1~9 号镜头）
"""
import sys, os

try:
    from PIL import Image
except ImportError:
    print("第一次使用需要先装 Pillow，正在自动安装...")
    os.system(f'"{sys.executable}" -m pip install pillow -i https://pypi.tuna.tsinghua.edu.cn/simple')
    from PIL import Image

if len(sys.argv) < 2:
    print("用法: python 切九宫格.py 九宫格图片.png")
    sys.exit(1)

src = sys.argv[1]
if not os.path.exists(src):
    print("找不到文件:", src)
    sys.exit(1)

img = Image.open(src).convert("RGB")
W, H = img.size
cw, ch = W // 3, H // 3
outdir = os.path.splitext(src)[0] + "_cells"
os.makedirs(outdir, exist_ok=True)

n = 1
for r in range(3):
    for c in range(3):
        box = (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)
        cell = img.crop(box)
        path = os.path.join(outdir, f"cell_{n}.png")
        cell.save(path)
        print("已保存", path)
        n += 1

print(f"\n完成！9 张图在: {outdir}")
print("下一步：把它们上传到 ComfyUI 的 First Frame 节点，一格生成一段视频")
