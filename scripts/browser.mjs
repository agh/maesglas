import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createServer } from "node:http";
import { mkdir, readFile, unlink, writeFile } from "node:fs/promises";
import { extname, resolve, sep } from "node:path";
import { chromium } from "@playwright/test";

const root = resolve("site");
const captures = resolve(".cache/visual");
await mkdir(captures, { recursive: true });
const types = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "text/javascript",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".otf": "font/otf",
};
const server = createServer(async (request, response) => {
  const pathname = new URL(request.url, "http://localhost").pathname;
  const path = resolve(root, `.${pathname === "/" ? "/index.html" : pathname}`);
  if (!path.startsWith(root + sep)) {
    response.writeHead(403).end();
    return;
  }
  try {
    const body = await readFile(path);
    response.writeHead(200, {
      "Content-Type": types[extname(path)] || "text/plain",
    });
    response.end(body);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    response.writeHead(404).end();
  }
});
await new Promise((accept) => server.listen(0, "localhost", accept));
const origin = `http://localhost:${server.address().port}`;
const browser = await chromium.launch({
  executablePath: chromium.executablePath(),
});
const lock = JSON.parse(await readFile("tools.lock", "utf8"));
const data = JSON.parse(await readFile("site/data.json", "utf8"));
assert.equal(browser.version(), lock.chromium);
const context = await browser.newContext({
  viewport: { width: 1280, height: 1000 },
  colorScheme: "light",
  reducedMotion: "reduce",
});
const page = await context.newPage();
const errors = [];
const requests = [];
page.on("pageerror", (error) => errors.push(error.message));
page.on("request", (request) => requests.push(request.url()));

async function settled() {
  await page.waitForFunction(() => {
    const plate = document.querySelector("#plate");
    return plate.complete && plate.naturalWidth === Number(plate.width);
  });
  await page.evaluate(() => document.fonts.ready);
}

