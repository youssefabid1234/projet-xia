"use strict";
// Capture locale uniquement. Aucun fragment n'est envoyé sur le réseau.
class CaptureColle extends AudioWorkletProcessor {
  process(inputs) {
    if (inputs[0]?.[0]) this.port.postMessage(inputs[0][0].slice());
    return true;
  }
}
registerProcessor("capture-colle", CaptureColle);
