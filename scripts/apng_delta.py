"""APNG 差分编码器：每帧只编码与上一帧不同的矩形区域。

APNG 的 fcTL 块支持 x_offset/y_offset/width/height，
配合 blend_op = SOURCE(0) + dispose_op = NONE(0)，
把「变化矩形」原样覆盖到画布上，解码结果与逐帧全画布完全等价。

压缩数据借用 Pillow：把裁剪后的帧存成 PNG，抽出其 IDAT 负载复用
（IDAT 是「滤波后扫描行」的 zlib 流，与 IHDR 尺寸无关，可直接嵌到 fcTL/fdAT 里）。
"""
from __future__ import annotations

import io
import struct
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def _idat_payload(im: Image.Image) -> bytes:
    """把单帧 RGBA 存成 PNG，取回其 IDAT 负载（已滤波 + 已压缩）。"""
    buf = io.BytesIO()
    im.save(buf, format="PNG", compress_level=9, optimize=True)
    data = buf.getvalue()
    out, i = b"", 8
    while i < len(data):
        (ln,) = struct.unpack(">I", data[i:i + 4])
        tag = data[i + 4:i + 8]
        if tag == b"IDAT":
            out += data[i + 8:i + 8 + ln]
        i += 12 + ln
    return out


def _bbox_diff(prev: np.ndarray, cur: np.ndarray) -> tuple[int, int, int, int] | None:
    d = np.any(prev != cur, axis=2)
    ys, xs = np.where(d)
    if len(xs) == 0:
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def save_delta_apng(frames: list[Image.Image], path: Path, durations: list[int],
                    full_compare: bool = False) -> dict:
    """写出差分 APNG；返回统计信息。"""
    assert frames, "没有帧"
    frames = [f.convert("RGBA") for f in frames]
    W, H = frames[0].size
    assert all(f.size == (W, H) for f in frames)
    assert len(durations) == len(frames)

    arrs = [np.asarray(f) for f in frames]

    out = bytearray(PNG_SIG)
    out += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
    out += _chunk(b"acTL", struct.pack(">II", len(frames), 0))  # loop=0 无限循环

    seq = 0
    total_px = 0
    full_px = 0
    rects = []

    for idx, (im, arr, dur) in enumerate(zip(frames, arrs, durations)):
        if idx == 0:
            box = (0, 0, W, H)
            region = im
        else:
            box = _bbox_diff(arrs[idx - 1], arr)
            if box is None:               # 与上一帧完全相同：用 1x1 占位帧
                box = (0, 0, 1, 1)
            region = im.crop(box)

        x0, y0, x1, y1 = box
        rw, rh = x1 - x0, y1 - y0
        total_px += rw * rh
        full_px += W * H
        rects.append((rw, rh))

        delay_cs = max(1, round(dur / 10))       # APNG 延迟单位是 1/100 秒
        fc = struct.pack(">IIIIIHHBB", seq, rw, rh, x0, y0, delay_cs, 1000, 0, 0)
        seq += 1
        payload = _idat_payload(region)

        if idx == 0:
            out += _chunk(b"fcTL", fc)
            out += _chunk(b"IDAT", payload)
        else:
            out += _chunk(b"fcTL", fc)
            out += _chunk(b"fdAT", struct.pack(">I", seq) + payload)
            seq += 1

    out += _chunk(b"IEND", b"")
    path.write_bytes(bytes(out))

    return {
        "frames": len(frames),
        "bytes": len(out),
        "rect_px": total_px,
        "full_px": full_px,
        "ratio": total_px / full_px if full_px else 1.0,
        "max_rect": max((w * h for w, h in rects), default=0),
    }


def read_back(path: Path) -> tuple[int, int, list[int]]:
    """用 Pillow 回读校验：帧数、尺寸、每帧时长。"""
    im = Image.open(path)
    durs = []
    for i in range(im.n_frames):
        im.seek(i)
        durs.append(im.info.get("duration", 0))
    return im.n_frames, im.size, durs
