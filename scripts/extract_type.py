"""从「写代码」webm 抽打字帧，走与吃白饭相同的抠像 + 配准流程。"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from extract_eat import ANCHOR, CHAR_H, base_anchor, bbox, key_black

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
FRAMES = ROOT / "work" / "type" / "frames"
OUT = ROOT / "work" / "type"

# 连续 6 帧（源 12fps，每 2 帧≈167ms）→ 自然的打字节奏
PICKS = [44, 46, 48, 50, 52, 54]
NEUTRAL = 1


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("type_*.png"):
        p.unlink()

    neutral = key_black(Image.open(FRAMES / f"f_{NEUTRAL:03d}.png"))
    nx0, ny0, nx1, ny1 = bbox(neutral)
    _, nby = base_anchor(neutral)
    k = CHAR_H / (ny1 - ny0)
    print(f"打字中立帧包围盒 {nx1-nx0}x{ny1-ny0}, 缩放 k={k:.4f}")

    art = Image.open(ROOT / "work" / "whale-full.png").convert("RGBA")
    art_bx, _ = base_anchor(art)
    target_x = 182 + art_bx * (CHAR_H / art.height)

    keyed = [key_black(Image.open(FRAMES / f"f_{i:03d}.png")) for i in PICKS]

    boxes = [bbox(k2) for k2 in keyed] + [(nx0, ny0, nx1, ny1)]
    ux0 = min(b[0] for b in boxes) - 2
    uy0 = min(b[1] for b in boxes) - 2
    ux1 = max(b[2] for b in boxes) + 2
    uy1 = max(b[3] for b in boxes) + 2

    W = round((ux1 - ux0) * k)
    H = round((uy1 - uy0) * k)
    bx, _ = base_anchor(neutral)
    px = target_x - (bx - ux0) * k
    py = ANCHOR[1] - (nby - uy0) * k
    print(f"并集 {(ux1-ux0)}x{(uy1-uy0)} -> 缩放后 {W}x{H}, 放置点 ({px:.1f}, {py:.1f})")

    for idx, im in zip(PICKS, keyed):
        im.crop((ux0, uy0, ux1, uy1)).resize((W, H), Image.LANCZOS).save(
            OUT / f"type_{idx:03d}.png"
        )

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
