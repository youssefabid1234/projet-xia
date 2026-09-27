# Aperçu des passages — 11 — Équations différentielles linéaires

Pages PDF (numérotation à partir de 1) et pages imprimées indiquées séparément.

## Définition 11.1.1 (Équation différentielle linéaire)

Type : définition — PDF : [69] — imprimées : [67]

Une équation différentielle linéaire d'ordre $r$ est de la forme $\sum_{k=0}^r a_k(x)y^{(k)}(x)=b(x)$, où $a_r$ n'est pas identiquement nulle. Les coefficients et l'inconnue sont à valeurs dans $\mathbb K=\mathbb R$ ou $\mathbb C$. On définit de même les équations à plusieurs fonctions inconnues et les systèmes linéaires par des relations affines entre leurs dérivées.

## Théorème 11.1.2 (Structure de l’ensemble des solutions)

Type : théorème — PDF : [69, 70] — imprimées : [67, 68]

Sur un intervalle $I$, si $y_p$ est une solution particulière de $L(y)=b$, l'ensemble des solutions est $S=y_p+S_0$, où $S_0=\{y:L(y)=0\}$ est un espace vectoriel. Éléments de preuve : par linéarité, $L(y)=b$ équivaut à $L(y-y_p)=0$ ; la fonction nulle et toute combinaison linéaire de solutions homogènes appartiennent à $S_0$.

## Proposition 11.1.3 (Principe de superposition)

Type : proposition — PDF : [70] — imprimées : [68]

Si $b=b_1+b_2$ et si $L(y_1)=b_1$, $L(y_2)=b_2$, alors $y_1+y_2$ est une solution particulière de $L(y)=b$. Éléments de preuve : $L(y_1+y_2)=L(y_1)+L(y_2)=b_1+b_2$ par linéarité de la dérivation.

## Théorème 11.2.1 (Résolution de l’équation y′ = a(x)y (a continue))

Type : théorème — PDF : [70, 71] — imprimées : [68, 69]

Si $a:I\to\mathbb K$ est continue et $A$ une primitive de $a$, les solutions de $y'=a(x)y$ sur l'intervalle $I$ sont exactement $y(x)=Ce^{A(x)}$, $C\in\mathbb K$. Éléments de preuve : poser $z=ye^{-A}$ ; alors $z'=e^{-A}(y'-ay)$, donc $z$ est constante si et seulement si $y$ est solution.

## Remarque 11.2.2 (Comment retrouver cette formule si on l’a oubliée)

Type : remarque — PDF : [71] — imprimées : [69]

• Au brouillon, on s’autorise des divisions par y (rigoureusement incorrect si on n’a pas justifié
que la fonction ne s’annule pas !) L’équation s’écrit alors y′
y = a(x).
• On reconnait en y′
y la dérivée de ln |y| (appelée dérivée logarithmique de y). On primitive, on
passe à l’exponentielle et le tour est joué.
• Au propre, il est préférable d’utiliser directement la formule du cours, pour éviter les problèmes
de justification issus de la division par y.

## Exemples 11.2.3

Type : exemple — PDF : [71] — imprimées : [69]

1. Résolution de y′ = ay (a constant)
2. Résolution de y′ = yxα sur R si α ⩾0, sur R∗
+ sinon.

## Méthode 11.2.4 (Méthode de variation de la constante)

Type : méthode — PDF : [71] — imprimées : [69]

Pour $y'=a(x)y+b(x)$, avec $a,b$ continues sur un intervalle et $A'=a$, rechercher $y=C(x)e^{A(x)}$. Substitution : $C'=be^{-A}$ ; on obtient $C$ par primitivation. Ajouter à une solution particulière toutes les solutions de l'équation homogène.

## Exemples 11.2.5

Type : exemple — PDF : [71] — imprimées : [69]

1. Résoudre $y'=2y+\sin x+e^x+x$ sur $\mathbb R$. 2. Résoudre $y'=-y/x+\arctan x$ sur $\mathbb R_+^*$.

## Remarque 11.2.6

Type : remarque — PDF : [71] — imprimées : [69]

Comme dit plus haut, et j’insiste dessus, il n’est pas toujours nécessaire d’employer la méthode de
variation de la constante pour trouver une solution particulière : parfois elle est suffisamment évidente
pour être devinée.

## Exemples 11.2.7

Type : exemple — PDF : [72] — imprimées : [70]

1. Si $a,b$ sont constants et $a\ne0$, la constante $-b/a$ résout $y'=ay+b$. 2. Pour $y'=ay+be^{\alpha x}$, chercher $y=ce^{\alpha x}$ : le coefficient doit satisfaire $(\alpha-a)c=b$. Note de relecture : la condition $a\ne0$, nécessaire à la division, est implicite dans le premier exemple du PDF.
