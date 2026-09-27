"use strict";

// Dessin et export adaptés de kholle_live/static/board.html, commit 0ff5f59.
// Aucun envoi automatique, aucune vérification des mathématiques.
window.TableauSaisie = class {
  constructor(canvas, changement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.traits = [];
    this.enCours = new Map();
    this.changement = changement;
    this.disabled = false;
    canvas.addEventListener("pointerdown", e => {
      if (this.disabled || (e.pointerType === "mouse" && e.button !== 0)) return;
      if (e.pointerType === "touch" && [...this.enCours.values()].some(t => t.stylet)) return;
      if (e.pointerType === "pen") {
        for (const [id, t] of this.enCours) if (!t.stylet) {
          this.enCours.delete(id); this.traits.splice(this.traits.indexOf(t), 1);
        }
      }
      e.preventDefault();
      canvas.setPointerCapture(e.pointerId);
      const trait = [this.point(e)];
      trait.stylet = e.pointerType === "pen";
      this.enCours.set(e.pointerId, trait);
      this.traits.push(trait);
      this.changement();
      this.redessiner();
    });
    canvas.addEventListener("pointermove", e => {
      const trait = this.enCours.get(e.pointerId);
      if (!trait || this.disabled) return;
      e.preventDefault();
      const evenements = e.getCoalescedEvents?.() || [];
      const debut = trait.length - 1;
      for (const ev of evenements.length ? evenements : [e]) trait.push(this.point(ev));
      this.tracer(this.ctx, trait.slice(debut));
    });
    const finir = e => { this.enCours.delete(e.pointerId); };
    canvas.addEventListener("pointerup", finir);
    canvas.addEventListener("pointercancel", finir);
    new ResizeObserver(() => this.redimensionner()).observe(canvas);
  }
  point(e) {
    const r = this.canvas.getBoundingClientRect();
    return [Math.max(0, Math.min(1000, (e.clientX - r.left) * 1000 / r.width)),
      Math.max(0, Math.min(500, (e.clientY - r.top) * 500 / r.height))];
  }
  redimensionner() {
    const r = this.canvas.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = Math.round(r.width * ratio);
    this.canvas.height = Math.round(r.height * ratio);
    this.ctx.setTransform(this.canvas.width / 1000, 0, 0, this.canvas.height / 500, 0, 0);
    this.redessiner();
  }
  tracer(c, trait) {
    c.lineWidth = 3; c.lineCap = "round"; c.lineJoin = "round";
    c.strokeStyle = "#000"; c.fillStyle = "#000";
    c.beginPath();
    if (trait.length === 1) {
      c.arc(trait[0][0], trait[0][1], 1.5, 0, 2 * Math.PI); c.fill(); return;
    }
    c.moveTo(trait[0][0], trait[0][1]);
    for (let i = 1; i < trait.length; i++) c.lineTo(trait[i][0], trait[i][1]);
    c.stroke();
  }
  redessiner() {
    this.ctx.clearRect(0, 0, 1000, 500);
    for (const t of this.traits) this.tracer(this.ctx, t);
  }
  effacer() { this.enCours.clear(); this.traits = []; this.redessiner(); this.changement(); }
  annuler() { this.enCours.clear(); this.traits.pop(); this.redessiner(); this.changement(); }
  async exporter() {
    if (!this.traits.length) throw new Error("Le tableau est vide.");
    if (this.enCours.size) throw new Error("Terminez votre trait avant de transcrire.");
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const t of this.traits) for (const [x, y] of t) {
      x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
    }
    x0 = Math.max(0, x0 - 24); y0 = Math.max(0, y0 - 24);
    x1 = Math.min(1000, x1 + 24); y1 = Math.min(500, y1 + 24);
    const echelle = Math.min(1400 / Math.max(1, x1 - x0), 2);
    const sortie = document.createElement("canvas");
    sortie.width = Math.ceil((x1 - x0) * echelle);
    sortie.height = Math.ceil((y1 - y0) * echelle);
    const c = sortie.getContext("2d");
    c.fillStyle = "#fff"; c.fillRect(0, 0, sortie.width, sortie.height);
    c.setTransform(echelle, 0, 0, echelle, -x0 * echelle, -y0 * echelle);
    for (const t of this.traits) this.tracer(c, t);
    const blob = await new Promise(ok => sortie.toBlob(ok, "image/png"));
    if (!blob || blob.size > 2 * 1024 * 1024) throw new Error("Tableau trop volumineux.");
    return blob;
  }
};
