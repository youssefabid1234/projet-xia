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

document.getElementById("chat-form")?.addEventListener("submit", () => {
  document.getElementById("send-message").disabled = true;
  document.getElementById("chat-pending").hidden = false;
});
window.addEventListener("pageshow", () => {
  const button = document.getElementById("send-message");
  if (button) {
    button.disabled = false;
    document.getElementById("chat-pending").hidden = true;
  }
});
if (!document.querySelector('[role="alert"]')) {
  document.getElementById("last-message")?.focus();
}
