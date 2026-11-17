"""手机皮肤键盘版式：1080x846，绝对定位排键（26 键 / 9 键）。

只做「完整预览图」，用于确认版式；正式投稿仍需分层 PSD + 按键切图。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import spec_v2 as S

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
OUT = ROOT / "out" / "mobile"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

W, H = 1080, 846
CAND_H, BAR_H = 96, 86
KB_TOP = CAND_H + BAR_H          # 182
PAD = 12                          # 键盘左右内边距
GAP = 12

T = S.THEMES[S.THEME]
C = T["colors"]


def hex_of(rgb):
    return "#%02x%02x%02x" % tuple(rgb)


def css() -> str:
    return f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;
  font-family:"Microsoft YaHei",sans-serif;-webkit-font-smoothing:antialiased}}
.stage{{position:relative;width:{W}px;height:{H}px;
  background:linear-gradient(180deg,{T['body_top']},{T['body_bot']})}}
.cand{{position:absolute;left:0;top:0;width:{W}px;height:{CAND_H}px;
  border-bottom:1px solid {T['border']};display:flex;align-items:center;
  gap:24px;padding:0 28px;font-size:30px}}
.cand .pyi{{color:{hex_of(C['pinyin_color'])};font-size:27px}}
.cand .on{{color:{hex_of(C['zhongwen_first_color'])};font-weight:700}}
.cand .c{{color:{hex_of(C['zhongwen_color'])}}}
.cand .num{{font-size:21px;opacity:.5;margin-right:3px}}
.toolbar{{position:absolute;left:0;top:{CAND_H}px;width:{W}px;height:{BAR_H}px;
  border-bottom:1px solid {T['border']};display:flex;align-items:center;
  justify-content:space-between;padding:0 24px}}
.logo{{width:58px;height:58px;border-radius:16px;border:1.6px solid {T['border']};
  display:flex;align-items:center;justify-content:center;font-weight:700;
  font-size:25px;color:{T['text_deep']};background:rgba(255,255,255,.55)}}
.tool{{width:54px;height:54px;border-radius:15px;border:1.6px solid {T['border']};
  display:flex;align-items:center;justify-content:center;font-size:23px;
  color:{T['text_deep']};background:rgba(255,255,255,.38)}}
.key{{position:absolute;border-radius:14px;display:flex;align-items:center;
  justify-content:center;font-size:36px;color:{T['text_deep']};
  border:1.6px solid rgba(0,0,0,.09);
  background:linear-gradient(180deg,rgba(255,255,255,.90),rgba(255,255,255,.52));
  box-shadow:0 3px 0 rgba(0,0,0,.06)}}
.key.fn{{font-size:23px;background:rgba(255,255,255,.34);color:{T['text_deep']}}}
.key.space{{font-size:24px}}
.sub{{position:absolute;right:8px;top:5px;font-size:16px;opacity:.5}}
.pop{{position:absolute;border-radius:18px;background:rgba(255,255,255,.97);
  border:1.8px solid {T['border']};box-shadow:0 8px 20px rgba(40,60,110,.20);
  display:flex;align-items:center;justify-content:center;font-size:44px;
  color:{T['text_deep']}}}
.poptip{{position:absolute;font-size:15px;color:{T['text_deep']};opacity:.55}}
"""


def key(x, y, w, h, label, cls="key", sub="") -> str:
    s = f"<span class='sub'>{sub}</span>" if sub else ""
    return (f"<div class='{cls}' style='left:{x:.1f}px;top:{y:.1f}px;"
            f"width:{w:.1f}px;height:{h:.1f}px'>{s}{label}</div>")


def cand_bar() -> str:
    return ("<div class='cand'>"
            "<span class='pyi'>ni hao</span>"
            "<span class='on'><span class='num'>1</span>你好</span>"
            "<span class='c'><span class='num'>2</span>拟合</span>"
            "<span class='c'><span class='num'>3</span>尼好</span>"
            "<span class='c'><span class='num'>4</span>你</span>"
            "</div>")


def toolbar() -> str:
    rest = "".join(f"<div class='tool'>{i}</div>" for i in ["☺", "◐", "⌨", "⚙"])
    return f"<div class='toolbar'><div class='logo'>S</div><div style='display:flex;gap:20px'>{rest}</div></div>"


