# 鲸鱼娘 · 搜狗输入法皮肤（成品 + 工程归档）

社区二创角色「大肥鱼」（鲸鱼娘）主题的 **Windows 搜狗拼音输入法皮肤**，五套配色。
仓库同时归档了**完整的生成脚本**与**踩坑记录**，方便复用或改配色重出。

> **非商业作品。** 形象授权为 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)，
> **不可以任何形式商业化**；转载请保留下面的署名段落。

---

## 一、成品

`skins/` 下双击任意 `.ssf` 导入搜狗输入法。

> ⚠️ **更新皮肤请装新版本名，不要同名覆盖**——同名安装会让搜狗的 `skin_v3.dat` 解析缓存变成半新半旧，
> 导致输入框异常，严重时只能卸载重装输入法。详见 [PITFALLS.md 第十一节](PITFALLS.md)。
> 恢复办法：退出输入法进程 → 删 `%USERPROFILE%\AppData\LocalLow\SogouPY\skin_v3.dat` → 重新激活输入法。

| 文件 | 配色 | 大小 |
| --- | --- | --- |
| `鲸鱼娘-羊皮卷-v4.2.ssf` | 羊皮纸底 + 单线金边 + 圆角卷饰 | 1079 KB |
| `鲸鱼娘-深海夜航-v4.2.ssf` | 深海军蓝半透明 + 冰蓝高亮 | 1089 KB |
| `鲸鱼娘-浪花泡沫-v4.2.ssf` | 雾白底 + 发丝主蓝单线边 | 1055 KB |
| `鲸鱼娘-软萌奶油-v4.2.ssf` | 奶白底 + 雾蓝边 + 腮红粉点缀 | 1045 KB |
| `鲸鱼娘-浮游版.ssf` | 无框，文字下只压一条羽化软阴影（旧版，未带 v4.2 前缀） | 1140 KB |

- 四种输入模式全适配（横排/竖排、合并/分离）
- 状态栏 18 帧循环：**待机 3 → 吃白饭 11 → 间隔 1 → 敲键盘 3**，一轮 3.38 秒（动作段 6.7 fps）
- 按键三态（常态 / 悬停 / 按下），鲸鱼喷水挂件，14px 圆角

> 要看到立绘动画，需输入法**状态栏未被隐藏**
> （右键候选框 → 属性设置 → 外观 → 显示状态栏）。

---

## 二、工程结构

```
skins/          5 套成品 .ssf
docs/           设计说明 + 四方案对比图
scripts/        全部生成脚本（33 个）
PITFALLS.md     踩坑记录（★ 最有价值的部分）
README.md       本文件
LICENSE         素材与形象：CC BY-NC-SA 4.0
```

### 脚本分工

| 脚本 | 作用 |
| --- | --- |
| `spec_v2.py` | **唯一配置源**：三套主题配色、状态栏编排与帧时长、四种模式的 `marge`/`layout`、按键位置 |
| `cut_character.py` | 立绘抠图（白底泛洪）+ 产出全身/半身/头部/头像素材 |
| `extract_eat.py` / `extract_type.py` | 从 pet 的 webm 抽帧、去黑底、按「底部 14% 锚点」配准 |
| `render_v2.py` | 用 HTML + Edge headless 逐帧渲染，合成 APNG |
| `build_v2.py` | 写 `skin.ini`（UTF-16LE+BOM）、打包 `.ssf`、结构校验 |
| `preview_v2.py` / `compare.py` | 生成预览图与多方案对比 |
| `make_store_assets.py` | 投稿图（效果图 ≤500×350、缩略图 ≤420×210） |
| `make_avatar.py` | 用立绘裁四版头像 |
| `mobile_keyboard.py` | 手机皮肤 1080×846 版式（26 键 / 9 键） |
| `apng_delta.py` / `exp_apng.py` | APNG 差分编码器 + 有效性对照实验（结论：本素材无效） |
| `thin_ssf.py` / `retime_existing.py` | 对已有成品抽帧 / 改帧时长（不改像素） |
| `audit_colors.py` / `report_state.py` | 配色与帧数时长审计 |

### 重出皮肤

```powershell
$py = "<你的 python>"
cd scripts
$env:SKIN_THEME = "foam"        # parch | foam | night | cream
$env:SKIN_LEAN  = "1"           # 可选：上架档（<600KB）
$env:SPEED      = "1.2"         # 可选：整体放慢 20%
& $py render_v2.py; & $py build_v2.py; & $py preview_v2.py
```

---

## 三、几个关键结论（详见 PITFALLS.md）

1. **`skin.ini` 必须 UTF-16LE+BOM；颜色是 `0xBBGGRR`；`marge` 是（上,下,左,右）**
2. **美术必须放在九宫格的非拉伸格**里，否则会被拉变形
3. **单帧成本由插画复杂度决定**（300×160 立绘 ≈ 33.7 KiB/帧）；裁画布、做差分**都不省**
4. **APNG 差分编码实测 1.00x**（全画布 660KiB vs 差分 661KiB）——这条路已否掉
5. **唯一有效的体积杠杆是重分配帧预算**（总帧数不变，把帧挪给动作段）
6. **动画只在状态栏常驻可见**；候选窗提交即销毁；状态栏可被用户隐藏
7. **600KiB 只是投稿限制**，本地自用无上限（24fps × 1.5 秒 ≈ 1.2MB）
8. **抽帧配准用「底部 14% 中心」**，用包围盒中心会被举起的道具带偏约 25px
9. **PC 与手机是两套体系**：PC 传 `.ssf`；手机要**分层 PSD**（1080×846），由平台生成皮肤
10. **授权分层**：代码 MIT，**素材/形象 CC BY-NC-SA 4.0，不可商用**

---

## 四、授权与署名

本作品为**非商业二创**，遵循 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)
（署名 · 非商业 · 相同方式共享）。

- **宠物形象**：社区二创的 DeepSeek「大肥鱼」（鲸鱼娘），**非 DeepSeek 官方形象**
- **原型「溟月」**：B 站 [@上善无形](https://space.bilibili.com/4456176)
- **DeepSeek 版（女仆鲸鱼娘）设计**：B 站 [@ZipZipPipe](https://space.bilibili.com/4168597)
- **素材与动作来源**：<https://github.com/PC2005-cloud/dsh-pet>
- **形象声明原文**：「大肥鱼是遵守 CC BY-NC-SA 4.0 协议的形象，不可以以任何形式商业化。」

**因此**：可自由下载、使用、非商业地二次修改，但**不得售卖**，
且再分发时须署名并采用相同协议。

`scripts/` 下的代码由本仓库作者编写，可按 MIT 使用。
