# Karatassos Family Recipes

Mom's handwritten recipe binder as a website: typed recipes you can search, plus her original pages to see or print.

**Live:** https://nexkiv.github.io/family-recipes/ · **Design prototypes:** https://nexkiv.github.io/family-recipes/prototypes/

CS 452 (BYU, Fall 2026) final project. [Initial design](docs/initial-design.md) · [Project log](docs/project-log.md)

| Path | What |
|---|---|
| `site/` | Static site deployed to GitHub Pages (`recipe.html?r=<slug>`; one JSON file per recipe for now) |
| `site/prototypes/` | Three design directions on the same data |
| `tools/prepare_image.py` | Rotates, optionally flattens a phone photo of a page, resizes, and strips metadata (incl. GPS) |
| `tools/simplify_corner.py` | Builds the card's corner ornaments from the family's drawing in `tools/source/` |
| `docs/` | Design doc, diagrams, log |

## Run locally

```sh
cd site && python3 -m http.server 8765   # then open http://localhost:8765
```

Image tool: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`
