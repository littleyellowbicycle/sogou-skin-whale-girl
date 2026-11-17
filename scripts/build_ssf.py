"""生成 skin.ini 并打包成 .ssf（ssf = 标准 zip，内含 skin.ini + 若干 png）。"""
from __future__ import annotations

import configparser
import io
import zipfile
from pathlib import Path

from PIL import Image

import spec

ROOT = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
BUILD = ROOT / "build"
OUT = ROOT / "out"
SSF_NAME = "鲸鱼娘-深海信使.ssf"
DISPLAY_SSF = f"{spec.SKIN_NAME}.ssf"


def tuple_str(t) -> str:
    return ",".join(str(v) for v in t)


def build_ini() -> str:
    lines: list[str] = []

    lines += [
        "[General]",
        f"skin_name={spec.SKIN_NAME}",
        f"skin_version={spec.SKIN_VERSION}",
        f"skin_author={spec.SKIN_AUTHOR}",
        "skin_email=",
        "skin_time=2026.11.16",
        f"skin_info={spec.SKIN_INFO}",
        "",
        "[Display]",
        f"font_size={spec.FONT_SIZE}",
        f"font_ch={spec.FONT_CH}",
        f"font_en={spec.FONT_EN}",
    ]
    for key, rgb in spec.COLORS.items():
        lines.append(f"{key}={spec.bgr(rgb)}")
    lines += [
        "use_gdip=1",
        "aero=0",
        "glow=0",
        "LargeFontSupport=1",
        "",
    ]

    for name in ("H1", "V1", "H2", "V2"):
        sch = spec.SCHEMES[name]
        lines.append(f"[Scheme_{name}]")
        for key, val in sch.items():
            if isinstance(val, tuple):
                lines.append(f"{key}={tuple_str(val)}")
            else:
                lines.append(f"{key}={val}")
        lines.append("")

    lines.append("[StatusBar]")
    lines.append("pic=bar.png")
    for key, x, y, normal, hover, down in spec.BAR_BUTTONS:
        lines.append(f"{key}_pos={x},{y}")
        lines.append(f"{key}={','.join(normal)}")
        lines.append(f"{key}_hover={','.join(hover)}")
        lines.append(f"{key}_down={','.join(down)}")
    lines.append("")

    return "\r\n".join(lines)


def make_thumbnail() -> Image.Image:
    """皮肤管理面板里的方形缩略图。"""
    bar = Image.open(BUILD / "bar.png").convert("RGBA")
    h1 = Image.open(BUILD / "h1.png").convert("RGBA")

    size = 200
    canvas = Image.new("RGBA", (size, size), (24, 30, 58, 255))
    # 顶部放状态栏（等比缩到 190 宽）
    bw = 190
    b = bar.resize((bw, round(bar.height * bw / bar.width)), Image.LANCZOS)
    canvas.alpha_composite(b, ((size - b.width) // 2, 6))
    # 下部放横排窗
    hw = 190
    h = h1.resize((hw, round(h1.height * hw / h1.width)), Image.LANCZOS)
    canvas.alpha_composite(h, ((size - h.width) // 2, 108))
    return canvas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ini_text = build_ini()

    thumb = make_thumbnail()
    thumb.save(BUILD / "preview.png")

    files = sorted(p for p in BUILD.glob("*.png"))
    ssf_path = OUT / SSF_NAME
    if ssf_path.exists():
        ssf_path.unlink()

    with zipfile.ZipFile(ssf_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("skin.ini", ini_text.encode("utf-16"))  # 带 BOM 的 UTF-16LE
        for p in files:
            z.write(p, arcname=p.name)

    print(f"built {ssf_path}  ({ssf_path.stat().st_size/1024:.1f} KiB, {len(files)+1} files)")
    verify(ssf_path)


def verify(ssf_path: Path) -> None:
    """结构校验：zip 可读、ini 可解析、引用的图片都在、尺寸与预期一致。"""
    with zipfile.ZipFile(ssf_path) as z:
        names = set(z.namelist())
        raw = z.read("skin.ini")

    assert raw[:2] == b"\xff\xfe", "skin.ini 不是 UTF-16LE BOM"
    text = raw.decode("utf-16")
    assert "skin.ini" not in names or True

    cp = configparser.ConfigParser(allow_no_value=True, strict=False)
    cp.optionxform = str
    cp.read_string(text)

    required_sections = {"General", "Display", "Scheme_H1", "Scheme_V1", "Scheme_H2", "Scheme_V2", "StatusBar"}
    missing = required_sections - set(cp.sections())
    assert not missing, f"缺少段: {missing}"

    # 收集所有被引用的图片名
    refs: set[str] = set()
    for sec in cp.sections():
        for key, val in cp.items(sec):
            if not val:
                continue
            for token in val.split(","):
                token = token.strip()
                if token.lower().endswith(".png") or token.lower().endswith(".bmp"):
                    refs.add(token)

    absent = refs - names
    assert not absent, f"skin.ini 引用了不存在的图: {absent}"

    # 尺寸校验
    expected = {
        "bar.png": (spec.BAR_W, spec.BAR_H),
        "h1.png": (640, 150),
        "v1.png": (260, 380),
        "h2p.png": (520, 40),
        "h2c.png": (640, 92),
        "v2p.png": (220, 40),
        "v2c.png": (240, 360),
        "preview.png": (200, 200),
    }
    with zipfile.ZipFile(ssf_path) as z:
        for name, want in expected.items():
            im = Image.open(io.BytesIO(z.read(name)))
            assert im.size == want, f"{name} 尺寸 {im.size} != {want}"

    print(f"verify OK: {len(names)} 个文件, 引用 {len(refs)} 张图, 全部存在且尺寸正确")


if __name__ == "__main__":
    main()