try {
  await page.goto(origin);
  await settled();
  assert.equal(await page.getAttribute("html", "data-theme"), "chalk");
  assert.equal(
    await page.evaluate(() => document.fonts.check("15px CommitMono")),
    true,
  );
  const openingMeasurements = [];
  async function checkOpening(mode, viewport) {
    await page.setViewportSize(viewport);
    await page.locator("#scene").selectOption("code");
    await settled();
    await page.evaluate(() => {
      if (document.activeElement instanceof HTMLElement)
        document.activeElement.blur();
      window.scrollTo(0, 0);
    });
    const measurement = await page.evaluate(async () => {
      const image = document.getElementById("plate");
      const box = image.getBoundingClientRect();
      const svg = new DOMParser().parseFromString(
        await (await fetch(image.src)).text(),
        "image/svg+xml",
      ).documentElement;
      svg.style.position = "absolute";
      svg.style.left = "-10000px";
      document.body.append(svg);
      const firstGlyph = svg.querySelectorAll("path")[1].getBBox();
      svg.remove();
      const canvas = document.createElement("canvas");
      const pen = canvas.getContext("2d");
      pen.font = "15px CommitMono";
      return {
        width: innerWidth,
        height: innerHeight,
        plateTop: box.top,
        plateBottom: box.bottom,
        plateWidth: box.width,
        firstGlyphTop: box.top + firstGlyph.y,
        cellWidth: pen.measureText("x").width,
        features: getComputedStyle(document.body).fontFeatureSettings,
        pageOverflow: document.documentElement.scrollWidth > innerWidth,
        overflowingElements: Array.from(document.querySelectorAll("body *"))
          .filter((element) => {
            const rect = element.getBoundingClientRect();
            return (
              rect.width &&
              rect.right > innerWidth + 1 &&
              !element.closest(".table-scroll, .plate-scroll, pre")
            );
          })
          .map((element) => element.outerHTML.slice(0, 180))
          .slice(0, 8),
      };
    });
    assert.equal(measurement.cellWidth, 9);
    for (const [name, value] of [
      ["calt", 1],
      ["ss01", 0],
      ["ss02", 0],
      ["liga", 0],
      ["dlig", 0],
    ]) {
      assert.match(
        measurement.features,
        new RegExp(`"${name}"${value === 1 ? "(?: 1)?" : " 0"}(?:,|$)`),
        "The site must use the same shaping features as the outlines",
      );
    }
    assert.equal(measurement.pageOverflow, false, JSON.stringify(measurement));
    assert.equal(measurement.plateWidth, data.scenes.code.width);
    if (viewport.width === 390) {
      assert(
        measurement.firstGlyphTop < viewport.height - 120,
        "Phone opening must show several lines of the specimen, not only its frame",
      );
    } else {
      assert(
        measurement.plateBottom <= viewport.height,
        "Laptop opening must show the complete specimen",
      );
    }
    assert.equal(await page.locator("footer #help").count(), 1);
    assert.equal(
      await page.locator("#scene option:checked").textContent(),
      "Python",
    );
    openingMeasurements.push({ mode, ...measurement });
    await page.screenshot({
      path: `${captures}/opening-${mode}-${viewport.width}x${viewport.height}.png`,
    });
  }
  await checkOpening("chalk", { width: 390, height: 844 });
  await checkOpening("chalk", { width: 1512, height: 982 });
  assert.deepEqual(
    await page.evaluate(() =>
      Array.from(document.fonts)
        .map((face) => [face.family, face.weight, face.status])
        .sort((a, b) => a[1].localeCompare(b[1])),
    ),
    [
      ["CommitMono", "400", "loaded"],
      ["CommitMono", "700", "loaded"],
    ],
  );
  await page.keyboard.press("Tab");
  assert.equal(await page.locator(":focus").textContent(), "Skip to content");
  assert.equal(
    await page
      .locator(":focus")
      .evaluate((el) => getComputedStyle(el).outlineStyle),
    "solid",
  );
  await page.keyboard.press("Enter");
  assert.equal(await page.locator(":focus").getAttribute("id"), "main");
  await page.keyboard.press("d");
  assert.equal(await page.getAttribute("html", "data-theme"), "shale");
  await page.reload();
  await settled();
  assert.equal(await page.getAttribute("html", "data-theme"), "shale");
  await page.keyboard.press("d");
  await page.emulateMedia({ colorScheme: "dark" });
  await page.reload();
  await settled();
  assert.equal(await page.getAttribute("html", "data-theme"), "chalk");

  await page.locator("#help").click();
  assert.equal(
    await page.locator("#shortcuts").evaluate((el) => el.open),
    true,
  );
  assert.equal(await page.locator("#shortcut-list dt").count(), 4);
  await page.keyboard.press("Escape");
  assert.equal(await page.locator(":focus").getAttribute("id"), "help");
  await page.keyboard.press("h");
  await page.locator("#shortcuts-enabled").uncheck();
  await page.locator("#close-help").click();
  await page.reload();
  await settled();
  await page.keyboard.press("d");
  assert.equal(await page.getAttribute("html", "data-theme"), "chalk");
  await page.locator("#help").click();
  await page.locator("#shortcuts-enabled").check();
  await page.locator("#close-help").click();
  await page.locator("#scene").focus();
  await page.keyboard.press("d");
  assert.equal(await page.getAttribute("html", "data-theme"), "chalk");
  await page.evaluate(() => {
    const input = document.createElement("textarea");
    input.id = "typing-probe";
    document.body.append(input);
    input.focus();
  });
  await page.keyboard.type("dhl");
  assert.equal(await page.getAttribute("html", "data-theme"), "chalk");
  await page.locator("#typing-probe").evaluate((el) => el.remove());
  await page.locator("#main").focus();
  await page.keyboard.press("Shift+D");
  await page.evaluate(() =>
    document.dispatchEvent(
      new KeyboardEvent("keydown", { key: "d", repeat: true }),
    ),
  );
  assert.equal(await page.getAttribute("html", "data-theme"), "chalk");

  for (const mode of ["chalk", "shale"]) {
    if ((await page.getAttribute("html", "data-theme")) !== mode) {
      await page.locator("#theme").click();
    }
    await checkOpening(mode, { width: 390, height: 844 });
    await checkOpening(mode, { width: 1512, height: 982 });
    const guidanceLinks = await page.locator("main a").evaluateAll((anchors) =>
      anchors.map((anchor) => ({
        href: anchor.getAttribute("href"),
        download: anchor.hasAttribute("download"),
      })),
    );
    for (const link of guidanceLinks) {
      if (link.href.startsWith("#")) {
        assert.equal(
          await page.locator(`[id="${link.href.slice(1)}"]`).count(),
          1,
          `Broken or ambiguous guidance target: ${link.href}`,
        );
      }
      if (link.href.endsWith(".md")) assert.equal(link.download, true);
    }
    await page.locator("#palette a[href='#contrast']").click();
    assert.equal(await page.evaluate(() => location.hash), "#contrast");
    await page.locator("#contrast > details").evaluate((node) => {
      node.open = true;
    });
    assert.equal(await page.getAttribute("html", "data-theme"), mode);
    await page.locator("#contrast > details").evaluate((node) => {
      node.open = false;
    });
    await page.locator("#install > details").evaluateAll((details) => {
      details.forEach((node) => {
        node.open = true;
      });
    });
    assert.equal((await page.locator("#install pre").count()) >= 27, true);
    for (const scene of Object.keys(data.scenes)) {
      await page.locator("#scene").selectOption(scene);
      await page.waitForFunction(
        ({ mode, scene }) => {
          const image = document.getElementById("plate");
          return image.src.endsWith(`/${mode}/${scene}.svg`) && image.complete;
        },
        { mode, scene },
      );
      const xml = await readFile(`site/specimens/${mode}/${scene}.svg`, "utf8");
      const dimensions = {
        width: Number(xml.match(/width="(\d+)"/)[1]),
        height: Number(xml.match(/height="(\d+)"/)[1]),
      };
      const image = await browser.newPage({ viewport: dimensions });
      await image.goto(`${origin}/specimens/${mode}/${scene}.svg`);
      await image.evaluate(
        () =>
          new Promise((done) =>
            requestAnimationFrame(() => requestAnimationFrame(done)),
          ),
      );
      await image.screenshot({ path: `${captures}/${mode}-${scene}.png` });
      await image.close();
    }
    await page.locator("#scene").selectOption("code");
    await settled();
    const colorFailures = await page.evaluate(() => {
      function channels(value) {
        return value.match(/[\d.]+/g).map(Number);
      }
      function luminance(value) {
        const rgb = channels(value)
          .slice(0, 3)
          .map((v) => {
            const c = v / 255;
            return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
          });
        return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
      }
      const failures = [];
      for (const element of document.querySelectorAll("body *")) {
        if (
          !element.getClientRects().length ||
          !Array.from(element.childNodes).some(
            (node) =>
              node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
          )
        )
          continue;
        let ground = element;
        while (
          ground.parentElement &&
          getComputedStyle(ground).backgroundColor === "rgba(0, 0, 0, 0)"
        )
          ground = ground.parentElement;
        const fg = luminance(getComputedStyle(element).color);
        const bg = luminance(getComputedStyle(ground).backgroundColor);
        const ratio = (Math.max(fg, bg) + 0.05) / (Math.min(fg, bg) + 0.05);
        if (ratio < 4.5) failures.push(element.tagName);
        if (getComputedStyle(element).transitionDuration !== "0s")
          failures.push("motion");
      }
      return failures;
    });
    assert.deepEqual(colorFailures, []);
    await page.evaluate(() => {
      if (document.activeElement instanceof HTMLElement)
        document.activeElement.blur();
    });
    await page.screenshot({
      path: `${captures}/site-${mode}.png`,
      fullPage: true,
    });
    await page.locator("#install > details").evaluateAll((details) => {
      details.forEach((node) => {
        node.open = false;
      });
    });
    for (const width of [390, 768, 1280]) {
      await page.setViewportSize({ width, height: 900 });
      await page.screenshot({
        path: `${captures}/${mode}-${width}.png`,
        fullPage: true,
      });
      assert.equal(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        true,
      );
    }
    await page.screenshot({
      path: `${captures}/mobile-${mode}.png`,
      fullPage: true,
    });
    await page.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    for (const width of [390, 768, 1280]) {
      await page.setViewportSize({ width, height: 900 });
      assert.equal(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        true,
        "Text resizing must not overflow the page",
      );
    }
    await page.evaluate(() => {
      document.documentElement.style.fontSize = "";
    });
  }
  assert.equal(errors.length, 0, errors.join("\n"));
  assert(
    requests.every((url) => url.startsWith(origin + "/")),
    "Third-party request",
  );
  await writeFile(
    `${captures}/opening-measurements.json`,
    JSON.stringify(openingMeasurements, null, 2) + "\n",
  );
  const downloadContext = await browser.newContext();
  const downloadPage = await downloadContext.newPage();
  await downloadPage.goto(`${origin}/#type`);
  const fontLink = downloadPage.locator("#type").getByRole("link", {
    name: "1.143 archive",
  });
  assert.equal(await fontLink.getAttribute("href"), data.fontArchive.url);
  const [fontDownload] = await Promise.all([
    downloadPage.waitForEvent("download"),
    fontLink.click(),
  ]);
  const fontPath = `${captures}/font-download.zip`;
  await fontDownload.saveAs(fontPath);
  assert.equal(
    createHash("sha256")
      .update(await readFile(fontPath))
      .digest("hex"),
    data.fontArchive.sha256,
    "The font link must download the pinned upstream archive",
  );
  await unlink(fontPath);
  await downloadContext.close();
  const fresh = await browser.newContext({ colorScheme: "dark" });
  const freshPage = await fresh.newPage();
  await freshPage.goto(origin);
  assert.equal(await freshPage.getAttribute("html", "data-theme"), "shale");
  await fresh.close();

  const blocked = await browser.newContext();
  await blocked.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      get() {
        throw new DOMException("Storage is disabled", "SecurityError");
      },
    });
  });
  const blockedPage = await blocked.newPage();
  await blockedPage.goto(origin);
  await blockedPage.locator("#storage-notice").waitFor({ state: "visible" });
  await blocked.close();
  console.log(
    "PASS browser: 390x844 and 1512x982 openings, themed guidance, font download, choice, keyboard, focus, 14 plates, and local requests",
  );
} finally {
  await browser.close();
  await new Promise((accept, reject) =>
    server.close((error) => (error ? reject(error) : accept())),
  );
}
