"""Draw the site's gold ornaments as SVG (original artwork in the style of the
printed scrollwork on Mother's recipe pages).

  python tools/ornaments.py site/assets/ornaments

Writes garland.svg (the leaf arch over the title) and chain.svg (the
diamond-and-dot strip). corner.svg is hand-drawn and edited directly.
"""
import math
import sys
from pathlib import Path

GOLD = "#B48E67"
VEIN = "#FFFFFF"


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


def vein(x, y, ang, length, bend=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
    return stem(P(length * 0.08, 0), P(length * 0.35, bend * length * 0.2), P(length * 0.6, bend * length * 0.45), P(length * 0.85, bend * length * 0.8), 0.9, 0.2, 16)


def garland():
    """Arch of broad leaves with center veins, two branches meeting at the top."""
    leaves, veins, stems = [], [], []
    for side in (-1, 1):
        p0, p1, p2, p3 = (300 + side * 12, 14), (300 + side * 80, 6), (300 + side * 170, 22), (300 + side * 262, 62)
        stems.append(stem(p0, p1, p2, p3, 2.6, 1.4))
        n = 7
        for k in range(n):
            t = 0.08 + 0.86 * k / n
            x, y = bez(p0, p1, p2, p3, t)
            x2, y2 = bez(p0, p1, p2, p3, min(t + 0.01, 1))
            ang = math.atan2(y2 - y, x2 - x)
            s = 1 - 0.25 * k / n
            for up in (-1, 1):
                a = ang + up * 0.68
                leaves.append(simple_leaf(x, y, a, 38 * s, 12.5 * s, 0.06 * up))
                veins.append(vein(x, y, a, 40 * s, 0.06 * up))
        x, y = p3
        ang = math.atan2(p3[1] - p2[1], p3[0] - p2[0])
        leaves.append(simple_leaf(x, y, ang, 40, 12))
        veins.append(vein(x, y, ang, 40))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -24 600 124">'
            f'<path d="{" ".join(stems + leaves)}" fill="{GOLD}"/>'
            f'<path d="{" ".join(veins)}" fill="{VEIN}" opacity="0.55"/></svg>')


def chain(n=8):
    """Diamonds alternating with dots, ending in an outlined diamond."""
    parts, x = [], 10
    for _ in range(n):
        parts.append(f'<path d="M{x - 5} 6 L{x} 1 L{x + 5} 6 L{x} 11Z"/>')
        parts.append(f'<circle cx="{x + 8}" cy="6" r="1.6"/>')
        x += 16
    parts.append(f'<path d="M{x - 5} 6 L{x} 1 L{x + 5} 6 L{x} 11Z" fill="none" stroke="{GOLD}" stroke-width="1.2"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="4 0 {x + 2} 12"><g fill="{GOLD}">{"".join(parts)}</g></svg>'


if __name__ == "__main__":
    out = Path(sys.argv[1])
    (out / "garland.svg").write_text(garland())
    (out / "chain.svg").write_text(chain())
    print("wrote garland.svg, chain.svg")
