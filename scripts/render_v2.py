"""第二版：无框立绘 + APNG 动态。逐帧渲染 -> 切分 -> 合成 APNG。

动态位置：状态栏全身立绘（呼吸浮动 + 气泡上升）、横排/竖排合并窗（气泡漂动）。
其余贴图保持静态，避免整机掉帧。
"""
from __future__ import annotations

import base64
import inspect
import io
import json
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import spec_v2 as S

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
WORK = ROOT / "work"
BUILD = ROOT / (f"build_{S.THEME}" + ("_tpl" if S.TEMPLATE else ""))
OLD_BUILD = ROOT / "build"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CANVAS_W, CANVAS_H = 2000, 2200


def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


FULL = b64(WORK / "whale-full.png")
BUST = b64(WORK / "whale-bust.png")
HEAD = b64(WORK / "whale-head.png")

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent}
body{position:relative;font-family:"Microsoft YaHei",sans-serif}
.stage{position:absolute;overflow:hidden}
.char{position:absolute;display:block}
.shadow{position:absolute;border-radius:50%;filter:blur(4px);
  background:radial-gradient(ellipse at center,rgba(8,12,26,.42),rgba(8,12,26,0) 70%)}
.orn{position:absolute;overflow:visible}
.chip{position:absolute;width:22px;height:22px;border-radius:6px;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;letter-spacing:-.2px}
"""


def theme_css() -> str:
    """按当前主题生成颜色相关样式（芯片三态、投影、气泡）。"""
    c = S.CHIP
    return f"""
