"""对比「已发布版」与「重建版」的包内差异，定位 spec 重建漂移。"""
import configparser
import io
import zipfile
from pathlib import Path

A = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin-gh\skins\鲸鱼娘-浪花泡沫.ssf")
B = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin\out\鲸鱼娘-浪花泡沫.ssf")

za, zb = zipfile.ZipFile(A), zipfile.ZipFile(B)
na, nb = set(za.namelist()), set(zb.namelist())
print("仅在已发布版:", sorted(na - nb) or "（无）")
print("仅在重建版:", sorted(nb - na) or "（无）")

diff = [n for n in sorted(na & nb) if za.read(n) != zb.read(n)]
print("内容不同的条目:", diff)


def cfg(z):
    cp = configparser.ConfigParser(allow_no_value=True, strict=False)
    cp.optionxform = str
    cp.read_string(z.read("skin.ini").decode("utf-16"))
    return cp


ca, cb = cfg(za), cfg(zb)
print("\n=== skin.ini 差异 ===")
for sec in ca.sections():
    if sec not in cb.sections():
        print(f"[{sec}] 缺失")
        continue
    for k, v in ca.items(sec):
        w = cb.get(sec, k, fallback="<缺>")
        if v != w:
            print(f"[{sec}] {k}: {v!r} -> {w!r}")
for sec in cb.sections():
    if sec not in ca.sections():
        print(f"[{sec}] 新增")
