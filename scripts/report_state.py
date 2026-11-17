"""列出完整版与上架档的帧数、时长、体积与合规性。"""
import io
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")

for label, sub in (("完整版", "out"), ("上架档", "out/upload")):
    print(f"\n=== {label} ({sub}) ===")
    for p in sorted((ROOT / sub).glob("鲸鱼娘-*.ssf")):
        z = zipfile.ZipFile(p)
        if "bar.png" not in z.namelist():
            print(f"  {p.name}: 无状态栏")
            continue
        im = Image.open(io.BytesIO(z.read("bar.png")))
        total = 0
        for i in range(im.n_frames):
            im.seek(i)
            total += im.info.get("duration", 0)
        kb = p.stat().st_size / 1024
        flag = ""
        if label == "上架档":
            flag = "OK" if kb < 600 else "超限"
        print(f"  {p.name}: {im.n_frames:2d} 帧 / {total/1000:.2f} 秒 / {kb:.0f} KiB {flag}")
