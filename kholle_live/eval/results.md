# Évaluation du tableau

## Avant / après (27/09)

Mêmes 14 échantillons, `gpt-4.1-mini`, un passage par colonne (deux pour la version finale).

| | Avant | Règle 7 + relecture | Final, passage 1 | Final, passage 2 |
|---|---|---|---|---|
| Erreurs détectées (E*) | 6/7 | 6/7 | 6/7 | 6/7 |
| Fausses alertes (C*) | 2/7 | 1/7 | 2/7 | 3/7 |
| Illisibles | 2 | 3 | 1 | 2 |
| Latence moyenne | 1.7 s | 2.3 s | 2.4 s | 2.4 s |
| Désaccords entre les deux lectures | — | 1 sur 8 | 0 sur 8 | 0 sur 9 |

« Final » = prompt d'origine (règle 7 retirée) + seconde lecture des lignes fausses.

**Étiquettes corrigées.** C3 et C4 sont faux tels qu'écrits : C3 `e^x = 1 + x^2/2 + x^3/6` (terme en x oublié), C4 `tan x = x + x^3/6` (il faut x^3/3). Leurs « fausses alertes » sont de vraies détections ; à redessiner. En les comptant comme erreurs (9 erreurs, 5 justes) :

| | Avant | Règle 7 + relecture | Final, passage 1 | Final, passage 2 |
|---|---|---|---|---|
| Erreurs détectées | 8/9 | 7/9 | 8/9 | 8/9 |
| Vraies fausses alertes | 0/5 | 0/5 | 0/5 | 1/5 (C1) |

**Constats.**
- E7 n'est jamais détecté : les parenthèses de `sin(x)` sont lues `|x|`, d'où `exp(sin(abs(x)))` et « ? ». Échec de lecture, pas du vérificateur.
- La règle 7 (« toujours exp(...) ») a été retirée : sur C3, 2 lectures justes sur 8 avec elle, 8/8 sans (6/8 « non vérifiable »). Sans elle, le lecteur écrit déjà `exp(...)` dans lhs 16/16. Côté vérificateur, `e^x`, `e**x`, `e^(sin x)` donnaient déjà `exp` (`e` → `E`).
- Seconde lecture : 1 désaccord sur 25 lignes fausses relues, et c'était C3 sous la règle 7 (vraie erreur masquée). Elle n'a pas rattrapé C1 au passage 2 : `x^3/6` lu `7x^3/6` par les deux lectures (erreur rare : 12/12 lectures justes au re-test). Coût : +0,7 s en moyenne, +1,2 s en moyenne sur les tableaux avec erreur (E1–E6).
- Écarts d'un échantillon entre passages (C1, C6) : du bruit de lecture ; 14 échantillons ne suffisent pas à départager les versions.

## Détail du dernier passage

Exercice : `dl_ln_sin` — 2026-09-27 18:21

- Erreurs détectées : **6/7** (échantillons E*)
- Fausses alertes : **3/7** (échantillons C*)
- Illisibles : **2** (lecture en échec ou aucune ligne vérifiable)
- Latence moyenne de lecture : **2.4 s** (seconde lecture comprise)
- Relectures des lignes fausses : **0 désaccord(s) sur 9**

| Échantillon | Attendu | Résultat | Lignes | Latence |
|---|---|---|---|---|
| C1_20260927-173645-739.png | juste | détecté ⚠ | L1 ✗ `sin(x) = x - 7x^3/6 + o(x^3)` (erreur sur le terme en x^3) | 3.7 s |
| C2_20260927-173732-683.png | juste | rien | L1 ✓ `cos(x) = 1 - \frac{x^{2}}{2} + \frac{x^{4}}{24} + o(x^{4})` | 1.9 s |
| C3_20260927-173821-009.png | juste | détecté ⚠ | L1 ✗ `e^x = 1 + \frac{x^2}{2} + \frac{x^3}{6} + 0(x^3)` (erreur sur le terme en x) | 2.8 s |
| C4_20260927-173858-956.png | juste | détecté ⚠ | L1 ✗ `tan(x) = x + x**3/6 + o(x**3)` (erreur sur le terme en x^3) | 2.7 s |
| C5_20260927-173930-929.png | juste | rien | L1 ✓ `1 / (1-x) = 1 + x + x^2 + x^3 + o(x^3)` | 1.4 s |
| C6_20260927-174014-672.png | juste | rien | L1 ? `ln(1 + sin(x)) = x - x^2/2 + x^3/6` | 1.5 s |
| C7_20260927-174101-022.png | juste | rien | L1 ✓ `e^{sin x} = 1 + x + \frac{x^{2}}{2} + o(x^{2})` | 1.6 s |
| E1_20260927-174131-662.png | erreur | détecté | L1 ✗ `sin (x) = x + x^3/6 + o(x^3)` (erreur sur le terme en x^3) | 2.6 s |
| E2_20260927-174300-984.png | erreur | détecté | L1 ✗ `cos(x) = 1 - x^2/2 + x^4/12 + o(x^4)` (erreur sur le terme en x^4) | 2.6 s |
| E3_20260927-174356-041.png | erreur | détecté | L1 ✗ `ln(1+x) = x - x**2/2 + x**3/6 + o(x**3)` (erreur sur le terme en x^3) | 3.0 s |
| E4_20260927-174434-018.png | erreur | détecté | L1 ✗ `tan x = x + x^3/6 + o(x^3)` (erreur sur le terme en x^3) | 2.8 s |
| E5_20260927-174526-879.png | erreur | détecté | L1 ✗ `\sqrt{1+x} = 1 + \frac{x}{2} - \frac{x^{2}}{4} + o(x^{2})` (erreur sur le terme en x^2) | 3.1 s |
| E6_20260927-174629-203.png | erreur | détecté | L1 ✗ `ln (1 + sin(x)) = x - x^2/2 - x^3/6 + o(x^3)` (erreur sur le terme en x^3) | 3.0 s |
| E7_20260927-174717-761.png | erreur | rien ⚠ | L1 ? `exp(sin |x|) = 1 + x + x^2/2 + x^3/6 + o(x^3)` | 1.4 s |
