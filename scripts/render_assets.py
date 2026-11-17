"""渲染搜狗皮肤全部贴图：一个 HTML 画布 -> Edge headless 截图 -> 按坐标切分。

设计基准（鲸鱼娘 · 深海信使）：
  面板 = 深海军蓝渐变 + 米白外描边 + 金色内发丝线 + 气泡点缀
  文字 = 冰蓝拼音 / 暖金首选 / 近白候选
"""
from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
WORK = ROOT / "work"
BUILD = ROOT / "build"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ---------- 素材 ----------

def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


HEAD = b64(WORK / "whale-head.png")
BUST = b64(WORK / "whale-bust.png")
FACE = b64(WORK / "whale-face.png")

# ---------- 样式 ----------

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent}
body{width:1000px;height:760px;position:relative;overflow:hidden;
     font-family:"Microsoft YaHei","微软雅黑",sans-serif;
     -webkit-font-smoothing:antialiased}
.stage{position:absolute;overflow:hidden}
.panel{position:absolute;border-radius:16px;
  background:linear-gradient(178deg,#31406F 0%,#26325B 38%,#1B2447 72%,#161D3B 100%);
  border:1px solid rgba(244,234,216,.78);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.26),
             inset 0 -1px 0 rgba(0,0,0,.50),
             inset 0 0 18px rgba(120,170,230,.10)}
.panel:after{content:"";position:absolute;left:3px;right:3px;top:3px;bottom:3px;
  border-radius:13px;border:1px solid rgba(201,164,76,.34);pointer-events:none}
.gloss{position:absolute;left:14px;right:14px;top:2px;height:38%;
  border-radius:14px 14px 40% 40%/14px 14px 14px 14px;
  background:linear-gradient(180deg,rgba(255,255,255,.13),rgba(255,255,255,0))}
.char{position:absolute;display:block}
.dot{position:absolute;border-radius:50%;
  background:radial-gradient(circle at 35% 32%,rgba(190,235,250,.95),rgba(127,211,232,.35) 62%,rgba(127,211,232,0) 72%)}
