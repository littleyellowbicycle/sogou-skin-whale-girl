"""无框版预览：按 spec_v2 的 marge 叠真实文本，并把按钮合成到状态栏上。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import spec_v2 as S

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
BUILD = ROOT / f"build_{S.THEME}"
WORK = ROOT / "work"
MSYH = r"C:\Windows\Fonts\msyh.ttc"
MSYH_BD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    try:
        return ImageFont.truetype(MSYH_BD if bold else MSYH, size)
    except OSError:
        return ImageFont.truetype(MSYH, size)


def lh(fs):
    return round(fs * 1.32)


def load(name, frame=0):
    im = Image.open(BUILD / name)
    if getattr(im, "n_frames", 1) > 1:
        im.seek(frame)
    return im.convert("RGBA")


def render_bar(frame=0):
    bar = load("bar.png", frame)
    for key, x, y, normal, _h, _d in S.BAR_BUTTONS:
        bar.alpha_composite(load(normal[0]), (x, y))
    return bar


def render_h1(frame=0, pinyin="ni hao shi jie", cands=("你好", "拟合", "尼好", "你", "匿名")):
    s = S.SCHEMES["H1"]
    im = load("h1.png", frame)
    d = ImageDraw.Draw(im)
    fs, fnt = S.FONT_SIZE, font(S.FONT_SIZE)
    ptop, _pb, pl, _pr = s["pinyin_marge"]
    cgap, _cb, cl, _cr = s["zhongwen_marge"]
    d.text((pl, ptop), pinyin, font=fnt, fill=S.COLORS["pinyin_color"] + (255,))
    x, y = cl, ptop + lh(fs) + cgap
    for i, w in enumerate(cands, 1):
        seg = f"{i} {w}"
        c = S.COLORS["zhongwen_first_color"] if i == 1 else S.COLORS["zhongwen_color"]
        d.text((x, y), seg, font=fnt, fill=c + (255,))
        x += d.textlength(seg, font=fnt) + 14
    return im


def render_v1(frame=0, pinyin="ni hao", cands=("你好", "拟合", "尼好", "你", "匿名", "泥壕")):
    s = S.SCHEMES["V1"]
    im = load("v1.png", frame)
    d = ImageDraw.Draw(im)
    fs, fnt = S.FONT_SIZE, font(S.FONT_SIZE)
    ptop, _pb, pl, _pr = s["pinyin_marge"]
    cgap, _cb, cl, _cr = s["zhongwen_marge"]
    d.text((pl, ptop), pinyin, font=fnt, fill=S.COLORS["pinyin_color"] + (255,))
    y = ptop + lh(fs) + cgap
    for i, w in enumerate(cands, 1):
        c = S.COLORS["zhongwen_first_color"] if i == 1 else S.COLORS["zhongwen_color"]
        d.text((cl, y), f"{i} {w}", font=fnt, fill=c + (255,))
        y += 26
    return im


def render_h2( pinyin="ni hao", cands=("你好", "拟合", "尼好", "你", "匿名")):
    s = S.SCHEMES["H2"]
    strip = load(s["pinyin_pic"])
    d = ImageDraw.Draw(strip)
    fnt = font(S.FONT_SIZE)
    pt, _pb, pl, _pr = s["pinyin_marge"]
    d.text((pl, pt), pinyin, font=fnt, fill=S.COLORS["pinyin_color"] + (255,))

    bar = load(s["zhongwen_pic"])
    d2 = ImageDraw.Draw(bar)
    ct, _cb, cl, _cr = s["zhongwen_marge"]
    x = cl
    for i, w in enumerate(cands, 1):
        seg = f"{i} {w}"
        c = S.COLORS["zhongwen_first_color"] if i == 1 else S.COLORS["zhongwen_color"]
        d2.text((x, ct), seg, font=fnt, fill=c + (255,))
        x += d2.textlength(seg, font=fnt) + 14
    return strip, bar


def checker(size, cell=12):
    bg = Image.new("RGB", size, (246, 247, 250))
    d = ImageDraw.Draw(bg)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(230, 232, 238))
    return bg.convert("RGBA")


def section(title, im, note=""):
    pad, head = 14, 26
    w = max(im.width, 260)
    canvas = Image.new("RGBA", (w + pad * 2, im.height + head + pad), (252, 252, 253, 255))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 5), title, font=font(13, bold=True), fill=(38, 46, 70, 255))
    if note:
        d.text((pad + d.textlength(title, font=font(13, bold=True)) + 8, 6),
               note, font=font(11), fill=(120, 128, 148, 255))
    bg = checker(im.size)
    bg.alpha_composite(im)
    canvas.alpha_composite(bg, (pad, head))
    return canvas


def main() -> None:
    bar = render_bar(0)
    h1 = render_h1(0)
    v1 = render_v1(0)
    strip, h2c = render_h2()

    left = [
        section("状态栏（第1帧）", bar, "300×160 十八帧 APNG（3 待机 + 8 吃白饭 + 2 间隔 + 5 敲键盘）"),
        section("横排合并窗 H1（第1帧）", h1, "640×136 四帧 APNG"),
        section("横排分离 H2 拼音条 + 候选条", strip),
    ]
    right = [
        section("竖排合并窗 V1（第1帧）", v1, "260×360 四帧 APNG"),
        section("H2 候选条", h2c, "640×88"),
        section("V2 候选窗", load("v2c.png"), "240×340"),
    ]

    lw = max(b.width for b in left)
    rw = max(b.width for b in right)
    lh_sum = sum(b.height + 10 for b in left)
    rh_sum = sum(b.height + 10 for b in right)
    W, H = lw + rw + 40, max(lh_sum, rh_sum) + 40

    canvas = Image.new("RGBA", (W, H), (238, 240, 245, 255))
    y = 16
    for b in left:
        canvas.alpha_composite(b, (14, y))
        y += b.height + 10
    y = 16
    for b in right:
        canvas.alpha_composite(b, (lw + 28, y))
        y += b.height + 10

    out = ROOT / f"预览图-{S.THEME_LABEL}.png"
    canvas.convert("RGB").save(out)
    print("preview ->", out, canvas.size)

    # 顺便把动画抽几帧横排出来看（确认真的在动）
    for name, n in (("bar", S.BAR_FRAMES), ("h1", 4)):
        frames = [load(f"{name}.png", i) for i in range(n)]
        strip_w = sum(f.width for f in frames) + 8 * (n - 1)
        sheet = Image.new("RGBA", (strip_w, frames[0].height), (246, 247, 250, 255))
        x = 0
        for f in frames:
            sheet.alpha_composite(f, (x, 0))
            x += f.width + 8
        sheet.convert("RGB").save(WORK / f"frames-{S.THEME}-{name}.png")
        print("frames ->", name, sheet.size)


if __name__ == "__main__":
    main()
