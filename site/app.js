"use strict";

async function start() {
  const response = await fetch("data.json");
  if (!response.ok) throw new Error("The specimen data could not be loaded.");
  const data = await response.json();
  const root = document.documentElement;
  const themeButton = document.getElementById("theme");
  const scene = document.getElementById("scene");
  const dialog = document.getElementById("shortcuts");
  const enabled = document.getElementById("shortcuts-enabled");
  const notice = document.getElementById("storage-notice");
  let explicitChoice = false;

  function storageFailure() {
    notice.hidden = false;
    notice.textContent =
      "Browser storage is unavailable. Your choices apply here but will not persist.";
  }

  function save(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      if (!(error instanceof DOMException)) throw error;
      storageFailure();
    }
  }

  try {
    enabled.checked = localStorage.getItem("maesglas-shortcuts") !== "off";
    const choice = localStorage.getItem("maesglas-appearance");
    explicitChoice = choice === "chalk" || choice === "shale";
  } catch (error) {
    if (!(error instanceof DOMException)) throw error;
    storageFailure();
  }
  if (root.dataset.storageUnavailable) storageFailure();

  function paint() {
    const mode = root.dataset.theme;
    const selected = data.scenes[scene.value];
    const plate = document.getElementById("plate");
    plate.src = `specimens/${mode}/${scene.value}.svg`;
    plate.width = selected.width;
    plate.height = selected.height;
    plate.alt = `${selected.title}. Synthetic ${mode === "chalk" ? "light" : "dark"} terminal drawing; plain text follows.`;
    document.getElementById("plain").textContent = selected.plain;
    themeButton.textContent = mode === "chalk" ? "Use Shale" : "Use Chalk";
    for (const element of document.querySelectorAll("[data-color]")) {
      element.textContent = data.colors[mode][element.dataset.color];
    }
  }

  function toggleTheme() {
    root.dataset.theme = root.dataset.theme === "chalk" ? "shale" : "chalk";
    explicitChoice = true;
    save("maesglas-appearance", root.dataset.theme);
    paint();
  }

  const shortcuts = [
    { key: "h", label: "Open help", run: () => dialog.showModal() },
    { key: "d", label: "Switch Chalk and Shale", run: toggleTheme },
    {
      key: "l",
      label: "Go home",
      run: () => {
        if (dialog.open) dialog.close();
        location.hash = "main";
        document.getElementById("main").focus();
      },
    },
    { key: "Escape", label: "Close help", run: () => dialog.close() },
  ];
  for (const shortcut of shortcuts) {
    const key = document.createElement("dt");
    key.textContent = shortcut.key === "Escape" ? "Esc" : shortcut.key;
    const description = document.createElement("dd");
    description.textContent = shortcut.label;
    document.getElementById("shortcut-list").append(key, description);
  }

  document.addEventListener("keydown", (event) => {
    if (
      event.defaultPrevented ||
      event.repeat ||
      event.isComposing ||
      event.altKey ||
      event.ctrlKey ||
      event.metaKey ||
      event.shiftKey
    )
      return;
    if (
      event.target instanceof Element &&
      event.target.closest(
        "input, textarea, select, [contenteditable]:not([contenteditable=false])",
      )
    )
      return;
    if (!enabled.checked && event.key !== "Escape") return;
    const shortcut = shortcuts.find((entry) => entry.key === event.key);
    if (shortcut) {
      event.preventDefault();
      shortcut.run();
    }
  });

  themeButton.addEventListener("click", toggleTheme);
  document
    .getElementById("help")
    .addEventListener("click", () => dialog.showModal());
  document
    .getElementById("close-help")
    .addEventListener("click", () => dialog.close());
  enabled.addEventListener("change", () =>
    save("maesglas-shortcuts", enabled.checked ? "on" : "off"),
  );
  scene.addEventListener("change", paint);
  matchMedia("(prefers-color-scheme: dark)").addEventListener(
    "change",
    (event) => {
      if (!explicitChoice) {
        root.dataset.theme = event.matches ? "shale" : "chalk";
        paint();
      }
    },
  );
  paint();
}

start().catch((error) => {
  const notice = document.getElementById("storage-notice");
  notice.hidden = false;
  notice.textContent =
    "The interactive specimens could not load. The static specimen remains available.";
  console.error(error);
});
