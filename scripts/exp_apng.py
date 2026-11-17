"""对照实验：同一批帧，全画布编码 vs 差分编码，比较体积。"""
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from apng_delta import read_back, save_delta_apng

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
SSF = ROOT / "out" / "鲸鱼娘-浪花泡沫.ssf"
TMP = ROOT / "work" / "_exp"
TMP.mkdir(exist_ok=True)


def load_bar_frames() -> tuple[list[Image.Image], list[int]]:
    with zipfile.ZipFile(SSF) as z:
        data = z.read("bar.png")
    im = Image.open(io.BytesIO(data))
    frames, durs = [], []
    for i in range(im.n_frames):
        im.seek(i)
        frames.append(im.convert("RGBA"))
        durs.append(im.info.get("duration", 150))
    return frames, durs


def main() -> None:
    frames, durs = load_bar_frames()
    print(f"源包状态栏：{len(frames)} 帧，全画布编码 {SSF.stat().st_size/1024:.0f} KiB（整个 ssf）")

    full_png = TMP / "full.png"
    frames[0].save(full_png, save_all=True, append_images=frames[1:],
                   duration=durs, loop=0, disposal=1, blend=0,
                   optimize=True, compress_level=9)
    full_kb = full_png.stat().st_size / 1024

    delta_png = TMP / "delta.png"
    st = save_delta_apng(frames, delta_png, durs)
    delta_kb = delta_png.stat().st_size / 1024

    print(f"  全画布编码: {full_kb:6.0f} KiB")
    print(f"  差分编码  : {delta_kb:6.0f} KiB    压缩比 {full_kb/delta_kb:.2f}x")
    print(f"  变化区域占全画布: {st['ratio']*100:.1f}%   最大矩形 {st['max_rect']:.0f} px")

    n, size, got = read_back(delta_png)
    print(f"  回读校验: {n} 帧, {size}, 时长合计 {sum(got)} ms")

    # 像素级等价校验：逐帧与源帧比对
    a = Image.open(full_png)
    b = Image.open(delta_png)
    bad = 0
    for i in range(min(a.n_frames, b.n_frames)):
        a.seek(i)
        b.seek(i)
        if a.convert("RGBA").tobytes() != b.convert("RGBA").tobytes():
            bad += 1
    print(f"  逐帧像素比对: {'完全一致' if bad == 0 else f'{bad} 帧不一致'}")


if __name__ == "__main__":
    main()
