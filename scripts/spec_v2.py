"""鲸鱼娘皮肤规格 —— 主题表 + 模板/上架档开关。

环境变量：
  SKIN_THEME   = foam | night | cream | parch   （配色主题，默认 foam）
  SKIN_LEAN    = 1                             （上架档：减帧压到 600KB 以内）
  SKIN_TEMPLATE= 1                             （框模板：无立绘/无挂件/无状态栏）
"""
from __future__ import annotations

import os

THEME = os.environ.get("SKIN_THEME", "foam")
LEAN = os.environ.get("SKIN_LEAN") == "1"
TEMPLATE = os.environ.get("SKIN_TEMPLATE") == "1"

THEMES = {
    # ---- 方案一：浪花泡沫（浅色日常） ----
    "foam": {
        "corners": False,
        "label": "浪花泡沫",
        "desc": "雾白底 + 发丝主蓝细边，最耐看",
        "body_top": "#F6FAFE",
        "body_bot": "#E6EFFA",
        "body_alpha": 1.0,
        "hl_alpha": 0.75,
        "border": "#486090",
        "border_alpha": 1.0,
        "inner": "#A8C8E8",
        "inner_alpha": 0.7,
        "text_deep": "#304878",
        "blush": "#F0A8A0",
        "bubble": "#A8C8E8",
        "shadow": "rgba(72,96,144,.18)",
        "orn_shadow": "rgba(48,72,120,.18)",
        "colors": {
            "pinyin_color": (124, 147, 184),
            "zhongwen_first_color": (48, 72, 120),
            "zhongwen_color": (85, 112, 154),
            "comphint_color": (150, 170, 200),
        },
        "chip": {
            "border": "#486090", "fg": "#304878",
            "bg1": "#FBFCFF", "bg2": "#E7EFFA",
            "hover_border": "#486090", "hover_fg": "#22335A",
            "hover_bg1": "#FFFFFF", "hover_bg2": "#D8E6F7",
            "hover_glow": "rgba(168,200,232,.9)", "hover_shadow": "rgba(72,96,144,.22)",
            "down_border": "#8FA9C9", "down_fg": "#486090",
            "down_bg1": "#DCE8F6", "down_bg2": "#C6D7EC",
            "down_inset": "rgba(48,72,120,.28)",
        },
        "icon": {"normal": "#304878", "hover": "#22335A", "down": "#486090"},
    },
    # ---- 方案二：深海夜航（深色护眼） ----
    "night": {
        "corners": False,
        "label": "深海夜航",
        "desc": "深海军蓝半透明，夜间不刺眼",
        "body_top": "#1B2A4A",
        "body_bot": "#131F38",
        "body_alpha": 0.88,
        "hl_alpha": 0.18,
        "border": "#486090",
        "border_alpha": 1.0,
        "inner": "#4FC3F7",
        "inner_alpha": 0.30,
        "text_deep": "#E8F1FA",
        "blush": "#F0A8A0",
        "bubble": "#4FC3F7",
        "shadow": "rgba(6,10,22,.45)",
        "orn_shadow": "rgba(0,0,0,.35)",
        "colors": {
            "pinyin_color": (159, 180, 216),
            "zhongwen_first_color": (79, 195, 247),
            "zhongwen_color": (232, 241, 250),
            "comphint_color": (150, 168, 200),
        },
        "chip": {
            "border": "#486090", "fg": "#E8F1FA",
            "bg1": "#2A3D66", "bg2": "#22355C",
            "hover_border": "#4FC3F7", "hover_fg": "#FFFFFF",
            "hover_bg1": "#35507F", "hover_bg2": "#2C4370",
            "hover_glow": "rgba(79,195,247,.75)", "hover_shadow": "rgba(0,0,0,.35)",
            "down_border": "#3E6FA0", "down_fg": "#4FC3F7",
            "down_bg1": "#16233D", "down_bg2": "#101A2E",
            "down_inset": "rgba(0,0,0,.55)",
        },
        "icon": {"normal": "#E8F1FA", "hover": "#FFFFFF", "down": "#4FC3F7"},
    },
    # ---- 方案三：软萌奶油（浅色 + 腮红点缀） ----
    "cream": {
        "corners": False,
        "label": "软萌奶油",
        "desc": "奶白底，腮红粉只做小面积点缀",
        "body_top": "#FFF9F4",
        "body_bot": "#FDF3EC",
        "body_alpha": 1.0,
        "hl_alpha": 0.60,
        "border": "#A8C8E8",
        "border_alpha": 1.0,
        "inner": "#F7C9C0",
        "inner_alpha": 0.55,
        "text_deep": "#3A4A6B",
        "blush": "#F7C9C0",
        "bubble": "#F7C9C0",
        "shadow": "rgba(94,74,66,.16)",
        "orn_shadow": "rgba(58,74,107,.16)",
        "colors": {
            "pinyin_color": (123, 141, 173),
            "zhongwen_first_color": (168, 88, 76),
            "zhongwen_color": (58, 74, 107),
            "comphint_color": (150, 160, 185),
        },
        "chip": {
            "border": "#A8C8E8", "fg": "#486090",
            "bg1": "#FFFDFB", "bg2": "#FDEFE8",
            "hover_border": "#F7C9C0", "hover_fg": "#486090",
            "hover_bg1": "#FFFFFF", "hover_bg2": "#FBE3DA",
            "hover_glow": "rgba(247,201,192,.9)", "hover_shadow": "rgba(94,74,66,.18)",
            "down_border": "#A8C8E8", "down_fg": "#3A4A6B",
            "down_bg1": "#FBEADF", "down_bg2": "#F5DCD0",
            "down_inset": "rgba(58,74,107,.22)",
        },
        "icon": {"normal": "#3A4A6B", "hover": "#C97F74", "down": "#486090"},
    },
    # ---- 方案四：羊皮卷（照参考截图复刻：单线金边 + 圆角卷饰） ----
    "parch": {
        "corners": True,
        "label": "羊皮卷",
        "desc": "照参考截图复刻：羊皮纸 + 单线金边 + 圆角卷饰",
        "body_top": "#FCF5E6",
        "body_bot": "#F4E7CD",
        "body_alpha": 1.0,
        "hl_alpha": 0.5,
        "border": "#C9A44C",
        "border_alpha": 1.0,
        "inner": "#E3C77E",
        "inner_alpha": 0.0,
        "text_deep": "#4A3A22",
        "blush": "#F0A8A0",
        "bubble": "#E3C77E",
        "shadow": "rgba(74,58,34,.22)",
        "orn_shadow": "rgba(74,58,34,.20)",
        "colors": {
            "pinyin_color": (154, 123, 78),
            "zhongwen_first_color": (168, 98, 26),
            "zhongwen_color": (62, 50, 34),
            "comphint_color": (160, 138, 106),
        },
        "chip": {
            "border": "rgba(201,164,76,.85)", "fg": "#4A3A22",
            "bg1": "#FDF7EA", "bg2": "#F3E4C6",
            "hover_border": "#A8823A", "hover_fg": "#2E2416",
            "hover_bg1": "#FFFDF6", "hover_bg2": "#EBD9B4",
            "hover_glow": "rgba(227,199,126,.9)", "hover_shadow": "rgba(74,58,34,.20)",
            "down_border": "#A8823A", "down_fg": "#A8823A",
            "down_bg1": "#EFE0C0", "down_bg2": "#E2CFA6",
            "down_inset": "rgba(74,58,34,.25)",
        },
        "icon": {"normal": "#4A3A22", "hover": "#2E2416", "down": "#A8823A"},
    },
}

