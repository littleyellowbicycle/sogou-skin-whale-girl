"""按搜狗皮肤站要求生成投稿图：效果图 ≤500x350、列表缩略图 ≤420x210，均为 jpg <600KB。

做法：直接从 .ssf 里取贴图和 skin.ini 的边距/配色，按真实排版叠字，
保证效果图和皮肤本体一致，而不是另画一张示意图。
"""
from __future__ import annotations

import configparser
import io
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
UPLOAD = ROOT / "out" / "upload"
STORE = ROOT / "out" / "store"
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size):
    return ImageFont.truetype(FONT, max(8, int(size)))


def bgr_to_rgb(s: str):
    v = int(s.strip(), 16)
    return (v % 256, (v % 65536) // 256, v // 65536)


def load_skin(ssf: Path):
    with zipfile.ZipFile(ssf) as z:
        raw = z.read("skin.ini")
        text = raw.decode("utf-16")
        cp = configparser.ConfigParser(allow_no_value=True, strict=False)
        cp.optionxform = str
        cp.read_string(text)

        def img(name):
            im = Image.open(io.BytesIO(z.read(name)))
            im.seek(0)
            return im.convert("RGBA")

        bar = img("bar.png")
        h1 = img("h1.png")

        # 状态栏按钮：按 skin.ini 里的 _pos / 文件名逐个叠上去
        if "StatusBar" in cp:
            sb = cp["StatusBar"]
            for key in [k for k in sb.keys() if k.endswith("_pos")]:
                name = key[:-4]
                pos = sb.get(key, "")
                files = sb.get(name, "")
                if not pos or not files:
                    continue
                try:
                    x, y = (int(v) for v in pos.split(","))
                    icon = img(files.split(",")[0].strip())
                except Exception:
                    continue
                bar.alpha_composite(icon, (x, y))

    disp = cp["Display"]
    colors = {
        "pinyin": bgr_to_rgb(disp["pinyin_color"]),
        "first": bgr_to_rgb(disp["zhongwen_first_color"]),
        "other": bgr_to_rgb(disp["zhongwen_color"]),
    }
    def margins(sec):
        p = [int(x) for x in cp[sec]["pinyin_marge"].split(",")]
        z_ = [int(x) for x in cp[sec]["zhongwen_marge"].split(",")]
        return p, z_

    return bar, h1, margins("Scheme_H1"), colors, int(disp["font_size"])


def render_h1(h1: Image.Image, pinyin_marge, zhongwen_marge, colors, fs, scale=1.0):
    im = h1.copy()
    if scale != 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    f = font(fs * scale)
    pt, _pb, pl, _pr = pinyin_marge
    ct, _cb, cl, _cr = zhongwen_marge
    d.text((pl * scale, pt * scale), "ni hao shi jie", font=f, fill=colors["pinyin"] + (255,))
    y = (pt + round(fs * 1.32) + ct) * scale
    x = cl * scale
    for i, w in enumerate(("你好", "拟合", "尼好", "你", "匿名"), 1):
        seg = f"{i} {w}"
        col = colors["first"] if i == 1 else colors["other"]
        d.text((x, y), seg, font=f, fill=col + (255,))
        x += d.textlength(seg, font=f) + 14 * scale
    return im


def backdrop(size):
    w, h = size
    bg = Image.new("RGB", size, (238, 242, 248))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=(int(238 - 10 * t), int(242 - 8 * t), int(248 - 6 * t)))
    return bg.convert("RGBA")


def compose(bar, h1c, size, bar_w):
    """把状态栏和候选窗摆到画布上，模拟真实桌面截图。"""
    W, H = size
    canvas = backdrop(size)

    hb = bar_w / bar.width
    b = bar.resize((bar_w, round(bar.height * hb)), Image.LANCZOS)
    canvas.alpha_composite(b, (W - b.width - 14, 12))

    hw = W - 40
    hs = hw / h1c.width
    h = h1c.resize((hw, round(h1c.height * hs)), Image.LANCZOS)
    canvas.alpha_composite(h, (20, H - h.height - 40))

    return canvas.convert("RGB")


def main() -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    rows = []
    for ssf in sorted(UPLOAD.glob("*.ssf")):
        bar, h1, (pm, zm), colors, fs = load_skin(ssf)
        h1c = render_h1(h1, pm, zm, colors, fs, scale=1.0)

        big = compose(bar, h1c, (500, 350), 240)
        thumb = compose(bar, h1c, (420, 210), 170)

        stem = ssf.stem
        p1 = STORE / f"{stem}-效果图.jpg"
        p2 = STORE / f"{stem}-缩略图.jpg"
        big.save(p1, "JPEG", quality=88, optimize=True)
        thumb.save(p2, "JPEG", quality=88, optimize=True)

        rows.append((stem, p1.stat().st_size, p2.stat().st_size, big.size, thumb.size))

    for stem, s1, s2, sz1, sz2 in rows:
        ok1 = s1 < 600 * 1024 and sz1[0] <= 500 and sz1[1] <= 350
        ok2 = s2 < 600 * 1024 and sz2[0] <= 420 and sz2[1] <= 210
        print(f"{stem}: 效果图 {sz1[0]}x{sz1[1]} {s1/1024:.0f}KiB {'OK' if ok1 else '不合规'} | "
              f"缩略图 {sz2[0]}x{sz2[1]} {s2/1024:.0f}KiB {'OK' if ok2 else '不合规'}")


if __name__ == "__main__":
    main()
