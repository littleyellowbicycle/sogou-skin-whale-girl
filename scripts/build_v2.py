"""打包无框动态版：skin.ini + APNG + 图标 -> .ssf，并做结构与帧数校验。"""
from __future__ import annotations

import configparser
import io
import zipfile
from pathlib import Path

from PIL import Image

import spec_v2 as S

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
BUILD = ROOT / (f"build_{S.THEME}" + ("_tpl" if S.TEMPLATE else ""))
OUT = (ROOT / "out" / "template") if S.TEMPLATE else (
    (ROOT / "out" / "upload") if S.LEAN else (ROOT / "out"))
SSF_NAME = (f"框模板-{S.THEME_LABEL}.ssf" if S.TEMPLATE
            else f"鲸鱼娘-{S.THEME_LABEL}.ssf")


def ts(t) -> str:
    return ",".join(str(v) for v in t)


def build_ini() -> str:
    L: list[str] = [
        "[General]",
        f"skin_name={S.SKIN_NAME}",
        f"skin_version={S.SKIN_VERSION}",
        f"skin_author={S.SKIN_AUTHOR}",
        "skin_email=",
        "skin_time=2026.11.16",
        f"skin_info={S.SKIN_INFO}",
        "",
        "[Display]",
        f"font_size={S.FONT_SIZE}",
        f"font_ch={S.FONT_CH}",
        f"font_en={S.FONT_EN}",
    ]
    for k, rgb in S.COLORS.items():
        L.append(f"{k}={S.bgr(rgb)}")
    L += ["use_gdip=1", "aero=0", "glow=0", "LargeFontSupport=1", ""]

    for name in ("H1", "V1", "H2", "V2"):
        L.append(f"[Scheme_{name}]")
        for k, v in S.SCHEMES[name].items():
            L.append(f"{k}={ts(v) if isinstance(v, tuple) else v}")
        L.append("")

    # 模板模式不含状态栏：整段省略，交给搜狗用默认状态栏
    if not S.TEMPLATE:
        L.append("[StatusBar]")
        L.append("pic=bar.png")
        for key, x, y, normal, hover, down in S.BAR_BUTTONS:
            L.append(f"{key}_pos={x},{y}")
            L.append(f"{key}={','.join(normal)}")
            L.append(f"{key}_hover={','.join(hover)}")
            L.append(f"{key}_down={','.join(down)}")
        L.append("")
    return "\r\n".join(L)


def thumbnail() -> Image.Image:
    """皮肤管理面板缩略图。模板模式没有状态栏，只摆输入框。"""
    h1 = Image.open(BUILD / "h1.png")
    h1.seek(0)

    size = 200
    canvas = Image.new("RGBA", (size, size), (232, 236, 244, 255))
    if not S.TEMPLATE:
        bar = Image.open(BUILD / "bar.png")
        bar.seek(0)
        b = bar.convert("RGBA")
        b = b.resize((190, round(b.height * 190 / b.width)), Image.LANCZOS)
        canvas.alpha_composite(b, ((size - b.width) // 2, 4))

    h = h1.convert("RGBA")
    h = h.resize((190, round(h.height * 190 / h.width)), Image.LANCZOS)
    canvas.alpha_composite(h, ((size - h.width) // 2, 60 if S.TEMPLATE else 120))
    return canvas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ini = build_ini()
    thumbnail().save(BUILD / "preview.png")

    files = sorted(BUILD.glob("*.png"))
    path = OUT / SSF_NAME
    if path.exists():
        path.unlink()

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("skin.ini", ini.encode("utf-16"))
        for p in files:
            z.write(p, arcname=p.name)

    size = path.stat().st_size
    limit = 600 * 1024
    print(f"built {path}  ({size/1024:.0f} KiB, {len(files)+1} files)")
    if S.LEAN:
        verdict = "OK" if size < limit else "超限"
        print(f"  上架限制 600 KiB -> {verdict}（{size/1024:.0f} KiB）")
        assert size < limit, f"{path.name} 超过 600KB 限制：{size/1024:.0f} KiB"
    verify(path)


def verify(path: Path) -> None:
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        raw = z.read("skin.ini")
        assert raw[:2] == b"\xff\xfe", "skin.ini 缺 UTF-16LE BOM"

        cp = configparser.ConfigParser(allow_no_value=True, strict=False)
        cp.optionxform = str
        cp.read_string(raw.decode("utf-16"))

        need = {"General", "Display", "Scheme_H1", "Scheme_V1", "Scheme_H2", "Scheme_V2"}
        if not S.TEMPLATE:
            need.add("StatusBar")
        else:
            assert "StatusBar" not in cp.sections(), "模板模式不应包含 [StatusBar]"
        assert need <= set(cp.sections()), need - set(cp.sections())

        refs = set()
        for sec in cp.sections():
            for _k, v in cp.items(sec):
                if not v:
                    continue
                for tok in v.split(","):
                    tok = tok.strip()
                    if tok.lower().endswith((".png", ".bmp")):
                        refs.add(tok)
        assert not (refs - names), f"引用了不存在的图: {refs - names}"

        anim = {"h1.png": S.ASSET_SPEC["h1"][2], "v1.png": S.ASSET_SPEC["v1"][2]}
        if not S.TEMPLATE:
            anim["bar.png"] = S.BAR_FRAMES
        total = 0
        for n in sorted(names):
            if not n.endswith(".png"):
                continue
            im = Image.open(io.BytesIO(z.read(n)))
            frames = getattr(im, "n_frames", 1)
            total += frames
            if n in anim:
                assert frames == anim[n], f"{n} 帧数 {frames} != {anim[n]}"
                print(f"  {n}: APNG {frames} 帧 {im.size}")
            else:
                assert frames == 1, f"{n} 意外多帧"

    print(f"verify OK: {len(names)} 个文件 / {len(refs)} 张引用图 / {total} 帧, 全部存在")


if __name__ == "__main__":
    main()