if THEME not in THEMES:
    raise SystemExit(f"未知主题 {THEME}，可选：{', '.join(THEMES)}")

_T = THEMES[THEME]

THEME_LABEL = _T["label"]
KIND = "框模板" if TEMPLATE else ""
SKIN_NAME = f"{THEME_LABEL}框模板" if TEMPLATE else f"鲸鱼娘·{THEME_LABEL}"
SKIN_VERSION = "1.0" if TEMPLATE else "4.0"
SKIN_AUTHOR = "littleyellowbicycle"
SKIN_INFO = (
    f"{THEME_LABEL}输入框模板：四种模式 + 三态按键，纯界面设计，不含任何角色形象。"
    if TEMPLATE
    else f"{THEME_LABEL}配色（{_T['desc']}）。对话框 + 立绘 + 状态栏三动作循环动画。"
)

FONT_SIZE = 16
FONT_CH = "微软雅黑"
FONT_EN = "Arial"

COLORS = _T["colors"]
BODY_TOP = _T["body_top"]
BODY_BOT = _T["body_bot"]
BODY_ALPHA = _T["body_alpha"]
HL_ALPHA = _T["hl_alpha"]
BORDER_BLUE = _T["border"]
BORDER_ALPHA = _T["border_alpha"]
INNER_BLUE = _T["inner"]
INNER_ALPHA = _T["inner_alpha"]
TEXT_DEEP = _T["text_deep"]
BLUSH = _T["blush"]
BUBBLE_COLOR = _T["bubble"]
SHADOW = _T["shadow"]
ORN_SHADOW = _T["orn_shadow"]
CHIP = _T["chip"]
ICON = _T["icon"]
CORNERS = _T.get("corners", False)
FOAM_TOP = BODY_TOP          # 兼容旧名

