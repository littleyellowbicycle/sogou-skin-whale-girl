"""给无法重建的旧包（浮游版）改动画时长：只换帧时长，像素不动。"""
import io
import zipfile
from pathlib import Path

from PIL import Image

import spec_v2 as S

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")

TARGETS = [
    ROOT / "out" / "鲸鱼娘-浮游版.ssf",
    ROOT / "out" / "upload" / "鲸鱼娘-浮游版.ssf",
]

DURS = [S.SEGMENT_MS[k] for k, _ in S.segments_expanded()] if hasattr(S, "segments_expanded") else None


def durations() -> list[int]:
    out = []
    for kind, count in S.SEGMENT_PLAN:
        out += [S.SEGMENT_MS[kind]] * count
    return out


def retime_bar(data: bytes, dur: list[int]) -> bytes:
    im = Image.open(io.BytesIO(data))
    n = getattr(im, "n_frames", 1)
    frames = []
    for i in range(n):
        im.seek(i)
        frames.append(im.convert("RGBA"))
    if n != len(dur):
        # 抽帧后的精简包：按总时长均分，保证一轮时长一致
        total = sum(dur)
        dur = [max(20, round(total / n))] * n
    buf = io.BytesIO()
    frames[0].save(buf, format="PNG", save_all=True, append_images=frames[1:],
                   duration=dur, loop=0, disposal=1, blend=0,
                   optimize=True, compress_level=9)
    return buf.getvalue()


def main() -> None:
    dur = durations()
    for p in TARGETS:
        if not p.is_file():
            print(f"跳过（不存在）: {p}")
            continue
        with zipfile.ZipFile(p) as z:
            entries = [(i.filename, z.read(i.filename)) for i in z.infolist()]

        out = []
        changed = False
        for name, data in entries:
            if name == "bar.png":
                new = retime_bar(data, dur)
                changed = new != data
                out.append((name, new))
            else:
                out.append((name, data))

        if not changed:
            print(f"无需改动: {p.name}")
            continue

        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, data in out:
                z.writestr(name, data)

        im = Image.open(io.BytesIO(next(d for n, d in out if n == "bar.png")))
        total = 0
        for i in range(im.n_frames):
            im.seek(i)
            total += im.info.get("duration", 0)
        print(f"{p.name}: 重打时长完成，一轮 {total/1000:.2f} 秒，{p.stat().st_size/1024:.0f} KiB")


if __name__ == "__main__":
    main()
