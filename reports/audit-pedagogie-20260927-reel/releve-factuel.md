# Audit pédagogique — relevé factuel

Sessions réelles via l'interface HTTP et les APIs OpenAI/Pipelex. Seul l'élève est joué par un modèle ; le tuteur et ses outils ne sont pas simulés.

Un seul compte, sans remise à zéro, dans l'ordre faible → moyen → fort. La comparaison est influencée par cet ordre et les acquis conservés. Le niveau chiffré évolue lors des évaluations du catalogue, pas lors des acquisitions de cours.

Chaque session est plafonnée à 20 échanges (choix du chapitre inclus en E1). « Avant l'échange 10 » signifie E1 à E9. Une session peut s'arrêter au plafond sans que le tuteur ait terminé sa progression.

Les repetitions ci-dessous sont détectées par couple source/nature pour le cours et par identifiant pour le catalogue ; elles nécessitent une lecture des conversations pour distinguer rappel, question équivalente et nouvelle acquisition.

Attention : ce tableau compte les tâches enregistrées par le serveur. Un exercice affiché librement sans outil (notamment une répétition) peut apparaître plus tôt dans la conversation ; le bilan relu corrige cette différence.

| Profil | Session | Échanges | Application enregistrée | Catalogue enregistré | Niveau | Nouveaux acquis |
|---|---:|---:|---:|---:|---|---:|
| faible | 1 | 20 | 9 | 14 | 1.5 → 2.4 | 4 |
| faible | 2 | 20 | — | 1 | 2.4 → 2.9 | 0 |
| faible | 3 | 20 | — | 6 | 2.9 → 2.8 | 0 |
| faible | 4 | 20 | — | 5 | 2.8 → 3.0 | 0 |
| moyen | 1 | 15 | — | 1 | 3.0 → 3.2 | 0 |

## Faible — session 1

[Conversation complète](faible-session-1.md). 20 échanges. Niveau 1.5 → 2.4. 4 nouveaux acquis.

Première application : 9. Premier exercice du catalogue : 14.

Évaluations : incorrecte : 4, incomplete : 4, correcte : 7.

### E1 — cours / definition ; difficulté non chiffrée

Donnez-moi la définition d'une série convergente.

Source : 16.1.5. Acquise en fin de session : True. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E4 — cours / theoreme ; difficulté non chiffrée

Donnez-moi l'énoncé du théorème fondamental assurant la convergence d'une série absolument convergente.

Source : 16.2.4. Acquise en fin de session : True. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E5 — demonstration / demonstration ; difficulté non chiffrée

Donnez-moi la démonstration du théorème fondamental assurant la convergence d'une série absolument convergente.

Source : 16.2.4. Acquise en fin de session : True. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E9 — applications / applications ; difficulté non chiffrée

Résoudre l'exercice d'application sur la convergence absolue d'une série.

Source : 16.2.6. Acquise en fin de session : True. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E14 — exercices / catalogue ; difficulté catalogue 2/5

Grâce à une comparaison entre série et intégrale, déterminer un équivalent de
$$\sum_{k=2}^n \ln k.$$ En déduire la nature de la
série de terme général
$$u_n = \left( \sum_{k=2}^n \ln k \right)^{-1}.$$

Source : 17.6. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E16 — exercices / catalogue ; difficulté catalogue 3/5

