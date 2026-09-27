// [lane B] Affichage du tableau vérifié (✓ / ✗ / ?) dans #board-panel.
(() => {
  const PERIODE_MS = 500;
  const panneau = document.getElementById("board-panel");
  if (!panneau) return;

  const style = document.createElement("style");
  style.textContent = `
    #board-panel .bp-entete { display: flex; align-items: baseline; gap: .75rem; margin-bottom: .5rem; }
    #board-panel .bp-entete h2 { margin: 0; font-size: 1.1rem; }
    #board-panel .bp-etat { color: var(--doux, #666); font-size: .85rem; }
    #board-panel .bp-etat.bp-erreur { color: var(--erreur, #b00020); }
    #board-panel .bp-image { display: block; width: 100%; max-height: 55vh; object-fit: contain; object-position: left top;
      background: #fff; border: 1px solid var(--trait, #ddd); border-radius: 6px; }
    #board-panel .bp-vide { color: var(--doux, #888); font-style: italic; }
    #board-panel ol { list-style: none; margin: .75rem 0 0; padding: 0; display: grid; gap: .35rem; }
    #board-panel li { display: grid; grid-template-columns: 2.2rem 1.6rem 1fr; align-items: start; gap: .5rem;
      padding: .35rem .5rem; border-radius: 6px; }
    #board-panel .bp-n { color: var(--doux, #888); font-variant-numeric: tabular-nums; }
    #board-panel .bp-badge { display: inline-grid; place-items: center; width: 1.5rem; height: 1.5rem; border-radius: 50%;
      color: #fff; font-weight: 700; font-size: .9rem; }
    #board-panel .bp-ok .bp-badge { background: #1b873f; }
    #board-panel .bp-faux { background: var(--erreur-pale, #fdecee); }
    #board-panel .bp-faux .bp-badge { background: #c62828; }
    #board-panel .bp-inconnu .bp-badge { background: #9e9e9e; }
    #board-panel .bp-texte { font-family: ui-monospace, Consolas, monospace; font-size: .95rem; overflow-wrap: anywhere; }
    #board-panel .bp-barre .bp-texte { text-decoration: line-through; color: var(--doux, #888); }
    #board-panel .bp-detail { display: block; font-family: system-ui, sans-serif; font-size: .85rem; color: var(--erreur, #c62828); margin-top: .15rem; }
    #board-panel .bp-flash { animation: bp-flash 0.6s ease-in-out 4; }
    @keyframes bp-flash { 50% { background: rgba(229, 57, 53, .45); } }
  `;
  document.head.appendChild(style);

  panneau.innerHTML = `
    <div class="bp-entete"><h2>Tableau</h2><span class="bp-etat"></span></div>
    <img class="bp-image" alt="Dernier tableau reçu" hidden>
    <p class="bp-vide">Rien d'écrit pour l'instant.</p>
    <ol></ol>`;
  const etatEl = panneau.querySelector(".bp-etat");
  const image = panneau.querySelector(".bp-image");
  const vide = panneau.querySelector(".bp-vide");
  const liste = panneau.querySelector("ol");

  const BADGES = { ok: ["bp-ok", "✓", "juste"], faux: ["bp-faux", "✗", "fausse"], "?": ["bp-inconnu", "?", "non vérifiée"] };
  let dernierRendu = "";
  let fauxPrecedents = new Set();
  let derniereMaj = null;

  function rendreLignes(lignes) {
    const faux = new Set();
    liste.replaceChildren(...lignes.map(l => {
      const [classe, symbole, titre] = BADGES[l.verdict] || BADGES["?"];
      const li = document.createElement("li");
      li.className = classe + (l.barre ? " bp-barre" : "");
      li.innerHTML = `<span class="bp-n">L${l.n}</span><span class="bp-badge" title="${titre}"></span><span class="bp-texte"></span>`;
      li.querySelector(".bp-badge").textContent = symbole;
      const texte = li.querySelector(".bp-texte");
      texte.textContent = l.texte;
      if (l.verdict === "faux") {
        faux.add(l.texte);
        if (l.detail) {
          const detail = document.createElement("span");
          detail.className = "bp-detail";
          detail.textContent = l.detail;
          texte.appendChild(detail);
        }
        // Clignote si la ligne vient de devenir fausse.
        if (!fauxPrecedents.has(l.texte)) li.classList.add("bp-flash");
      }
      return li;
    }));
    fauxPrecedents = faux;
    vide.hidden = lignes.length > 0 || !image.hidden;
  }

  function rendreEtat(etat) {
    let texte = "";
    if (etat.lecture_en_cours) texte = "lecture…";
    else if (derniereMaj) texte = `mis à jour il y a ${Math.max(0, Math.round(Date.now() / 1000 - derniereMaj))} s`;
    if (etat.erreur) texte = etat.erreur;
    etatEl.textContent = texte;
    etatEl.classList.toggle("bp-erreur", Boolean(etat.erreur));
  }

  async function sonder() {
    try {
      const r = await fetch("/api/board/state", { cache: "no-store" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const etat = await r.json();
      derniereMaj = etat.updated_at;

      if (etat.image_url) {
        if (image.getAttribute("src") !== etat.image_url) image.src = etat.image_url;
        image.hidden = false;
      } else {
        image.hidden = true;
        image.removeAttribute("src");
      }

      const rendu = JSON.stringify(etat.lines);
      if (rendu !== dernierRendu) {
        dernierRendu = rendu;
        rendreLignes(etat.lines);
      }
      vide.hidden = etat.lines.length > 0 || Boolean(etat.image_url);
      rendreEtat(etat);
    } catch (err) {
      etatEl.textContent = "serveur injoignable";
      etatEl.classList.add("bp-erreur");
    } finally {
      setTimeout(sonder, PERIODE_MS);
    }
  }

  sonder();
})();
