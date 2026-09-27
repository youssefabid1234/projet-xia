// node scripts/verifier_modalites.cjs [chemin du module playwright]
// Fournisseurs simulés ; vrai DOM, dessin, microphone Chrome et AudioWorklet.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const {spawnSync} = require("node:child_process");
const {chromium} = require(process.argv[2] || "playwright");
const root = path.resolve(__dirname, "..");
const python = path.join(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const rendu = spawnSync(python, ["-m", "scripts.fixture_modalites"], {cwd: root, encoding: "utf8"});
assert.equal(rendu.status, 0, rendu.stderr);
const fixture = JSON.parse(rendu.stdout);
const journal = [], erreurs = [], resultats = [];
let delai = 0, disponible = true, prochainTexte = "Texte transcrit.", donnees;
const wav = Buffer.alloc(4844);
wav.write("RIFF"); wav.writeUInt32LE(wav.length - 8, 4); wav.write("WAVEfmt ", 8);
wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22);
wav.writeUInt32LE(24000, 24); wav.writeUInt32LE(48000, 28); wav.writeUInt16LE(2, 32);
wav.writeUInt16LE(16, 34); wav.write("data", 36); wav.writeUInt32LE(4800, 40);
const server = http.createServer(async (req, res) => {
  if (req.url === "/") { res.setHeader("Content-Type", "text/html; charset=utf-8"); return res.end(fixture.html); }
  if (/^\/static\/(colle\.(css|js)|modalites\.js|tableau\.js|micro-worklet\.js)$/.test(req.url)) {
    res.setHeader("Content-Type", req.url.endsWith(".css") ? "text/css" : "application/javascript");
    return res.end(fs.readFileSync(path.join(root, "app/web", req.url)));
  }
  res.setHeader("Content-Type", "application/json");
  if (req.url === "/api/modalites") return res.end(JSON.stringify({manuscrit: disponible, dictee: disponible, lecture: disponible}));
  if (req.url === "/api/etat") return res.end(JSON.stringify(donnees));
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const body = Buffer.concat(chunks);
  journal.push({url: req.url, body, headers: req.headers});
  if (req.url === "/api/modalites/lecture") {
    res.setHeader("Content-Type", "audio/wav"); return res.end(wav);
  }
  if (req.url === "/api/modalites/manuscrit" || req.url === "/api/modalites/dictee") {
    const texte = prochainTexte;
    return setTimeout(() => res.end(JSON.stringify({texte})), delai);
  }
  if (req.url === "/api/message") {
    const {message} = JSON.parse(body);
    donnees.messages.push({role: "eleve", texte: message});
    const question = "Consigne suivante déjà révélée.";
    donnees.etat.tache.question_active = question;
    donnees.etat.tache.etape_resolution = 1;
    res.setHeader("Content-Type", "application/x-ndjson");
    res.write(JSON.stringify({type: "texte", texte: "Correction affichée, jamais lue."}) + "\n");
    return setTimeout(() => res.end(JSON.stringify({type: "etat", etat: donnees.etat}) + "\n"), 250);
  }
  if (req.url === "/api/bilan") {
    donnees.etat.terminee = true;
    res.setHeader("Content-Type", "application/x-ndjson");
    return res.end(JSON.stringify({type: "texte", texte: "Bilan privé de lecture."}) + "\n" +
      JSON.stringify({type: "etat", etat: donnees.etat}) + "\n");
  }
  res.statusCode = 404; res.end("{}");
});
const messages = () => journal.filter(r => r.url === "/api/message");
const conversions = () => journal.filter(r => /manuscrit|dictee/.test(r.url));
const lectures = () => journal.filter(r => r.url === "/api/modalites/lecture");