Soit $(\varepsilon_n)_{n \in \mathbb{N}}$ une suite de réels de $]0,1[$, telle que $\varepsilon_n \xrightarrow[n \to +\infty]{} 0$. Pour tout $n \in \mathbb{N}^*$, on pose 
$$p_n = \prod_{i=1}^n (1 - \varepsilon_i).$$
Montrer que 
$$p_n \xrightarrow[n \to +\infty]{} 0 \iff \sum \varepsilon_n \text{ diverge.}$$

Source : 17.9. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E18 — exercices / catalogue ; difficulté catalogue 4/5

Soit $(a_n)_{n\geq 1}$ une suite de nombres complexes telle que la série $\sum_{n=1}^\infty a_n$ est absolument convergente. On suppose que pour tout $k \in \mathbb{N}^*$,
$$
\sum_{n=1}^\infty a_n n^k = 0.
$$
Que peut-on dire de la suite $(a_n)_{n\geq 1}$ ?

Source : 17.20. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

## Faible — session 2

[Conversation complète](faible-session-2.md). 20 échanges. Niveau 2.4 → 2.9. 0 nouveaux acquis.

Première application : aucune. Premier exercice du catalogue : 1.

Évaluations : correcte : 2, incomplete : 4.

### E1 — exercices / catalogue ; difficulté catalogue 2/5

Soit $(u_n)$ une suite de réels positifs. On pose $v_n = \frac{u_n}{1 + u_n}$. Montrer que les séries $\sum u_n$ et $\sum v_n$ sont de même nature.

Source : 17.12. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E7 — exercices / catalogue ; difficulté catalogue 3/5

Règle de Cauchy

1. Soit $(a_n)_{n \in \mathbb{N}} \in \mathbb{S}(\mathbb{C})$ telle que

$$\lim_{n \to +\infty} \sqrt[n]{|a_n|} = \ell \in \mathbb{R}^+ \cup \{+\infty\}.$$

- Si $\ell < 1$, montrer que

$$\sum a_n$$

est absolument convergente.

- Si $\ell > 1$ ou si $\ell = 1^+$, montrer que

$$\sum a_n$$

diverge grossièrement.

- Lorsque $\ell = 1$, montrer qu’on ne peut pas conclure.

2. En déduire la nature des séries

$$\sum \frac{n + 1}{2n + 5} a_n$$

et

$$\sum \frac{n \ln n}{(\ln n)^n}.$$

Source : 17.13. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E16 — exercices / catalogue ; difficulté catalogue 3/5

\text{\alpha désigne un réel strictement positif. Pour tout } n \in \mathbb{N}, \text{ on note } a_n = \frac{(n \alpha)^n}{\sum_{k=0}^n (k!)}.\
Déterminer la nature de la série } \sum a_n.

Source : 17.14. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

## Faible — session 3

[Conversation complète](faible-session-3.md). 20 échanges. Niveau 2.9 → 2.8. 0 nouveaux acquis.

Première application : aucune. Premier exercice du catalogue : 6.

Évaluations : incorrecte : 3, correcte : 2, incomplete : 1.

### E6 — exercices / catalogue ; difficulté catalogue 3/5

Soit $a, b, c \in \mathbb{C}$. Étudier la série \(\sum u_n\), où \(u_n = a \sqrt{n} + b \sqrt{n+1} + c \sqrt{n+2}\).

Source : 17.11. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E12 — exercices / catalogue ; difficulté catalogue 3/5

Soit $(u_n)$ une suite réelle décroissante qui tend vers $0$. 
Montrer que les séries 
$$\sum_{n} u_n$$ 
 et 
$$\sum_{n} 2^n u_{2^n}$$ 
ont la même nature. 
En déduire la nature de 
$$\sum_{n \geq 2} \frac{1}{n (\ln n)^{\beta}},$$ 
où $\beta \in \mathbb{R}$.

Source : 17.16. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

## Faible — session 4

[Conversation complète](faible-session-4.md). 20 échanges. Niveau 2.8 → 3.0. 0 nouveaux acquis.

Première application : aucune. Premier exercice du catalogue : 5.

Évaluations : incomplete : 3, correcte : 3, incorrecte : 1.

### E5 — exercices / catalogue ; difficulté catalogue 3/5

Soit $(a_n)$ une suite décroissante de réels positifs. On suppose que la série $\sum_{n=0}^{+\infty} a_n$ converge. Montrer que $n a_n \xrightarrow[n \to +\infty]{} 0$.

Source : 17.15. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E9 — exercices / catalogue ; difficulté catalogue 3/5

Soient $a \in \mathbb{R}^*_+$ et $\alpha \in \mathbb{R}$. Nature de la série $\sum a_n$ où
$$a_n = \frac{n^{\alpha}}{(1+a)(1+a^2) \dots (1+a^n)}.$$

Source : 17.18. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

## Moyen — session 1

[Conversation complète](moyen-session-1.md). 15 échanges. Niveau 3.0 → 3.2. 0 nouveaux acquis.

Première application : aucune. Premier exercice du catalogue : 1.

Évaluations : incomplete : 4.

### E1 — exercices / catalogue ; difficulté catalogue 3/5

Soit \(\varphi : \mathbb{N}^* \to \mathbb{N}^*\) une application injective. Montrer que la série

$$\sum_{n=1}^{+\infty} \frac{1}{\varphi(n) n^2}$$

diverge.

Source : 17.22. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.

### E3 — exercices / catalogue ; difficulté catalogue 2/5

Calculer
$$\sum_{n=2}^{+\infty} \ln\left(1 + \frac{(-1)^n}{n}\right).$$

Source : 17.26. Acquise en fin de session : False. Même source/nature déjà proposée : False. Déjà validée avant cette proposition : False.
