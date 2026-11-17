"""生成三方案对比图：同一段输入，三种配色并排。"""
import importlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
MSYH = r"C:\Windows\Fonts\msyh.ttc"
MSYH_BD = r"C:\Windows\Fonts\msyhbd.ttc"
THEMES = [
    ("parch", "羊皮卷 · 照截图复刻（单线金边 + 角饰）"),
    ("foam", "浪花泡沫 · 浅色日常"),
    ("night", "深海夜航 · 深色护眼"),
    ("cream", "软萌奶油 · 浅色腮红"),
]


def font(size, bold=False):
    return ImageFont.truetype(MSYH_BD if bold else MSYH, size)


def mock(theme: str) -> Image.Image:
    """临时切主题，借用 preview_v2 的渲染逻辑出一张带文字的横排窗。"""
    os.environ["SKIN_THEME"] = theme
    for mod in ("spec_v2", "preview_v2"):
        if mod in sys.modules:
            del sys.modules[mod]
    import preview_v2 as P

    h1 = P.render_h1(0, pinyin="ni hao shi jie",
                     cands=("你好", "拟合", "尼好", "你", "匿名"))
    return h1.convert("RGBA")


def main() -> None:
    tiles = []
    for key, label in THEMES:
        im = mock(key)
        tiles.append((label, im))

    pad, head, gap = 18, 30, 14
    w = max(im.width for _, im in tiles) + pad * 2
    h = sum(im.height + head + gap for _, im in tiles) + pad
    canvas = Image.new("RGB", (w, h), (244, 246, 250))
    d = ImageDraw.Draw(canvas)

    y = pad
    for label, im in tiles:
        d.text((pad, y), label, font=font(14, bold=True), fill=(30, 38, 60))
        y += head
        canvas.paste(im, (pad, y), im)
        y += im.height + gap

    out = ROOT / "对比图-四方案.png"
    canvas.save(out, quality=95)
    print("compare ->", out, canvas.size)


if __name__ == "__main__":
    main()
