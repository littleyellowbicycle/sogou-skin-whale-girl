"""成品瘦身：对已打包的 .ssf 做「抽帧 + 重压」，不改 skin.ini、不改画面内容。

用于没有主题入口的旧版皮肤（如浮游版）：bar 18->9 帧、候选窗 4->1 帧，
按原总时长均分新的帧间隔，播放速度不变。
"""
from __future__ import annotations

import hashlib
import io
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")

# 目标帧数（按文件名主干匹配）
TARGETS = {
    "bar": 9,
    "h1": 1,
    "v1": 1,
}


def target_for(name: str) -> int | None:
    stem = Path(name).stem
    return TARGETS.get(stem)


def thin_apng(data: bytes, target: int) -> bytes:
    im = Image.open(io.BytesIO(data))
    n = getattr(im, "n_frames", 1)
    if n <= target:
        return data

    frames, durs = [], []
    for i in range(n):
        im.seek(i)
        durs.append(im.info.get("duration", 150))
        frames.append(im.convert("RGBA"))

    total = sum(durs)
    if target == 1:
        keep = [0]
    else:
        keep = [round(k * (n - 1) / (target - 1)) for k in range(target)]
        keep = sorted(set(keep))

    picked = [frames[i] for i in keep]
    per = max(20, round(total / len(picked)))

    buf = io.BytesIO()
    if len(picked) == 1:
        picked[0].save(buf, format="PNG", optimize=True, compress_level=9)
    else:
        picked[0].save(
            buf, format="PNG", save_all=True, append_images=picked[1:],
            duration=per, loop=0, disposal=1, blend=0,
            optimize=True, compress_level=9,
        )
    return buf.getvalue()


def main(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as z:
        entries = [(i, z.read(i.filename)) for i in z.infolist()]

    out_bytes = []
    saved = 0
    for info, data in entries:
        new = data
        tgt = target_for(Path(info.filename).name) if info.filename.endswith(".png") else None
        if tgt:
            before = len(data)
            new = thin_apng(data, tgt)
            saved += before - len(new)
        out_bytes.append((info.filename, new))

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in out_bytes:
            z.writestr(name, data)

    size = dst.stat().st_size
    lim = 600 * 1024
    print(f"{src.name} -> {dst.name}  {size/1024:.0f} KiB  "
          f"（省 {saved/1024:.0f} KiB，600KB 限制：{'OK' if size < lim else '超限'}）")
    assert size < lim, f"{dst.name} 仍超限：{size/1024:.0f} KiB"


if __name__ == "__main__":
    src = ROOT / "out" / "鲸鱼娘-浮游版.ssf"
    dst = ROOT / "out" / "upload" / "鲸鱼娘-浮游版.ssf"
    main(src, dst)
