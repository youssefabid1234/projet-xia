// node scripts/verifier_rendu_katex.cjs [chemin du module playwright]
// Chrome doit être installé ; aucun compte, profil élève ou modèle n'est utilisé.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const {spawnSync} = require("node:child_process");
const {chromium} = require(process.argv[2] || "playwright");
const root = path.resolve(__dirname, "..");
const python = path.join(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const fixture = spawnSync(python, ["-m", "scripts.fixture_rendu_katex"], {cwd: root, encoding: "utf8"});
assert.equal(fixture.status, 0, fixture.stderr);
const pages = JSON.parse(fixture.stdout);
const out = path.join(root, "reports", "verification-rendu-katex");
fs.mkdirSync(out, {recursive: true});
const server = http.createServer((req, res) => {
  if (pages[req.url]) {
    res.writeHead(200, {"Content-Type": "text/html; charset=utf-8"});
    return res.end(pages[req.url]);
  }
  const assets = {"/static/colle.css": "text/css", "/static/colle.js": "application/javascript"};
  if (assets[req.url]) {
    res.writeHead(200, {"Content-Type": assets[req.url]});
    return res.end(fs.readFileSync(path.join(root, "app/web", req.url)));
  }
  res.writeHead(404).end();
});

(async () => {
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({channel: "chrome", headless: true});
    const results = [];
    for (const width of [1280, 390]) {
      for (const route of Object.keys(pages)) {
        const page = await browser.newPage({viewport: {width, height: 1000}});
        const errors = [];
        page.on("pageerror", err => errors.push(err.message));
        await page.goto(base + route);
        await page.waitForFunction(() => document.querySelectorAll(".katex").length === 5);
        await page.evaluate(() => document.fonts.ready);
        assert.equal(await page.locator(".katex-error").count(), 0);
        assert.equal(await page.locator("#math-warning").isVisible(), false);
        assert.equal(await page.evaluate(() => Boolean(window.injection)), false);
        assert.deepEqual(errors, []);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
        const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.family.startsWith("KaTeX") && f.status === "loaded").length);
        assert.ok(fonts > 0, "Les polices KaTeX doivent être chargées.");
        await page.screenshot({path: path.join(out, `${route.slice(1)}-${width}.png`), fullPage: true});
        results.push({route, width, formules: 5, fonts, erreurs: errors});
        await page.close();
      }
    }
    const fallback = await browser.newPage();
    await fallback.route("https://cdn.jsdelivr.net/**", route => route.abort());
    await fallback.goto(base + "/chat");
    assert.equal(await fallback.locator("#math-warning").isVisible(), true);
    assert.ok((await fallback.locator(".md").innerText()).includes("\\(\\frac{1}{n^2}\\)"));
    fs.writeFileSync(path.join(out, "resultats.json"), JSON.stringify({results, cdn_indisponible: "texte lisible et avertissement visible"}, null, 2));
    console.log("KaTeX : 2 formats vérifiés, 5 formules par page, polices chargées, aucun débordement ; repli hors réseau vérifié.");
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
