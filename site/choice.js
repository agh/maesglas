"use strict";

(() => {
  let choice = null;
  try {
    choice = localStorage.getItem("maesglas-appearance");
  } catch (error) {
    if (!(error instanceof DOMException)) throw error;
    document.documentElement.dataset.storageUnavailable = "true";
  }
  const theme =
    choice === "chalk" || choice === "shale"
      ? choice
      : matchMedia("(prefers-color-scheme: dark)").matches
        ? "shale"
        : "chalk";
  document.documentElement.dataset.theme = theme;
})();
