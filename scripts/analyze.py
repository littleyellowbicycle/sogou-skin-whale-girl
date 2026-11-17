from PIL import Image
import numpy as np

SRC = r"C:\Users\10215\.dsh\profiles\desktop\node_modules\dsh-pet\assets\main-character.png"
im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(np.int16)
mx = a.max(axis=2)
mn = a.min(axis=2)

# stricter: clearly not background
content = (mx < 235) | ((mx - mn) > 25)
colcount = content.sum(axis=0)
rowcount = content.sum(axis=1)

def runs_from_counts(cnt, thresh, gap=40, min_len=20):
    mask = cnt > thresh
    out, start, last = [], None, None
    for i, v in enumerate(mask):
        if v:
            if start is None:
                start = i
            last = i
        else:
            if start is not None and (i - last) > gap:
                if last - start >= min_len:
                    out.append((start, last))
                start = None
    if start is not None and last - start >= min_len:
        out.append((start, last))
    return out

print("col runs:", runs_from_counts(colcount, 3))
print("row runs:", runs_from_counts(rowcount, 3))
print("max col count:", colcount.max(), "max row count:", rowcount.max())
print("col sample 0..40:", colcount[:40].tolist())
