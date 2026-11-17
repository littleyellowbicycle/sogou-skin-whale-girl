def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


print("cream first-candidate on #FFF9F4:")
for c in ("#C97F74", "#BB6F63", "#B06054", "#A8584C", "#9E5045"):
    print("  %s  %.2f:1" % (c, ratio(c, "#FFF9F4")))

print("foam other-candidates on #F6FAFE:")
for c in ("#5A759F", "#55709A", "#526B95", "#4C658F", "#486090"):
    print("  %s  %.2f:1" % (c, ratio(c, "#F6FAFE")))
