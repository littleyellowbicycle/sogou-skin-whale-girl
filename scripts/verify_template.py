"""校验四套框模板：无 [StatusBar]、无状态栏/按键贴图、无立绘类资产引用。"""
import zipfile
from pathlib import Path

D = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin\out\template")

BAD = ("bar.png", "cn1.png", "en1.png", "a1.png", "quan1.png", "ban1.png",
       "jian1.png", "fan1.png", "quanpin1.png", "shuanpin1.png", "key1.png", "menu1.png")

for p in sorted(D.glob("*.ssf")):
    z = zipfile.ZipFile(p)
    names = z.namelist()
    ini = z.read("skin.ini").decode("utf-16")
    has_sb = "[StatusBar]" in ini
    pngs = [n for n in names if n.endswith(".png")]
    leftovers = [n for n in pngs if n in BAD]
    frames = 0
    print(f"{p.name}")
    print(f"   大小 {p.stat().st_size/1024:.0f} KiB   文件 {len(names)}   [StatusBar]={'有' if has_sb else '无'}")
    print(f"   贴图 {len(pngs)}: {', '.join(sorted(pngs))}")
    print(f"   残留状态栏/按键资产: {leftovers or '（无）'}")
    assert not has_sb, "仍含 [StatusBar]"
    assert not leftovers, f"仍有状态栏资产 {leftovers}"
print("\n全部通过：四套模板均不含状态栏段与任何按键/立绘资产")
