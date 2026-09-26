# Aperçu des passages — Séries numériques

Pages PDF (numérotation à partir de 1) et pages imprimées indiquées séparément.

## Définition 16.1.1 (Série)

Type : définition — PDF : [139, 140] — imprimées : [137, 138]

(i) Soit $(u_n)_{n\in\mathbb N}$ une suite de réels ou complexes. La série de terme général $u_n$, notée $\sum_{n\geq 0} u_n$, ou plus simplement $\sum u_n$, est, avec l’abus mentionné dans l’introduction du chapitre, la suite $(S_n)_{n\in\mathbb N}$ des sommes partielles de la suite $(u_n)$, à savoir :

$$S_n=\sum_{k=0}^{n}u_k.$$

(ii) $S_n$ est appelé somme partielle (d’ordre $n$) de la série $\sum u_n$, et $u_n$ est appelé terme général de la série $\sum u_n$.

## Remarques 16.1.2

Type : remarque — PDF : [140] — imprimées : [138]

1. La donnée de la suite $(S_n)$ des sommes partielles de $\sum u_n$ permet de retrouver le terme général $u_n$ de la série, puisque

$$u_0=S_0\quad\text{et}\quad\forall n\in\mathbb N^*,\quad u_n=S_n-S_{n-1}.$$

2. La définition se généralise de façon évidente pour des séries dont le premier terme est $u_{n_0}$, $n_0\in\mathbb N$ (ou même $n_0\in\mathbb Z$).

## Avertissement 16.1.3

Type : avertissement — PDF : [140] — imprimées : [138]

Attention à ne pas confondre suite $(u_n)_{n\in\mathbb N}$ et série de terme général $u_n$.

La comparaison à des séries de référence permettra d’obtenir des critères efficaces de convergence, rendant en général l’étude de la convergence des séries beaucoup plus aisée que celle des suites. Pour cette raison, il est souvent intéressant de pouvoir ramener l’étude de la convergence d’une suite à celle d’une série, via la relation de la remarque précédente :

## Méthode 16.1.4 (Comment étudier la convergence d’une suite via les séries)

Type : méthode — PDF : [140] — imprimées : [138]

La convergence de la suite $(u_n)_{n\in\mathbb N}$ équivaut à la convergence de la série $\sum(u_{n+1}-u_n)$. C’est un moyen pratique de démontrer la convergence de certaines suites, en utilisant les techniques spécifiques et performantes des séries.

## Définition 16.1.5 (Convergence d’une série)

Type : définition — PDF : [140] — imprimées : [138]

(i) On dit que la série $\sum u_n$ de terme général $u_n$ converge si la suite $(S_n)_{n\in\mathbb N}$ de ses sommes partielles admet une limite finie. On note alors

$$\sum_{n=0}^{+\infty}u_n=\lim_{n\to+\infty}S_n.$$

Cette quantité est appelée somme de la série de terme général $u_n$.

(ii) Une série non convergente est dite divergente.

(iii) Soit $\sum_{n\in\mathbb N}u_n$ une série convergente, et soit $n\in\mathbb N$. Le $n$-ième reste de la série est :

$$r_n=\sum_{k=n+1}^{+\infty}u_k=\sum_{k=0}^{+\infty}u_k-S_n.$$

(iv) La nature de la série $\sum u_n$ est le fait d’être convergente ou divergente.

## Remarque 16.1.6

Type : remarque — PDF : [141] — imprimées : [139]

Par convention, afin de ne pas avoir d’ambiguïté dans la terminologie, nous parlerons de série divergente également lorsque nous adopterons un point de vue dans $\overline{\mathbb R}$, dans le cas d’une série dont les sommes partielles tendent vers $+\infty$ ou $-\infty$. Nous nous autoriserons cependant parfois dans cette situation à écrire l’égalité suivante, valable dans $\overline{\mathbb R}$

$$\sum_{n=0}^{+\infty}u_n=+\infty\quad\text{ou}\quad\sum_{n=0}^{+\infty}u_n=-\infty.$$

## Avertissement 16.1.7

Type : avertissement — PDF : [141] — imprimées : [139]

Toute série divergente ne diverge pas vers $+\infty$ ou $-\infty$ !

## Exemple 16.1.8

Type : exemple — PDF : [141] — imprimées : [139]

$\sum(-1)^n$

Nous verrons plus loin qu’une façon efficace de montrer la convergence d’une série est de la comparer à une autre série dont on connaît les propriétés de convergence. Pour cette raison, il est important de connaître les propriétés de convergence d’un certain nombre de séries de référence. De l’importance du théorème suivant !

## Théorème 16.1.9 (Séries géométriques)

Type : théorème — PDF : [141] — imprimées : [139]

Soit $a\in\mathbb C$. La série $\sum a^n$ converge si et seulement si $|a|<1$ ; dans ce cas,

$$\sum_{n=0}^{+\infty}a^n=\frac{1}{1-a}.$$

L’exemple suivant est également d’une grande importance (peut-être encore plus que les séries géométriques). Nous nous contentons de l’indiquer en exemple pour le moment : nous énoncerons un théorème plus général un peu plus tard.

## Exemple 16.1.10 (Série de Riemann de paramètre 1)

Type : exemple — PDF : [141] — imprimées : [139]

La série $\sum_{n\geq 1}\frac{1}{n}$ est divergente. Cette série est appelée série harmonique.
