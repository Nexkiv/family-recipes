"""Build the site's corner ornament from the family's sectioned acanthus drawing.

  python tools/simplify_corner.py tools/source/leaf-page-corner.svg site/assets/ornaments/corner.svg

Keeps the top arm and the upper part of the side arm, drops the lower side-arm
sections, and moves the bottom swept leaf up so it finishes the shorter arm.
"""
import re
import sys

KEEP = ["upper-left-scroll", "hanging-acanthus", "upper-branch", "central-scroll",
        "top-swept-leaf", "hanging-sprig"]
# pieces of central-scroll that run into the dropped sections (they'd show a flat cut)
DROP_SUBPATHS = ("M 179.914 345.264", "M 107.699 340.967")
END_LEAF = "bottom-swept-leaf"
END_LEAF_MOVE = (32, -362)      # puts its tip on the side arm's new end (y ~306)
GOLD = "#B48E67"


def sections(svg):
    out = {}
    for gid, body in re.findall(r'<g id="([^"]+)"[^>]*>(.*?)</g>', svg, re.S):
        out[gid] = re.search(r'\sd="([^"]+)"', body).group(1)
    return out


def drop_subpaths(d, starts):
    parts = re.split(r"(?<=[zZ])\s*(?=M)", d.strip())
    return " ".join(p for p in parts if not p.startswith(starts))


def main(src, dst):
    sec = sections(open(src).read())
    body = []
    for name in KEEP:
        d = sec[name]
        if name == "central-scroll":
            d = drop_subpaths(d, DROP_SUBPATHS)
        body.append(f'  <path id="{name}" d="{d}"/>')
    dx, dy = END_LEAF_MOVE
    body.append(f'  <path id="{END_LEAF}" transform="translate({dx} {dy})" d="{sec[END_LEAF]}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="44 44 556 400" fill="{GOLD}">\n'
           "  <!-- Acanthus page corner (top-left; CSS flips it for the other corners).\n"
           "       Simplified by tools/simplify_corner.py from the family's drawing of Mother's page. -->\n"
           + "\n".join(body) + "\n</svg>\n")
    open(dst, "w").write(svg)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
