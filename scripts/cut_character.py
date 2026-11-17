"""从三视图立绘中抠出鲸鱼娘（透明底），产出全身 / 半身 / 头部三套素材。"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = r"C:\Users\10215\.dsh\profiles\desktop\node_modules\dsh-pet\assets\main-character.png"
OUT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin\work")

FRONT = (118, 148, 687, 908)  # 正视图包围盒


def remove_white_bg(im: Image.Image) -> Image.Image:
    """从四边泛洪填充去掉纯白背景，保留角色内部的白（围裙/蕾丝）。"""
    rgb = im.convert("RGB")
    w, h = rgb.size
    sentinel = (255, 0, 255)

    # 在若干边框点播种，覆盖背景可能被分割的情况
    seeds = []
    for x in range(0, w, max(1, w // 12)):
        seeds += [(x, 0), (x, h - 1)]
    for y in range(0, h, max(1, h // 12)):
        seeds += [(0, y), (w - 1, y)]

    for xy in seeds:
        r, g, b = rgb.getpixel(xy)
        if r > 236 and g > 236 and b > 236:
            ImageDraw.floodfill(rgb, xy, sentinel, thresh=36)

    arr = np.asarray(rgb).astype(np.int16)
    bg = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255)

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    alpha_im = Image.fromarray(alpha, "L")

    # 收缩 1px 去掉白色描边，再轻微羽化，保证边缘不脏
    alpha_im = alpha_im.filter(ImageFilter.MinFilter(3))
    alpha_im = alpha_im.filter(ImageFilter.GaussianBlur(0.6))

    out = im.convert("RGBA")
    out.putalpha(alpha_im)
    return out


def tight_bbox(im: Image.Image, pad: int = 2) -> Image.Image:
    """按 alpha 收紧裁切。"""
    a = np.asarray(im.getchannel("A"))
    ys, xs = np.where(a > 8)
    if len(xs) == 0:
        return im
    x0, x1 = max(0, xs.min() - pad), min(im.width, xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(im.height, ys.max() + pad + 1)
    return im.crop((x0, y0, x1, y1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SRC).convert("RGB")
    front = sheet.crop(FRONT)

    full = tight_bbox(remove_white_bg(front))
    full.save(OUT / "whale-full.png")
    print("full:", full.size)

    # 半身（头 + 上半身 + 围裙）
    w, h = front.size
    bust = tight_bbox(remove_white_bg(front.crop((0, 0, w, int(h * 0.68)))))
    bust.save(OUT / "whale-bust.png")
    print("bust:", bust.size)

    # 头部特写（含下巴）
    head = tight_bbox(remove_white_bg(front.crop((0, 0, w, int(h * 0.54)))))
    head.save(OUT / "whale-head.png")
    print("head:", head.size)

    # 状态栏用的方形头像：以头部为中心取 0.86 宽高比的竖幅
    hh = int(h * 0.54)
    face_w = int(hh * 0.86)
    cx = 290  # 正视图脸部中心（相对 FRONT 裁切）
    left = max(0, min(w - face_w, cx - face_w // 2))
    face = tight_bbox(remove_white_bg(front.crop((left, 0, left + face_w, hh))), pad=0)
    face.save(OUT / "whale-face.png")
    print("face:", face.size)

    # 拼一张白灰棋盘预览，便于肉眼确认抠图质量
    def checker(size, cell=16):
        bg = Image.new("RGB", size, (255, 255, 255))
        d = ImageDraw.Draw(bg)
        for yy in range(0, size[1], cell):
            for xx in range(0, size[0], cell):
                if (xx // cell + yy // cell) % 2:
                    d.rectangle([xx, yy, xx + cell - 1, yy + cell - 1], fill=(226, 226, 226))
        return bg

    canvas = checker((full.width + bust.width + head.width + 40, max(full.height, bust.height, head.height)))
    x = 0
    for piece in (full, bust, head):
        canvas.paste(piece, (x, 0), piece)
        x += piece.width + 20
    canvas.save(OUT / "cutout-preview.png")
    print("preview:", canvas.size)


if __name__ == "__main__":
    main()
