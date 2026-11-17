"""字段审计：我的 skin.ini 与两份已证实可用的参考皮肤逐键对照。"""
from __future__ import annotations

import configparser
import zipfile
from pathlib import Path

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
REF = ROOT / "ref"


def parse_text(text: str) -> dict[str, set[str]]:
    cp = configparser.ConfigParser(allow_no_value=True, strict=False)
    cp.optionxform = str
    cp.read_string(text)
    return {sec: {k.lower() for k, _ in cp.items(sec)} for sec in cp.sections()}


def load_file(path: Path) -> dict[str, set[str]]:
    raw = path.read_bytes()
    text = raw.decode("utf-16") if raw[:2] == b"\xff\xfe" else raw.decode("utf-8", "ignore")
    return parse_text(text)


def main() -> None:
    with zipfile.ZipFile(ROOT / "out" / "whale-girl-deep-sea.ssf") as z:
        mine = parse_text(z.read("skin.ini").decode("utf-16"))

    mall = load_file(REF / "mall-sample" / "skin.ini")     # 商城商业皮（字段最全）
    hand = load_file(REF / "real-sample" / "Skin.ini")     # 2026 手作皮（最小可用集）

    ref_keys = set()
    for src in (mall, hand):
        for ks in src.values():
            ref_keys |= ks

    print("== 我用到但参考里都没出现过的键（拼写风险）==")
    risky = []
    for sec, ks in mine.items():
        for k in sorted(ks - ref_keys):
            risky.append(f"  [{sec}] {k}")
    print("\n".join(risky) if risky else "  （无）")

    print("\n== 我漏掉、但商城皮里有的段 ==")
    print("  " + ", ".join(sorted(set(mall) - set(mine))) or "  （无）")

    print("\n== 状态栏：商城皮有而我未定义的按钮（将不可见）==")
    mall_bar = mall.get("StatusBar", set())
    mine_bar = mine.get("StatusBar", set())
    mall_buttons = {k.rsplit("_pos", 1)[0] for k in mall_bar if k.endswith("_pos")}
    mine_buttons = {k.rsplit("_pos", 1)[0] for k in mine_bar if k.endswith("_pos")}
    print("  商城皮:", ", ".join(sorted(mall_buttons)))
    print("  我的  :", ", ".join(sorted(mine_buttons)))
    print("  未覆盖:", ", ".join(sorted(mall_buttons - mine_buttons)) or "（无）")

    print("\n== 每种 Scheme：参考键 vs 我的键 ==")
    for name in ("Scheme_H1", "Scheme_V1", "Scheme_H2", "Scheme_V2"):
        m = mine.get(name, set())
        a = mall.get(name, set())
        b = hand.get(name, set())
        only_mine = sorted(m - (a | b))
        print(f"  {name}: 我的 {len(m)} 键，参考 {len(a | b)} 键"
              + (f"，独有: {only_mine}" if only_mine else "，全部有参考"))


if __name__ == "__main__":
    main()
