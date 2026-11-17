"""在搜狗安装目录里搜 UTF-16 中文串，确认状态栏相关菜单项的准确措辞。"""
from pathlib import Path

ROOT = Path(r"D:\codetools\SogouInput\16.6.0.4780")
NEEDLES = ["状态栏", "隐藏状态栏", "显示状态栏", "悬浮栏", "皮肤"]

def u16(s: str) -> bytes:
    return s.encode("utf-16-le")

targets = []
for p in ROOT.rglob("*"):
    if p.suffix.lower() not in (".exe", ".dll", ".dat", ".ini", ".xml", ".json"):
        continue
    try:
        if p.stat().st_size > 40 * 1024 * 1024:
            continue
    except OSError:
        continue
    targets.append(p)

print(f"扫描 {len(targets)} 个文件 ...")
found: dict[str, list[str]] = {}
for p in targets:
    try:
        data = p.read_bytes()
    except OSError:
        continue
    for n in NEEDLES:
        if u16(n) in data:
            found.setdefault(n, []).append(p.name)

for n in NEEDLES:
    hits = found.get(n)
    print(f"  {n:8s} -> {', '.join(sorted(set(hits))[:6]) if hits else '（未命中）'}")
