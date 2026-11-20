"""Draw the site's gold ornaments as SVG (original artwork in the style of the
printed scrollwork on Mother's recipe pages).

  python tools/ornaments.py site/assets/ornaments

Writes garland.svg (the leaf arch over the title) and chain-link.svg,
chain-link-v.svg + chain-end.svg (the diamond-and-bead strips, repeated by CSS). corner.svg is hand-drawn and edited directly.
"""
import math
import sys
from pathlib import Path

GOLD = "#B48E67"


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def poly(points):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points) + "Z"


def ribbon(center, widths):
    """Filled outline around a centerline, with a width at each point."""
    left, right = [], []
    for i, ((x, y), w) in enumerate(zip(center, widths)):
        x0, y0 = center[max(i - 1, 0)]
        x1, y1 = center[min(i + 1, len(center) - 1)]
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    return poly(left + right[::-1])


def stem(p0, p1, p2, p3, w0, w1, n=40):
    pts = [bez(p0, p1, p2, p3, i / n) for i in range(n + 1)]
    return ribbon(pts, [w0 + (w1 - w0) * i / n for i in range(n + 1)])


def blade(p0, p1, p2, p3, width, n=48):
    """A leaf along a curved centerline."""
    pts = [bez(p0, p1, p2, p3, i / n) for i in range(n + 1)]
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / n
        base = width * math.sin(math.pi * min(t * 1.08, 1)) ** 0.85 * (1 - 0.35 * t)
        wl = base
        x0, y0 = pts[max(i - 1, 0)]
        x1, y1 = pts[min(i + 1, n)]
        dx, dy = x1 - x0, y1 - y0
        m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m, dx / m
        left.append((x + nx * wl / 2, y + ny * wl / 2))
        right.append((x - nx * base / 2, y - ny * base / 2))
    return poly(left + right[::-1])


def simple_leaf(x, y, ang, length, width, bend=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
    return blade(P(0, 0), P(length * 0.35, bend * length * 0.2), P(length * 0.7, bend * length * 0.5), P(length, bend * length), width)


def garland():
    """Arch of broad, plain leaves: one stem that crosses the top center and droops
    out to each side, leaves pointing steeply outward (as on Mother's printed page)."""
    stems, leaves = [], []
    # one continuous stem across the middle
    stems.append(stem((286, 16), (294, 13), (306, 13), (314, 16), 2.4, 2.4, 10))
    for side in (-1, 1):
        p0, p1, p2, p3 = (300 + side * 12, 15), (300 + side * 70, 10), (300 + side * 170, 30), (300 + side * 250, 82)
        stems.append(stem(p0, p1, p2, p3, 2.6, 1.6))
        n = 7
        for k in range(n):
            t = 0.06 + 0.84 * k / n
            x, y = bez(p0, p1, p2, p3, t)
            x2, y2 = bez(p0, p1, p2, p3, min(t + 0.01, 1))
            ang = math.atan2(y2 - y, x2 - x)
            s = 1 - 0.12 * k / n
            for up in (-1, 1):
                # upper leaves stand up steeply; lower ones hang a little less steeply
                a = ang + up * (0.95 if up == -1 else 0.8)
                leaves.append(simple_leaf(x, y, a, 44 * s, 16 * s, 0.05 * up))
        ang = math.atan2(p3[1] - p2[1], p3[0] - p2[0])
        leaves.append(simple_leaf(*p3, ang, 42, 15))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -30 600 150">'
            f'<path d="{" ".join(stems + leaves)}" fill="{GOLD}"/></svg>')


def chain_link(vertical=False):
    """One diamond and one bead on a hairline; CSS repeats it to any length."""
    g = (f'<path d="M0.5 6 H15.5" stroke="{GOLD}" stroke-width="0.8"/>'
         f'<path d="M1 6 L6 2 L11 6 L6 10Z"/><circle cx="13.5" cy="6" r="1.7"/>')
    if vertical:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 16"><g fill="{GOLD}" transform="matrix(0 1 1 0 0 0)">{g}</g></svg>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 12"><g fill="{GOLD}">{g}</g></svg>'


def chain_end():
    """Outlined diamond that finishes a chain."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
            f'<path d="M1 6 L6 1 L11 6 L6 11Z" fill="none" stroke="{GOLD}" stroke-width="1.2"/></svg>')


if __name__ == "__main__":
    out = Path(sys.argv[1])
    (out / "garland.svg").write_text(garland())
    (out / "chain-link.svg").write_text(chain_link())
    (out / "chain-link-v.svg").write_text(chain_link(vertical=True))
    (out / "chain-end.svg").write_text(chain_end())
    print("wrote garland.svg, chain-link.svg, chain-link-v.svg, chain-end.svg")
