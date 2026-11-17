"""从 pet 的「吃白饭」webm 里抽关键帧，去黑底，并按状态栏立绘做尺寸/位置配准。

webm 是 640x360、24fps、10s、纯黑背景（无 alpha 通道）。
配准口径：以中立帧的包围盒高度映射到状态栏立绘高度 150，脚底中心对齐 (238, 158)。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
FRAMES = ROOT / "work" / "ffmpeg" / "frames"
OUT = ROOT / "work" / "eat"

# 关键姿势：立 → 碗到胯边 → 上举 → 咬(鼓腮) → 咀嚼×3 → 碗放低（首尾都接近中立，减少循环跳变）
PICKS = [24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54]
NEUTRAL = 20          # 用于配准的中立帧
CHAR_H = 150          # 状态栏立绘高度（与 whale-full.png 一致）
ANCHOR = (238, 158)   # 脚底中心在 300x160 状态栏里的坐标


def key_black(im: Image.Image) -> Image.Image:
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    mx = a.max(axis=2)
    alpha = np.clip((mx - 2.0) / 6.0, 0.0, 1.0)   # 背景恒为 0，2..8 之间做抗锯齿过渡
    out = np.dstack([a, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def bbox(im: Image.Image, thr: int = 8):
    a = np.asarray(im.getchannel("A"))
    ys, xs = np.where(a > thr)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def base_anchor(im: Image.Image, thr: int = 8, band: float = 0.14):
    """以底部 band 区域（脚+裙摆）的中心作为水平锚点：举碗、抬手都不影响它。"""
    a = np.asarray(im.getchannel("A"))
    ys, xs = np.where(a > thr)
    y0, y1 = ys.min(), ys.max()
    cut = y1 - (y1 - y0) * band
    bx = xs[ys >= cut]
    return (bx.min() + bx.max()) / 2.0, float(y1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*.png"):
        p.unlink()

    neutral = key_black(Image.open(FRAMES / f"f_{NEUTRAL:03d}.png"))
    nx0, ny0, nx1, ny1 = bbox(neutral)
    _, nby = base_anchor(neutral)
    k = CHAR_H / (ny1 - ny0)
    print(f"中立帧包围盒 {nx1-nx0}x{ny1-ny0}, 缩放 k={k:.4f}")

    # 立绘的底部锚点 -> 状态栏画布坐标，作为对齐目标
    art = Image.open(ROOT / "work" / "whale-full.png").convert("RGBA")
    art_bx, _ = base_anchor(art)
    k_art = CHAR_H / art.height
    target_x = 182 + art_bx * k_art
    print(f"立绘底部锚点 {art_bx:.1f} -> 画布 x={target_x:.1f}")

    keyed = []
    for i in PICKS:
        keyed.append(key_black(Image.open(FRAMES / f"f_{i:03d}.png")))

    # 所有帧并集包围盒（保证碗举起时不被裁）
    boxes = [bbox(k2) for k2 in keyed] + [(nx0, ny0, nx1, ny1)]
    ux0 = min(b[0] for b in boxes) - 2
    uy0 = min(b[1] for b in boxes) - 2
    ux1 = max(b[2] for b in boxes) + 2
    uy1 = max(b[3] for b in boxes) + 2

    W = round((ux1 - ux0) * k)
    H = round((uy1 - uy0) * k)

    eat_bx, _ = base_anchor(neutral)
    px = target_x - (eat_bx - ux0) * k
    py = ANCHOR[1] - (nby - uy0) * k

    print(f"并集 {(ux1-ux0)}x{(uy1-uy0)} -> 缩放后 {W}x{H}, 放置点 ({px:.1f}, {py:.1f})")

    for idx, im in zip(PICKS, keyed):
        crop = im.crop((ux0, uy0, ux1, uy1)).resize((W, H), Image.LANCZOS)
        crop.save(OUT / f"eat_{idx:03d}.png")

    meta = {
        "picks": PICKS,
        "width": W,
        "height": H,
        "left": round(px, 2),
        "top": round(py, 2),
        "scale": round(k, 5),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("wrote", len(PICKS), "frames ->", OUT)


if __name__ == "__main__":
    main()