(async () => {
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const browser = await chromium.launch({channel: "chrome", headless: true,
    args: ["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream", "--autoplay-policy=no-user-gesture-required"]});
  try {
    async function pageNeuve(width = 1280) {
      journal.length = 0; delai = 0; disponible = true; prochainTexte = "Texte transcrit.";
      donnees = structuredClone(fixture.donnees);
      const page = await browser.newPage({viewport: {width, height: 1000}});
      page.on("pageerror", e => erreurs.push(e.message));
      // Suite fonctionnelle hors CDN ; le vrai rendu est vérifié séparément.
      await page.route("https://cdn.jsdelivr.net/**", route => route.abort());
      await page.goto(`http://127.0.0.1:${server.address().port}`);
      await page.waitForFunction(() => !document.querySelector('[data-modalite="manuscrit"]').disabled);
      return page;
    }
    async function dessiner(page) {
      await page.click('[data-modalite="manuscrit"]');
      const rect = await page.locator("#tableau").boundingBox();
      await page.mouse.move(rect.x + 25, rect.y + 25); await page.mouse.down();
      await page.mouse.move(rect.x + 130, rect.y + 70, {steps: 12}); await page.mouse.up();
    }
    let page = await pageNeuve();
    assert.equal(lectures().length, 0);
    await page.fill("#message", "Clavier seul");
    await page.evaluate(() => { envoyer(); envoyer(); });
    await page.waitForFunction(() => !occupe);
    assert.equal(messages().length, 1);
    assert.deepEqual(JSON.parse(messages()[0].body), {message: "Clavier seul"});
    assert.equal(conversions().length, 0);
    resultats.push("Clavier par défaut, un seul POST même avec double soumission");
    await page.close();

    page = await pageNeuve();
    await dessiner(page);
    await page.waitForTimeout(1700);
    assert.equal(conversions().length, 0);
    await page.click("#tableau-transcrire");
    await page.waitForFunction(() => document.querySelector("#message").value === "Texte transcrit.");
    assert.equal(messages().length, 0);
    assert.equal(conversions().length, 1);
    assert.equal(conversions()[0].body.subarray(1, 4).toString(), "PNG");
    await page.click("#envoyer"); await page.waitForFunction(() => !occupe);
    assert.equal(messages().length, 1);
    assert.deepEqual(JSON.parse(messages()[0].body), {message: "Texte transcrit."});
    resultats.push("Manuscrit : aucun envoi après pause, PNG sur demande, brouillon puis envoi unique");
    await page.close();

    page = await pageNeuve();
    delai = 600;
    await dessiner(page); await page.click("#tableau-transcrire");
    await page.fill("#message", "Brouillon modifié");
    await page.waitForFunction(() => document.querySelector("#modalites-statut").textContent.includes("écartée"));
    assert.equal(await page.inputValue("#message"), "Brouillon modifié");
    await page.click("#tableau-transcrire");
    await page.click("#modalite-annuler");
    await page.waitForTimeout(700);
    assert.equal(await page.inputValue("#message"), "Brouillon modifié");
    assert.equal(messages().length, 0);
    resultats.push("Brouillon modifié et annulation : résultat tardif écarté sans envoi");
    await page.close();

    page = await pageNeuve();
    delai = 500;
    await dessiner(page); await page.click("#tableau-transcrire");
    await page.evaluate(() => {
      const etat = structuredClone(donnees.etat);
      etat.tache.question_active = "Autre question"; majEtat(etat);
    });
    await page.waitForTimeout(600);
    assert.equal(await page.inputValue("#message"), "");
    assert.equal(messages().length, 0);
    resultats.push("Changement de question pendant transcription : ancien résultat ignoré");
    await page.close();

    page = await pageNeuve();
    await page.evaluate(() => {
      navigator.mediaDevices.getUserMedia = async () => { throw new DOMException("Refus", "NotAllowedError"); };
    });
    await page.click('[data-modalite="dictee"]'); await page.click("#dicter");
    await page.waitForFunction(() => document.querySelector("#modalites-statut").textContent.includes("Micro refusé"));
    await page.fill("#message", "Réponse au clavier après refus du micro");
    await page.click("#envoyer"); await page.waitForFunction(() => !occupe);
    assert.equal(messages().length, 1); assert.equal(conversions().length, 0);
    resultats.push("Micro refusé : aucune soumission audio, clavier immédiatement utilisable");
    await page.close();

    page = await pageNeuve();
    await dessiner(page); await page.fill("#message", "Brouillon conservé");
    await page.route("**/api/modalites/manuscrit", route => route.abort());
    await page.click("#tableau-transcrire");
    await page.waitForFunction(() => document.querySelector("#modalite-annuler").hidden);
    assert.equal(await page.inputValue("#message"), "Brouillon conservé");
    await page.click("#envoyer"); await page.waitForFunction(() => !occupe);
    assert.equal(messages().length, 1);
    resultats.push("Erreur réseau de conversion : brouillon conservé et clavier utilisable");
    await page.close();

    page = await pageNeuve();
    await page.click('[data-modalite="dictee"]'); await page.click("#dicter");
    await page.waitForFunction(() => !document.querySelector("#dictee-fin").hidden);
    await page.waitForTimeout(500);
    assert.equal(conversions().length, 0);
    await page.click("#dictee-fin");
    await page.waitForFunction(() => document.querySelector("#message").value === "Texte transcrit.");
    assert.equal(conversions().length, 1);
    const audio = conversions()[0].body;
    assert.equal(audio.subarray(0, 4).toString(), "RIFF");
    assert.equal(audio.readUInt32LE(24), 24000); assert.equal(audio.readUInt16LE(22), 1);
    assert.ok(audio.length > 4800);
    assert.equal(messages().length, 0);
    await page.click("#envoyer"); await page.waitForFunction(() => !occupe);
    assert.equal(messages().length, 1);
    resultats.push("Micro Chrome + AudioWorklet : WAV mono 24 kHz final, aucun fragment réseau ni envoi implicite");
    await page.close();

    page = await pageNeuve();
    await page.click("#lecture-audio");
    await page.waitForTimeout(300);
    assert.equal(lectures().length, 1);
    assert.equal(JSON.parse(lectures()[0].body).question, fixture.donnees.etat.tache.question_active);
    await page.fill("#message", "Ma réponse"); await page.click("#envoyer");
    await page.waitForFunction(() => document.querySelector("#fil").textContent.includes("Correction affichée"));
    assert.equal(await page.evaluate(() => occupe), true); // rendu pendant le flux
    await page.waitForFunction(() => !occupe);
    await page.waitForTimeout(300);
    assert.deepEqual(lectures().map(r => JSON.parse(r.body).question),
      [fixture.donnees.etat.tache.question_active, "Consigne suivante déjà révélée."]);
    await page.evaluate(() => majEtat(donnees.etat)); await page.waitForTimeout(100);
    assert.equal(lectures().length, 2);
    await page.evaluate(() => terminer(true));
    assert.equal(lectures().length, 2);
    resultats.push("Audio : consignes publiques seules, étape révélée sans doublon, correction et bilan exclus, diffusion progressive intacte");
    await page.reload();
    await page.waitForTimeout(150);
    assert.equal(lectures().length, 2);
    assert.equal(await page.getAttribute("#lecture-audio", "aria-pressed"), "false");
    resultats.push("Rechargement : audio désactivé, aucune relecture de l’historique");
    await page.close();

    page = await pageNeuve();
    delai = 700;
    await dessiner(page); await page.click("#tableau-transcrire");
    await page.evaluate(() => { finMinuteur = Date.now() - 1000; tic(); });
    await page.waitForFunction(() => donnees.etat.terminee);
    await page.waitForTimeout(800);
    assert.equal(await page.inputValue("#message"), "");
    assert.equal(messages().length, 0);
    assert.equal(journal.filter(r => r.url === "/api/bilan").length, 1);
    resultats.push("Expiration pendant conversion : bilan normal, résultat ignoré, aucun délai ajouté au chronomètre");
    await page.close();

    page = await pageNeuve(390);
    await dessiner(page);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    const dossier = path.join(root, "reports/verification-modalites");
    fs.mkdirSync(dossier, {recursive: true});
    await page.screenshot({path: path.join(dossier, "manuscrit-mobile.png"), fullPage: true});
    await page.close();

    page = await pageNeuve();
    await page.route("**/api/modalites", route => route.fulfill({json: {manuscrit: false, dictee: false, lecture: false}}));
    await page.reload();
    await page.waitForFunction(() => document.querySelector("#modalites-statut").textContent.includes("indisponibles"));
    await page.fill("#message", "Repli clavier"); await page.click("#envoyer");
    await page.waitForFunction(() => !occupe);
    assert.equal(messages().length, 1); assert.equal(conversions().length, 0);
    resultats.push("Mobile sans débordement ; services optionnels absents : clavier fonctionnel");
    await page.close();
    assert.deepEqual(erreurs, []);
    fs.writeFileSync(path.join(dossier, "resultats.json"), JSON.stringify({resultats, erreurs}, null, 2));
    console.log(resultats.join("\n"));
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
