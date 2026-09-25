# Aperçu — Chapitre 18 : Topologie

Transcription du polycopié de Quentin De Muynck. Formules en LaTeX.

Pages PDF 52 (énoncés) et 203 (corrigés), numérotées 46 et 197 dans le document.

Remarque : le corrigé 18.2 comporte « par continuité de φ » et affirme l’appartenance de la limite à E avant de la justifier. Ces défauts du texte source sont conservés.

## Exercice 18.1

**Énoncé**

Montrer que $\mathbb{C}\setminus\{0\}$ est dense dans $\mathbb{C}$.

**Corrigé du document**

On a naturellement $\mathbb{C}^*\subset\mathbb{C}$ donc $\overline{\mathbb{C}^*}\subset\overline{\mathbb{C}}=\mathbb{C}$.

Maintenant, $\frac{1}{n}\xrightarrow[n\to+\infty]{}0$ et $\left(\frac{1}{n}\right)_{n\in\mathbb{N}^*}\in(\mathbb{C}^*)^{\mathbb{N}}$, donc $0\in\overline{\mathbb{C}^*}$, donc $\mathbb{C}\subset\overline{\mathbb{C}^*}$.

Ainsi $\overline{\mathbb{C}^*}=\mathbb{C}$, c’est-à-dire que $\mathbb{C}^*$ est dense dans $\mathbb{C}$, d’après le cours.

## Exercice 18.2

**Énoncé**

Montrer que $E=\{x+iy\in\mathbb{C}\,/\,x,y\in\mathbb{R},\ x^2+y^2\leq3,\ x^3+y^3-3xy\geq0\}$ est un compact de $\mathbb{C}$.

**Corrigé du document**

Soit $(x_n+iy_n)\in E^{\mathbb{N}}$, telle que, $\forall n\in\mathbb{N}$, $x_n^2\leq3$, $y_n^2\leq3$, donc $(x_n+iy_n)$ est bornée en module. D’après Bolzano-Weierstrass, il existe $\varphi:\mathbb{N}\longrightarrow\mathbb{N}$ telle que $x_{\varphi(n)}+iy_{\varphi(n)}\xrightarrow[n\to+\infty]{}x+iy\in E$, qui est une certaine valeur d’adhérence de la suite.

$\forall n\in\mathbb{N},\ x_{\varphi(n)}^2+y_{\varphi(n)}^2\leq3$ donc par continuité de $\varphi$, $x^2+y^2\leq3$, on a la même chose pour l’autre inégalité. Et donc $\lim_{n\to+\infty}(x_{\varphi(n)}+iy_{\varphi(n)})\in E$, donc $E$ est compact puisque toute suite de $E$ admet au moins une valeur d’adhérence dans $E$.

Alternativement, on aurait pu montrer que $E$ était fermé et borné.

## Exercice 18.3

**Énoncé**

Montrer que $U=\{(x,y,z)\in\mathbb{R}^3\,/\,\ln(x^2+y^2+1)\sin(z)<e^{x+z}\text{ et }x+y-z>1\}$ est un ouvert de $\mathbb{R}^3$.

**Corrigé du document**

On a $U=U_1\cap U_2$ où $U_1=\{(x,y,z)\in\mathbb{R}^3\,/\,\ln(x^2+y^2+1)\sin(z)<e^{x+z}\}$ et $U_2=\{(x,y,z)\in\mathbb{R}^3\,/\,x+y-z>1\}$.

On pose $F_1=\mathbb{R}^3\setminus U_1$ et $F_2=\mathbb{R}^3\setminus U_2$.

Soit $(a_n)\in F_1^{\mathbb{N}}$ une suite convergente telle que $a_n=(x_n,y_n,z_n)\xrightarrow[n\to+\infty]{}(x,y,z)$. Alors :

$$\ln(x_n^2+y_n^2+1)\sin(z_n)\geq e^{x_n+z_n}$$
$$\ln(x^2+y^2+1)\sin(z)\geq e^{x+z}$$

par passage à la limite et continuité de $\ln$ et $\sin$.

Donc $(x,y,z)\in F_1$ donc $U_1$ est ouvert.

De même, on montre que $F_2$ est fermé, donc que $U_2$ est ouvert. $U=U_1\cap U_2$, une intersection finie d’ouverts, on a bien que $U$ est ouvert.
