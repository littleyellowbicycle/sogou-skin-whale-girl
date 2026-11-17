"""统一上架档的元数据（作者名/简介），并校验每套都含状态栏段。"""
import io
import re
import zipfile
from pathlib import Path

UP = Path(r"C:\Users\10215\Documents\deepseek-harness\default-workspace\sogou-skin\out\upload")

AUTHOR = "littleyellowbicycle"
INFO = {
    "羊皮卷": "羊皮纸底 + 单线金边 + 圆角卷饰；带鲸鱼立绘与状态栏三动作循环动画。",
    "浪花泡沫": "雾白底 + 发丝主蓝细边；带鲸鱼立绘与状态栏三动作循环动画。",
    "深海夜航": "深海军蓝半透明 + 冰蓝高亮，夜间护眼；带鲸鱼立绘与状态栏三动作循环动画。",
    "软萌奶油": "奶白底 + 雾蓝边 + 腮红粉点缀；带鲸鱼立绘与状态栏三动作循环动画。",
    "浮游版": "无框：文字下只压一条羽化软阴影；带鲸鱼立绘与状态栏三动作循环动画。",
}


def main() -> None:
    for p in sorted(UP.glob("*.ssf")):
        key = p.stem.split("-")[1]
        info = INFO.get(key, "")
        with zipfile.ZipFile(p) as z:
            entries = [(i.filename, z.read(i.filename)) for i in z.infolist()]

        out = []
        changed = False
        for name, data in entries:
            if name == "skin.ini":
                text = data.decode("utf-16")
                new = re.sub(r"(?m)^skin_author=.*$", f"skin_author={AUTHOR}", text)
                new = re.sub(r"(?m)^skin_info=.*$", f"skin_info={info}", new)
                if new != text:
                    changed = True
                out.append((name, new.encode("utf-16")))
            else:
                out.append((name, data))

        if changed:
            with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                for name, data in out:
                    z.writestr(name, data)

        ini = next(d for n, d in out if n == "skin.ini").decode("utf-16")
        has_sb = "[StatusBar]" in ini
        print(f"{p.name}: {p.stat().st_size/1024:.0f} KiB  [StatusBar]={'有' if has_sb else '无'}"
              f"  author={'更新' if changed else '已是'}  {info[:18]}...")


if __name__ == "__main__":
    main()
