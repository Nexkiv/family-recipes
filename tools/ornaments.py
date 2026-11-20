"""Draw the site's gold ornaments as SVG (original artwork in the style of the
printed scrollwork on Mother's recipe pages).

  python tools/ornaments.py site/assets/ornaments

Writes corner.svg (top-left; CSS flips it for the other corners), garland.svg
(the leaf arch over the title) and chain.svg (the diamond-and-dot strip).
Shapes are filled outlines rather than strokes so lines can taper like print.
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


def spiral(cx, cy, r0, turns, a0, direction, w0, w1, n=70):
    pts, ws = [], []
    for i in range(n + 1):
        t = i / n
        a = a0 + direction * t * turns * 2 * math.pi
        r = r0 * (1 - 0.8 * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        ws.append(w0 + (w1 - w0) * t)
    return ribbon(pts, ws)


def blade(p0, p1, p2, p3, width, lobes=0, lobe_depth=0.45, n=48):
    """A leaf along a curved centerline. lobes > 0 scallops one edge (acanthus)."""
    pts = [bez(p0, p1, p2, p3, i / n) for i in range(n + 1)]
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / n
        base = width * math.sin(math.pi * min(t * 1.08, 1)) ** 0.85 * (1 - 0.35 * t)
        wl = base * (1 + lobe_depth * abs(math.sin(lobes * math.pi * t))) if lobes else base
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


def fern(x, y, ang, length, pairs=4):
    """Small wheat/fern sprig."""
    out = [stem((x, y), (x + math.cos(ang) * length / 3, y + math.sin(ang) * length / 3),
                (x + math.cos(ang) * 2 * length / 3, y + math.sin(ang) * 2 * length / 3),
                (x + math.cos(ang) * length, y + math.sin(ang) * length), 1.4, 0.6, 12)]
    for k in range(pairs):
        t = 0.3 + 0.7 * k / pairs
        px, py = x + math.cos(ang) * length * t, y + math.sin(ang) * length * t
        s = 1 - 0.3 * k / pairs
        out += [simple_leaf(px, py, ang + 0.6, 9 * s, 3.2 * s), simple_leaf(px, py, ang - 0.6, 9 * s, 3.2 * s)]
    out.append(simple_leaf(x + math.cos(ang) * length, y + math.sin(ang) * length, ang, 9, 3.4))
    return out


def leafy_scroll(cx, cy, r0, turns, a0, direction, w0, w1, leaves=5, leaf_len=13, outward=1):
    """A curling frond: a tapering spiral with small leaves along its outer edge."""
    out = [spiral(cx, cy, r0, turns, a0, direction, w0, w1)]
    for k in range(leaves):
        t = 0.05 + 0.6 * k / leaves
        a = a0 + direction * t * turns * 2 * math.pi
        r = r0 * (1 - 0.8 * t)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        s = 1 - 0.45 * k / leaves
        # leaflets stand out from the curl and sweep back toward its base, like acanthus
        out.append(simple_leaf(x, y, a - direction * 0.55, leaf_len * s, leaf_len * 0.48 * s, -0.12 * direction))
    return out


def corner():
    """Top-left corner, 244x244. The top arm is drawn once and mirrored for the left arm."""
    arm = []
    # main scroll stem running along the top edge
    arm.append(stem((40, 44), (64, 14), (130, 18), (192, 16), 4.2, 1.8))
    # big swept leaf at the end of the arm, with a vein
    arm.append(blade((188, 16), (204, 3), (224, 1), (240, 11), 14))
    # fronds curling down off the stem
    # each frond leaves the stem heading right, then curls down and back under itself
    arm += leafy_scroll(84, 17 + 21, 21, 0.95, math.radians(-90), 1, 3.4, 0.9, leaves=6, leaf_len=13)
    arm += leafy_scroll(140, 17 + 14, 14, 0.95, math.radians(-90), 1, 2.6, 0.7, leaves=4, leaf_len=10)
    # small leaves riding on top of the stem
    for x, y, a, L in [(110, 16, -0.35, 14), (124, 16, -0.4, 11), (164, 15, -0.3, 11)]:
        arm.append(simple_leaf(x, y, a, L, L * 0.38, -0.1))
    # wheat sprig under the swept leaf
    arm += fern(178, 22, math.radians(32), 22, pairs=3)

    middle = [
        # leafy C-scroll filling the corner
        *leafy_scroll(46, 46, 22, 1.0, math.radians(225), 1, 4.6, 0.9, leaves=6, leaf_len=14),
        # one broad leaf on the diagonal pointing into the page
        simple_leaf(52, 52, math.radians(45), 34, 14),
    ]
    veins = [vein(188, 15, math.radians(-14), 46, -0.22), vein(52, 52, math.radians(45), 34)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in [(66, 28, 2), (28, 66, 2)])
    arm_d = " ".join(arm)
    vein_arm = veins[0]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 244 244"><g fill="{GOLD}">'
            f'<path d="{arm_d}"/><path d="{arm_d}" transform="matrix(0 1 1 0 0 0)"/>'
            f'<path d="{" ".join(middle)}"/>{dots}</g>'
            f'<g fill="{VEIN}" opacity="0.55"><path d="{vein_arm}"/><path d="{vein_arm}" transform="matrix(0 1 1 0 0 0)"/><path d="{veins[1]}"/></g></svg>')


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
                leaves.append(simple_leaf(x, y, a, 40 * s, 10.5 * s, 0.06 * up))
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
    (out / "corner.svg").write_text(corner())
    (out / "garland.svg").write_text(garland())
    (out / "chain.svg").write_text(chain())
    print("wrote corner.svg, garland.svg, chain.svg")