.chip{position:absolute;width:22px;height:22px;border-radius:6px;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;letter-spacing:-.2px;
  border:1px solid rgba(244,234,216,.50);color:#E7EDF8;
  background:linear-gradient(180deg,#2C3866,#1D2545)}
.chip.hover{border-color:rgba(255,233,190,.95);color:#FFF6E2;
  background:linear-gradient(180deg,#3D508C,#283560);
  box-shadow:0 0 0 1px rgba(201,164,76,.35),0 0 6px rgba(127,211,232,.35)}
.chip.down{border-color:rgba(201,164,76,.55);color:#F0D9A2;
  background:linear-gradient(180deg,#141A35,#0E1226);
  box-shadow:inset 0 1px 3px rgba(0,0,0,.65)}
"""


def panel(x, y, w, h, r=16, gloss=True) -> str:
    css = f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:{r}px;"
    inner = (f"<div class='gloss'></div>" if gloss else "")
    return f"<div class='panel' style='{css}'>{inner}</div>"


def dots(items) -> str:
    out = []
    for x, y, d, op in items:
        out.append(
            f"<div class='dot' style='left:{x}px;top:{y}px;width:{d}px;height:{d}px;opacity:{op}'></div>"
        )
    return "".join(out)


SPARK = """<svg width="{w}" height="{w}" viewBox="0 0 20 20" style="position:absolute;left:{x}px;top:{y}px;opacity:{o}">
<path d="M10 0 L12.4 7.6 L20 10 L12.4 12.4 L10 20 L7.6 12.4 L0 10 L7.6 7.6 Z"
 fill="url(#g{x})"/><defs><linearGradient id="g{x}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#FFF3D0"/><stop offset="1" stop-color="#C9A44C"/></linearGradient></defs></svg>"""


def wave(w, h, top, gid) -> str:
    """底部水波纹装饰，落在面板下缘的不拉伸格里。"""
    amp = 5
    mid = top + amp
    path = (
        f"M0,{mid} C{w*0.16},{top-amp} {w*0.32},{top+amp*2.4} {w*0.5},{mid} "
        f"C{w*0.68},{top-amp*0.6} {w*0.84},{top+amp*2} {w},{top+1} "
        f"L{w},{h} L0,{h} Z"
    )
    return (
        f"<svg width='{w}' height='{h}' style='position:absolute;left:0;top:0'>"
        f"<defs><linearGradient id='{gid}' x1='0' y1='0' x2='0' y2='1'>"
        f"<stop offset='0' stop-color='#7FD3E8' stop-opacity='.42'/>"
        f"<stop offset='1' stop-color='#7FD3E8' stop-opacity='.08'/></linearGradient></defs>"
        f"<path d='{path}' fill='url(#{gid})'/></svg>"
    )


# ---------- 各贴图 ----------

def html_bar() -> str:
    """状态栏 320x92：左侧 6 个按钮位，右侧整颗头像"""
    parts = [
        panel(0, 0, 320, 92, 18),
        f"<img class='char' src='{HEAD}' style='right:2px;top:2px;height:88px;'>",
        dots([(176, 12, 10, .55), (192, 66, 7, .35), (210, 34, 6, .28)]),
        SPARK.format(w=11, x=180, y=4, o=.75),
    ]
    return "".join(parts)


def html_h1() -> str:
    """横排合并窗 640x150：面板 y=76..150，头像从面板后探头"""
    parts = [
        # 先画头像，再画面板 → 下巴被面板压住，形成“从栏后探头”的效果
        f"<img class='char' src='{HEAD}' style='right:10px;top:2px;height:74px;'>",
        dots([(470, 40, 12, .6), (450, 14, 8, .45), (620, 22, 7, .4), (480, 58, 6, .35)]),
        SPARK.format(w=12, x=470, y=2, o=.8),
        SPARK.format(w=8, x=626, y=50, o=.45),
        panel(0, 76, 640, 74, 16),
    ]
    return "".join(parts)


def html_v1() -> str:
    """竖排合并窗 260x380：面板 y=110..380，半身像从面板后探出"""
    parts = [
        f"<img class='char' src='{BUST}' style='left:42px;top:0;height:150px;'>",
        dots([(18, 30, 11, .55), (8, 72, 7, .4), (234, 36, 9, .5), (224, 88, 6, .35)]),
        SPARK.format(w=11, x=10, y=10, o=.7),
        SPARK.format(w=9, x=238, y=62, o=.6),
        panel(0, 110, 260, 270, 16),
    ]
    return "".join(parts)


def html_h2p() -> str:
    """H2 拼音条 520x40"""
    parts = [
        panel(0, 0, 520, 40, 13, gloss=False),
        dots([(492, 12, 9, .5), (510, 6, 6, .35)]),
    ]
    return "".join(parts)


def html_h2c() -> str:
    """H2 候选条 640x92（纯面板 + 水波纹，避免与文字抢位）"""
    parts = [
        dots([(18, 12, 9, .45), (30, 30, 6, .3), (612, 16, 8, .4), (596, 34, 6, .3)]),
        SPARK.format(w=11, x=608, y=4, o=.6),
        SPARK.format(w=8, x=14, y=40, o=.45),
        panel(0, 0, 640, 92, 16),
        wave(640, 92, 78, "wh2"),
    ]
    return "".join(parts)


def html_v2p() -> str:
    parts = [
        panel(0, 0, 220, 40, 13, gloss=False),
        dots([(196, 10, 8, .45)]),
    ]
    return "".join(parts)


def html_v2c() -> str:
    """V2 候选窗 240x360（无立绘，纯面板 + 气泡 + 水波纹）"""
    parts = [
        dots([(206, 16, 10, .5), (192, 42, 6, .3), (28, 22, 7, .3)]),
        SPARK.format(w=9, x=204, y=6, o=.55),
        panel(0, 0, 240, 360, 16),
        wave(240, 360, 340, "wv2"),
    ]
    return "".join(parts)


ASSETS = {
    "bar": (320, 92, html_bar),
    "h1": (640, 150, html_h1),
    "v1": (260, 380, html_v1),
    "h2p": (520, 40, html_h2p),
    "h2c": (640, 92, html_h2c),
    "v2p": (220, 40, html_v2p),
    "v2c": (240, 360, html_v2c),
}

# 图标：id, 状态类, 内容类型
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


def build_html() -> tuple[str, dict]:
    """拼出整张画布，返回 (html, 坐标表)。"""
    layout = {}
    body = []

    # 主贴图
    pos = {
        "bar": (20, 20), "h1": (340, 20), "v1": (20, 180),
        "h2p": (300, 180), "h2c": (300, 236),
        "v2p": (300, 344), "v2c": (548, 344),
    }
    for name, (w, h, fn) in ASSETS.items():
        x, y = pos[name]
        layout[name] = {"x": x, "y": y, "w": w, "h": h}
        body.append(f"<div class='stage' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px'>{fn()}</div>")

    # 图标
    ix, iy = 20, 590
    for i, (fname, glyph, state) in enumerate(ICONS):
        col, row = i % 12, i // 12
        x, y = ix + col * 30, iy + row * 30
        layout[fname] = {"x": x, "y": y, "w": 22, "h": 22}
        cls = f"chip {state}".strip()
        if glyph == "KB":
            color = "#F0D9A2" if state == "down" else ("#FFF6E2" if state == "hover" else "#E7EDF8")
            inner = kb_svg(color)
        elif glyph == "MENU":
            color = "#F0D9A2" if state == "down" else ("#FFF6E2" if state == "hover" else "#E7EDF8")
            inner = menu_svg(color)
        else:
            inner = glyph
        body.append(f"<div class='{cls}' style='left:{x}px;top:{y}px'>{inner}</div>")

    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body>{''.join(body)}</body></html>"""
    return html, layout


def screenshot(html_path: Path, png_path: Path) -> None:
    if png_path.exists():
        png_path.unlink()
    args = [
        EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--window-size=1000,760",
        "--default-background-color=00000000",
        f"--screenshot={png_path}", html_path.as_uri(),
    ]
    # Edge 首次启动可能残留进程，重试几次
    for attempt in range(3):
        r = subprocess.run(args, capture_output=True, text=True, timeout=180)
        if png_path.exists() and png_path.stat().st_size > 1000:
            return
        print(f"  edge retry {attempt+1}: rc={r.returncode} {r.stderr[-300:]}", file=sys.stderr)
    raise RuntimeError("Edge 截图失败")


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    for stale in BUILD.glob("*.png"):
        stale.unlink()

    html, layout = build_html()
    html_path = WORK / "sprites.html"
    html_path.write_text(html, encoding="utf-8")
    sheet = WORK / "sprites.png"
    screenshot(html_path, sheet)

    im = Image.open(sheet).convert("RGBA")
    print("sheet:", im.size)

    for name, box in layout.items():
        crop = im.crop((box["x"], box["y"], box["x"] + box["w"], box["y"] + box["h"]))
        crop.save(BUILD / f"{name}.png")

    (WORK / "layout.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")
    print(f"wrote {len(layout)} assets -> {BUILD}")


if __name__ == "__main__":
    main()