BUBBLE_OPACITY = 0.18
RADIUS = 14


def bgr(rgb):
    r, g, b = rgb
    return f"0x{b:02x}{g:02x}{r:02x}"


# ---- 状态栏 ----
BAR_W, BAR_H = 300, 160
if LEAN:
    SEGMENT_PLAN = [("idle", 2), ("eat", 6), ("idle", 1), ("type", 2)]
else:
    SEGMENT_PLAN = [("idle", 3), ("eat", 11), ("idle", 1), ("type", 3)]
BAR_FRAMES = sum(c for _, c in SEGMENT_PLAN)
IDLE_FRAMES = SEGMENT_PLAN[0][1]

BAR_BUTTONS = [
    ("cn_en", 20, 56, ["cn1.png", "en1.png", "a1.png"],
     ["cn2.png", "en2.png", "a2.png"], ["cn3.png", "en3.png", "a3.png"]),
    ("quan_ban", 52, 56, ["quan1.png", "ban1.png"],
     ["quan2.png", "ban2.png"], ["quan3.png", "ban3.png"]),
    ("fan_jian", 84, 56, ["jian1.png", "fan1.png"],
     ["jian2.png", "fan2.png"], ["jian3.png", "fan3.png"]),
    ("quan_shuang", 20, 86, ["quanpin1.png", "shuanpin1.png"],
     ["quanpin2.png", "shuanpin2.png"], ["quanpin3.png", "shuanpin3.png"]),
    ("softkeyboard", 52, 86, ["key1.png"], ["key2.png"], ["key3.png"]),
    ("menu", 84, 86, ["menu1.png"], ["menu2.png"], ["menu3.png"]),
]

