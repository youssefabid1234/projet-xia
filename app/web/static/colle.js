"use strict";

const $ = (id) => document.getElementById(id);
const csrf = document.querySelector('meta[name="csrf"]').content;
let donnees = JSON.parse($("donnees").textContent);
let occupe = false;
let finMinuteur = null;

/* ---------- Rendu : Markdown léger + formules KaTeX, sans HTML brut ---------- */

const MATH = /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^$\n]+?\$)/g;

function echapper(texte) {
  return texte.replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
}

function enLigne(texte) {
  return texte
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*\w])\*(?!\s)(.+?)\*(?!\w)/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function markdown(texte) {
  const formules = [];
  const sansMath = texte.replace(MATH, (m) => { formules.push(m); return `\u0000${formules.length - 1}\u0000`; });
  const blocs = echapper(sansMath).split(/\n{2,}/);
  const html = blocs.map((bloc) => {
    const lignes = bloc.split("\n");
    if (lignes.every((l) => /^\s*[-*•]\s+/.test(l))) {
      return "<ul>" + lignes.map((l) => "<li>" + enLigne(l.replace(/^\s*[-*•]\s+/, "")) + "</li>").join("") + "</ul>";
    }
    if (lignes.every((l) => /^\s*\d+[.)]\s+/.test(l))) {
      return "<ol>" + lignes.map((l) => "<li>" + enLigne(l.replace(/^\s*\d+[.)]\s+/, "")) + "</li>").join("") + "</ol>";
    }
    return "<p>" + lignes.map(enLigne).join("<br>") + "</p>";
  }).join("");
  return html.replace(/\u0000(\d+)\u0000/g, (_, i) => echapper(formules[Number(i)]));
}

function rendre(element, texte) {
  element.innerHTML = markdown(texte || "");
  if (window.renderMathInElement) {
    window.renderMathInElement(element, {
      delimiters: [
        {left: "$$", right: "$$", display: true}, {left: "\\[", right: "\\]", display: true},
        {left: "$", right: "$", display: false}, {left: "\\(", right: "\\)", display: false},
      ],
      throwOnError: false, trust: false,
    });
  }
}

/* ---------- Fil de discussion ---------- */

function bulle(role, texte, extra = {}, automatique = true) {
  const article = document.createElement("article");
  article.className = `msg ${role}` + (extra.bilan ? " bilan" : "");
  const auteur = document.createElement("div");
  auteur.className = "auteur";
  auteur.textContent = role === "eleve" ? "Vous" : (extra.bilan ? "Bilan de X-hôlleur" : "X-hôlleur");
  const corps = document.createElement("div");
  corps.className = "corps";
  const contenu = document.createElement("div");
  contenu.className = "md";
  corps.append(contenu);
  article.append(auteur, corps);
  rendre(contenu, texte);
  if (role === "colleur") {
    window.modalites?.affiche(contenu, texte, true, automatique);
    const relire = document.createElement("button");
    relire.type = "button"; relire.className = "bouton-secondaire";
    relire.textContent = "Relire ce message";
    relire.addEventListener("click", () => window.modalites?.relire(article));
    corps.append(relire);
  }
  if (extra.question) ajouterQuestion(article, extra.question, automatique);
  $("fil").append(article);
  return {article, contenu};
}

function ajouterQuestion(article, question, automatique = true) {
  const bloc = document.createElement("div");
  bloc.className = "question";
  const etiquette = document.createElement("div");
  etiquette.className = "etiquette";
  etiquette.textContent = question.libelle;
  const texte = document.createElement("div");
  texte.className = "md";
  bloc.append(etiquette, texte);
  article.querySelector(".corps").append(bloc);
  rendre(texte, question.texte);
  window.modalites?.affiche(etiquette, question.libelle, true, automatique);
  window.modalites?.affiche(texte, question.texte, true, automatique);
}

function statut(texte) {
  let ligne = $("statut");
  if (!texte) { ligne?.remove(); return; }
  if (!ligne) {
    ligne = document.createElement("div");
    ligne.id = "statut";
    ligne.className = "statut";
    ligne.innerHTML = '<span class="points"><i></i><i></i><i></i></span><span></span>';
    $("fil").append(ligne);
  }
  ligne.lastElementChild.textContent = texte;
  defiler();
}

function defiler() {
  window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});
}

function alerte(texte) {
  $("alerte").textContent = texte || "";
  $("alerte").hidden = !texte;
}

/* ---------- Affichage de l'état ---------- */

