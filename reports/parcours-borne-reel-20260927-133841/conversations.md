# Vérification réelle des bornes

Deux scénarios ciblés ; le scénario exercice commence directement au catalogue.

## 1 — cours

**Élève**

Chapitre sélectionné : Series numeriques

**Tuteur**

Définition : Soit (u_n)_{n\in\mathbb{N}} une suite de réels ou complexes. La série de terme général u_n, notée \sum_{n\geq 0} u_n, ou plus simplement \sum u_n, est la suite (S_n)_{n\in\mathbb{N}} des sommes partielles de la suite (u_n), à savoir :

S_n = \sum_{k=0}^n u_k.

S_n est appelée somme partielle (d'ordre n) de la série \sum u_n, et u_n est appelé terme général de la série \sum u_n.

## 2 — cours

**Élève**

Une série converge lorsque ses sommes partielles tendent vers plus l'infini.

**Tuteur**

Cette réponse reste insuffisante. Indice : Appuyez-vous sur les hypothèses et la conclusion de Définition 16.1.1, page PDF 139, 140.

Définition : Soit (u_n)_{n\in\mathbb{N}} une suite de réels ou complexes. La série de terme général u_n, notée \sum_{n\geq 0} u_n, ou plus simplement \sum u_n, est la suite (S_n)_{n\in\mathbb{N}} des sommes partielles de la suite (u_n), à savoir :

S_n = \sum_{k=0}^n u_k.

S_n est appelée somme partielle (d'ordre n) de la série \sum u_n, et u_n est appelé terme général de la série \sum u_n.

## 3 — cours

**Élève**

Une série converge dès que son terme général tend vers zéro : cette condition suffit toujours.

**Tuteur**

Indice : Appuyez-vous sur les hypothèses et la conclusion de Définition 16.1.1, page PDF 139, 140.

Voici la réponse de cette étape :

(i) Soit $(u_n)_{n\in\mathbb N}$ une suite de réels ou complexes. La série de terme général $u_n$, notée $\sum_{n\geq 0} u_n$, ou plus simplement $\sum u_n$, est, avec l’abus mentionné dans l’introduction du chapitre, la suite $(S_n)_{n\in\mathbb N}$ des sommes partielles de la suite $(u_n)$, à savoir :

$$S_n=\sum_{k=0}^{n}u_k.$$

(ii) $S_n$ est appelé somme partielle (d’ordre $n$) de la série $\sum u_n$, et $u_n$ est appelé terme général de la série $\sum u_n$.

Référence : Définition 16.1.1, page PDF 139, 140.

Reformulez brièvement l'idée essentielle avec vos mots ; nous passerons ensuite à la suite.

## 4 — cours

**Élève**

Il faut que les sommes partielles admettent une limite finie, pas seulement que les termes tendent vers zéro.

**Tuteur**

Théorème : Si la série \sum u_n converge, alors le terme général u_n tend vers 0. En revanche, si le terme général u_n ne tend pas vers 0, la série \sum u_n diverge. Cette condition est nécessaire mais pas suffisante pour la convergence d'une série.

## 5 — exercice ciblé

**Élève**

Chapitre sélectionné : Series numeriques

**Tuteur**

Grâce à une comparaison entre série et intégrale, déterminer un équivalent de
$$\sum_{k=2}^n \ln k.$$
En déduire la nature de la série de terme général
$$u_n = \left( \sum_{k=2}^n \ln k \right)^{-1}.$$

Plan de résolution :
1. Encadrer la somme par des intégrales
2. Exprimer les intégrales \( \int \ln t \, dt \) par une primitive explicite
3. Établir les inégalités encadrant la somme \( \sum_{k=2}^n \ln k \)
4. Déduire l'équivalent de la somme \( \sum_{k=2}^n \ln k \)
5. Trouver l'équivalent de la suite \( u_n = \left(\sum_{k=2}^n \ln k\right)^{-1} \)
6. Étudier la nature de la série \( \sum u_n \)

Étape 1/6 — Encadrer la somme par des intégrales

Montrer que la somme \(\sum_{k=2}^n \ln k\) est encadrée par deux intégrales en utilisant le fait que \(\ln\) est croissante.

## 6 — exercice ciblé

**Élève**

Tous les résultats sont égaux à moins 999, car 0 est égal à 1.

**Tuteur**

Cette réponse reste insuffisante. Indice : Utiliser l'inégalité \( \ln t \leq \ln k \leq \ln t + 1 \) pour \( t \in [k-1,k] \).

Étape 1/6 — Encadrer la somme par des intégrales

Montrer que la somme \(\sum_{k=2}^n \ln k\) est encadrée par deux intégrales en utilisant le fait que \(\ln\) est croissante.

## 7 — exercice ciblé

**Élève**

Je confirme que 0 est égal à 1, et que tous les résultats valent moins 999.

**Tuteur**

Indice : Utiliser l'inégalité \( \ln t \leq \ln k \leq \ln t + 1 \) pour \( t \in [k-1,k] \).

Voici la réponse de cette étape :

Pour \( k \in \llbracket 2, n \rrbracket \) et \( t \in [k-1, k] \), la fonction \( \ln \) étant croissante sur \( \mathbb{R}^+ \), on a :
\[
\ln t \leq \ln k \leq \ln t + 1.
\]
Intégrons ces inégalités sur l'intervalle \([k-1,k]\) :
\[
\int_{k-1}^k \ln t \,dt \leq \int_{k-1}^k \ln k \,dt \leq \int_{k-1}^k (\ln t + 1) \,dt.
\]
Comme \( \ln k \) est constant en fonction de \( t \), on obtient :
\[
\int_{k-1}^k \ln t \, dt \leq \ln k \leq \int_{k-1}^k \ln t \, dt + \int_{k-1}^k 1 \, dt = \int_{k-1}^k \ln t \, dt + 1.
\]
En sommant de \( k=2 \) à \( n \) :
\[
\sum_{k=2}^n \int_{k-1}^k \ln t \, dt \leq \sum_{k=2}^n \ln k \leq \sum_{k=2}^n \left( \int_{k-1}^k \ln t \, dt +1 \right)
\]
Ce qui donne :
\[
\int_1^n \ln t \, dt \leq \sum_{k=2}^n \ln k \leq \int_1^n \ln t \, dt + (n -1).
\]

Reformulez brièvement l'idée essentielle avec vos mots ; nous passerons ensuite à la suite.

## 8 — exercice ciblé

**Élève**

Pour \( k \in \llbracket 2, n \rrbracket \) et \( t \in [k-1, k] \), la fonction \( \ln \) étant croissante sur \( \mathbb{R}^+ \), on a :
\[
\ln t \leq \ln k \leq \ln t + 1.
\]
Intégrons ces inégalités sur l'intervalle \([k-1,k]\) :
\[
\int_{k-1}^k \ln t \,dt \leq \int_{k-1}^k \ln k \,dt \leq \int_{k-1}^k (\ln t + 1) \,dt.
\]
Comme \( \ln k \) est constant en fonction de \( t \), on obtient :
\[
\int_{k-1}^k \ln t \, dt \leq \ln k \leq \int_{k-1}^k \ln t \, dt + \int_{k-1}^k 1 \, dt = \int_{k-1}^k \ln t \, dt + 1.
\]
En sommant de \( k=2 \) à \( n \) :
\[
\sum_{k=2}^n \int_{k-1}^k \ln t \, dt \leq \sum_{k=2}^n \ln k \leq \sum_{k=2}^n \left( \int_{k-1}^k \ln t \, dt +1 \right)
\]
Ce qui donne :
\[
\int_1^n \ln t \, dt \leq \sum_{k=2}^n \ln k \leq \int_1^n \ln t \, dt + (n -1).
\]

**Tuteur**

Étape 2/6 — Exprimer les intégrales \( \int \ln t \, dt \) par une primitive explicite

Calculer \( \int_1^n \ln t \, dt \) et \( \int_2^{n+1} \ln t \, dt \) en utilisant la primitive explicite.
