// Photo upload, proof-of-concept version: checks files in the browser and shows a
// preview. Nothing is sent anywhere yet. These checks are only for quick feedback;
// the real gate will run on the server (see docs/initial-design.md).

const MAX_BYTES = 15 * 1024 * 1024;

// A file's first bytes say what it really is, whatever its name or extension claims.
const SIGNATURES = [
  { type: "JPEG", test: (b) => b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff },
  { type: "PNG", test: (b) => [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a].every((v, i) => b[i] === v) },
  { type: "WebP", test: (b) => ascii(b, 0, 4) === "RIFF" && ascii(b, 8, 12) === "WEBP" },
  { type: "HEIC", test: (b) => ascii(b, 4, 8) === "ftyp" && ["heic", "heix", "mif1", "msf1"].includes(ascii(b, 8, 12)) },
];

function ascii(bytes, start, end) {
  return String.fromCharCode(...bytes.slice(start, end));
}

async function check(file) {
  if (file.size > MAX_BYTES) {
    return { ok: false, message: `Too large (${(file.size / 1048576).toFixed(1)} MB). Photos can be up to 15 MB.` };
  }
  const head = new Uint8Array(await file.slice(0, 16).arrayBuffer());
  const match = SIGNATURES.find((s) => s.test(head));
  if (!match) {
    return { ok: false, message: "This isn't a JPEG, PNG, WebP or HEIC photo, so it can't be added." };
  }
  return { ok: true, type: match.type, message: "Looks good. Saving photos isn't switched on yet, so this preview stays on your screen only." };
}

function row(file, result) {
  const li = document.createElement("li");
  li.className = result.ok ? "queued ok" : "queued rejected";
  if (result.ok && result.type !== "HEIC") {
    // HEIC can't be previewed in most browsers; the server will convert it to JPEG.
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.alt = "";
    img.onload = () => URL.revokeObjectURL(img.src);
    li.append(img);
  }
  const text = document.createElement("div");
  const name = document.createElement("strong");
  name.textContent = file.name;
  const msg = document.createElement("span");
  msg.textContent = result.message;
  text.append(name, msg);
  li.append(text);
  return li;
}

async function handle(files) {
  const queue = document.getElementById("upload-queue");
  for (const file of files) queue.append(row(file, await check(file)));
}

const input = document.getElementById("photo-input");
const zone = document.getElementById("dropzone");

input.addEventListener("change", () => {
  handle(input.files);
  input.value = "";
});
zone.addEventListener("dragover", (e) => {
  e.preventDefault();
  zone.classList.add("dragging");
});
zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));
zone.addEventListener("drop", (e) => {
  e.preventDefault();
  zone.classList.remove("dragging");
  handle(e.dataTransfer.files);
});
