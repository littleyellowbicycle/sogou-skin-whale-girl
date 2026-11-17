"""组装 GitHub 仓库内容（仅完整版）：5 套皮肤 + 说明 + 署名与授权。"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

SRC = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin")
GH = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin-gh")

FULL = [
    "鲸鱼娘-羊皮卷.ssf",
    "鲸鱼娘-浪花泡沫.ssf",
    "鲸鱼娘-深海夜航.ssf",
    "鲸鱼娘-软萌奶油.ssf",
    "鲸鱼娘-浮游版.ssf",
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


README = """# 鲸鱼娘 · 搜狗输入法皮肤

社区二创角色「大肥鱼」（鲸鱼娘）主题的 Windows 搜狗拼音输入法皮肤，五套配色。

> **非商业作品。** 形象授权为 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)，
> **不可以任何形式商业化**；转载请保留本文的署名段落。

## 下载

`skins/` 目录下双击任意 `.ssf` 即可导入搜狗输入法：

| 文件 | 配色 | 大小 |
| --- | --- | --- |
{skin_table}

## 内容

- **四种输入模式**：横排合并窗、竖排合并窗、横排分离、竖排分离
- **状态栏 18 帧循环动画**（APNG，150ms/帧，约 2.7 秒一轮）：
  待机浮动 3 帧 → 吃白饭 8 帧 → 间隔 2 帧 → 敲键盘 5 帧
- **鲸鱼喷水挂件**：候选框左侧小鲸鱼剪影 + 喷出的水花（含一颗腮红粉水滴）
- **按键三态**：常态 / 悬停 / 按下，各自独立贴图
- 四种配色主题共用同一结构，只换色板

> 提示：要看到立绘动画，需要输入法**状态栏未被隐藏**
> （右键候选框 → 属性设置 → 外观 → 显示状态栏）。

## 五套配色

| 方案 | 特点 |
| --- | --- |
| 羊皮卷 | 羊皮纸底 + 单线金边 + 圆角卷饰 |
| 浪花泡沫 | 雾白底 + 发丝主蓝单线边，浅色日常 |
| 深海夜航 | 深海军蓝 88% 半透明 + 冰蓝高亮，夜间护眼 |
| 软萌奶油 | 奶白底 + 雾蓝边 + 腮红粉点缀 |
| 浮游版 | 无框：没有面板，文字下只压一条羽化软阴影 |

配色取自立绘实测：主蓝紫 `#4F5FA0`、深靛 `#263066`、砂金 `#CDAD82`、发丝高光 `#7784B6`。

## 授权与署名

本作品为**非商业二创**，遵循 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)
（署名 · 非商业 · 相同方式共享）。

- **宠物形象**：社区二创的 DeepSeek「大肥鱼」（鲸鱼娘），**非 DeepSeek 官方形象**
- **原型「溟月」**：B 站 [@上善无形](https://space.bilibili.com/4456176)
- **DeepSeek 版（女仆鲸鱼娘）设计**：B 站 [@ZipZipPipe](https://space.bilibili.com/4168597)
- **素材与动作来源**：<https://github.com/PC2005-cloud/dsh-pet>
  （其许可：代码 MIT；素材与形象遵循上述 CC BY-NC-SA 4.0，二创在公开渠道须附该地址）
- **形象声明原文**：「大肥鱼是遵守 CC BY-NC-SA 4.0 协议的形象，不可以以任何形式商业化。」

**因此**：可自由下载、使用、非商业地二次修改，但**不得售卖**，
且再分发时须署名并采用相同协议。

## 制作说明

皮肤为 `.ssf` 包（zip），内含 `skin.ini`（UTF-16LE + BOM）与若干 png / apng。
动画由 APNG 承载：状态栏 18 帧、候选窗 4 帧。
动作帧从 `dsh-pet` 的 webm 抽取——源片无 alpha、背景纯黑，
按亮度阈值键像后用「底部 14%（脚+裙摆）中心」做水平配准。

详细设计文档见 [docs/说明.md](docs/说明.md)。
"""

LICENSE = """本仓库中的皮肤作品（.ssf 及其中的界面设计、配色、动画编排）采用
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
(CC BY-NC-SA 4.0) 许可协议。

协议全文：
https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.zh-hans
协议摘要：
https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans

署名要求（BY）：
- 宠物形象：社区二创的 DeepSeek「大肥鱼」（鲸鱼娘），非官方形象
- 原型「溟月」：B 站 @上善无形 https://space.bilibili.com/4456176
- DeepSeek 版（女仆鲸鱼娘）设计：B 站 @ZipZipPipe https://space.bilibili.com/4168597
- 素材与动作来源：https://github.com/PC2005-cloud/dsh-pet

非商业（NC）：不得以任何形式商业化，包括售卖、付费下载、与收入绑定的打赏等。

相同方式共享（SA）：再分发或改编本作品，须采用相同协议发布。

本仓库不是 DeepSeek 官方项目，也不代表 DeepSeek 或上述任何一方的立场。
"""


def main() -> None:
    if GH.exists():
        shutil.rmtree(GH)
    (GH / "skins").mkdir(parents=True)
    (GH / "docs").mkdir(parents=True)

    rows = []
    for name in FULL:
        src = SRC / "out" / name
        assert src.is_file(), src
        dst = GH / "skins" / name
        shutil.copy2(src, dst)
        rows.append((name, dst.stat().st_size, sha256(dst)))

    shutil.copy2(SRC / "说明.md", GH / "docs" / "说明.md")
    shutil.copy2(SRC / "对比图-四方案.png", GH / "docs" / "对比图-四方案.png")

    table = "\n".join(
        f"| `{n}` | {n.split('-')[1].replace('.ssf','')} | {s/1024:.0f} KB |" for n, s, _ in rows
    )
    (GH / "README.md").write_text(README.replace("{skin_table}", table), encoding="utf-8", newline="\n")
    (GH / "LICENSE").write_text(LICENSE, encoding="utf-8", newline="\n")

    # 校验文件清单
    (GH / "SHA256SUMS.txt").write_text(
        "\n".join(f"{d}  {n}" for n, _, d in rows) + "\n", encoding="utf-8", newline="\n"
    )
    total = sum(s for _, s, _ in rows)
    print(f"repo assembled at {GH}  ({total/1024/1024:.2f} MiB, {len(rows)} skins)")


if __name__ == "__main__":
    main()