# ---- 输入模式：带立绘（默认）----
SCHEMES = {
    "H1": {
        "pic": "h1.png",
        "layout_horizontal": (0, 160, 150),
        "layout_vertical": (0, 92, 44),
        "pinyin_marge": (62, 0, 44, 150),
        "zhongwen_marge": (3, 28, 44, 150),
    },
    "V1": {
        "pic": "v1.png",
        "layout_horizontal": (0, 130, 130),
        "layout_vertical": (0, 140, 50),
        "pinyin_marge": (110, 0, 24, 24),
        "zhongwen_marge": (3, 26, 24, 24),
    },
    "H2": {
        "pinyin_pic": "h2p.png",
        "pinyin_layout_horizontal": (0, 26, 26),
        "pinyin_layout_vertical": (0, 18, 18),
        "pinyin_marge": (10, 10, 18, 18),
        "zhongwen_pic": "h2c.png",
        "zhongwen_layout_horizontal": (0, 30, 150),
        "zhongwen_layout_vertical": (0, 30, 28),
        "zhongwen_marge": (28, 28, 44, 150),
    },
    "V2": {
        "pinyin_pic": "v2p.png",
        "pinyin_layout_horizontal": (0, 26, 26),
        "pinyin_layout_vertical": (0, 18, 18),
        "pinyin_marge": (10, 10, 18, 18),
        "zhongwen_pic": "v2c.png",
        "zhongwen_layout_horizontal": (0, 120, 120),
        "zhongwen_layout_vertical": (0, 30, 30),
        "zhongwen_marge": (26, 26, 26, 26),
    },
}

# ---- 模板模式：无立绘，框体铺满，不带状态栏 ----
if TEMPLATE:
    BAR_W, BAR_H = 0, 0
    BAR_BUTTONS = []
    SCHEMES = {
        "H1": {
            "pic": "h1.png",
            "layout_horizontal": (0, 30, 30),
            "layout_vertical": (0, 92, 44),
            "pinyin_marge": (62, 0, 26, 26),
            "zhongwen_marge": (3, 28, 26, 26),
        },
        "V1": {
            "pic": "v1.png",
            "layout_horizontal": (0, 30, 30),
            "layout_vertical": (0, 60, 50),
            "pinyin_marge": (22, 0, 24, 24),
            "zhongwen_marge": (3, 26, 24, 24),
        },
        "H2": {
            "pinyin_pic": "h2p.png",
            "pinyin_layout_horizontal": (0, 26, 26),
            "pinyin_layout_vertical": (0, 18, 18),
            "pinyin_marge": (10, 10, 18, 18),
            "zhongwen_pic": "h2c.png",
            "zhongwen_layout_horizontal": (0, 30, 30),
            "zhongwen_layout_vertical": (0, 30, 28),
            "zhongwen_marge": (28, 28, 26, 26),
        },
        "V2": {
            "pinyin_pic": "v2p.png",
            "pinyin_layout_horizontal": (0, 26, 26),
            "pinyin_layout_vertical": (0, 18, 18),
            "pinyin_marge": (10, 10, 18, 18),
            "zhongwen_pic": "v2c.png",
            "zhongwen_layout_horizontal": (0, 120, 120),
            "zhongwen_layout_vertical": (0, 30, 30),
            "zhongwen_marge": (26, 26, 26, 26),
        },
    }

_H1F = 1 if LEAN else 4
_V1F = 1 if LEAN else 4

ASSET_SPEC = {
    **({} if TEMPLATE else {"bar": (300, 160, BAR_FRAMES)}),
    "h1": (640, 136, _H1F),
    "v1": ((260, 340, _V1F) if TEMPLATE else (260, 360, _V1F)),
    "h2p": (520, 40, 1),
    "h2c": (640, 88, 1),
    "v2p": (220, 40, 1),
    "v2c": (240, 340, 1),
}

# 状态栏动画节奏：按段落分别给每帧毫秒数（整体倍率可直接调 SPEED）
SPEED = float(os.environ.get("SKIN_SPEED", "1.0"))
_BASE_SEGMENT_MS = {"idle": 320, "eat": 150, "type": 150}
SEGMENT_MS = {k: max(20, round(v * SPEED)) for k, v in _BASE_SEGMENT_MS.items()}

# 候选窗气泡动画保持较快（它只在打字时短暂出现）
FRAME_MS = {"h1": 180, "v1": 180}

# 状态栏一轮时长（毫秒）
BAR_LOOP_MS = sum(SEGMENT_MS[k] * c for k, c in SEGMENT_PLAN)
