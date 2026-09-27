"use strict";

(() => {
  const el = id => document.getElementById(id);
  const zone = el("message");
  if (!zone || !window.TableauSaisie) return;
  let disponible = {manuscrit: false, dictee: false, lecture: false};
  let mode = "clavier", bloque = false, termine = true, cle = "", question = "";
  let revision = 0, generation = 0, conversion = null, capture = null;
  let audioActif = false, generationAudio = 0, audioRequete = null, lecteur = null, urlAudio = null;
  let derniereLecture = "";
  const tableau = new window.TableauSaisie(el("tableau"), () => { revision++; });
  const note = texte => { el("modalites-statut").textContent = texte; };
  const noteAudio = texte => { el("audio-statut").textContent = texte; };
  const encoreActive = () => !termine && !bloque && finMinuteur !== null && Date.now() < finMinuteur;

  function actualiser() {
    const indisponible = bloque || termine;
    for (const bouton of document.querySelectorAll("[data-modalite]")) {
      const valeur = bouton.dataset.modalite;
      bouton.setAttribute("aria-pressed", String(mode === valeur));
      bouton.disabled = indisponible || (valeur !== "clavier" && !disponible[valeur]);
    }
    el("saisie-manuscrite").hidden = mode !== "manuscrit";
    el("saisie-orale").hidden = mode !== "dictee";
    for (const id of ["tableau-transcrire", "tableau-effacer", "tableau-annuler"]) {
      el(id).disabled = indisponible || Boolean(conversion);
    }
    tableau.disabled = indisponible || Boolean(conversion);
    el("dicter").disabled = indisponible || Boolean(conversion) || Boolean(capture);
    el("dictee-fin").hidden = !capture?.pret;
    el("modalite-annuler").hidden = !conversion && !capture;
    el("envoyer").disabled = indisponible || Boolean(conversion) || Boolean(capture);
    el("lecture-audio").disabled = !disponible.lecture || termine;
    el("lecture-audio").setAttribute("aria-pressed", String(audioActif));
    el("lecture-audio").textContent = audioActif ? "Lecture audio : activée" : "Activer la lecture audio";
    el("audio-relire").hidden = !audioActif;
    el("audio-relire").disabled = indisponible || Boolean(capture) || !question;
    el("audio-arreter").hidden = !audioRequete && !lecteur;
  }

  async function requeteMedia(route, corps, type, signal) {
    const reponse = await fetch("/api/modalites/" + route, {
      method: "POST", headers: {"Content-Type": type, "X-CSRF-Token": csrf}, body: corps, signal,
    });
    if (reponse.status === 401) {
      window.location.href = "/connexion"; throw new Error("Session expirée.");
    }
    if (!reponse.ok) {
      const erreur = await reponse.json().catch(() => ({}));
      throw new Error(erreur.erreur || "Conversion indisponible. Le clavier reste disponible.");
    }
    return reponse;
  }

  function libererMicro(c) {
    if (!c) return;
    clearTimeout(c.minuteur);
    c.flux?.getTracks().forEach(p => p.stop());
    c.noeud?.disconnect(); c.source?.disconnect();
    if (c.contexte && c.contexte.state !== "closed") c.contexte.close().catch(() => {});
  }

  function annulerSaisie(message = "") {
    generation++;
    conversion?.abort(); conversion = null;
    libererMicro(capture); capture = null;
    note(message); actualiser();
  }

  async function transcrire(route, obtenirBlob) {
    if (!encoreActive() || conversion) return;
    const controle = new AbortController();
    conversion = controle;
    const tour = ++generation, r = revision, contexte = cle, brouillon = zone.value;
    note("Transcription en cours… Vous pourrez relire le texte avant de l’envoyer."); actualiser();
    try {
      const blob = await obtenirBlob();
      if (tour !== generation || !encoreActive()) return;
      const reponse = await requeteMedia(route, blob, blob.type, controle.signal);
      const resultat = await reponse.json();
      if (tour !== generation || contexte !== cle || !encoreActive()) return;
      if (r !== revision || zone.value !== brouillon) {
        note("Le brouillon a changé : transcription écartée. Relancez-la si nécessaire."); return;
      }
      const texte = [brouillon.trim(), resultat.texte?.trim()].filter(Boolean).join("\n");
      if (!resultat.texte?.trim() || texte.length > 6000) throw new Error("Transcription vide ou brouillon trop long (6 000 caractères maximum).");
      zone.value = texte; revision++; majApercu(); zone.focus();
      note("Transcription ajoutée au brouillon. Relisez-la, puis cliquez sur Envoyer.");
    } catch (e) {
      if (tour === generation && e.name !== "AbortError") note(e.message);
    } finally {
      if (tour === generation) { conversion = null; actualiser(); }
    }
  }

  async function wav(c) {
    if (c.total < c.frequence / 10) throw new Error("Enregistrement trop court.");
    const n = Math.min(c.total, c.frequence * 120);
    const horsLigne = new OfflineAudioContext(1, Math.round(n * 24000 / c.frequence), 24000);
    const tampon = horsLigne.createBuffer(1, n, c.frequence);
    const donnees = tampon.getChannelData(0);
    let position = 0;
    for (const morceau of c.morceaux) {
      const fin = Math.min(morceau.length, n - position);
      if (fin <= 0) break;
      donnees.set(morceau.subarray(0, fin), position); position += fin;
    }
    const source = horsLigne.createBufferSource();
    source.buffer = tampon; source.connect(horsLigne.destination); source.start();
    const pcm = (await horsLigne.startRendering()).getChannelData(0);
    const buffer = new ArrayBuffer(44 + pcm.length * 2), vue = new DataView(buffer);
    const ascii = (offset, texte) => [...texte].forEach((c, i) => vue.setUint8(offset + i, c.charCodeAt(0)));
    ascii(0, "RIFF"); vue.setUint32(4, buffer.byteLength - 8, true); ascii(8, "WAVE");
    ascii(12, "fmt "); vue.setUint32(16, 16, true); vue.setUint16(20, 1, true); vue.setUint16(22, 1, true);
    vue.setUint32(24, 24000, true); vue.setUint32(28, 48000, true); vue.setUint16(32, 2, true); vue.setUint16(34, 16, true);
    ascii(36, "data"); vue.setUint32(40, pcm.length * 2, true);
    pcm.forEach((x, i) => vue.setInt16(44 + i * 2, Math.max(-1, Math.min(1, x)) * (x < 0 ? 32768 : 32767), true));
    return new Blob([buffer], {type: "audio/wav"});
  }

  async function dicter() {
    if (!encoreActive() || capture || conversion) return;
    arreterAudio();
    const c = {morceaux: [], total: 0, pret: false};
    capture = c; const tour = ++generation;
    note("Autorisez le micro pour dicter votre réponse."); actualiser();
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode || !window.OfflineAudioContext) {
        throw new Error("Micro indisponible : utilisez un navigateur compatible sur HTTPS ou localhost, ou le clavier.");
      }
      // Créé pendant le clic pour respecter les restrictions audio du navigateur.
      c.contexte = new AudioContext();
      await c.contexte.resume();
      c.flux = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true, channelCount: 1}});
      if (tour !== generation || !encoreActive()) { libererMicro(c); return; }
      await c.contexte.audioWorklet.addModule("/static/micro-worklet.js");
      if (tour !== generation || !encoreActive()) { libererMicro(c); return; }
      c.frequence = c.contexte.sampleRate;
      c.source = c.contexte.createMediaStreamSource(c.flux);
      c.noeud = new AudioWorkletNode(c.contexte, "capture-colle");
      c.noeud.port.onmessage = e => {
        if (capture !== c || !c.pret) return;
        c.morceaux.push(e.data); c.total += e.data.length;
        if (c.total >= c.frequence * 120) finirDictee();
      };
      c.source.connect(c.noeud); c.noeud.connect(c.contexte.destination);
      c.pret = true; c.minuteur = setTimeout(finirDictee, 120000);
      note("Micro ouvert (2 minutes maximum). Cliquez sur Arrêter et transcrire quand vous avez fini."); actualiser();
    } catch (e) {
      libererMicro(c);
      if (tour === generation) {
        capture = null; note(e.name === "NotAllowedError" ? "Micro refusé. Vous pouvez écrire au clavier." : e.message); actualiser();
      }
    }
  }

  function finirDictee() {
    const c = capture;
    if (!c?.pret) return;
    capture = null; libererMicro(c);
    transcrire("dictee", () => wav(c));
    actualiser();
  }

  function arreterAudio() {
    generationAudio++;
    audioRequete?.abort(); audioRequete = null;
    if (lecteur) { lecteur.pause(); lecteur.removeAttribute("src"); lecteur.load(); lecteur = null; }
    if (urlAudio) URL.revokeObjectURL(urlAudio);
    urlAudio = null; noteAudio(""); actualiser();
  }

  async function lire(force = false) {
    if (!audioActif || !question || !encoreActive() || capture || (!force && derniereLecture === cle)) return;
    arreterAudio();
    derniereLecture = cle;
    const tour = generationAudio, contexte = cle, controle = new AbortController();
    audioRequete = controle;
    noteAudio("Préparation de la lecture…"); actualiser();
    try {
      const reponse = await requeteMedia("lecture", JSON.stringify({question}), "application/json", controle.signal);
      const blob = await reponse.blob();
      if (tour !== generationAudio || cle !== contexte || !encoreActive() || !audioActif) return;
      urlAudio = URL.createObjectURL(blob); lecteur = new Audio(urlAudio);
      lecteur.onended = () => { if (tour === generationAudio) arreterAudio(); };
      lecteur.onerror = () => {
        if (tour === generationAudio) { arreterAudio(); noteAudio("Lecture impossible. L’énoncé reste disponible à l’écrit."); }
      };
      await lecteur.play();
      if (tour === generationAudio) noteAudio("Lecture de la consigne en cours.");
    } catch (e) {
      if (tour === generationAudio && e.name !== "AbortError") {
        arreterAudio();
        noteAudio(e.name === "NotAllowedError" ? "Lecture bloquée par le navigateur. Cliquez sur Relire." : e.message);
      }
    } finally {
      if (tour === generationAudio) { audioRequete = null; actualiser(); }
    }
  }

  window.modalites = {
    etat(etat) {
      const nouvelleCle = JSON.stringify([etat?.debut, etat?.etape, etat?.resultats?.length,
        etat?.tache?.question, etat?.tache?.etape_resolution, etat?.tache?.question_active]);
      termine = !etat || Boolean(etat.terminee) || etat.temps_restant <= 0;
      question = termine ? "" : (etat.tache?.question_active || "");
      if (nouvelleCle !== cle || termine) {
        cle = nouvelleCle; annulerSaisie(); arreterAudio(); tableau.effacer();
      }
      actualiser();
    },
    occuper(oui) {
      bloque = oui;
      if (oui) { annulerSaisie(); arreterAudio(); }
      actualiser();
      if (!oui) lire();
    },
    peutEnvoyer() { return !capture && !conversion; },
    expiration() { annulerSaisie(); arreterAudio(); },
    reinitialiser() { this.etat(null); },
  };
  zone.addEventListener("input", () => { revision++; });
  for (const bouton of document.querySelectorAll("[data-modalite]")) bouton.addEventListener("click", () => {
    annulerSaisie(); mode = bouton.dataset.modalite; actualiser();
    if (mode === "manuscrit") tableau.redimensionner();
    if (mode === "clavier") zone.focus();
  });
  el("tableau-annuler").addEventListener("click", () => tableau.annuler());
  el("tableau-effacer").addEventListener("click", () => tableau.effacer());
  el("tableau-transcrire").addEventListener("click", () => transcrire("manuscrit", () => tableau.exporter()));
  el("dicter").addEventListener("click", dicter);
  el("dictee-fin").addEventListener("click", finirDictee);
  el("modalite-annuler").addEventListener("click", () => annulerSaisie("Saisie annulée. Votre brouillon est conservé."));
  el("lecture-audio").addEventListener("click", () => {
    audioActif = !audioActif;
    if (audioActif) lire(true); else arreterAudio();
    actualiser();
  });
  el("audio-arreter").addEventListener("click", arreterAudio);
  el("audio-relire").addEventListener("click", () => lire(true));
  window.addEventListener("pagehide", () => { annulerSaisie(); arreterAudio(); });
  fetch("/api/modalites").then(r => {
    if (!r.ok) throw new Error();
    return r.json();
  }).then(config => {
    disponible = config; actualiser();
    if (!config.dictee || !config.manuscrit) note("Certaines modalités sont indisponibles. La saisie au clavier reste disponible.");
  }).catch(() => { actualiser(); note("Modalités indisponibles. Vous pouvez écrire au clavier."); });
  actualiser();
})();
