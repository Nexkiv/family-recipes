// Shared renderer for the design prototypes. Each prototype page has the same
// data-field hooks; options switch the few behaviours that differ between them.
// Text goes in through textContent only (the real data will come from a database).

export function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  }
  node.append(...children.flat(Infinity).filter((c) => c !== null && c !== undefined && c !== false));
  return node;
}

// What the site calls the recipes' author. Her pages say "Mom", "Mother",
// "Nana Faithann" or "Mim"; the family will decide. Change it here only.
export const MOTHER = "Mother";

const field = (name) => document.querySelector(`[data-field="${name}"]`);
const fill = (name, ...nodes) => field(name)?.append(...nodes);

export async function renderRecipe({ base = "../", checkable = false, stepLabel = null } = {}) {
  const slug = new URLSearchParams(location.search).get("r") || "tzatziki";
  const r = await (await fetch(`${base}recipes/${encodeURIComponent(slug)}.json`)).json();
  const src = (p) => base + p;

  document.title = `${r.title} | Karatassos Family Recipes`;
  document.querySelectorAll("[data-mother]").forEach((n) => (n.textContent = MOTHER));
  fill("title", r.title);
  fill("subtitle", r.subtitle);
  fill("category", r.category);
  fill("times", ...r.times.map((t) => el("div", { class: "time" }, el("dt", { text: t.label }), el("dd", { text: t.value }))));
  fill("tags", ...r.tags.map((t) => el("li", {}, el("a", { href: "#", text: t }))));
  fill("keyPhoto", el("img", { src: src(r.keyPhoto.src), alt: r.keyPhoto.alt, width: "1050", height: "1400" }));

  const note = (text) => text && [" ", el("span", { class: "note", text: `(${text})` })];
  let n = 0;
  fill("ingredients", ...r.ingredientGroups.map((g) =>
    el("div", { class: "group" },
      g.name && el("h3", { text: g.name }),
      el("ul", {}, g.items.map((i) => {
        const body = [i.qty && el("span", { class: "qty", text: i.qty }), " ", el("span", { class: "item", text: i.item }), note(i.note)];
        if (!checkable) return el("li", {}, body);
        const id = `ing-${n++}`;
        return el("li", {}, el("input", { type: "checkbox", id }), el("label", { for: id }, body));
      }))
    )
  ));
  fill("steps", ...r.steps.map((s, i) =>
    el("li", {},
      stepLabel && el("span", { class: "step-label", text: stepLabel(i + 1) }),
      el("p", {}, s.text, note(s.note))
    )
  ));
  fill("notes", ...r.notes.map((t) => el("p", { text: t })));

  const scan = (s) => el("img", { src: src(s.src), alt: `${MOTHER}'s handwritten ${r.title} recipe, page ${s.page}`, width: "1314", height: "1700" });
  fill("scans", ...r.scans.map(scan));
  fill("printScans", ...r.scans.map(scan));
  fill("thumb", scan(r.scans[0]));
  fill("photos", r.photos.length
    ? r.photos.map((p) => el("li", {}, el("img", { src: src(p.src), alt: p.alt || "" })))
    : el("li", { class: "empty", text: "No family photos yet. Be the first to add one." }));

  wireOriginal();
  return r;
}

function wireOriginal() {
  const dialog = document.getElementById("original-dialog");
  document.querySelectorAll("[data-action=view-original]").forEach((b) => b.addEventListener("click", () => dialog.showModal()));
  document.querySelectorAll("[data-action=print-original]").forEach((b) =>
    b.addEventListener("click", () => {
      document.documentElement.classList.add("printing-original");
      addEventListener("afterprint", () => document.documentElement.classList.remove("printing-original"), { once: true });
      print();
    })
  );
}
