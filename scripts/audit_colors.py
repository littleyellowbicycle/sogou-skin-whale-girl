"""配色审计：把你给的规格表和工作区实现逐条比对。"""
import spec_v2 as S

# 你给的规格（原样抄录）
SPEC = {
    "foam": {
        "候选框背景": "#F6FAFE",
        "边框/分隔线": "#486090",
        "选中高亮": "#A8C8E8",
        "候选文字": "#304878",
        "点缀·腮红": "#F0A8A0",
    },
    "night": {
        "候选框背景": "#1B2A4A",
        "边框/键帽": "#486090",
        "选中高亮": "#4FC3F7",
        "候选文字": "#E8F1FA",
        "点缀·模式切换键": "#F0A8A0",
    },
    "cream": {
        "候选框背景": "#FFF9F4",
        "边框·雾蓝": "#A8C8E8",
        "选中高亮": "#F7C9C0",
        "候选文字": "#3A4A6B",
        "功能键·发丝主色": "#486090",
    },
}


def hexof(rgb):
    return "#%02X%02X%02X" % rgb


def main() -> None:
    for key, spec in SPEC.items():
        os_theme = S.THEMES[key]
        c = os_theme["colors"]
        chip = os_theme["chip"]

        impl = {
            "候选框背景": os_theme["body_top"],
            "选中高亮(首选词文字)": hexof(c["zhongwen_first_color"]),
            "候选文字(其它)": hexof(c["zhongwen_color"]),
            "内侧/气泡色": os_theme["inner"] if os_theme["inner_alpha"] > 0 else os_theme["bubble"],
            "点缀": os_theme["blush"],
            "键帽描边": chip["border"],
            "键帽字色": chip["fg"],
        }
        border_key = [k for k in spec if k.startswith("边框")]
        func_key = [k for k in spec if k.startswith("功能键")]

        print(f"\n=== {key} ({os_theme['label']}) ===")
        for label, want in spec.items():
            if label.startswith("边框") or label.startswith("功能键"):
                got = impl["键帽描边"] if label.startswith("边框") else impl["键帽字色"]
                if label.startswith("功能键"):
                    got = impl["键帽字色"]
            elif label == "候选框背景":
                got = impl["候选框背景"]
            elif label == "选中高亮":
                got = impl["选中高亮(首选词文字)"]
            elif label == "候选文字":
                got = impl["候选文字(其它)"]
            else:
                got = impl["点缀"]
            norm = got.replace("rgba(72,96,144,.55)", "#486090")
            ok = norm.upper().startswith(want.upper()) or want.upper() in norm.upper()
            print(f"  {'OK ' if ok else '差异'} {label:16s} 规格 {want}  实际 {got}")


if __name__ == "__main__":
    main()
