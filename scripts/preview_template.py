"""模板模式预览：无立绘、无状态栏，只看输入框本体。"""
import os
import sys
from pathlib import Path

os.environ["SKIN_TEMPLATE"] = "1"
os.environ.setdefault("SKIN_THEME", "foam")

from PIL import Image, ImageDraw, ImageFont

import spec_v2 as S

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
BUILD = ROOT / f"build_{S.THEME}_tpl"
FONT = r"C:\Windows\Fonts\msyh.ttc"


def render(name, marge_key, vertical=False, cands=None):
    im = Image.open(BUILD / f"{name}.png").convert("RGBA")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, S.FONT_SIZE)
    pt, _pb, pl, _pr = S.SCHEMES[marge_key]["pinyin_marge"]
    ct, _cb, cl, _cr = S.SCHEMES[marge_key]["zhongwen_marge"]
    C = S.COLORS
    d.text((pl, pt), "ni hao shi jie", font=f, fill=C["pinyin_color"] + (255,))
    y = pt + round(S.FONT_SIZE * 1.32) + ct
    x = cl
    for i, w in enumerate(cands or ("你好", "拟合", "尼好", "你", "匿名", "泥壕"), 1):
        seg = f"{i} {w}"
        col = C["zhongwen_first_color"] if i == 1 else C["zhongwen_color"]
        d.text((x, y), seg, font=f, fill=col + (255,))
        if vertical:
            y += 26
        else:
            x += d.textlength(seg, font=f) + 14
    return im


def checker(size, cell=12):
    bg = Image.new("RGB", size, (247, 248, 250))
    d = ImageDraw.Draw(bg)
    for yy in range(0, size[1], cell):
        for xx in range(0, size[0], cell):
            if (xx // cell + yy // cell) % 2:
                d.rectangle([xx, yy, xx + cell - 1, yy + cell - 1], fill=(232, 234, 238))
    return bg.convert("RGBA")


def main():
    h1 = render("h1", "H1")
    v1 = render("v1", "V1", vertical=True)
    h2c = Image.open(BUILD / "h2c.png").convert("RGBA")
    h2p = Image.open(BUILD / "h2p.png").convert("RGBA")

    tiles = [("横排合并窗 H1 640×136", h1), ("竖排合并窗 V1 260×340", v1),
             ("横排分离 H2 拼音条 + 候选条", None)]
    pad = 16
    w = max(t[1].width if t[1] else 640 for t in tiles) + pad * 2
    h = 0
    for label, im in tiles:
        h += 30 + (im.height if im else (40 + 88 + 8)) + 14

    canvas = Image.new("RGB", (w, h + pad), (250, 251, 253))
    from PIL import ImageDraw as ID
    d = ID.Draw(canvas)
    y = pad
    for label, im in tiles:
        d.text((pad, y), label, font=ImageFont.truetype(FONT, 13), fill=(40, 48, 70))
        y += 26
        if im is None:
            for strip in (h2p, h2c):
                bg = checker(strip.size)
                bg.alpha_composite(strip)
                canvas.paste(bg.convert("RGB"), (pad, y))
                y += strip.height + 8
        else:
            bg = checker(im.size)
            bg.alpha_composite(im)
            canvas.paste(bg.convert("RGB"), (pad, y))
            y += im.height + 14

    out = ROOT / "预览图-框模板.png"
    canvas.save(out)
    print("preview ->", out, canvas.size)


if __name__ == "__main__":
    main()
