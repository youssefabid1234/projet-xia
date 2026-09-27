# Profil moyen — session 2

Compte partagé : audit-longitudinal. APIs réelles. E1 inclut le choix du chapitre.

## Échange 1

**Élève**

[Choix du chapitre : Séries numériques]

**Tuteur**

Commençons par un exercice du chapitre Series numeriques.

Grâce à une comparaison entre série et intégrale, déterminer un équivalent de
$$\sum_{k=2}^n \ln k.$$
En déduire la nature de la
série de terme général
$$u_n = \left( \sum_{k=2}^n \ln k \right)^{-1}.$$

Donnez votre réponse.

*Étape : Exercices du catalogue — HTTP 200 — 2.78 s.*

## Échange 2

**Élève**

Pour déterminer un équivalent de \(\sum_{k=2}^n \ln k\), on peut comparer cette somme à l'intégrale de la fonction \(\ln x\) sur \([2, n]\).

On sait que :
\[
\int_2^n \ln x \, dx = \left[ x \ln x - x \right]_2^n = n \ln n - n - (2 \ln 2 - 2) = n \ln n - n - 2 \ln 2 + 2.
\]

Par la méthode de comparaison série/intégrale, on a :
\[
\sum_{k=2}^n \ln k \sim n \ln n - n.
\]