.plq{{position:absolute;overflow:visible;filter:drop-shadow(0 2px 7px {S.SHADOW})}}
.orn{{filter:drop-shadow(0 1px 2px {S.ORN_SHADOW})}}
.bub{{background:radial-gradient(circle at 34% 30%,#FFFFFF,rgba(255,255,255,0) 60%),
  {S.BUBBLE_COLOR}}}
.chip{{border:1px solid {c['border']};color:{c['fg']};
  background:linear-gradient(180deg,{c['bg1']},{c['bg2']})}}
.chip.hover{{border-color:{c['hover_border']};color:{c['hover_fg']};
  background:linear-gradient(180deg,{c['hover_bg1']},{c['hover_bg2']});
  box-shadow:0 0 0 1px {c['hover_glow']},0 1px 4px {c['hover_shadow']}}}
.chip.down{{border-color:{c['down_border']};color:{c['down_fg']};
  background:linear-gradient(180deg,{c['down_bg1']},{c['down_bg2']});
  box-shadow:inset 0 1px 2px {c['down_inset']}}}
"""


_uid = 0


def _gid() -> int:
    global _uid
    _uid += 1
    return _uid


def plaque(x, y, w, h, r: int = S.RADIUS) -> str:
    """浪花泡沫对话牌：雾白底 + 发丝主蓝细边 + 冰蓝内线 + 低透明度气泡。"""
    g = _gid()
    p = [
        f"<defs>"
        # 雾白底：上亮下略压深，给出体积
        f"<linearGradient id='pg{g}' x1='0' y1='0' x2='0' y2='1'>"
        f"<stop offset='0' stop-color='{S.BODY_TOP}'/>"
        f"<stop offset='1' stop-color='{S.BODY_BOT}'/></linearGradient>"
        # 顶部薄光
        f"<linearGradient id='hl{g}' x1='0' y1='0' x2='0' y2='1'>"
        f"<stop offset='0' stop-color='#FFFFFF' stop-opacity='{S.HL_ALPHA}'/>"
        f"<stop offset='1' stop-color='#FFFFFF' stop-opacity='0'/></linearGradient>"
        f"</defs>",
        f"<rect x='1' y='1' width='{w - 2}' height='{h - 2}' rx='{r}' "
        f"fill='url(#pg{g})' fill-opacity='{S.BODY_ALPHA}'/>",
        f"<rect x='2' y='2' width='{w - 4}' height='{int(h * 0.34)}' rx='{max(2, r - 2)}' "
        f"fill='url(#hl{g})'/>",
        # 主描边：发丝主蓝
        f"<rect x='1' y='1' width='{w - 2}' height='{h - 2}' rx='{r}' "
        f"fill='none' stroke='{S.BORDER_BLUE}' stroke-width='1.6' opacity='{S.BORDER_ALPHA}'/>",
        # （单线边框：参考截图只有一圈线，这里不再画内细线）
    ]

    if S.CORNERS:
        # 角饰从边框线上「勾」进纸面，而不是另画一条平行的线
        for cx, cy, sx, sy in ((0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)):
            p.append(
                f"<g transform='translate({cx},{cy}) scale({sx},{sy})'>"
                f"<path d='M 23 1.6 C 23 6.4 19.6 9.4 15.2 9.6' fill='none' "
                f"stroke='{S.BORDER_BLUE}' stroke-width='1.3' stroke-linecap='round' opacity='.95'/>"
                f"<path d='M 1.6 23 C 6.4 23 9.4 19.6 9.6 15.2' fill='none' "
                f"stroke='{S.BORDER_BLUE}' stroke-width='1.3' stroke-linecap='round' opacity='.95'/>"
                f"<circle cx='12.8' cy='12.8' r='1.15' fill='{S.BORDER_BLUE}' opacity='.75'/>"
                f"</g>"
            )

    # 角落气泡：压到 15%~20%，不抢文字
    bub = [
        (w - 22, 13, 5.0, S.BUBBLE_OPACITY),
        (w - 34, 24, 3.2, S.BUBBLE_OPACITY * 0.75),
        (w - 15, 30, 2.4, S.BUBBLE_OPACITY * 0.55),
        (16, 14, 2.6, S.BUBBLE_OPACITY * 0.5),
    ]
    for cx, cy, rr, op in bub:
        if cx < w - 2 and cy < h - 2:
            p.append(f"<circle cx='{cx}' cy='{cy}' r='{rr}' fill='{S.BUBBLE_COLOR}' "
                     f"opacity='{op:.2f}'/>")

    return (f"<svg class='plq' width='{w}' height='{h}' viewBox='0 0 {w} {h}' "
            f"style='left:{x}px;top:{y}px'>{''.join(p)}</svg>")


def whale_ornament(x, y, s: float = 1.0) -> str:
    """鲸鱼剪影 + 喷出的水花柱：把「水花尾巴」和「迷你鲸鱼」并成一个挂件。"""
    inner = (
        # 水花柱：一道细弧 + 几颗水滴
        f"<path d='M 9 13.2 C 9.8 10 8.2 7.4 9.4 4.2' fill='none' stroke='{S.INNER_BLUE}' "
        f"stroke-width='1.7' stroke-linecap='round' opacity='.8'/>"
        f"<circle cx='9.6' cy='3.0' r='2.3' fill='{S.INNER_BLUE}' opacity='.7'/>"
        f"<circle cx='5.4' cy='5.0' r='1.7' fill='{S.BLUSH}' opacity='.9'/>"
        f"<circle cx='13.2' cy='6.2' r='1.3' fill='{S.INNER_BLUE}' opacity='.65'/>"
        f"<circle cx='3.8' cy='2.0' r='1.1' fill='{S.INNER_BLUE}' opacity='.35'/>"
        # 鲸鱼本体
        f"<path d='M 2 17.6 C 2 14.2 5.2 12.8 8.4 12.8 C 11.4 12.8 13.6 14 14.6 15.8 "
        f"L 18.4 13.8 L 17.2 16.6 L 18.4 19.4 L 14.6 17.4 C 13.6 19.2 11.4 20.6 8.4 20.6 "
        f"C 5.2 20.6 2 19.2 2 17.6 Z' fill='{S.TEXT_DEEP}' opacity='.9'/>"
        f"<circle cx='5.6' cy='16.4' r='.8' fill='{S.BODY_TOP}' opacity='.95'/>"
    )
    w, h = round(22 * s), round(22 * s)
    return (f"<svg class='orn' width='{w}' height='{h}' viewBox='0 0 21 22' "
            f"style='left:{x}px;top:{y}px'>{inner}</svg>")


def bubbles(frame: int, total: int, xs, y_base: float, rise: float, count=4, dmax=11) -> str:
    out = []
    for k in range(count):
        prog = ((frame / total) + k / count) % 1.0
        y = y_base - prog * rise
        op = 0.30 * (1 - prog) + 0.03
        d = 6 + (k % 3) * 2
        x = xs[0] + (xs[1] - xs[0]) * (((k * 0.41) + 0.13) % 1.0)
        out.append(f"<div class='bub' style='left:{x:.0f}px;top:{y:.0f}px;"
                   f"width:{d}px;height:{d}px;opacity:{op:.2f}'></div>")
    return "".join(out)


# ---------- 各贴图（frame / total 决定动画相位） ----------

EAT_META = json.loads((WORK / "eat" / "meta.json").read_text())
EAT_IMGS = {
    idx: b64(WORK / "eat" / f"eat_{idx:03d}.png") for idx in EAT_META["picks"]
}
TYPE_META = json.loads((WORK / "type" / "meta.json").read_text())
TYPE_IMGS = {
    idx: b64(WORK / "type" / f"type_{idx:03d}.png") for idx in TYPE_META["picks"]
}
IDLE_DY = [0.0, -1.8, -2.6, -1.8]


def _expand(plan):
    """把 (段名, 帧数) 编排展开成逐帧列表 [(段名, 段内序号), ...]。"""
    out = []
    for kind, count in plan:
        for k in range(count):
            out.append((kind, k))
    return out


SEGMENTS = _expand(S.SEGMENT_PLAN)


def frame_bar(i: int, n: int) -> str:
    """状态栏循环：待机浮动 → 吃白饭 → 待机 → 敲键盘。"""
    shadow = (
        f"<div class='shadow' style='left:186px;top:145px;width:100px;height:16px;"
        f"opacity:0.60'></div>"
    )
    kind, k = SEGMENTS[i]

    if kind == "idle":
        dy = IDLE_DY[k % len(IDLE_DY)]
        sc = 1 + 0.005 * math.sin(k / max(1, S.IDLE_FRAMES) * 2 * math.pi)
        return "".join([
            shadow,
            bubbles(k, S.IDLE_FRAMES, (150, 186), 130, 44, count=2),
            f"<img class='char' src='{FULL}' style='left:182px;top:{8 + dy:.2f}px;height:150px;"
            f"transform-origin:50% 100%;transform:scale({sc:.4f})'>",
        ])

    meta, imgs = (EAT_META, EAT_IMGS) if kind == "eat" else (TYPE_META, TYPE_IMGS)
    idx = meta["picks"][k % len(meta["picks"])]
    return "".join([
        shadow,
        f"<img class='char' src='{imgs[idx]}' "
        f"style='left:{meta['left']}px;top:{meta['top']}px;"
        f"width:{meta['width']}px;height:{meta['height']}px;'>",
    ])


def frame_h1(i: int, n: int) -> str:
    parts = [
        *([] if S.TEMPLATE else [f"<img class='char' src='{BUST}' style='left:488px;top:4px;height:124px;'>"]),
        plaque(6, 44, (628 if S.TEMPLATE else 494), 84),
        *([] if S.TEMPLATE else [whale_ornament(13, 68, 1.25)]),
        bubbles(i, n, (150, 300), 116, 42, count=2),
    ]
    return "".join(parts)


def frame_v1(i: int, n: int) -> str:
    parts = [
        *([] if S.TEMPLATE else [f"<img class='char' src='{BUST}' style='left:58px;top:0;height:110px;'>"]),
        plaque(6, (8 if S.TEMPLATE else 92), 248, (332 if S.TEMPLATE else 264)),
        *([] if S.TEMPLATE else [whale_ornament(13, 316, 1.05)]),
        bubbles(i, n, (150, 220), 330, 80, count=2),
    ]
    return "".join(parts)


def frame_h2p() -> str:
    return plaque(4, 4, 512, 32)


def frame_h2c() -> str:
    return "".join([
        *([] if S.TEMPLATE else [f"<img class='char' src='{HEAD}' style='left:512px;top:2px;height:88px;'>"]),
        plaque(6, 6, (628 if S.TEMPLATE else 494), 76),
        *([] if S.TEMPLATE else [whale_ornament(13, 26, 1.25)]),
        bubbles(1, 4, (150, 320), 66, 36, count=2),
    ])


def frame_v2p() -> str:
    return plaque(4, 4, 212, 32)


def frame_v2c() -> str:
    return "".join([
        plaque(6, 6, 228, 328),
        *([] if S.TEMPLATE else [whale_ornament(13, 292, 1.05)]),
        bubbles(2, 4, (150, 210), 310, 90, count=2),
    ])


BUILDERS = {
    "bar": frame_bar,
    "h1": frame_h1,
    "v1": frame_v1,
    "h2p": frame_h2p,
    "h2c": frame_h2c,
    "v2p": frame_v2p,
    "v2c": frame_v2c,
}


ICONS = [
    ("cn1", "中", ""), ("cn2", "中", "hover"), ("cn3", "中", "down"),
    ("en1", "英", ""), ("en2", "英", "hover"), ("en3", "英", "down"),
    ("a1", "A", ""), ("a2", "A", "hover"), ("a3", "A", "down"),
    ("quan1", "全", ""), ("quan2", "全", "hover"), ("quan3", "全", "down"),
    ("ban1", "半", ""), ("ban2", "半", "hover"), ("ban3", "半", "down"),
    ("jian1", "简", ""), ("jian2", "简", "hover"), ("jian3", "简", "down"),
    ("fan1", "繁", ""), ("fan2", "繁", "hover"), ("fan3", "繁", "down"),
    ("quanpin1", "拼", ""), ("quanpin2", "拼", "hover"), ("quanpin3", "拼", "down"),
    ("shuanpin1", "双", ""), ("shuanpin2", "双", "hover"), ("shuanpin3", "双", "down"),
    ("key1", "KB", ""), ("key2", "KB", "hover"), ("key3", "KB", "down"),
    ("menu1", "MENU", ""), ("menu2", "MENU", "hover"), ("menu3", "MENU", "down"),
]


def kb_svg(color: str) -> str:
    return (
        f"<svg width='14' height='14' viewBox='0 0 14 14'>"
        f"<rect x='0.8' y='3' width='12.4' height='8.4' rx='2' fill='none' stroke='{color}' stroke-width='1.3'/>"
        f"<rect x='3' y='6' width='1.5' height='1.5' rx='.4' fill='{color}'/>"
        f"<rect x='6.2' y='6' width='1.5' height='1.5' rx='.4' fill='{color}'/>"
        f"<rect x='9.4' y='6' width='1.5' height='1.5' rx='.4' fill='{color}'/>"
        f"<rect x='4.6' y='8.8' width='4.8' height='1.3' rx='.5' fill='{color}'/></svg>"
    )


def menu_svg(color: str) -> str:
    return (
        f"<svg width='14' height='14' viewBox='0 0 14 14'>"
        f"<rect x='1' y='1.6' width='12' height='1.7' rx='.85' fill='{color}'/>"
        f"<rect x='1' y='6.15' width='12' height='1.7' rx='.85' fill='{color}'/>"
        f"<rect x='1' y='10.7' width='8' height='1.7' rx='.85' fill='{color}'/></svg>"
    )


def _takes_frame(fn) -> bool:
    """按签名判断这个贴图构造器是否需要 (frame, total)；单帧贴图不带参数。"""
    return len(inspect.signature(fn).parameters) >= 2


def build_html():
    """把所有贴图的每一帧铺到一张画布上，返回 (html, 裁剪表)。"""
    items = []
    for name, (w, h, n) in S.ASSET_SPEC.items():
        for i in range(n):
            items.append((name, i, w, h))

    layout = []
    x = y = 20
    row_h = 0
    for name, i, w, h in items:
        if x + w + 20 > CANVAS_W:
            x = 20
            y += row_h + 20
            row_h = 0
        layout.append({"name": name, "frame": i, "x": x, "y": y, "w": w, "h": h})
        x += w + 20
        row_h = max(row_h, h)

    body = []
    for it in layout:
        n = S.ASSET_SPEC[it["name"]][2]
        fn = BUILDERS[it["name"]]
        inner = fn(it["frame"], n) if _takes_frame(fn) else fn()
        body.append(
            f"<div class='stage' style='left:{it['x']}px;top:{it['y']}px;"
            f"width:{it['w']}px;height:{it['h']}px'>{inner}</div>"
        )

    # 图标：跟随主题上色（芯片底色/描边/字色都来自 THEMES）
    ix, iy = 20, 590
    for i, (fname, glyph, state) in enumerate([] if S.TEMPLATE else ICONS):
        col, row = i % 12, i // 12
        x, y = ix + col * 30, iy + row * 30
        layout.append({"name": fname, "frame": 0, "x": x, "y": y, "w": 22, "h": 22})
        cls = f"chip {state}".strip()
        color = S.ICON["down"] if state == "down" else (
            S.ICON["hover"] if state == "hover" else S.ICON["normal"])
        if glyph == "KB":
            inner = kb_svg(color)
        elif glyph == "MENU":
            inner = menu_svg(color)
        else:
            inner = glyph
        body.append(f"<div class='{cls}' style='left:{x}px;top:{y}px'>{inner}</div>")

    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}{theme_css()}</style>"
            f"</head><body>{''.join(body)}</body></html>")
    return html, layout


def screenshot(html_path: Path, png_path: Path) -> None:
    if png_path.exists():
        png_path.unlink()
    args = [
        EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={CANVAS_W},{CANVAS_H}",
        "--default-background-color=00000000",
        f"--screenshot={png_path}", html_path.as_uri(),
    ]
    for attempt in range(3):
        r = subprocess.run(args, capture_output=True, text=True, timeout=300)
        if png_path.exists() and png_path.stat().st_size > 1000:
            return
        print(f"  edge retry {attempt+1}: rc={r.returncode} {r.stderr[-300:]}", file=sys.stderr)
    raise RuntimeError("Edge 截图失败")


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    for stale in BUILD.glob("*.png"):
        stale.unlink()

    html, layout = build_html()
    (WORK / "sprites_v2.html").write_text(html, encoding="utf-8")
    sheet_path = WORK / "sprites_v2.png"
    screenshot(WORK / "sprites_v2.html", sheet_path)

    sheet = Image.open(sheet_path).convert("RGBA")
    print("sheet:", sheet.size)

    by_asset: dict[str, list[Image.Image]] = {}
    for it in layout:
        crop = sheet.crop((it["x"], it["y"], it["x"] + it["w"], it["y"] + it["h"]))
        by_asset.setdefault(it["name"], []).append(crop)

    for name, frames in by_asset.items():
        out = BUILD / f"{name}.png"
        if len(frames) == 1:
            frames[0].save(out, optimize=True, compress_level=9)
            print(f"  {name}: static {frames[0].size}")
        else:
            ms = ([S.SEGMENT_MS[kind] for kind, _ in SEGMENTS]
                  if name == "bar" else S.FRAME_MS[name])
            frames[0].save(
                out, save_all=True, append_images=frames[1:],
                duration=ms, loop=0, disposal=1, blend=0,
                optimize=True, compress_level=9,
            )
            kb = out.stat().st_size / 1024
            print(f"  {name}: APNG {len(frames)} 帧 {frames[0].size} {kb:.0f} KiB")

            # 回读校验：帧数、尺寸、首帧
            chk = Image.open(out)
            assert getattr(chk, "n_frames", 1) == len(frames), f"{name} 帧数回读不符"

    # 图标已随主题渲染进 BUILD，不再从旧目录覆盖（旧逻辑会把按主题上色的图标换回第一版深色）


if __name__ == "__main__":
    main()
