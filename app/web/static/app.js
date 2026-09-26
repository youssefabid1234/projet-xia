"use strict";

if (window.renderMathInElement) {
  document.querySelectorAll(".math").forEach((element) => {
    window.renderMathInElement(element, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: false},
        {left: "\\[", right: "\\]", display: true},
      ],
      throwOnError: false,
      trust: false,
    });
  });
} else {
  document.getElementById("math-warning").hidden = false;
}

document.getElementById("answer-form")?.addEventListener("submit", () => {
  const button = document.getElementById("submit-answer");
  if (!button) return;
  button.disabled = true;
  button.textContent = "Évaluation…";
  document.getElementById("pending").hidden = false;
});

window.addEventListener("pageshow", () => {
  const button = document.getElementById("submit-answer");
  if (button) {
    button.disabled = false;
    button.textContent = "Vérifier ma réponse";
    document.getElementById("pending").hidden = true;
  }
});
document.getElementById("result")?.focus();
