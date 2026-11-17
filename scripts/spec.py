"""皮肤规格：所有几何与配色集中在这里，skin.ini 与预览图共用同一份数字。"""

SKIN_NAME = "鲸鱼娘·深海信使"
SKIN_VERSION = "1.0"
SKIN_AUTHOR = "本机自制（基于 dsh-pet 鲸鱼娘形象）"
SKIN_INFO = (
    "参考 DeepSeek Harness 的 dsh-pet 插件「鲸鱼娘」形象制作。"
    "深海军蓝渐变面板 + 米白描边 + 金色发丝线，右端海洋气泡与鲸鱼娘探头。"
)

FONT_SIZE = 16
FONT_CH = "微软雅黑"
FONT_EN = "Arial"

# skin.ini 里的颜色是 0xBBGGRR 打包（已由参考皮肤反推确认）
COLORS = {
    "pinyin_color": (169, 199, 239),        # 冰蓝：输入码
    "zhongwen_first_color": (255, 217, 138),  # 暖金：首选词
    "zhongwen_color": (233, 239, 250),      # 近白：其它候选
    "comphint_color": (144, 166, 201),      # 灰蓝：补全提示
}


def bgr(rgb):
    r, g, b = rgb
    return f"0x{b:02x}{g:02x}{r:02x}"


# ---- 状态栏 ----
BAR_W, BAR_H = 320, 92
BAR_BUTTONS = [
    # (key, x, y, 状态图列表, hover 列表, down 列表)
    ("cn_en", 12, 35, ["cn1.png", "en1.png", "a1.png"],
     ["cn2.png", "en2.png", "a2.png"], ["cn3.png", "en3.png", "a3.png"]),
    ("quan_ban", 44, 35, ["quan1.png", "ban1.png"],
     ["quan2.png", "ban2.png"], ["quan3.png", "ban3.png"]),
    ("fan_jian", 76, 35, ["jian1.png", "fan1.png"],
     ["jian2.png", "fan2.png"], ["jian3.png", "fan3.png"]),
    ("quan_shuang", 108, 35, ["quanpin1.png", "shuanpin1.png"],
     ["quanpin2.png", "shuanpin2.png"], ["quanpin3.png", "shuanpin3.png"]),
    ("softkeyboard", 140, 35, ["key1.png"], ["key2.png"], ["key3.png"]),
    ("menu", 172, 35, ["menu1.png"], ["menu2.png"], ["menu3.png"]),
]

# ---- 四种输入模式 ----
# marge / layout 的语义：(上,下,左,右) 与 (模式,左/上,右/下)，模式 0 = 中间拉伸
SCHEMES = {
    "H1": {
        "pic": "h1.png",
        # 右格宽度必须盖住右端探头（头像在 x≥510），左格盖住圆角
        "layout_horizontal": (0, 180, 130),
        # 顶格要盖住拼音行（84..105），让拼音永远不被拉伸带偏
        "layout_vertical": (0, 106, 44),
        "pinyin_marge": (84, 0, 26, 26),
        "zhongwen_marge": (2, 18, 26, 26),
    },
    "V1": {
        "pic": "v1.png",
        "layout_horizontal": (0, 130, 130),
        # 顶格盖住拼音行（118..139）与立绘，其余留作候选区
        "layout_vertical": (0, 145, 50),
        "pinyin_marge": (118, 0, 28, 28),
        "zhongwen_marge": (6, 26, 28, 28),
    },
    "H2": {
        "pinyin_pic": "h2p.png",
        "pinyin_layout_horizontal": (0, 26, 26),
        "pinyin_layout_vertical": (0, 18, 18),
        "pinyin_marge": (10, 10, 18, 18),
        "zhongwen_pic": "h2c.png",
        "zhongwen_layout_horizontal": (0, 30, 30),
        "zhongwen_layout_vertical": (0, 30, 30),
        "zhongwen_marge": (32, 32, 26, 26),
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
