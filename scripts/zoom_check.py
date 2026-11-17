"""放大检查贴图细节，并把文本按 skin.ini 的 marge 叠上去做几何自检。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BUILD = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin\build")
WORK = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin\work")
FONT = r"C:\Windows\Fonts\msyh.ttc"


def zoom(name: str, scale: int = 4) -> Image.Image:
    im = Image.open(BUILD / f"{name}.png").convert("RGBA")
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def on_checker(im: Image.Image) -> Image.Image:
    bg = Image.new("RGB", im.size, (250, 250, 250))
    d = ImageDraw.Draw(bg)
    for y in range(0, im.height, 12):
        for x in range(0, im.width, 12):
            if (x // 12 + y // 12) % 2:
                d.rectangle([x, y, x + 11, y + 11], fill=(228, 228, 228))
    out = bg.convert("RGBA")
    out.alpha_composite(im)
    return out


def sheet() -> None:
    bar = zoom("bar", 3)
    icons = [zoom(n, 5) for n in ("cn1", "cn2", "cn3", "quan1", "fan1", "quanpin1", "key1", "menu1")]
    w = max(bar.width, sum(i.width + 8 for i in icons))
    h = bar.height + max(i.height for i in icons) + 24
    canvas = Image.new("RGB", (w, h), (250, 250, 250))
    canvas.paste(on_checker(bar).convert("RGB"), (0, 0))
    x = 0
    for i in icons:
        canvas.paste(on_checker(i).convert("RGB"), (x, bar.height + 16))
        x += i.width + 8
    canvas.save(WORK / "zoom-check.png")
    print("zoom:", canvas.size)


if __name__ == "__main__":
    sheet()
