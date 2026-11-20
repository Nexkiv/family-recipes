// Renders one recipe from recipes/<slug>.json into recipe.html.
// Everything goes in through textContent/attributes, never innerHTML, because
// later the data comes from the database and from family uploads.

const slug = new URLSearchParams(location.search).get("r") || "tzatziki";

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  }
  node.append(...children.filter(Boolean));
  return node;
}

const field = (name) => document.querySelector(`[data-field="${name}"]`);
const momNote = (text) => [" ", el("span", { class: "mom-note", text })];

function render(r) {
  document.title = `${r.title} | Karatassos Family Recipes`;
  field("title").textContent = r.title;
  field("subtitle").textContent = r.subtitle || "";
  field("category").textContent = r.category;

  field("times").append(
    ...r.times.flatMap((t) => [el("dt", { text: t.label }), el("dd", { text: t.value })])
  );
  field("tags").append(...r.tags.map((tag) => el("li", { text: tag })));

  field("keyPhoto").append(
    el("img", { src: r.keyPhoto.src, alt: r.keyPhoto.alt, width: "1050", height: "1400" })
  );

  field("ingredientGroups").append(
    ...r.ingredientGroups.map((group) =>
      el("div", { class: "ingredient-group" },
        group.name && el("h3", { text: group.name }),
        el("ul", {},
          ...group.items.map((i) =>
            el("li", {},
              i.qty && el("span", { class: "qty", text: i.qty }),
              el("span", { class: "item", text: i.item }),
              ...(i.note ? momNote(i.note) : [])
            )
          )
        )
      )
    )
  );

  field("steps").append(
    ...r.steps.map((s) => el("li", {}, el("span", { text: s.text }), ...(s.note ? momNote(s.note) : [])))
  );
  field("notes").append(...r.notes.map((n) => el("p", { class: "mom-note", text: n })));

  const scanImg = (s) =>
    el("img", { src: s.src, alt: `Mom's handwritten ${r.title} recipe, page ${s.page}`, width: "1314", height: "1700" });
  field("scans").append(...r.scans.map(scanImg));
  field("printScans").append(...r.scans.map(scanImg));

  const gallery = field("photos");
  if (r.photos.length === 0) {
    gallery.append(el("li", { class: "gallery-empty", text: "No family photos yet. Be the first to add one." }));
  } else {
    gallery.append(...r.photos.map((p) => el("li", {}, el("img", { src: p.src, alt: p.alt || "", loading: "lazy" }))));
  }

  document.getElementById("recipe").removeAttribute("aria-busy");
}

function wireOriginalButtons() {
  const dialog = document.getElementById("original-dialog");
  document.getElementById("view-original").addEventListener("click", () => dialog.showModal());

  // Printing the original: a class on <html> switches the print stylesheet from
  // the typed recipe to the scanned pages, then comes off once printing is done.
  document.getElementById("print-original").addEventListener("click", () => {
    document.documentElement.classList.add("printing-original");
    window.addEventListener("afterprint", () => document.documentElement.classList.remove("printing-original"), { once: true });
    window.print();
  });
}

fetch(`recipes/${encodeURIComponent(slug)}.json`)
  .then((res) => {
    if (!res.ok) throw new Error(`No recipe called “${slug}”.`);
    return res.json();
  })
  .then((recipe) => {
    render(recipe);
    wireOriginalButtons();
  })
  .catch((err) => {
    field("title").textContent = "Recipe not found";
    field("subtitle").textContent = `${err.message} Check the link and try again.`;
    document.querySelector(".actions").hidden = true;
    document.getElementById("recipe").removeAttribute("aria-busy");
  });
