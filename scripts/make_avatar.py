"""用鲸鱼娘立绘做头像：圆形/方形、多种底色与描边。

不是 AI 生成，是裁切 + 构图 + 描边（图像合成）。
素材：work/whale-head.png（透明底头部特写）
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
SRC = ROOT / "work" / "whale-bust.png"
OUT = ROOT / "out" / "avatar"
S = 512          # 输出边长


def head_square() -> Image.Image:
    """从头部特写里取一个以脸为中心的方框。"""
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    side = int(w * 0.82)
    cx = int(w * 0.50)
    cy = int(h * 0.47)
    left = max(0, min(w - side, cx - side // 2))
    top = max(0, min(h - side, cy - side // 2))
    return im.crop((left, top, left + side, top + side))


def circle_mask(size: int, inset: int = 0) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([inset, inset, size - 1 - inset, size - 1 - inset], fill=255)
    return m


def vgrad(size, top, bottom):
    img = Image.new("RGB", (size, size), top)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        d.line([(0, y), (size, y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def make_circle(head, bg_top, bg_bottom, ring_color, ring_w=10, pad_ratio=0.98, glow=None):
    canvas = vgrad(S, bg_top, bg_bottom).convert("RGBA")

    # 柔和光晕
    if glow:
        g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([S * 0.10, S * 0.10, S * 0.90, S * 0.90], fill=glow)
        g = g.filter(ImageFilter.GaussianBlur(46))
        canvas.alpha_composite(g)

    # 角色：缩放到圆内并裁成圆形
    inner = int(S * pad_ratio)
    ch = head.resize((inner, inner), Image.LANCZOS)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    off = (S - inner) // 2
    layer.paste(ch, (off, off), ch)
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (S, S), 0),
                                   circle_mask(S, int(S * 0.055))))
    canvas.alpha_composite(layer)

    # 描边环
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    e = int(S * 0.055)
    d.ellipse([e, e, S - 1 - e, S - 1 - e], outline=ring_color, width=ring_w)
    canvas.alpha_composite(ring)
    return canvas


def make_rounded(head, bg_top, bg_bottom, ring_color, radius=92, ring_w=9):
    canvas = vgrad(S, bg_top, bg_bottom).convert("RGBA")
    inner = int(S * 0.90)
    ch = head.resize((inner, inner), Image.LANCZOS)
    off = (S - inner) // 2
    canvas.alpha_composite(ch, (off, off))

    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=255)
    canvas.putalpha(mask)

    edge = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle([ring_w // 2, ring_w // 2, S - 1 - ring_w // 2,
                                            S - 1 - ring_w // 2],
                                           radius=radius, outline=ring_color, width=ring_w)
    canvas.alpha_composite(edge)
    return canvas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    head = head_square()

    variants = {
        "头像-浅蓝气泡": make_circle(head, (226, 242, 255), (176, 208, 246),
                                (255, 255, 255, 235), glow=(255, 255, 255, 70)),
        "头像-深海夜航": make_circle(head, (43, 62, 118), (18, 26, 52),
                                (140, 200, 248, 235), glow=(80, 160, 240, 60)),
        "头像-奶油腮红": make_circle(head, (255, 246, 238), (250, 222, 214),
                                (255, 255, 255, 240), glow=(255, 220, 210, 80)),
        "头像-方形圆角": make_rounded(head, (246, 250, 254), (214, 232, 250),
                                 (255, 255, 255, 235)),
    }

    for name, im in variants.items():
        p = OUT / f"{name}.png"
        im.save(p)
        print(f"{name}: {p.stat().st_size/1024:.0f} KiB  {im.size}")

    # 预览拼板
    pad = 18
    tiles = list(variants.values())
    board = Image.new("RGB", (S * len(tiles) + pad * (len(tiles) + 1), S + pad * 2), (238, 241, 246))
    x = pad
    for im in tiles:
        board.paste(im, (x, pad), im)
        x += S + pad
    board.save(OUT / "头像-四版预览.png")
    print("预览:", OUT / "头像-四版预览.png")


if __name__ == "__main__":
    main()