function afficher() {
  const enCours = Boolean(donnees.etat);
  $("accueil").hidden = enCours;
  $("colle").hidden = !enCours;
  if (!enCours) { window.modalites?.reinitialiser(); return afficherAccueil(); }
  window.modalites?.vider();
  $("fil").replaceChildren();
  for (const m of donnees.messages) bulle(m.role, m.texte, m, m === donnees.messages.at(-1));
  majEtat(donnees.etat);
  defiler();
}

function afficherAccueil() {
  const choix = $("choix-chapitres");
  choix.replaceChildren();
  for (const chapitre of donnees.chapitres) {
    const bouton = document.createElement("button");
    bouton.type = "button";
    bouton.textContent = `Commencer : ${chapitre.nom}`;
    bouton.addEventListener("click", () => demarrer(chapitre.index, bouton));
    choix.append(bouton);
  }
  if (!donnees.chapitres.length) choix.textContent = "Aucun chapitre n'est prêt pour une colle.";
  $("duree-annonce").textContent = `Durée : ${donnees.duree} minutes. Votre progression est enregistrée dans votre profil.`;
  const liste = $("anciennes-liste");
  liste.replaceChildren();
  for (const ancienne of donnees.anciennes || []) {
    const details = document.createElement("details");
    details.className = "ancienne";
    const resume = document.createElement("summary");
    const date = new Date(ancienne.debut * 1000).toLocaleString("fr-FR", {dateStyle: "medium", timeStyle: "short"});
    const note = (ancienne.bilan || "").match(/Note\s*:\s*([\d.,]+\s*\/\s*20)/i);
    resume.textContent = `${ancienne.chapitre} · ${date}` + (note ? ` · ${note[1].replace(/\s/g, "")}` : "");
    const contenu = document.createElement("div");
    contenu.className = "md";
    details.append(resume, contenu);
    details.addEventListener("toggle", () => { if (details.open && !contenu.childElementCount) rendre(contenu, ancienne.bilan); });
    liste.append(details);
  }
  $("anciennes").hidden = !(donnees.anciennes || []).length;
}

function majEtat(etat) {
  donnees.etat = etat;
  const etapes = $("etapes");
  etapes.replaceChildren();
  const ordre = etat.etapes.map((e) => e.cle);
  const abordees = new Set(etat.resultats.map((r) => r.etape));
  const position = etat.etape === "fin" ? -1 : ordre.indexOf(etat.etape);
  etat.etapes.forEach((e, i) => {
    const li = document.createElement("li");
    li.textContent = e.libelle;
    // À la fin, seules les étapes réellement abordées sont cochées.
    if (etat.etape === "fin" ? abordees.has(e.cle) : i < position) li.className = "faite";
    if (i === position) { li.className = "active"; li.setAttribute("aria-current", "step"); }
    etapes.append(li);
  });
  const finie = etat.terminee;
  $("saisie").hidden = finie;
  $("fin").hidden = !finie;
  finMinuteur = finie ? null : Date.now() + etat.temps_restant * 1000;
  $("minuteur").hidden = finie;
  tic();
  window.modalites?.etat(etat);
}

function tic() {
  if (finMinuteur === null) return;
  const reste = Math.max(0, Math.round((finMinuteur - Date.now()) / 1000));
  const texte = `${String(Math.floor(reste / 60)).padStart(2, "0")}:${String(reste % 60).padStart(2, "0")}`;
  $("minuteur-temps").textContent = reste ? texte : "Temps écoulé";
  $("minuteur").classList.toggle("fini", !reste);
  $("terminer").classList.toggle("urgent", !reste);
  if (!reste) window.modalites?.expiration();
  if (!reste && !occupe && !donnees.etat?.terminee) terminer(true);
}
setInterval(tic, 1000);

/* ---------- Échanges avec le serveur ---------- */

async function requete(url, corps) {
  const reponse = await fetch(url, {
    method: "POST", headers: {"Content-Type": "application/json", "X-CSRF-Token": csrf},
    body: JSON.stringify(corps || {}),
  });
  if (reponse.status === 401) { window.location.href = "/connexion"; throw new Error("Session expirée."); }
  if (!reponse.ok) {
    const erreur = await reponse.json().catch(() => ({}));
    throw new Error(erreur.erreur || `Erreur ${reponse.status}.`);
  }
  return reponse;
}