def layout_26() -> str:
    usable = W - PAD * 2
    kw = (usable - GAP * 9) / 10            # 10 列基准
    row_h = 132.0
    y0 = KB_TOP + 14
    out = []

    # 第 1 行 10 键
    for i, ch in enumerate("qwertyuiop"):
        x = PAD + i * (kw + GAP)
        out.append(key(x, y0, kw, row_h, ch, sub=ch.upper()))

    # 第 2 行 9 键，居中
    y1 = y0 + row_h + GAP
    off = (kw + GAP) / 2
    for i, ch in enumerate("asdfghjkl"):
        out.append(key(PAD + off + i * (kw + GAP), y1, kw, row_h, ch, sub=ch.upper()))

    # 第 3 行：z..m + 退格（退格 1.5 宽）
    y2 = y1 + row_h + GAP
    bw = kw * 1.5 + GAP * 0.5
    start = PAD + off
    for i, ch in enumerate("zxcvbnm"):
        out.append(key(start + i * (kw + GAP), y2, kw, row_h, ch, sub=ch.upper()))
    out.append(key(start + 7 * (kw + GAP), y2, bw, row_h, "⌫", cls="key fn"))

    # 第 4 行：?123 / 中英 / ， / 空格 / 。 / 回车
    y3 = y2 + row_h + GAP
    h3 = H - y3 - 12
    w_fn, w_comma, w_space, w_enter = 118, kw, 300, 118
    total = w_fn * 2 + w_comma + w_space + w_comma + w_enter + GAP * 5
    x = (W - total) / 2
    out.append(key(x, y3, w_fn, h3, "?123", cls="key fn"))
    x += w_fn + GAP
    out.append(key(x, y3, w_fn, h3, "中/英", cls="key fn"))
    x += w_fn + GAP
    out.append(key(x, y3, w_comma, h3, "，", cls="key fn"))
    x += w_comma + GAP
    out.append(key(x, y3, w_space, h3, "空格", cls="key fn"))
    x += w_space + GAP
    out.append(key(x, y3, w_comma, h3, "。", cls="key fn"))
    x += w_comma + GAP
    out.append(key(x, y3, w_enter, h3, "↵", cls="key fn"))

    # 点击弹泡示例（规范要求有这个要素）
    out.append(f"<div class='pop' style='left:{PAD + 3 * (kw + GAP) - 6:.0f}px;"
               f"top:{y0 - 62:.0f}px;width:{kw + 24:.0f}px;height:66px'>t</div>")
    out.append(f"<div class='poptip' style='left:{PAD + 3 * (kw + GAP):.0f}px;"
               f"top:{y0 - 82:.0f}px'>点击弹泡</div>")
    return "".join(out)


def layout_9() -> str:
    """标准 T9：3 列 x 4 行，末行 中/英 · 0 · 退格。"""
    cols, rows = 3, 4
    left, right = PAD + 6, W - PAD - 6
    gw = right - left
    kw = (gw - GAP * (cols - 1)) / cols
    y0 = KB_TOP + 16
    kh = (H - y0 - 14 - GAP * (rows - 1)) / rows
    labels = [("1", ".,"), ("2", "abc"), ("3", "def"),
              ("4", "ghi"), ("5", "jkl"), ("6", "mno"),
              ("7", "pqrs"), ("8", "tuv"), ("9", "wxyz"),
              ("中/英", ""), ("0", "␣"), ("⌫", "")]
    out = []
    for i, (main, sub) in enumerate(labels):
        r, c = divmod(i, cols)
        x = left + c * (kw + GAP)
        y = y0 + r * (kh + GAP)
        cls = "key" if main.isdigit() else "key fn"
        out.append(key(x, y, kw, kh, main, cls=cls, sub=sub))

    # 点击弹泡示例
    out.append(f"<div class='pop' style='left:{left + (kw + GAP):.0f}px;"
               f"top:{y0 - 66:.0f}px;width:{kw + 20:.0f}px;height:70px'>5</div>")
    out.append(f"<div class='poptip' style='left:{left + (kw + GAP):.0f}px;"
               f"top:{y0 - 86:.0f}px'>点击弹泡</div>")
    return "".join(out)


def build(variant: str) -> Path:
    body = cand_bar() + toolbar() + (layout_26() if variant == "26键" else layout_9())
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{css()}</style>"
            f"</head><body><div class='stage'>{body}</div></body></html>")
    OUT.mkdir(parents=True, exist_ok=True)
    hp = OUT / f"_mock_{variant}.html"
    hp.write_text(html, encoding="utf-8")
    png = OUT / f"手机皮肤-{S.THEME_LABEL}-{variant}.png"
    if png.exists():
        png.unlink()
    args = [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", f"--window-size={W},{H}",
            f"--screenshot={png}", hp.as_uri()]
    for _ in range(3):
        subprocess.run(args, capture_output=True, timeout=180)
        if png.exists() and png.stat().st_size > 1000:
            break
    return png


def main() -> None:
    for v in ("26键", "9键"):
        p = build(v)
        print(f"{v}: {p.name}  {p.stat().st_size/1024:.0f} KiB")


if __name__ == "__main__":
    main()
