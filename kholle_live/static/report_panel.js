// [lane C] Compte-rendu : dès que la khôlle est finie, il s'affiche en plein écran
// par-dessus la page. Sondage toutes les 0,5 s de /api/report/status ; si personne
// n'a lancé la rédaction, POST /api/report (idempotent côté serveur).
(() => {
  const PERIODE_MS = 500;
  const ESSAIS_MAX = 3;
  const panneau = document.getElementById("report-panel");

  const style = document.createElement("style");
  style.textContent = `
    #cr-voile { position: fixed; inset: 0; z-index: 1000; display: none; flex-direction: column;
      background: #fbfaf6; }
    #cr-voile.ouvert { display: flex; }
    #cr-barre { display: flex; align-items: center; gap: 12px; padding: 10px 16px;
      background: #1d2230; color: #fbfaf6; font: 600 15px/1.2 system-ui, sans-serif; }
    #cr-barre span { flex: 1; }
    #cr-barre button { font: inherit; padding: 6px 16px; border-radius: 6px; border: 1px solid #fbfaf6;
      background: transparent; color: inherit; cursor: pointer; }
    #cr-barre button:hover { background: #fbfaf6; color: #1d2230; }
    #cr-cadre { flex: 1; border: 0; width: 100%; }
    #cr-attente { flex: 1; display: grid; place-items: center; font: 20px/1.4 Georgia, serif; color: #5d6475; }
  `;
  document.head.appendChild(style);

  const voile = document.createElement("div");
  voile.id = "cr-voile";
  voile.innerHTML = `
    <div id="cr-barre"><span>Compte-rendu de khôlle</span><button type="button">Fermer</button></div>
    <div id="cr-attente">Le khôlleur rédige votre compte-rendu…</div>
    <iframe id="cr-cadre" title="Compte-rendu de khôlle" hidden></iframe>`;
  document.body.appendChild(voile);
  const attente = voile.querySelector("#cr-attente");
  const cadre = voile.querySelector("#cr-cadre");

  let fermee = null;    // session dont l'utilisateur a fermé le compte-rendu
  let affichee = null;  // session dont le compte-rendu est chargé dans le cadre
  let demandee = null;  // session pour laquelle on a lancé la rédaction
  let essais = 0;

  function ouvrir() { voile.classList.add("ouvert"); }

  voile.querySelector("button").addEventListener("click", () => {
    voile.classList.remove("ouvert");
    fermee = affichee || demandee;
    if (panneau && affichee) {
      panneau.innerHTML = "";
      const bouton = document.createElement("button");
      bouton.type = "button";
      bouton.textContent = "Revoir le compte-rendu";
      bouton.addEventListener("click", ouvrir);
      panneau.appendChild(bouton);
    }
  });

  function rediger(id) {
    demandee = id;
    essais += 1;
    fetch("/api/report", { method: "POST" })
      .then((r) => { if (!r.ok) throw new Error(r.status); })
      .catch(() => {
        if (essais < ESSAIS_MAX) demandee = null;  // le prochain tour relance
        else attente.textContent = "Le compte-rendu n'a pas pu être rédigé.";
      });
  }

  async function tour() {
    try {
      const st = await (await fetch("/api/report/status", { cache: "no-store" })).json();
      if (!st.finished || st.session_id === fermee) return;
      if (st.pret) {
        if (affichee !== st.session_id) {
          affichee = st.session_id;
          cadre.src = `/api/report/latest?session=${encodeURIComponent(st.session_id)}`;
          cadre.hidden = false;
          attente.hidden = true;
          ouvrir();
        }
        return;
      }
      if (demandee !== st.session_id) {
        if (demandee !== null) essais = 0;  // nouvelle session
        attente.hidden = false;
        cadre.hidden = true;
        ouvrir();
        if (!st.en_cours) rediger(st.session_id);
        else demandee = st.session_id;
      }
    } catch (e) {
      // serveur momentanément injoignable : on réessaie au prochain tour
    }
  }

  setInterval(tour, PERIODE_MS);
  tour();
})();
