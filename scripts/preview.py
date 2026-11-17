"""按 spec 的几何把真实文本叠到贴图上，做几何自检 + 产出给用户看的预览图。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import spec

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
BUILD = ROOT / "build"
WORK = ROOT / "work"
MSYH = r"C:\Windows\Fonts\msyh.ttc"
MSYH_BD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    try:
        return ImageFont.truetype(MSYH_BD if bold else MSYH, size)
    except OSError:
        return ImageFont.truetype(MSYH, size)


def line_height(fs):
    return round(fs * 1.32)


def load(name):
    return Image.open(BUILD / name).convert("RGBA")


def draw_text(d: ImageDraw.ImageDraw, xy, text, fnt, rgb):
    d.text(xy, text, font=fnt, fill=rgb + (255,))


def render_bar() -> Image.Image:
    bar = load("bar.png")
    for key, x, y, normal, _hover, _down in spec.BAR_BUTTONS:
        icon = load(normal[0])
        bar.alpha_composite(icon, (x, y))
    return bar


def render_h1(pinyin="ni hao shi jie", cands=("你好", "拟合", "尼好", "你", "匿名")) -> Image.Image:
    s = spec.SCHEMES["H1"]
    im = load(s["pic"])
    d = ImageDraw.Draw(im)
    fs = spec.FONT_SIZE
    fnt = font(fs)
    ptop, _pbot, pl, _pr = s["pinyin_marge"]
    cgap, _cb, cl, _cr = s["zhongwen_marge"]
    draw_text(d, (pl, ptop), pinyin, fnt, spec.COLORS["pinyin_color"])
    ctop = ptop + line_height(fs) + cgap
    x = cl
    for i, word in enumerate(cands, 1):
        seg = f"{i} {word}"
        color = spec.COLORS["zhongwen_first_color"] if i == 1 else spec.COLORS["zhongwen_color"]
        draw_text(d, (x, ctop), seg, fnt, color)
        x += d.textlength(seg, font=fnt) + 14
    return im


def render_v1(pinyin="ni hao", cands=("你好", "拟合", "尼好", "你", "匿名", "泥壕")) -> Image.Image:
    s = spec.SCHEMES["V1"]
    im = load(s["pic"])
    d = ImageDraw.Draw(im)
    fs = spec.FONT_SIZE
    fnt = font(fs)
    ptop, _pbot, pl, _pr = s["pinyin_marge"]
    cgap, _cb, cl, _cr = s["zhongwen_marge"]
    draw_text(d, (pl, ptop), pinyin, fnt, spec.COLORS["pinyin_color"])
    y = ptop + line_height(fs) + cgap
    step = 26
    for i, word in enumerate(cands, 1):
        color = spec.COLORS["zhongwen_first_color"] if i == 1 else spec.COLORS["zhongwen_color"]
        draw_text(d, (cl, y), f"{i} {word}", fnt, color)
        y += step
    return im


def checker(size, cell=12):
    bg = Image.new("RGB", size, (247, 248, 250))
    d = ImageDraw.Draw(bg)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(232, 234, 238))
    return bg.convert("RGBA")


def section(title, im, scale=1):
    """把一张贴图放到浅色底板上并加标题，返回底板图像。"""
    w = max(im.width, 240)
    pad = 16
    head = 28
    canvas = Image.new("RGBA", (w + pad * 2, im.height + head + pad), (252, 252, 253, 255))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 6), title, font=font(14, bold=True), fill=(40, 48, 72, 255))
    bg = checker(im.size)
    bg.alpha_composite(im)
    canvas.alpha_composite(bg, (pad, head))
    return canvas


def main() -> None:
    bar = render_bar()
    h1 = render_h1()
    v1 = render_v1()
    h2 = load("h2c.png")
    v2 = load("v2c.png")

    # 保存单图自检
    for name, im in (("p_bar", bar), ("p_h1", h1), ("p_v1", v1)):
        im.save(WORK / f"{name}.png")

    # 拼一张总览：左侧状态栏 + 横排，右侧竖排
    blocks = [
        section("状态栏 320×92（含 6 个按钮）", bar),
        section("横排合并窗 H1 640×150", h1),
        section("横排分离窗 H2 候选条 640×92", h2),
    ]
    right = [
        section("竖排合并窗 V1 260×380", v1),
        section("竖排分离窗 V2 候选窗 240×360", v2),
    ]
    lw = max(b.width for b in blocks)
    lh = sum(b.height + 10 for b in blocks)
    rw = max(b.width for b in right)
    rh = sum(b.height + 10 for b in right)
    W, H = lw + rw + 40, max(lh, rh) + 30

    canvas = Image.new("RGBA", (W, H), (240, 242, 246, 255))
    y = 14
    for b in blocks:
        canvas.alpha_composite(b, (14, y))
        y += b.height + 10
    y = 14
    for b in right:
        canvas.alpha_composite(b, (lw + 28, y))
        y += b.height + 10

    out = ROOT / "预览图.png"
    canvas.convert("RGB").save(out, quality=95)
    print("preview ->", out, canvas.size)


if __name__ == "__main__":
    main()