async function flux(url, corps, surEvenement) {
  const reponse = await requete(url, corps);
  const lecteur = reponse.body.getReader();
  const decodeur = new TextDecoder();
  let tampon = "";
  for (;;) {
    const {value, done} = await lecteur.read();
    if (done) break;
    tampon += decodeur.decode(value, {stream: true});
    let fin;
    while ((fin = tampon.indexOf("\n")) >= 0) {
      const ligne = tampon.slice(0, fin);
      tampon = tampon.slice(fin + 1);
      if (ligne.trim()) surEvenement(JSON.parse(ligne));
    }
  }
  if (tampon.trim()) surEvenement(JSON.parse(tampon));
}

async function resynchroniser() {
  const reponse = await fetch("/api/etat");
  if (reponse.ok) { donnees = await reponse.json(); afficher(); }
}

function occuper(etat) {
  occupe = etat;
  for (const id of ["envoyer", "terminer"]) $(id).disabled = etat;
  window.modalites?.occuper(etat);
}

async function suivreColleur(url, corps, {apresErreur} = {}) {
  let texte = "";
  let courant = null;
  let enAttente = false;
  let erreur = null;
  const dessiner = (fin = false) => {
    enAttente = false;
    if (courant) {
      rendre(courant.contenu, texte);
      window.modalites?.affiche(courant.contenu, texte, fin);
    }
  };
  try {
    await flux(url, corps, (e) => {
      if (e.type === "statut") statut(e.texte);
      else if (e.type === "texte") {
        if (!courant) { statut(null); courant = bulle("colleur", "", {bilan: url === "/api/bilan"}); }
        texte += e.texte;
        if (!enAttente) { enAttente = true; requestAnimationFrame(() => { dessiner(); defiler(); }); }
      } else if (e.type === "question") {
        statut(null);
        if (!courant) courant = bulle("colleur", "");
        dessiner(true);
        ajouterQuestion(courant.article, e.question);
        defiler();
      } else if (e.type === "etat") majEtat(e.etat);
      else if (e.type === "erreur") erreur = e.texte;
    });
  } catch (exc) {
    erreur = exc.message;
  }
  statut(null);
  dessiner(true);
  if (erreur) {
    alerte(erreur);
    await resynchroniser();
    apresErreur?.();
  }
}

async function envoyer(evenement) {
  evenement?.preventDefault();
  const zone = $("message");
  const texte = zone.value.trim();
  if (!texte || occupe || (window.modalites && !window.modalites.peutEnvoyer())) return;
  alerte(null);
  occuper(true);
  zone.value = "";
  majApercu();
  bulle("eleve", texte);
  defiler();
  await suivreColleur("/api/message", {message: texte}, {
    apresErreur: () => {
      // Message non enregistré : on le rend à l'élève.
      const dernier = [...donnees.messages].reverse().find((m) => m.role === "eleve");
      if (!dernier || dernier.texte !== texte) { zone.value = texte; majApercu(); }
    },
  });
  occuper(false);
  zone.focus();
}

async function demarrer(index, bouton) {
  if (occupe) return;
  occuper(true);
  bouton.disabled = true;
  bouton.textContent = "X-hôlleur prépare la colle…";
  try {
    const reponse = await requete("/api/colle", {chapitre: index});
    donnees = await reponse.json();
    afficher();
    $("message").focus();
  } catch (exc) {
    bouton.disabled = false;
    bouton.textContent = "Réessayer";
    window.alert(exc.message);
  }
  occuper(false);
}

async function terminer(automatique = false) {
  if (occupe) return;
  if (!automatique && !donnees.etat?.terminee && !window.confirm("Terminer la colle et obtenir votre bilan ?")) return;
  alerte(null);
  occuper(true);
  await suivreColleur("/api/bilan", {});
  occuper(false);
}

async function nouvelle() {
  try {
    const reponse = await requete("/api/nouvelle", {});
    donnees = await reponse.json();
    afficher();
    window.scrollTo({top: 0});
  } catch (exc) {
    alerte(exc.message);
  }
}

/* ---------- Saisie ---------- */

let minuterieApercu = null;
function majApercu() {
  clearTimeout(minuterieApercu);
  minuterieApercu = setTimeout(() => {
    const texte = $("message").value;
    const formules = /\$|\\\(|\\\[/.test(texte);
    $("apercu").hidden = !formules;
    if (formules) rendre($("apercu"), texte);
  }, 150);
}

$("saisie").addEventListener("submit", envoyer);
$("message").addEventListener("input", majApercu);
$("message").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) envoyer(e);
});
$("terminer").addEventListener("click", () => terminer());
$("nouvelle").addEventListener("click", nouvelle);

window.addEventListener("load", () => {
  if (!window.renderMathInElement) $("math-warning").hidden = false;
  afficher();
});
