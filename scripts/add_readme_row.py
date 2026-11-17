"""在同步仓 README 的「目录」表里追加一行（幂等）。"""
from pathlib import Path

README = Path(r"D:\project\mem_pool\blueyellow-sync\README.md")
ANCHOR = "reports/trans-mooncake-vs-direct-2026-11-14/"
ROW = (
    "| [`packages/sogou-skin-whale-girl-4.0/`](packages/sogou-skin-whale-girl-4.0/README.md) "
    "| 搜狗输入法皮肤「鲸鱼娘」五套配色（羊皮卷 / 浪花泡沫 / 深海夜航 / 软萌奶油 / 浮游版）："
    "状态栏 APNG 三动作循环 + 四种输入模式，附逐文件 SHA-256 | 2026-11-16 |"
)

text = README.read_text(encoding="utf-8")

if "sogou-skin-whale-girl-4.0" in text:
    print("already listed, skip")
else:
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if ANCHOR in line:
            lines.insert(i + 1, ROW + "\n")
            break
    else:
        raise SystemExit("找不到目录表的锚点行")
    README.write_text("".join(lines), encoding="utf-8", newline="")
    print("row appended")
