"""把五套搜狗皮肤打包进 blueyellow-sync 的 packages/ 目录，并生成带 SHA-256 的 README。"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

SRC = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
REPO = Path(r"D:\project\mem_pool\blueyellow-sync")
PKG = REPO / "packages" / "sogou-skin-whale-girl-4.0"

# 文件名 -> (方案名, 一句话说明)
SKINS = {
    "鲸鱼娘-羊皮卷.ssf": ("羊皮卷", "照参考截图复刻：羊皮纸底 + 单线金边 + 圆角卷饰"),
    "鲸鱼娘-浪花泡沫.ssf": ("浪花泡沫", "雾白底 + 发丝主蓝单线边，浅色日常"),
    "鲸鱼娘-深海夜航.ssf": ("深海夜航", "深海军蓝 88% 半透明 + 冰蓝高亮，夜间护眼"),
    "鲸鱼娘-软萌奶油.ssf": ("软萌奶油", "奶白底 + 雾蓝边 + 腮红粉点缀"),
    "鲸鱼娘-浮游版.ssf": ("浮游版", "无框：没有面板，文字下只压一条羽化软阴影"),
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    PKG.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, (label, desc) in SKINS.items():
        src = SRC / "out" / name
        assert src.is_file(), src
        dst = PKG / name
        shutil.copy2(src, dst)
        rows.append((name, label, desc, dst.stat().st_size, sha256(dst)))

    # 附带：说明文档 + 四方案对比图
    shutil.copy2(SRC / "说明.md", PKG / "说明.md")
    shutil.copy2(SRC / "对比图-四方案.png", PKG / "对比图-四方案.png")

    total = sum(r[3] for r in rows)
    lines = [
        "# 搜狗输入法皮肤：鲸鱼娘（五套配色）",
        "",
        "基于 DeepSeek Harness 的 `dsh-pet` 插件「鲸鱼娘」立绘制作的 Windows 搜狗拼音输入法皮肤。",
        "五套共用同一结构，只换配色；每套含四种输入模式 + 状态栏三动作循环动画。",
        "",
        "## 文件",
        "",
        "| 文件 | 配色 | 说明 | 大小 | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, label, desc, size, digest in rows:
        lines.append(f"| `{name}` | {label} | {desc} | {size/1024:.0f} KiB | `{digest}` |")

    lines += [
        "",
        f"合计 {total/1024/1024:.2f} MiB（5 个文件均 < 2 MB，符合 `packages/` 单文件上限）。",
        "",
        "## 安装",
        "",
        "双击 `.ssf` → 搜狗弹出安装窗口 → 确认；或 状态栏右键 → 更换皮肤 → 皮肤管理器 → 添加皮肤。",
        "",
        "## 内容",
        "",
        "- 四种输入模式：横排合并窗、竖排合并窗、横排分离、竖排分离",
        "- 状态栏 18 帧循环：待机浮动 3 → 吃白饭 8 → 待机 2 → 敲键盘 5（APNG，150ms/帧）",
        "- 按键三态（常态 / 悬停 / 按下），鲸鱼喷水挂件，14px 圆角",
        "",
        "## 已知未验证项",
        "",
        "APNG 动画**未在真实输入法里实测过**（制作环境无法驱动 IME 界面截图）。",
        "若某套装上后不动，最坏情况是只显示第一帧（静态立绘），不会损坏皮肤。",
        "",
        "## 来源与授权",
        "",
        "- 角色形象与动作来自 `dsh-pet` 插件（<https://github.com/PC2005-cloud/dsh-pet>，MIT）。",
        "- 本套皮肤是本机对该形象的二次创作，仅供自用；上架或商用需先确认原作者意愿并保留署名。",
        "- 制作产物、源规格与渲染脚本在制作机 `sogou-skin/` 目录；详细设计说明见同目录 `说明.md`。",
        "",
        "## 复核",
        "",
        "`sha256sum`（Linux/macOS）或 `Get-FileHash <file> -Algorithm SHA256`（Windows）可校验下载完整性。",
        "",
    ]

    (PKG / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"packed {len(rows)} skins -> {PKG}  ({total/1024/1024:.2f} MiB)")
    for name, label, _desc, size, digest in rows:
        print(f"  {name}  {size/1024:.0f} KiB  {digest[:16]}...")


if __name__ == "__main__":
    main()