Donc un équivalent est \(\sum_{k=2}^n \ln k \sim n \ln n\) (car \(n \ln n\) domine \(n\) quand \(n\) tend vers l'infini).

Ensuite, pour la série de terme général \(u_n = \left(\sum_{k=2}^n \ln k\right)^{-1}\), on a 
\[
u_n \sim \frac{1}{n \ln n}.
\]

On reconnaît une série de type \(\sum \frac{1}{n \ln n}\) qui est divergente (critère intégral ou connu).

Donc, la série \(\sum u_n\) est divergente.

**Tuteur**

Passons à un exercice.

Soit \((u_n)\) une suite décroissante de réels strictement positifs. On suppose qu’il existe \(k \in \mathbb{N}\) avec \(k \geq 2\) et \(n_0 \in \mathbb{N}^*\) tels que, pour tout \(n \geq n_0\), \(k^{kn} \geq u_n\).

Montrer que la série \(\sum u_n\) est divergente.

Donnez votre raisonnement.

*Étape : Exercices du catalogue — HTTP 200 — 6.72 s.*

## Échange 3

**Élève**

Si \( (u_n) \) est une suite décroissante de réels strictement positifs et on a pour \( n \geq n_0 \), \( k^{kn} \geq u_n \) avec \( k \geq 2 \), alors on peut utiliser ce majorant pour étudier la série \( \sum u_n \).

Comme \( k^{kn} \) grandit très vite (exponentielle), la suite \( u_n \) est majorée par une suite qui tend vers \( +\infty \), ce qui me paraît contradictoire avec le fait que \( u_n \) soit strictement positive et décroissante. 

Cependant, si je poursuis, la série \( \sum u_n \), où \( u_n \leq k^{kn} \), est comparable à une série dont les termes explosent, et donc ne tend pas vers zéro, donc la série diverge.

Mais je ne suis pas sûr du lien exact entre la décroissance de \( u_n \) et cette comparaison. Peux-tu me donner un indice, s'il te plaît ?

**Tuteur**

Voici un passage utile du cours pour votre problème :

Le Théorème 16.2.2 (Théorème de comparaison des séries à termes positifs, TCSTP, page 143 du PDF) dit que si on a deux séries à termes positifs \(\sum u_n\) et \(\sum v_n\) avec \(0 \le u_n \le v_n\) à partir d'un certain rang, alors :
1. Si \(\sum v_n\) converge, alors \(\sum u_n\) converge aussi.
2. Si \(\sum u_n\) diverge, alors \(\sum v_n\) diverge aussi.

De plus, la série diverge grossièrement si les termes \(u_n\) ne tendent pas vers 0 (Définition 16.1.13, page 142).

Ici, on a \(k^{kn} \geq u_n > 0\). Mais puisque \(k \geq 2\), la suite \(k^{kn}\) tend vers \(+\infty\), donc ne peut pas être un majorant utile pour une série convergente, car les termes doivent tendre vers 0.

Pouvez-vous reformuler précisément ce que signifie \(k^{kn} \ge u_n\) dans le contexte d'une suite décroissante positive, et réfléchir sur ce qui en découle pour la limite de \((u_n)\) ? Cela vous aidera à avancer.

*Étape : Exercices du catalogue — HTTP 200 — 5.61 s.*

## Échange 4

**Élève**

Si on a pour tout \( n \geq n_0 \), \( k^{kn} \geq u_n \) avec \( k \geq 2 \) et \( (u_n) \) décroissante et strictemet positive, alors en particulier \( u_n \leq k^{kn} \). Or, \( k^{kn} \) est très grande, elle tend vers \( +\infty \) quand \( n \to +\infty \).

Mais ça ne peut pas être possible car \(u_n\) est strictement positive et décroissante, donc \( u_n \) doit tendre vers une limite \( \ell \geq 0 \). Or, la majoration \( k^{kn} \ge u_n \) avec \( k^{kn} \to +\infty \) ne dit rien de la limite de \( u_n \), sauf que \( u_n \) est bornée supérieurement par quelque chose qui tend vers l'infini. Ça n'impose pas forcément que \( u_n \to 0 \).

Donc je pense qu'il y a un problème dans l'expression \( k^{kn} \geq u_n \), ou que je ne comprends pas bien l'énoncé.

Peux-tu me redonner précisément l'inégalité ? Parce que une majoration par \( k^{kn} \) ne permet pas d'obtenir la divergence de la série \( \sum u_n \). En revanche, si on avait une minoration du type \( u_n \geq \frac{1}{k^{kn}} \), ce serait un terme positif non négligeable, et la série pourrait diverger. Est-ce que c'était plutôt ça ?

**Tuteur**

L’énoncé donné contient une incohérence dans l’inégalité : la majoration \( k^{kn} \geq u_n \) avec \( k \geq 2 \) ne peut pas justifier la divergence car \( k^{kn} \to +\infty \), ce qui ne donne aucune information utile sur la limite ni la décroissance de \( u_n \).

Je dois changer d’exercice. 

Je vous propose donc un autre exercice du chapitre Séries numériques. Voici l’énoncé :

Soit \((\varepsilon_n)_{n \in \mathbb{N}}\) une suite de réels dans \(]0,1[\), telle que \(\varepsilon_n \to 0\). Pour tout \(n \in \mathbb{N}^*\), on pose 
\[
p_n = \prod_{i=1}^n (1 - \varepsilon_i).
\]
Montrer que 
\[
p_n \to 0 \iff \sum \varepsilon_n \text{ diverge.}
\]

Donnez votre réponse.

*Étape : Exercices du catalogue — HTTP 200 — 32.31 s.*

## Échange 5

**Élève**

On étudie la suite \( p_n = \prod_{i=1}^n (1 - \varepsilon_i) \) avec \(\varepsilon_n \in (0,1)\) et \(\varepsilon_n \to 0\).

On veut montrer que \( p_n \to 0 \) si et seulement si la série \(\sum \varepsilon_n\) diverge.

**Sens direct** : Si \(\sum \varepsilon_n\) diverge, alors \(\prod (1 - \varepsilon_n)\) tend vers 0.

Pour voir cela, on peut utiliser l'équivalence \(\ln(1 - x) \sim -x\) quand \(x \to 0\). Ainsi,
\[
\ln p_n = \sum_{i=1}^n \ln(1 - \varepsilon_i) \sim - \sum_{i=1}^n \varepsilon_i.
\]
Si \(\sum \varepsilon_n = +\infty\), alors \(\ln p_n \to -\infty\), donc \(p_n \to 0\).

**Sens réciproque** : Si \(p_n \to 0\), alors la suite \(\ln p_n \to -\infty\). Comme pour \(n\) grand,
\[
\ln p_n = \sum_{i=1}^n \ln(1 - \varepsilon_i) \sim - \sum_{i=1}^n \varepsilon_i,
\]
on en déduit que la série \(\sum \varepsilon_n\) diverge.

**Conclusion** : \(p_n \to 0 \iff \sum \varepsilon_n \text{ diverge}\).

**Tuteur**

Votre raisonnement est correct : en utilisant \(\ln p_n = \sum_{i=1}^n \ln(1 - \varepsilon_i)\) et l'équivalence \(\ln(1-x) \sim -x\) lorsque \(x \to 0\), vous établissez bien que \(p_n \to 0\) si et seulement si \(\sum \varepsilon_n\) diverge.

Souhaitez-vous passer à un autre exercice ou faire une question de cours sur ce chapitre ?

*Étape : Exercices du catalogue — HTTP 200 — 3.45 s.*

## Échange 6

**Élève**

Je préfère passer à un autre exercice pour bien consolider ma compréhension des séries numériques.

**Tuteur**

Voici un nouvel exercice :

Règle de Duhamel  
Soit \(\sum a_n\) une série à termes strictement positifs.

1. On suppose qu’il existe \(\alpha \in \mathbb{R}\) tel que
\[
\frac{a_{n+1}}{a_n} = 1 - \frac{\alpha}{n} + o\left(\frac{1}{n}\right).
\]
Montrer que si \(\alpha > 1\), alors \(\sum a_n\) converge et si \(\alpha < 1\), alors \(\sum a_n\) diverge.

2. Déterminer la nature de la série \(\sum a_n\), où
\[
a_n = \frac{2 \times 4 \times \cdots \times (2n - 2) \times (2n)}{3 \times 5 \times \cdots \times (2n - 1) \times (2n + 1)}.
\]

Donnez votre raisonnement pour la première question.

*Étape : Exercices du catalogue — HTTP 200 — 8.72 s.*

## Échange 7

**Élève**

Pour la première question, on considère une série à termes strictement positifs \(\sum a_n\) telle que

\[
\frac{a_{n+1}}{a_n} = 1 - \frac{\alpha}{n} + o\left( \frac{1}{n} \right).
\]

L'idée est d'étudier le comportement asymptotique des termes \(a_n\) à partir du rapport de deux termes consécutifs :

1. Si \(\alpha > 1\), on peut montrer que \(a_n\) décroît suffisamment vite pour que la série converge.
   
En effet, en utilisant le fait que 
\[
\ln a_{n+1} - \ln a_n = \ln \frac{a_{n+1}}{a_n} \sim -\frac{\alpha}{n},
\]
on peut approximer la somme des différences logarithmiques pour obtenir
\[
\ln a_n \sim -\alpha \ln n + C = \ln \left( \frac{C'}{n^\alpha} \right),
\]
c’est-à-dire que
\[
a_n \sim \frac{C'}{n^\alpha}.
\]
La série \(\sum a_n\) est donc comparable à une série de Riemann \(\sum \frac{1}{n^\alpha}\).

La convergence ou divergence de la série suit celle de la série de Riemann : convergente si \(\alpha > 1\) et divergente si \(\alpha \leq 1\).

2. Dans le cas \(\alpha < 1\), on retrouve donc la divergence car la série est similaire à une série de Riemann avec un exposant inférieur ou égal à 1.

Ainsi, la règle de Duhamel se ramène à comparer le rapport \(\frac{a_{n+1}}{a_n}\) à l’expression \(1 - \frac{\alpha}{n}\) et utiliser l'équivalent pour déduire la nature de la série.

**Tuteur**

Votre raisonnement pour la première question est pertinent et correct dans l'essentiel : vous avez utilisé la transformation logarithmique pour déduire un équivalent asymptotique de \(a_n\), aboutissant à une comparaison avec une série de Riemann.

Pour approfondir, pouvez-vous détailler pourquoi, dans le cas \(\alpha < 1\), la série \(\sum a_n\) diverge, en explicitant la borne inférieure ou un argument rigoureux qui exclut la convergence ? Cela permettra de clore proprement la justification pour ce cas.

*Étape : Exercices du catalogue — HTTP 200 — 49.03 s.*

## Échange 8

**Élève**

Dans le cas \( \alpha < 1 \), on a l'équivalent \( a_n \sim \frac{C'}{n^\alpha} \) avec \( C' > 0 \). Or, la série de Riemann \(\sum \frac{1}{n^\alpha}\) diverge dès que \(\alpha \leq 1\). 

Ici, puisque \(\alpha < 1\), \(a_n\) décroît moins vite que \(\frac{1}{n}\), ce qui implique que la série \(\sum a_n\) ne peut pas converger.

Plus précisément, pour \(n\) assez grand, on peut trouver une constante \(c > 0\) telle que \(a_n \geq \frac{c}{n^\alpha}\). Comme \(\sum \frac{1}{n^\alpha}\) diverge, le critère de comparaison directe avec termes positifs garantit la divergence de \(\sum a_n\).

Ainsi, la série diverge rigoureusement lorsque \(\alpha < 1\).

**Tuteur**

Votre complément est très bien argumenté pour la première question.

Passons maintenant à la seconde question : 

Déterminez la nature de la série \(\sum a_n\) où 
\[
a_n = \frac{2 \times 4 \times \cdots \times (2n - 2) \times (2n)}{3 \times 5 \times \cdots \times (2n - 1) \times (2n + 1)}.
\]

Commencez par analyser le rapport \(\frac{a_{n+1}}{a_n}\) et déduisez-en sa nature grâce à la règle de Duhamel vue précédemment. Quelle est votre réponse ?

*Étape : Exercices du catalogue — HTTP 200 — 74.02 s.*

## Échange 9

**Élève**

Pour étudier la nature de la série de terme général
\[
a_n = \frac{2 \times 4 \times \cdots \times (2n)}{3 \times 5 \times \cdots \times (2n+1)},
\]
je commence par calculer le rapport
\[
\frac{a_{n+1}}{a_n} = \frac{\frac{2 \times 4 \times \cdots \times (2n) \times (2n+2)}{3 \times 5 \times \cdots \times (2n+1) \times (2n+3)}}{\frac{2 \times 4 \times \cdots \times (2n)}{3 \times 5 \times \cdots \times (2n+1)}} = \frac{2n+2}{2n+3}.
\]

Je simplifie donc :
\[
\frac{a_{n+1}}{a_n} = \frac{2n+2}{2n+3} = 1 - \frac{1}{2n+3}.
\]

Pour \(n\) grand, on peut écrire
\[
\frac{a_{n+1}}{a_n} = 1 - \frac{1}{2n} + o\left(\frac{1}{n}\right).
\]

On reconnait la forme de la règle de Duhamel avec \(\alpha = \frac{1}{2}\).

Or, puisque \(\alpha = \frac{1}{2} < 1\), la règle de Duhamel dit que la série \(\sum a_n\) diverge.

Donc, la série \(\sum a_n\) est divergente.

**Tuteur**

Vous avez démontré correctement que pour la série donnée, le rapport de termes consécutifs admet un développement donnant \(\alpha = \frac{1}{2}\), strictement inférieur à 1. La règle de Duhamel s'applique donc et induit la divergence de la série.

Ainsi, la série \(\sum a_n\) est divergente.

Souhaitez-vous approfondir un point particulier dans ce chapitre ou poursuivre avec un autre exercice ?

*Étape : Exercices du catalogue — HTTP 200 — 39.89 s.*

## Échange 10

**Élève**

Je souhaite poursuivre avec un autre exercice, merci.

**Tuteur**

Voici un nouvel exercice.

Soit \((u_n)\) une suite décroissante de réels qui tend vers 0.

Montrer que
\[
\sum u_n
\]
et
\[
\sum n (u_n - u_{n+1})
\]
ont la même nature.

Lorsqu'elles sont définies, comparer les sommes de ces deux séries.

Donnez votre réponse.

*Étape : Exercices du catalogue — HTTP 200 — 5.3 s.*

## Échange 11

**Élève**

On considère une suite décroissante \\((u_n)\\) qui tend vers 0.

Calculons la somme partielle de \\(\sum_{k=1}^n n (u_n - u_{n+1})\\) :  
Plus précisément, on regarde la série de terme général \\(v_n = n(u_n - u_{n+1})\\).

Remarquons que  
\[
\sum_{k=1}^n k (u_k - u_{k+1}) = \sum_{k=1}^n (k u_k - k u_{k+1}) = \sum_{k=1}^n k u_k - \sum_{k=1}^n k u_{k+1}.
\]

Décalons l'indice dans la deuxième somme :  
\[
\sum_{k=1}^n k u_{k+1} = \sum_{k=2}^{n+1} (k-1) u_k = \sum_{k=2}^{n+1} k u_k - \sum_{k=2}^{n+1} u_k.
\]

Donc,
\[
\sum_{k=1}^n k (u_k - u_{k+1}) = \sum_{k=1}^n k u_k - \sum_{k=2}^{n+1} k u_k + \sum_{k=2}^{n+1} u_k = u_1 - (n+1) u_{n+1} + \sum_{k=2}^{n+1} u_k.
\]

Comme \\(u_n \to 0\\), \\((n+1) u_{n+1} \to 0\\) si la suite \\(u_n\\) est décroissante et tend vers zéro suffisamment vite.

Enfin, on obtient  
\[
\sum_{k=1}^n k (u_k - u_{k+1}) = u_1 + \sum_{k=2}^{n+1} u_k - (n+1) u_{n+1} \sim \sum_{k=1}^n u_k \quad \text{quand } n \to \infty.
\]

Par conséquent, les séries \\(\sum u_n\\) et \\(\sum n (u_n - u_{n+1})\\) ont la même nature (convergence ou divergence).

De plus, lorsqu'elles convergent, leurs sommes sont reliées par  
\[
\sum_{n=1}^\infty n (u_n - u_{n+1}) = u_1 + \sum_{n=2}^\infty u_n,
\]
c'est-à-dire que ces deux séries ont la même somme.

**Tuteur**

Votre démonstration met bien en œuvre la manipulation des sommes partielles et le décalage d'indices pour montrer que les deux séries ont des sommes partiellement reliées.

Toutefois, il manque une justification rigoureuse supplémentaire pour garantir que \((n+1) u_{n+1} \to 0\) sous l'hypothèse de décroissance et de limite nulle de \((u_n)\). Cette hypothèse est nécessaire pour l'équivalence asymptotique des sommes partielles.

De plus, la comparaison précise des sommes lorsque les séries convergent mérite d'être explicitée avec un encadrement propre.

Merci de reformuler précisément ces points avant qu'on puisse valider ce résultat.

*Étape : Exercices du catalogue — HTTP 200 — 32.59 s.*

## Échange 12

**Élève**

Pour justifier rigoureusement que \\((n+1) u_{n+1} \\to 0\\), nous utilisons le fait que \\((u_n)\\) est décroissante et tend vers 0.

Comme \\(u_n \\to 0\\) et \\(u_n > 0\\) pour \\(n\\) grand (sinon on peut considérer la suite en valeur absolue), et que \\(u_n\\) décroît, on sait que \\(n u_n \\to 0\\) n’est pas toujours vrai, mais la décroissance impose que \\(u_n\\) ne peut pas décroître trop lentement.

Cependant, dans cette démonstration et pour l’équivalence, on suppose implicitement que \\(n u_n \\to 0\\) (ou que la décroissance est suffisante), ce qui garantit que le terme \\((n+1)u_{n+1}\\) est un terme négligeable dans la limite.

Ainsi, lorsque \\(n \\to +\\infty\\),
\\[
\\sum_{k=1}^n k (u_k - u_{k+1}) = u_1 + \\sum_{k=2}^{n+1} u_k - (n+1) u_{n+1} \\sim u_1 + \\sum_{k=2}^n u_k,
\\]
et la différence \\((n+1) u_{n+1}\\) tend vers 0.

Concernant la somme des séries lorsque celles-ci convergent, l’égalité limite donne :

\\[
\\sum_{n=1}^{+\\infty} n (u_n - u_{n+1}) = u_1 + \\sum_{n=2}^{+\\infty} u_n = \\sum_{n=1}^{+\\infty} u_n.
\\]

Ainsi, les deux séries ont la même somme quand elles convergent.

En résumé :
- Sous l’hypothèse que \\(u_n\\) décroît vers 0 assez vite pour que \\((n+1) u_{n+1} \\to 0\\),
- on a la même nature (convergence ou divergence) des séries \\(\\sum u_n\\) et \\(\\sum n (u_n - u_{n+1})\\),
- et leurs sommes coïncident si convergence il y a.

**Tuteur**

Vous avez bien identifié que l'hypothèse \((n+1) u_{n+1} \to 0\) est essentielle pour déduire l'équivalence asymptotique des sommes partielles, et vous avez présenté une justification intuitive basée sur la décroissance de \((u_n)\).

Pour consolider cette démarche, il faudrait préciser ou démontrer explicitement dans quelles conditions sur la décroissance de \((u_n)\) on a cette propriété, et pourquoi cette condition garantit que terme correctif \((n+1) u_{n+1}\) est négligeable.

Voulez-vous que nous approfondissions cette démonstration rigoureuse de cette hypothèse clé ou préférez-vous changer d'exercice ?

*Étape : Exercices du catalogue — HTTP 200 — 24.73 s.*

## Échange 13

**Élève**

Je préfère changer d'exercice, merci.

**Tuteur**

Bien noté, changeons d'exercice.

Je vous propose :

Soit \((u_n)\) une suite de réels positifs. On pose \(v_n = \frac{u_n}{1 + u_n}\).

Montrer que les séries \(\sum u_n\) et \(\sum v_n\) sont de même nature.

Donnez votre réponse.

*Étape : Exercices du catalogue — HTTP 200 — 3.92 s.*

## Échange 14

**Élève**

On considère la suite \\((u_n)\\) de réels positifs et la suite \\((v_n)\\) définie par \\(v_n = \\frac{u_n}{1 + u_n}\\).

1. Si la série \\(\\sum u_n\\) converge, alors \\(u_n \\to 0\\). Pour \\(n\\) assez grand, on a donc aussi \\(v_n \\sim u_n\\), car
\\[
v_n = \\frac{u_n}{1 + u_n} = u_n \\cdot \\frac{1}{1 + u_n} \\sim u_n.
\\]
Ainsi, les termes \\(v_n\\) sont asymptotiquement équivalents à \\(u_n\\), donc la série \\(\\sum v_n\\) converge aussi par critère de comparaison.

2. Si la série \\(\\sum u_n\\) diverge, alors assez souvent \\(u_n\\) est non négligeable. On remarque que pour tout \\(n\\),
\\[
v_n = \\frac{u_n}{1 + u_n} \\leq u_n.
\\]
De plus, puisque \\(u_n \\geq 0\\),
\\[
v_n = \\frac{u_n}{1 + u_n} \\geq \\frac{u_n}{1 + M}
\\]
où \\(M = \\sup_n u_n\\) si cette borne existe, sinon on peut argumenter localement.

Mais surtout, si \\(u_n\\) ne tend pas vers 0, la série des termes \\(v_n\\) aussi ne tend pas vers 0, donc diverge.

Enfin, pour \\(u_n\\) petit, \\(v_n \\sim u_n\\), donc si \\(\\sum v_n\\) converge, \\(\\sum u_n\\) aussi.

---

En conclusion, \\(\\sum u_n\\) et \\(\\sum v_n\\) sont de même nature : elles convergent ou divergent simultanément.

**Tuteur**

L’étape exercices comporte plusieurs réussites pertinentes mais présente encore des lacunes sur certains points essentiels.

Je vous invite à poursuivre vos révisions en approfondissant la justification rigoureuse des hypothèses sur la décroissance rapide dans l'exercice 17.23, et la preuve par blocs dyadiques sur 17.16, ainsi que le traitement complet des séries pondérées sur 17.13.

Souhaitez-vous que je vous propose un exercice plus ciblé sur ces aspects, ou préférez-vous changer de chapitre ?

*Étape : Exercices du catalogue — HTTP 200 — 24.72 s.*

## Échange 15

**Élève**

Je voudrais continuer avec un exercice plus ciblé sur la décroissance rapide et la preuve par blocs dyadiques pour mieux comprendre ces points essentiels.

**Tuteur**

Nous devons terminer l'étape en cours avant de poursuivre. Revenons à l'exercice précédent :

Soit \((u_n)\) une suite décroissante de réels qui tend vers 0.

Montrer que les séries \(\sum u_n\) et \(\sum n (u_n - u_{n+1})\) ont la même nature.

Lorsqu'elles sont définies, comparer les sommes de ces deux séries.

*Étape : Exercices du catalogue — HTTP 200 — 5.84 s.*

## Échange 16

**Élève**

Reprenons cet exercice rigoureusement.

Soit \((u_n)\) décroissante vers 0. Posons \(S_n = \sum_{k=1}^n u_k\) et \(T_n = \sum_{k=1}^n k(u_k - u_{k+1})\).

Calculons \(T_n\) par sommation par parties :

\[
T_n = \sum_{k=1}^n k(u_k - u_{k+1}) = \sum_{k=1}^n k u_k - \sum_{k=1}^n k u_{k+1}.
\]

Décalons l’indice dans la deuxième somme :

\[
\sum_{k=1}^n k u_{k+1} = \sum_{k=2}^{n+1} (k - 1) u_k = \sum_{k=2}^{n+1} k u_k - \sum_{k=2}^{n+1} u_k.
\]

D’où

\[
T_n = \sum_{k=1}^n k u_k - \sum_{k=2}^{n+1} k u_k + \sum_{k=2}^{n+1} u_k = u_1 - (n+1) u_{n+1} + \sum_{k=2}^{n+1} u_k.
\]

Par suite

\[
T_n = \sum_{k=1}^{n+1} u_k - (n+1) u_{n+1}.
\]

Or, puisque \((u_n)\) est décroissante vers 0, on a \(u_{n+1} \le u_n\), donc

\[
(n+1) u_{n+1} \to 0 \quad \iff \quad u_n = o\left(\frac{1}{n}\right).
\]

Dans le cas où \((n u_n) \to 0\), on obtient

\[
T_n \sim S_{n+1} \quad \text{quand } n \to \infty,
\]

donc les séries \(\sum u_n\) et \(\sum n(u_n - u_{n+1})\) ont la même nature (convergence ou divergence).

Par ailleurs, si ces séries convergent, leurs sommes limite vérifient

\[
\sum_{n=1}^\infty n (u_n - u_{n+1}) = \sum_{n=1}^\infty u_n,
\]

car \(\lim_{n \to \infty} (n+1) u_{n+1} = 0\).

En revanche, si \(\limsup n u_n > 0\), alors \((n+1) u_{n+1}\) ne tend pas vers zéro, et par conséquent la différence \(T_n - S_{n+1}\) ne tend pas vers zéro, ce qui modifie la comparaison.

Ainsi la condition \((n u_n) \to 0\) est nécessaire pour que les deux séries aient la même somme et la même nature. En tout état de cause, sous l’hypothèse initiale de décroissance et convergeant suffisamment vite, la nature est la même et les sommes coïncident.

**Tuteur**

Vous avez fourni une démonstration plus rigoureuse reliant la nature des séries \(\sum u_n\) et \(\sum n(u_n - u_{n+1})\) ainsi qu'une condition nécessaire sur la décroissance de \((u_n)\), à savoir \((n u_n) \to 0\).

Cependant, cette hypothèse additionnelle n'était pas donnée dans l'énoncé, ce qui la rend une hypothèse extérieure. Son absence dans l'énoncé initial mériterait d'être signalée et reformulée par vous, pour une compréhension complète.

Il est normal que vous ayez ressenti le besoin d'introduire cette condition. Pouvez-vous reformuler précisément cette erreur d'hypothèse non donnée, expliquer pourquoi elle est nécessaire, puis la corriger dans votre raisonnement ?

*Étape : Exercices du catalogue — HTTP 200 — 26.3 s.*

## Échange 17

**Élève**

L’erreur dans mon raisonnement précédent est d’avoir implicitement supposé que \((n u_n) \to 0\) sans que cette hypothèse soit donnée dans l’énoncé. Or, cette condition est nécessaire pour que le terme correctif \((n+1) u_{n+1}\) tendant vers zéro permette d’avoir \(T_n \sim S_{n+1}\), donc la même nature et la même somme des séries.

Sans cette hypothèse, \((n u_n)\) peut ne pas tendre vers zéro, ce qui fait que la différence entre les sommes partielles
\[
T_n - S_{n+1} = - (n+1) u_{n+1}
\]
ne tend pas forcément vers zéro, empêchant d’assurer la même nature ou somme.

Pour corriger cela, il faut préciser dans la démonstration que :
- Si \((n u_n) \to 0\), alors on a bien l’équivalence des natures et des sommes.
- Si \(\limsup n u_n > 0\), on ne peut pas conclure ainsi.

En résumé, la proposition doit être reformulée en précisant cette condition supplémentaire sur la décroissance de \((u_n)\) pour garantir que les séries \(\sum u_n\) et \(\sum n (u_n - u_{n+1})\) ont la même nature et somme.

**Tuteur**

Voici un autre exercice pour vous :

Pour tout \(n \in \mathbb{N}^*\), on note :
\[
h_n = \sum_{k=1}^n \frac{1}{k}
\]
et
\[
u_n = h_n - \ln n.
\]

1. Trouver un équivalent de \(u_{n+1} - u_n\).

2. Déterminer la nature de la série
\[
\sum (u_{n+1} - u_n)
\]
puis en déduire la convergence de la suite \((u_n)\). On notera \(\gamma\) la limite de la suite \((u_n)\).

3. Montrer que
\[
h_n = \ln n + \gamma + o(1).
\]

4. Montrer qu’il existe \(\alpha\) et \(\beta\) tels que
\[
\sum_{k=1}^{2n} \frac{(-1)^k}{k} = \alpha h_{2n} + \beta h_n.
\]

5. En déduire que
\[
\sum_{k=1}^{+\infty} \frac{(-1)^k}{k} = -\ln 2.
\]

Soit \(\sigma \in \mathbb{R}\). On note \((w_n)\) la suite définie par : \(w_k = \sigma^k\) lorsque 4 divise \(k\) et \(w_k = \frac{1}{k}\) sinon. De plus, on note
\[
S_n = \sum_{k=1}^n w_k.
\]

6. Montrer que \((S_n)\) converge si et seulement si \(\sigma = -3\).

7. Étudier la nature et calculer la somme de la série
\[
\sum w_k.
\]

8. Question bonus : Soit \((\sigma_n)_{n \in \mathbb{N}} \in \mathbb{C}^N\), \(T\)-périodique. Donner une condition nécessaire et suffisante pour que
\[
\sum_{n \geq 1} \frac{\sigma_n}{n}
\]
soit semi-convergente.

Commencez par la première question.

*Étape : Exercices du catalogue — HTTP 200 — 81.55 s.*

## Échange 18

**Élève**

On commence par étudier la différence 
\[
u_{n+1} - u_n = (h_{n+1} - \ln (n+1)) - (h_n - \ln n) = (h_{n+1} - h_n) - (\ln (n+1) - \ln n).
\]

On sait que 
\[
h_{n+1} - h_n = \frac{1}{n+1}
\]
et 
\[
\ln (n+1) - \ln n = \ln\left(1 + \frac{1}{n}\right) \sim \frac{1}{n} - \frac{1}{2 n^2} + o\left(\frac{1}{n^2}\right).
\]

Donc :
\[
u_{n+1} - u_n = \frac{1}{n+1} - \left(\frac{1}{n} - \frac{1}{2 n^2} + o\left(\frac{1}{n^2}\right)\right) = \frac{1}{n+1} - \frac{1}{n} + \frac{1}{2 n^2} + o\left(\frac{1}{n^2}\right).
\]

Or 
\[
\frac{1}{n+1} - \frac{1}{n} = -\frac{1}{n(n+1)} \sim -\frac{1}{n^2} + o\left(\frac{1}{n^2}\right).
\]

Donc en sommant ces termes :
\[
u_{n+1} - u_n \sim -\frac{1}{n^2} + \frac{1}{2 n^2} = -\frac{1}{2 n^2}.
\]

Ainsi, un équivalent de \(u_{n+1} - u_n\) est :
\[
u_{n+1} - u_n \sim -\frac{1}{2 n^2} \quad \text{quand } n \to +\infty.
\]

**Tuteur**

Vous avez correctement trouvé un équivalent asymptotique de \(u_{n+1} - u_n\) :

\[
u_{n+1} - u_n \sim -\frac{1}{2n^2}.
\]

Cette expression vous permet d’examiner la nature de la série \(\sum (u_{n+1} - u_n)\).

Comment pouvez-vous conclure sur cette nature et en déduire la convergence de la suite \((u_n)\) ? Quel est le rôle de cette série des différences ici ?

*Étape : Exercices du catalogue — HTTP 200 — 85.23 s.*

## Échange 19

**Élève**

La série \\(\sum (u_{n+1} - u_n)\\) est une série télescopique, car \\(u_{n+1} - u_n\\) est la différence entre deux termes consécutifs de la suite \\((u_n)\\).

La somme partielle s’écrit :
\\[
S_N = \sum_{n=1}^N (u_{n+1} - u_n) = u_{N+1} - u_1.
\\]

Donc, la série \\(\sum (u_{n+1} - u_n)\\) converge si et seulement si la suite \\((u_n)\\) converge.

Comme on a trouvé que \\(u_{n+1} - u_n \sim -\frac{1}{2 n^2}\\), les différences sont négatives pour \\(n\\) grand, donc \\((u_n)\\) est presque décroissante pour \\(n\\) assez grand.

La somme des termes équivalents \\(-\frac{1}{2 n^2}\\) est convergente (car la série \\(\sum 1/n^2\\) converge).

Cela suggère que les différences \\((u_{n+1} - u_n)\\) sont sommables, donc la suite \\((u_n)\\) converge vers une limite \\(\gamma\\).

Ainsi, la série \\(\sum (u_{n+1} - u_n)\\) converge et la suite \\((u_n)\\) converge vers une limite \\(\gamma\\).

**Tuteur**

Votre raisonnement est clair et rigoureux : 

- La série \(\sum (u_{n+1} - u_n)\) est télescopique et converge si et seulement si \((u_n)\) converge.
- L’équivalent trouvé pour \(u_{n+1} - u_n\) montre que \((u_n)\) est presque décroissante et que la série des différences est sommable.
- Cela assure la convergence de \((u_n)\) vers une limite \(\gamma\).

Poursuivez maintenant la question 3 pour montrer que 
\[
h_n = \ln n + \gamma + o(1).
\]

Comment procédez-vous ?

*Étape : Exercices du catalogue — HTTP 200 — 66.61 s.*

## Échange 20

**Élève**

On a défini \\( u_n = h_n - \ln n \\) et on vient de montrer que \\( (u_n) \\) converge vers \\( \gamma \\).

Par définition, cela s'écrit :  
\[
h_n - \ln n \xrightarrow[n \to +\infty]{} \gamma,
\]
donc  
\[
h_n = \ln n + \gamma + o(1).
\]

Autrement dit, la différence entre \( h_n \) et \( \ln n + \gamma \) tend vers 0 quand \( n \to +\infty \), ce qui donne exactement l’équivalent demandé.

**Tuteur**

Votre raisonnement est correct, la série des différences est télescopique, donc la convergence de \(\sum (u_{n+1} - u_n)\) implique la convergence de \((u_n)\), et inversement.

L'équivalent asymptotique \(-\frac{1}{2n^2}\) montre que la série des différences converge, donc la suite \((u_n)\) converge vers une limite \(\gamma\).

Ainsi,
\[
h_n = \ln n + \gamma + o(1).
\]

Souhaitez-vous poursuivre avec la question suivante, qui porte sur l'existence de coefficients \(\alpha, \beta\) tels que
\[
\sum_{k=1}^{2n} \frac{(-1)^k}{k} = \alpha h_{2n} + \beta h_n,
\]
ou préférez-vous un rappel ou un exercice différent ?

*Étape : Exercices du catalogue — HTTP 200 — 89.73 s.*
