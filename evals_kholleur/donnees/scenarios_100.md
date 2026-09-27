# X-IA — 100 scénarios pour un khôlleur qui fait réagir

Chaque cas possède trois réactions : justification, erreur persistante, blocage. Les exemples de relance sont indicatifs : on juge le sens et l'adaptation. Les références sont synthétiques et ne constituent pas des annales officielles.

Statut : scénarios préparés ; aucun résultat de réussite du modèle n'est déduit de la validation des fichiers. Voir ../README.md pour lancer des essais.

## K001 — Définition reformulée

Famille : definitions

**Question / contexte :** Définir la convergence d'une série réelle.

**Référence réservée à l'évaluateur :** La suite S_N=sum_{n=1}^N u_n converge vers un réel fini. u_n=S_n-S_{n-1} tend alors vers zéro.

**Première réponse de l'élève :** Les sommes des premiers termes se rapprochent d'un réel fini.

**Statut interne :** correcte

**Défi attendu :** Accepter la définition en mots et faire préciser la notation, sans redemander mot pour mot la définition.

**Exemple de relance, pas une phrase imposée :** Écrivez ces sommes S_N, puis exprimez u_N à l'aide de deux d'entre elles.

### Réaction : justifiee

Élève : S_N=sum_{n=1}^N u_n et u_N=S_N-S_{N-1}, donc u_N tend vers zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : u_N=S_N, donc les deux ont la même limite.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas distinguer un terme et une somme partielle.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K002 — Condition nécessaire prise pour suffisante

Famille : definitions

**Question / contexte :** La condition u_n tend vers zéro suffit-elle à la convergence de sum u_n ?

**Référence réservée à l'évaluateur :** Non : 1/n tend vers zéro mais la série harmonique diverge ; grouper de 2^k à 2^{k+1}-1 donne des blocs d'au moins 1/2.

**Première réponse de l'élève :** Oui, les termes deviennent négligeables.

**Statut interne :** incorrecte

**Défi attendu :** Faire construire le contre-exemple harmonique ; ne pas annoncer seulement « faux ».

**Exemple de relance, pas une phrase imposée :** Que donne votre argument avec u_n=1/n ? Examinez un bloc de 2^k termes.

### Réaction : justifiee

Élève : Chaque bloc de 2^k à 2^{k+1}-1 vaut au moins 1/2 : la condition ne suffit pas.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Les termes tendent vers zéro, donc même les blocs tendent forcément vers zéro.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Combien de termes contient ce bloc ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K003 — Divergence grossière

Famille : definitions

**Question / contexte :** Étudier sum_{n>=1} n/(n+1).

**Référence réservée à l'évaluateur :** Le terme général tend vers 1, donc ne tend pas vers zéro ; les sommes positives tendent vers +infini.

**Première réponse de l'élève :** Je vais calculer une primitive.

**Statut interne :** hors_sujet

**Défi attendu :** Faire identifier le test nécessaire avant une méthode plus lourde.

**Exemple de relance, pas une phrase imposée :** Quelle condition tout terme général d'une série convergente doit-il vérifier ici ?

### Réaction : justifiee

Élève : n/(n+1) tend vers 1, la condition nécessaire échoue.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Sa limite est finie, donc la série converge.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je confonds limite finie et limite nulle.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K004 — Positivité et sommes bornées

Famille : definitions

**Question / contexte :** Justifier : une série à termes positifs converge si ses sommes partielles sont majorées.

**Référence réservée à l'évaluateur :** Les sommes partielles sont croissantes par positivité, puis convergentes par croissance et majoration.

**Première réponse de l'élève :** Une suite bornée converge.

**Statut interne :** incorrecte

**Défi attendu :** Distinguer monotonie des sommes partielles et monotonie du terme général.

**Exemple de relance, pas une phrase imposée :** Quelle propriété supplémentaire des sommes partielles apporte la positivité ?

### Réaction : justifiee

Élève : Elles sont croissantes, et une suite croissante majorée converge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La positivité rend toute suite monotone, y compris le terme général.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je vois que S_{N+1}-S_N=u_{N+1}, sans savoir conclure.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K005 — Sommes bornées avec signes variables

Famille : definitions

**Question / contexte :** Des sommes partielles bornées suffisent-elles à faire converger une série réelle ?

**Référence réservée à l'évaluateur :** Non : sum_{n>=0}(-1)^n a des sommes partielles 1,0,1,0,..., bornées mais non convergentes.

**Première réponse de l'élève :** Oui, sinon elles partiraient à l'infini.

**Statut interne :** incorrecte

**Défi attendu :** Garder la convention n>=0 et distinguer convergence ordinaire d'une méthode de sommation.

**Exemple de relance, pas une phrase imposée :** Calculez les quatre premières sommes de sum_{n>=0}(-1)^n.

### Réaction : justifiee

Élève : Elles valent 1,0,1,0 : bornées, mais deux sous-suites ont des limites différentes.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La somme vaut 1/2, moyenne de 0 et 1.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas si l'indice commence à zéro ou à un.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K006 — Un nombre fini de termes

Famille : definitions

**Question / contexte :** Changer les dix premiers termes d'une série change-t-il sa convergence ou sa somme ?

**Référence réservée à l'évaluateur :** La nature est inchangée ; si la série converge, sa somme change de la somme finie des modifications.

**Première réponse de l'élève :** Cela ne change rien.

**Statut interne :** incomplete

**Défi attendu :** Faire préciser ce qui est invariant et ce qui ne l'est pas.

**Exemple de relance, pas une phrase imposée :** Et si j'ajoute 7 au premier terme seulement, que deviennent les sommes partielles ?

### Réaction : justifiee

Élève : À partir de ce terme elles sont augmentées de 7 : même nature, somme augmentée de 7.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La somme reste identique puisque la limite dépend seulement des grands indices.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas la différence entre nature et valeur.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K007 — Série et suite de termes

Famille : definitions

**Question / contexte :** Si sum u_n converge vers 3, quelle est la limite de u_n ?

**Référence réservée à l'évaluateur :** u_n tend vers zéro ; 3 est la limite des sommes partielles, pas celle des termes.

**Première réponse de l'élève :** u_n tend vers 3.

**Statut interne :** incorrecte

**Défi attendu :** Exiger une identité exacte ; une conclusion correcte issue de u_n=S_n/n n'est pas une justification.

**Exemple de relance, pas une phrase imposée :** Exprimez u_n en fonction de S_n et S_{n-1}, dont vous connaissez les limites.

### Réaction : justifiee

Élève : u_n=S_n-S_{n-1} tend vers 3-3=0.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : u_n=S_n/n tend vers zéro car c'est la moyenne.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Pourquoi soustraire deux sommes ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K008 — Restes et existence de la somme

Famille : definitions

**Question / contexte :** Définir R_N, reste d'une série convergente commençant à n=1.

**Référence réservée à l'évaluateur :** R_N=S-S_N=sum_{n=N+1}^inf u_n ; R_N tend vers zéro. La somme S doit exister.

**Première réponse de l'élève :** R_N=sum_{n=N}^inf u_n.

**Statut interne :** incomplete

**Défi attendu :** Repérer la convention d'indexation sans pénaliser une autre convention explicitement définie.

**Exemple de relance, pas une phrase imposée :** Si S_N s'arrête au terme u_N, quel est le premier terme qui manque ?

### Réaction : justifiee

Élève : Le premier est u_{N+1}, donc R_N=S-S_N.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : On soustrait S_N mais on garde aussi u_N dans le reste.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je perds le décalage d'un indice.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K009 — Critère de Cauchy : quantificateurs

Famille : definitions

**Question / contexte :** Énoncer le critère de Cauchy pour une série réelle.

**Référence réservée à l'évaluateur :** Pour tout epsilon>0, il existe N tel que pour tout q>=p>=N, |sum_{n=p}^q u_n|<epsilon.

**Première réponse de l'élève :** Pour n assez grand, |u_n|<epsilon.

**Statut interne :** incomplete

**Défi attendu :** Faire apparaître le contrôle uniforme des queues, pas seulement la condition nécessaire.

**Exemple de relance, pas une phrase imposée :** Le critère doit-il contrôler un seul terme ou toutes les sommes sur une tranche éloignée ?

### Réaction : justifiee

Élève : Il contrôle uniformément toutes les tranches p à q, pour q>=p>=N.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Il suffit de contrôler les tranches de longueur un.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas où placer « pour tout q ».

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K010 — Convergence complexe

Famille : definitions

**Question / contexte :** Quand une série de nombres complexes converge-t-elle ?

**Référence réservée à l'évaluateur :** Elle converge si et seulement si les séries des parties réelles et imaginaires convergent ; la convergence des modules est suffisante, pas nécessaire.

**Première réponse de l'élève :** Il faut que la série des modules converge.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer convergence et convergence absolue dans C.

**Exemple de relance, pas une phrase imposée :** Une série réelle alternée convergente est aussi une série complexe : que deviennent ses modules ?

### Réaction : justifiee

Élève : Pour (-1)^{n-1}/n, les modules donnent l'harmonique divergente ; il suffit de la convergence des deux composantes.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une série réelle n'est pas une série complexe.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas comment séparer les composantes.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K011 — Majorant convergent

Famille : comparaisons

**Question / contexte :** Étudier sum_{n>=1} 1/(n^2+n).

**Référence réservée à l'évaluateur :** 0<=1/(n^2+n)<=1/n^2, donc convergence par comparaison à Riemann p=2.

**Première réponse de l'élève :** Le terme est inférieur à 1/n^2, donc la série converge.

**Statut interne :** correcte

**Défi attendu :** Challenger une réponse juste sur les hypothèses sans faire croire qu'elle est fausse.

**Exemple de relance, pas une phrase imposée :** Quelles hypothèses rendent cette comparaison suffisante ?

### Réaction : justifiee

Élève : Les termes sont positifs et la série majorante sum 1/n^2 converge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une majoration par n'importe quelle série suffit.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je connais l'inégalité, pas le théorème exact.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K012 — Majorant divergent

Famille : comparaisons

**Question / contexte :** Étudier sum_{n>=1} 1/n^2 à partir de 1/n^2<=1/n.

**Référence réservée à l'évaluateur :** Cette majoration par une série divergente ne conclut pas ; la série converge par Riemann p=2.

**Première réponse de l'élève :** Elle diverge car elle est plus petite que l'harmonique.

**Statut interne :** incorrecte

**Défi attendu :** Faire corriger le sens logique d'une comparaison, pas uniquement mémoriser le résultat.

**Exemple de relance, pas une phrase imposée :** Une quantité plus petite qu'une quantité non bornée doit-elle elle-même être non bornée ?

### Réaction : justifiee

Élève : Non, cette comparaison ne décide rien ; ici Riemann avec p=2 donne convergence.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Oui : tout ce qui est sous l'infini est infini.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais plus dans quel sens comparer.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K013 — Minorant divergent

Famille : comparaisons

**Question / contexte :** Étudier sum_{n>=1} 1/sqrt(n).

**Référence réservée à l'évaluateur :** Pour n>=1, 1/sqrt(n)>=1/n>=0 ; l'harmonique diverge donc la série diverge vers +infini.

**Première réponse de l'élève :** Elle diverge par comparaison.

**Statut interne :** incomplete

**Défi attendu :** Faire écrire le bon sens de l'inégalité et son effet sur les sommes.

**Exemple de relance, pas une phrase imposée :** Dans quel sens faut-il comparer à 1/n, et pourquoi ?

### Réaction : justifiee

Élève : 1/sqrt(n)>=1/n ; ses sommes partielles dominent celles de l'harmonique.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 1/sqrt(n)<=1/n, donc divergence.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je confonds sqrt(n) et n dans les dénominateurs.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K014 — Équivalent positif

Famille : comparaisons

**Question / contexte :** Étudier sum_{n>=1} (3n+1)/(n^3+2).

**Référence réservée à l'évaluateur :** Le terme positif est équivalent à 3/n^2, d'où convergence.

**Première réponse de l'élève :** C'est équivalent à 3/n^2, donc convergence.

**Statut interne :** correcte

**Défi attendu :** Vérifier que l'élève sait convertir un équivalent en comparaison de termes positifs.

**Exemple de relance, pas une phrase imposée :** Transformez cet équivalent en un encadrement valable à partir d'un certain rang.

### Réaction : justifiee

Élève : Le rapport tend vers 1 ; à partir d'un rang, le terme est entre 3/(2n^2) et 6/n^2.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un équivalent signifie une égalité pour tout n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas choisir les constantes de l'encadrement.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K015 — Équivalent de signe variable

Famille : comparaisons

**Question / contexte :** Un équivalent conserve-t-il toujours la nature d'une série de réels ?

**Référence réservée à l'évaluateur :** Non : a_n=(-1)^n/sqrt(n), b_n=a_n+1/n ont un rapport tendant vers 1 ; sum a_n converge et sum b_n diverge vers +infini.

**Première réponse de l'élève :** Oui, deux termes équivalents donnent toujours la même nature.

**Statut interne :** incorrecte

**Défi attendu :** Faire exhiber un contre-exemple complet, rapport et natures inclus.

**Exemple de relance, pas une phrase imposée :** Comparez a_n=(-1)^n/sqrt(n) et b_n=a_n+1/n : quel est leur rapport ?

### Réaction : justifiee

Élève : b_n/a_n=1+(-1)^n/sqrt(n) tend vers 1, mais l'ajout de l'harmonique fait diverger la seconde série.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le 1/n est plus petit donc sa somme ne peut rien changer.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas séparer les deux séries.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K016 — Petit o insuffisant

Famille : comparaisons

**Question / contexte :** La condition u_n=o(1/n) garantit-elle la convergence de sum u_n, avec u_n>=0 ?

**Référence réservée à l'évaluateur :** Non : u_n=1/(n log n), n>=2, est o(1/n) et sa série diverge par comparaison intégrale.

**Première réponse de l'élève :** Oui, c'est plus petit que le seuil harmonique.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer seuil en puissance et petite amélioration logarithmique.

**Exemple de relance, pas une phrase imposée :** Essayez u_n=1/(n log n) : quel est son rapport à 1/n et quelle intégrale lui correspond ?

### Réaction : justifiee

Élève : Le rapport vaut 1/log n et tend vers zéro, mais l'intégrale a pour primitive log(log x), non bornée.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Tout petit o d'une série divergente est convergent.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne trouve pas la primitive de 1/(x log x).

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K017 — Grand O sommable

Famille : comparaisons

**Question / contexte :** Si u_n=O(1/n^2), que peut-on dire de sum u_n sans hypothèse de signe ?

**Référence réservée à l'évaluateur :** Il existe C,N tels que |u_n|<=C/n^2 pour n>=N, donc convergence absolue.

**Première réponse de l'élève :** Il faut encore que u_n soit positif.

**Statut interne :** incorrecte

**Défi attendu :** Utiliser la définition quantitative du grand O pour obtenir la convergence absolue.

**Exemple de relance, pas une phrase imposée :** Quelle valeur absolue est déjà contenue dans la définition du grand O ?

### Réaction : justifiee

Élève : |u_n|<=C/n^2 à partir d'un rang ; la série des modules converge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : O ne borne que u_n, jamais son module.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas développer la notation O.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K018 — Sinus et domination absolue

Famille : comparaisons

**Question / contexte :** Étudier sum_{n>=1} sin(n)/n^2.

**Référence réservée à l'évaluateur :** |sin n|/n^2<=1/n^2, donc convergence absolue ; aucun argument sur une alternance régulière n'est nécessaire.

**Première réponse de l'élève :** Elle converge car sin(n) alterne de signe à chaque entier.

**Statut interne :** incorrecte

**Défi attendu :** Rectifier la justification même si la conclusion de convergence était juste.

**Exemple de relance, pas une phrase imposée :** Pouvez-vous conclure en majorant la valeur absolue, sans supposer une alternance régulière ?

### Réaction : justifiee

Élève : Oui, le module est au plus 1/n^2, qui est sommable.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : sin(n) vaut toujours (-1)^n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas quelle borne utiliser pour sin(n).

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K019 — Somme de deux séries positives

Famille : comparaisons

**Question / contexte :** Si a_n,b_n>=0 et sum(a_n+b_n) converge, que dire de sum a_n et sum b_n ?

**Référence réservée à l'évaluateur :** 0<=a_n,b_n<=a_n+b_n, donc les deux séries convergent ; sans positivité, la conclusion échoue.

**Première réponse de l'élève :** Les deux convergent.

**Statut interne :** correcte

**Défi attendu :** Faire tester la nécessité de l'hypothèse par un contre-exemple simple.

**Exemple de relance, pas une phrase imposée :** Quelle hypothèse empêche les deux termes de se compenser ?

### Réaction : justifiee

Élève : La positivité ; sans elle, a_n=1 et b_n=-1 donnent une somme nulle et deux séries divergentes.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Aucune, une somme convergente impose toujours la convergence de chaque morceau.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas ce que veut dire compensation.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K020 — Positivité seulement à partir d'un rang

Famille : comparaisons

**Question / contexte :** Un théorème de comparaison reste-t-il utilisable si les premiers termes ont des signes différents ?

**Référence réservée à l'évaluateur :** Oui, si les hypothèses tiennent à partir d'un rang : une somme finie n'affecte pas la nature.

**Première réponse de l'élève :** Non, il faut la positivité depuis le premier terme.

**Statut interne :** incorrecte

**Défi attendu :** Faire utiliser le caractère asymptotique des critères de convergence.

**Exemple de relance, pas une phrase imposée :** Séparez la somme en un début fini et une queue : laquelle décide de la convergence ?

### Réaction : justifiee

Élève : La queue ; les premiers termes ne changent que la somme lorsqu'elle existe.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un seul terme négatif rend toute comparaison impossible.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment écrire la séparation à l'indice N ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K021 — Géométrique et module

Famille : calculs_exacts

**Question / contexte :** Pour q réel, quand sum_{n>=0} q^n converge-t-elle ?

**Référence réservée à l'évaluateur :** Exactement pour |q|<1, avec somme 1/(1-q). Pour |q|>=1, q^n ne tend pas vers zéro.

**Première réponse de l'élève :** Elle converge pour q<1.

**Statut interne :** incorrecte

**Défi attendu :** Faire retrouver la condition en module à partir d'un cas limite révélateur.

**Exemple de relance, pas une phrase imposée :** Votre condition inclut q=-2 : que devient alors q^n ?

### Réaction : justifiee

Élève : Son module croît ; il faut |q|<1 et non seulement q<1.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un terme négatif ne peut pas empêcher la convergence.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas interpréter une puissance de -2.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K022 — Indice initial géométrique

Famille : calculs_exacts

**Question / contexte :** Calculer sum_{n>=1} (1/2)^n.

**Référence réservée à l'évaluateur :** La somme vaut (1/2)/(1-1/2)=1. Depuis n=0 elle vaudrait 2.

**Première réponse de l'élève :** La somme vaut 2.

**Statut interne :** incorrecte

**Défi attendu :** Faire vérifier l'indice de départ avant d'appliquer la formule mémorisée.

**Exemple de relance, pas une phrase imposée :** Le terme correspondant à n=0 est-il présent dans l'énoncé ?

### Réaction : justifiee

Élève : Non ; on retire 1 à la somme qui commence à zéro, donc on obtient 1.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Changer l'indice de départ ne change jamais la somme.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas écrire les trois premiers termes.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K023 — Géométrique alternée

Famille : calculs_exacts

**Question / contexte :** Calculer sum_{n>=0} (-1/2)^n.

**Référence réservée à l'évaluateur :** La raison est -1/2 de module inférieur à 1 ; somme 1/(1+1/2)=2/3.

**Première réponse de l'élève :** La somme vaut 2, car la raison a pour module 1/2.

**Statut interne :** incorrecte

**Défi attendu :** Distinguer le rôle du module dans le critère et celui du signe dans le calcul.

**Exemple de relance, pas une phrase imposée :** Le module sert à décider la convergence ; quelle raison faut-il conserver dans la formule de la somme ?

### Réaction : justifiee

Élève : La raison -1/2, donc la somme est 2/3 ; 2 serait la somme des modules.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : On peut remplacer chaque terme par son module sans changer la somme.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je mélange somme et somme des valeurs absolues.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K024 — Bord géométrique q=1

Famille : calculs_exacts

**Question / contexte :** Que vaut sum_{n>=0} q^n pour q=1 ?

**Référence réservée à l'évaluateur :** Les sommes partielles valent N+1 et tendent vers +infini ; 1/(1-q) n'est pas une formule valable ici.

**Première réponse de l'élève :** La formule donne 1/0, donc la somme vaut l'infini.

**Statut interne :** incomplete

**Défi attendu :** Remplacer une manipulation indéfinie par un calcul de sommes finies.

**Exemple de relance, pas une phrase imposée :** Sans division par zéro, écrivez directement la somme des N+1 premiers termes.

### Réaction : justifiee

Élève : S_N=N+1, ce qui prouve sa divergence vers +infini.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 1/0 est un réel très grand.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas combien de termes il y a de zéro à N.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K025 — Bord géométrique q=-1

Famille : calculs_exacts

**Question / contexte :** Étudier les sommes partielles de sum_{n>=0}(-1)^n.

**Référence réservée à l'évaluateur :** S_{2k}=1 et S_{2k+1}=0 ; la série ordinaire diverge.

**Première réponse de l'élève :** La formule géométrique infinie donne 1/2.

**Statut interne :** incorrecte

**Défi attendu :** Faire vérifier le domaine de validité de la formule infinie.

**Exemple de relance, pas une phrase imposée :** Comparez les sommes partielles d'indices pairs et impairs.

### Réaction : justifiee

Élève : Elles valent respectivement 1 et 0, donc aucune limite commune n'existe.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une limite peut prendre alternativement deux valeurs.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : J'obtiens 0 ou 1 mais je ne sais pas conclure.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K026 — Télescopage simple

Famille : calculs_exacts

**Question / contexte :** Calculer sum_{n>=1} 1/(n(n+1)).

**Référence réservée à l'évaluateur :** 1/[n(n+1)]=1/n-1/(n+1) ; somme jusqu'à N : 1-1/(N+1), donc somme 1.

**Première réponse de l'élève :** Tout s'annule, la somme est zéro.

**Statut interne :** incorrecte

**Défi attendu :** Faire conserver les termes de bord dans un télescopage.

**Exemple de relance, pas une phrase imposée :** Écrivez les termes jusqu'à n=3 : quels termes de bord restent ?

### Réaction : justifiee

Élève : La somme finie vaut 1-1/(N+1), donc la limite est 1.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le premier terme finit aussi par s'annuler à l'infini.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je n'arrive pas à décomposer la fraction.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K027 — Télescopage décalé

Famille : calculs_exacts

**Question / contexte :** Calculer sum_{n>=1} 1/(n(n+2)).

**Référence réservée à l'évaluateur :** Le terme vaut (1/2)(1/n-1/(n+2)). S_N=(1/2)(1+1/2-1/(N+1)-1/(N+2)), limite 3/4.

**Première réponse de l'élève :** Comme pour n(n+1), la somme vaut 1.

**Statut interne :** incorrecte

**Défi attendu :** Faire adapter le télescopage au décalage de deux indices.

**Exemple de relance, pas une phrase imposée :** Quel coefficient rend exacte la différence 1/n-1/(n+2) ?

### Réaction : justifiee

Élève : Il faut 1/2, et deux termes initiaux restent : somme 3/4.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La différence vaut 1/(n(n+2)) sans coefficient.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je perds les deux termes du bord final.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K028 — Logarithme télescopique

Famille : calculs_exacts

**Question / contexte :** Étudier sum_{n>=1} log(1+1/n).

**Référence réservée à l'évaluateur :** log(1+1/n)=log(n+1)-log n ; S_N=log(N+1), donc divergence vers +infini.

**Première réponse de l'élève :** Elle converge puisque log(1+1/n) tend vers zéro.

**Statut interne :** incorrecte

**Défi attendu :** Utiliser un calcul exact pour contester la fausse suffisance du terme nul.

**Exemple de relance, pas une phrase imposée :** Pouvez-vous écrire le logarithme comme une différence de deux logarithmes ?

### Réaction : justifiee

Élève : S_N=log(N+1) par télescopage, donc les sommes sont non bornées.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : log(N+1) tend vers zéro car ses accroissements tendent vers zéro.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne reconnais pas (n+1)/n.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K029 — Télescopage et suite sans limite

Famille : calculs_exacts

**Question / contexte :** La série sum_{n>=0}(v_{n+1}-v_n) converge-t-elle pour toute suite bornée v_n ?

**Référence réservée à l'évaluateur :** S_N=v_{N+1}-v_0, donc convergence équivalente à celle de v_n. v_n=(-1)^n est un contre-exemple borné.

**Première réponse de l'élève :** Oui, les différences se compensent.

**Statut interne :** incorrecte

**Défi attendu :** Faire relier télescopage et existence d'une limite de la suite de bord.

**Exemple de relance, pas une phrase imposée :** Que reste-t-il exactement dans la somme jusqu'à N, puis pour v_n=(-1)^n ?

### Réaction : justifiee

Élève : Il reste v_{N+1}-v_0, qui oscille dans cet exemple.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une différence télescopique a toujours une somme nulle.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas quel terme final subsiste.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K030 — Poids n et géométrique

Famille : calculs_exacts

**Question / contexte :** Justifier la convergence de sum_{n>=1} n/2^n sans calculer sa somme.

**Référence réservée à l'évaluateur :** Le rapport u_{n+1}/u_n=(n+1)/(2n) tend vers 1/2<1, donc convergence ; on peut aussi majorer finalement par une géométrique.

**Première réponse de l'élève :** Une exponentielle domine une puissance, donc c'est fini.

**Statut interne :** incomplete

**Défi attendu :** Faire convertir un slogan asymptotique en critère de convergence.

**Exemple de relance, pas une phrase imposée :** Transformez cette intuition en une majoration géométrique ou un rapport de termes consécutifs.

### Réaction : justifiee

Élève : Le rapport tend vers 1/2 et est finalement inférieur à 3/4, ce qui donne une majoration géométrique.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : u_n tend vers zéro, cela remplace la majoration.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment choisir une constante entre 1/2 et 1 ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K031 — Seuil de Riemann

Famille : riemann_integrales

**Question / contexte :** Pour p réel, quand sum_{n>=1} 1/n^p converge-t-elle ?

**Référence réservée à l'évaluateur :** Exactement pour p>1 ; pour p<=0 les termes ne tendent pas vers zéro, pour 0<p<=1 comparaison intégrale divergente.

**Première réponse de l'élève :** Pour p>=1.

**Statut interne :** incorrecte

**Défi attendu :** Faire traiter le bord du domaine et le caractère strict de l'inégalité.

**Exemple de relance, pas une phrase imposée :** Que donne précisément votre condition au point p=1 ?

### Réaction : justifiee

Élève : On obtient l'harmonique divergente ; il faut p>1 strictement.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : L'harmonique converge lentement.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne me rappelle plus le cas p=1.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K032 — Primitive au cas p=1

Famille : riemann_integrales

**Question / contexte :** Comparer intégralement la série harmonique.

**Référence réservée à l'évaluateur :** Pour 1/x positive décroissante, H_N>=int_1^{N+1} dx/x=log(N+1), donc divergence.

**Première réponse de l'élève :** J'utilise x^{1-p}/(1-p) avec p=1.

**Statut interne :** incorrecte

**Défi attendu :** Repérer le cas exceptionnel plutôt que poursuivre une formule hors domaine.

**Exemple de relance, pas une phrase imposée :** Votre expression est-elle définie pour p=1 ? Quelle fonction a pour dérivée 1/x ?

### Réaction : justifiee

Élève : Il faut log x, et son intégrale jusqu'à N+1 n'est pas bornée.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : On remplace 1-p par zéro et on simplifie.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne connais pas la primitive de 1/x.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K033 — Bertrand logarithme au carré

Famille : riemann_integrales

**Question / contexte :** Étudier sum_{n>=2} 1/(n(log n)^2).

**Référence réservée à l'évaluateur :** La fonction est positive décroissante sur [2,+infini[ ; son intégrale vaut une constante moins 1/log x, donc convergence.

**Première réponse de l'élève :** Elle diverge car il y a n au dénominateur.

**Statut interne :** incorrecte

**Défi attendu :** Faire prendre en compte le facteur logarithmique au seuil harmonique.

**Exemple de relance, pas une phrase imposée :** Dans l'intégrale, que donne le changement de variable t=log x ?

### Réaction : justifiee

Élève : On obtient int dt/t^2, convergente à l'infini.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un facteur logarithmique ne change jamais la nature d'une série.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas transformer dx/x.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K034 — Bertrand logarithme simple

Famille : riemann_integrales

**Question / contexte :** Étudier sum_{n>=2} 1/(n log n).

**Référence réservée à l'évaluateur :** Fonction positive décroissante ; primitive log(log x), non bornée, d'où divergence.

**Première réponse de l'élève :** Elle converge car elle est plus petite que 1/n.

**Statut interne :** incorrecte

**Défi attendu :** Combiner correction du sens de comparaison et outil intégral pertinent.

**Exemple de relance, pas une phrase imposée :** Une majoration par l'harmonique décide-t-elle le résultat ? Essayez plutôt une primitive.

### Réaction : justifiee

Élève : Non ; la primitive log(log x) diverge, donc la série aussi.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une série strictement plus petite que l'harmonique converge toujours.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je bloque sur le logarithme du logarithme.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K035 — Paramètre logarithmique

Famille : riemann_integrales

**Question / contexte :** Pour a réel, étudier sum_{n>=2} 1/(n(log n)^a).

**Référence réservée à l'évaluateur :** La fonction est finalement décroissante pour tout a fixé. t=log x donne int t^{-a}dt ; convergence exactement pour a>1.

**Première réponse de l'élève :** Elle converge dès que a>0.

**Statut interne :** incorrecte

**Défi attendu :** Faire déterminer le domaine complet, pas seulement un signe du paramètre.

**Exemple de relance, pas une phrase imposée :** Après t=log x, quel seuil de Riemann retrouvez-vous, y compris pour a=1 ?

### Réaction : justifiee

Élève : L'intégrale de t^{-a} converge seulement pour a>1 ; a=1 diverge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le simple fait que (log n)^a tende vers l'infini suffit.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas pourquoi le seuil vaut encore 1.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K036 — Logarithme sur carré

Famille : riemann_integrales

**Question / contexte :** Étudier sum_{n>=2} log(n)/n^2.

**Référence réservée à l'évaluateur :** log n=o(sqrt n), donc le terme positif est finalement majoré par 1/n^{3/2}, sommable.

**Première réponse de l'élève :** Le logarithme tend vers l'infini, donc la série diverge.

**Statut interne :** incorrecte

**Défi attendu :** Faire raisonner sur le quotient et choisir une marge de puissance sommable.

**Exemple de relance, pas une phrase imposée :** Comparez log n à sqrt n : que devient alors le quotient complet ?

### Réaction : justifiee

Élève : Il est finalement inférieur à 1/n^{3/2}, donc la série converge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un numérateur non borné empêche toujours la convergence.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas quelle puissance choisir pour dominer le logarithme.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K037 — Reste p=2 encadré

Famille : riemann_integrales

**Question / contexte :** Encadrer R_N=sum_{n=N+1}^inf 1/n^2 par des intégrales.

**Référence réservée à l'évaluateur :** Pour f décroissante, int_{N+1}^inf f<=R_N<=int_N^inf f, donc 1/(N+1)<=R_N<=1/N.

**Première réponse de l'élève :** R_N est égal à 1/N.

**Statut interne :** incorrecte

**Défi attendu :** Distinguer borne, équivalent et identité exacte.

**Exemple de relance, pas une phrase imposée :** L'aire des rectangles coïncide-t-elle exactement avec celle sous la courbe décroissante ?

### Réaction : justifiee

Élève : Non ; les intégrales donnent 1/(N+1)<=R_N<=1/N, donc seulement R_N~1/N.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une équivalence est une égalité exacte.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas de quel côté placer les rectangles.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K038 — Sommes harmoniques

Famille : riemann_integrales

**Question / contexte :** Montrer H_N~log N.

**Référence réservée à l'évaluateur :** log(N+1)<=H_N<=1+log N ; division par log N pour N>=2 et encadrement donnent l'équivalent.

**Première réponse de l'élève :** H_N=log N.

**Statut interne :** incorrecte

**Défi attendu :** Faire contrôler un énoncé exact sur un petit cas puis établir la bonne asymptotique.

**Exemple de relance, pas une phrase imposée :** Testez votre égalité pour N=1, puis remplacez-la par un encadrement intégral.

### Réaction : justifiee

Élève : H_1=1 et log 1=0 ; les bornes intégrales donnent un équivalent, pas l'égalité.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une erreur bornée doit être exactement nulle.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment les bornes donnent-elles un rapport qui tend vers 1 ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K039 — Racine et logarithme

Famille : riemann_integrales

**Question / contexte :** Étudier sum_{n>=2} 1/(sqrt(n) log n).

**Référence réservée à l'évaluateur :** log n<=n^{1/4} finalement, donc le terme est au moins n^{-3/4} ; divergence par comparaison positive.

**Première réponse de l'élève :** Le logarithme supplémentaire doit faire converger.

**Statut interne :** incorrecte

**Défi attendu :** Faire utiliser correctement un minorant divergent malgré l'amélioration logarithmique.

**Exemple de relance, pas une phrase imposée :** En majorant log n par n^{1/4}, obtenez-vous un minorant utile du terme général ?

### Réaction : justifiee

Élève : Oui, 1/(sqrt(n)log n)>=1/n^{3/4} finalement, donc divergence.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Majorer le dénominateur donne une majoration du quotient.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je me trompe dans le sens en passant à l'inverse.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K040 — Terme à indice décalé

Famille : riemann_integrales

**Question / contexte :** Étudier sum_{n>=1} 1/(n+10)^{3/2}.

**Référence réservée à l'évaluateur :** C'est une queue de la série de Riemann p=3/2, ou un terme équivalent à n^{-3/2} : convergence.

**Première réponse de l'élève :** Je dois trouver un nouveau critère car ce n'est pas n^{3/2}.

**Statut interne :** hors_sujet

**Défi attendu :** Faire reconnaître une structure inchangée par un décalage fini.

**Exemple de relance, pas une phrase imposée :** Que devient la série après le changement d'indice k=n+10 ?

### Réaction : justifiee

Élève : C'est la queue à partir de k=11 d'une série de Riemann convergente.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un changement d'indice permet aussi de modifier l'exposant.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Quel est le nouveau premier indice ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K041 — Hypothèses du critère alterné

Famille : alternance

**Question / contexte :** Justifier la convergence de sum_{n>=1}(-1)^{n-1}/n.

**Référence réservée à l'évaluateur :** Les amplitudes 1/n sont positives, décroissantes et tendent vers zéro : critère alterné. Pas de convergence absolue.

**Première réponse de l'élève :** Les signes alternent donc ça converge.

**Statut interne :** incomplete

**Défi attendu :** Faire énoncer et vérifier les hypothèses plutôt que réciter le nom d'un critère.

**Exemple de relance, pas une phrase imposée :** Quelles propriétés des amplitudes faut-il vérifier en plus des signes ?

### Réaction : justifiee

Élève : 1/n décroît vers zéro, ce qui permet d'appliquer le critère alterné.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Les signes seuls suffisent, même pour (-1)^n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne me souviens plus de l'hypothèse de monotonie.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K042 — Absolue versus simple

Famille : alternance

**Question / contexte :** La série sum_{n>=1}(-1)^{n-1}/n converge-t-elle absolument ?

**Référence réservée à l'évaluateur :** Non : la série des modules est l'harmonique. La série signée converge par le critère alterné.

**Première réponse de l'élève :** Oui, puisqu'elle converge.

**Statut interne :** incorrecte

**Défi attendu :** Distinguer série des modules et module de la somme.

**Exemple de relance, pas une phrase imposée :** Quelle série obtenez-vous en prenant le module de chaque terme ?

### Réaction : justifiee

Élève : L'harmonique divergente ; la convergence est seulement conditionnelle.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le module d'une somme est la somme des modules, donc cela ne change rien.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je prends le module avant ou après la somme ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K043 — Alternance et amplitude constante

Famille : alternance

**Question / contexte :** Étudier sum_{n>=1}(-1)^n.

**Référence réservée à l'évaluateur :** Les amplitudes ne tendent pas vers zéro ; le terme général n'a pas pour limite zéro, donc divergence.

**Première réponse de l'élève :** Le critère alterné s'applique.

**Statut interne :** incorrecte

**Défi attendu :** Faire isoler l'hypothèse manquante malgré la monotonie large des amplitudes.

**Exemple de relance, pas une phrase imposée :** Que vaut ici l'amplitude et quelle limite exige le critère ?

### Réaction : justifiee

Élève : L'amplitude vaut 1 et ne tend pas vers zéro ; le critère ne s'applique pas et la série diverge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une amplitude constante est décroissante, donc toutes les hypothèses sont remplies.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas laquelle des hypothèses manque.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K044 — Alternée en racine

Famille : alternance

**Question / contexte :** Étudier sum_{n>=1}(-1)^{n-1}/sqrt(n), puis la série de ses modules.

**Référence réservée à l'évaluateur :** Convergence par le critère alterné ; divergence de la série des modules par Riemann p=1/2.

**Première réponse de l'élève :** Riemann dit p<1, donc la série signée diverge.

**Statut interne :** incorrecte

**Défi attendu :** Faire choisir un critère tenant compte du signe.

**Exemple de relance, pas une phrase imposée :** Le critère de Riemann porte ici sur la série signée ou sur les amplitudes positives ?

### Réaction : justifiee

Élève : Sur les amplitudes ; la série signée converge par alternance, sans convergence absolue.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Changer les signes ne peut jamais changer la convergence.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas quel critère choisir en premier.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K045 — Alternance avec dérive harmonique

Famille : alternance

**Question / contexte :** Étudier sum_{n>=1} [(-1)^n/sqrt(n)+1/n].

**Référence réservée à l'évaluateur :** La partie alternée converge ; la partie harmonique tend vers +infini ; les sommes totales tendent vers +infini.

**Première réponse de l'élève :** Le terme est équivalent à (-1)^n/sqrt(n), donc convergence.

**Statut interne :** incorrecte

**Défi attendu :** Faire détecter une dérive non sommable cachée derrière une alternance dominante.

**Exemple de relance, pas une phrase imposée :** Séparez les sommes partielles des deux morceaux : que devient chacun ?

### Réaction : justifiee

Élève : Le premier a une limite finie, le second diverge vers +infini, donc la somme diverge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le morceau 1/n est négligeable terme à terme, donc aussi après sommation.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas quand on peut sommer un équivalent.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K046 — Amplitudes non monotones

Famille : alternance

**Question / contexte :** Soit a_{2k}=1/(2k), a_{2k-1}=1/sqrt(2k-1). Étudier sum_{n>=1}(-1)^n a_n.

**Référence réservée à l'évaluateur :** a_n>0 tend vers zéro mais n'est pas finalement décroissante. Les paires valent 1/(2k)-1/sqrt(2k-1)~ -1/sqrt(2k), d'où divergence vers -infini, y compris les sommes impaires.

**Première réponse de l'élève :** Alternance et limite nulle suffisent.

**Statut interne :** incorrecte

**Défi attendu :** Faire constater que la monotonie ne peut pas être supprimée du critère alterné.

**Exemple de relance, pas une phrase imposée :** Regroupez les termes d'indices 2k-1 et 2k : quel signe et quel ordre obtenez-vous ?

### Réaction : justifiee

Élève : Chaque paire est équivalente à -1/sqrt(2k) ; leurs sommes tendent vers -infini, et le terme restant tend vers zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Tous les blocs de deux s'annulent dès que les signes alternent.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas écrire les amplitudes paires et impaires ensemble.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K047 — Alternée logarithmique

Famille : alternance

**Question / contexte :** Étudier sum_{n>=2}(-1)^n/log n.

**Référence réservée à l'évaluateur :** 1/log n décroît vers zéro, donc convergence alternée. Pour n>=2, log n<=n, donc 1/log n>=1/n : pas de convergence absolue.

**Première réponse de l'élève :** Elle diverge parce que le logarithme est trop lent.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer vitesse de décroissance et hypothèses réellement requises.

**Exemple de relance, pas une phrase imposée :** La lenteur empêche-t-elle 1/log n de décroître vers zéro ?

### Réaction : justifiee

Élève : Non, le critère alterné s'applique ; les modules divergent par minoration par 1/n.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le critère alterné exige une décroissance au moins en 1/n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas si 1/log n est décroissante.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K048 — Série absolument convergente

Famille : alternance

**Question / contexte :** Étudier sum_{n>=1}(-1)^n/n^2.

**Référence réservée à l'évaluateur :** La série des modules est sum 1/n^2, convergente ; donc convergence absolue, plus forte que la convergence alternée.

**Première réponse de l'élève :** Elle converge par le critère alterné.

**Statut interne :** correcte

**Défi attendu :** Faire approfondir une preuve valide sans la traiter comme une erreur.

**Exemple de relance, pas une phrase imposée :** Pouvez-vous obtenir une propriété plus forte en examinant ses modules ?

### Réaction : justifiee

Élève : Les modules forment une série de Riemann p=2, donc la convergence est absolue.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une série contenant des signes moins ne peut jamais converger absolument.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Que signifie une propriété plus forte ici ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K049 — Parties positives et négatives

Famille : alternance

**Question / contexte :** Pour une série réelle convergente non absolument, que dire des sommes des parties positives et négatives ?

**Référence réservée à l'évaluateur :** Avec u_n^+=max(u_n,0), u_n^-=max(-u_n,0), leurs deux séries divergent vers +infini, sinon la convergence de sum u_n forcerait celle de l'autre et donc de sum |u_n|.

**Première réponse de l'élève :** On peut calculer séparément les deux sommes finies puis les soustraire.

**Statut interne :** incorrecte

**Défi attendu :** Faire éviter les soustractions de séries divergentes tout en justifiant la structure des signes.

**Exemple de relance, pas une phrase imposée :** Si l'une des deux séries positives avait une somme finie, que forcerait la convergence de leur différence ?

### Réaction : justifiee

Élève : L'autre aurait aussi une somme finie, contradiction avec la non-convergence absolue.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : On peut toujours calculer +infini moins +infini.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas exprimer |u_n| avec u_n^+ et u_n^-.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K050 — Regroupement abusif

Famille : alternance

**Question / contexte :** Peut-on prouver la convergence de 1-1+1-1+... en regroupant (1-1)+(1-1)+... ?

**Référence réservée à l'évaluateur :** Le regroupement ne contrôle qu'une sous-suite des sommes partielles. Les autres valent 1 ; divergence ordinaire.

**Première réponse de l'élève :** Oui, tous les blocs valent zéro.

**Statut interne :** incorrecte

**Défi attendu :** Faire contrôler toutes les sommes partielles et pas une seule sous-suite.

**Exemple de relance, pas une phrase imposée :** Que se passe-t-il quand vous vous arrêtez juste avant de compléter un bloc ?

### Réaction : justifiee

Élève : Les sommes impaires en nombre de termes valent 1 : une sous-suite convergente ne suffit pas.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : On a le droit de supprimer les sommes qui ne terminent pas un bloc.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je n'ai regardé que les sommes avec un nombre pair de termes.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K051 — Logarithme corrigé

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}[log(1+1/n)-1/n].

**Référence réservée à l'évaluateur :** log(1+x)-x=-x^2/2+O(x^3), donc terme ~-1/(2n^2) et convergence absolue.

**Première réponse de l'élève :** Les deux séries divergent, donc leur différence diverge.

**Statut interne :** incorrecte

**Défi attendu :** Faire traiter l'annulation dans le terme général avant toute séparation de séries divergentes.

**Exemple de relance, pas une phrase imposée :** Développez le terme complet à l'ordre où le premier coefficient ne s'annule pas.

### Réaction : justifiee

Élève : Le terme en 1/n s'annule et il reste -1/(2n^2)+O(1/n^3), sommable en module.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Infini moins infini vaut zéro.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : À quel ordre faut-il pousser le logarithme ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K052 — Exponentielle corrigée

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}[exp(1/n)-1-1/n].

**Référence réservée à l'évaluateur :** exp x-1-x=x^2/2+O(x^3), donc terme ~1/(2n^2) positif : convergence.

**Première réponse de l'élève :** exp(1/n)~1 donc le terme est équivalent à -1/n.

**Statut interne :** incorrecte

**Défi attendu :** Faire respecter les limites des opérations sur les équivalents.

**Exemple de relance, pas une phrase imposée :** Une équivalence peut-elle être soustraite après l'annulation du terme principal ?

### Réaction : justifiee

Élève : Il faut un DL d'ordre deux ; le reste vaut 1/(2n^2)+O(1/n^3).

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : On soustrait toujours les équivalents terme à terme.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Le premier ordre s'annule, je ne sais pas continuer.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K053 — Sinus corrigé

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}[sin(1/n)-1/n].

**Référence réservée à l'évaluateur :** sin x-x=-x^3/6+O(x^5), donc convergence absolue par comparaison à n^{-3}.

**Première réponse de l'élève :** sin(1/n)~1/n, donc le terme est nul.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer une annulation asymptotique du terme dominant et une identité.

**Exemple de relance, pas une phrase imposée :** Équivalent veut-il dire égal ? Quel est le premier terme non nul après x dans le DL du sinus ?

### Réaction : justifiee

Élève : C'est -x^3/6 ; ici on obtient un terme équivalent à -1/(6n^3).

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une différence de deux équivalents est toujours exactement nulle.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je connais seulement sin x~x.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K054 — Cosinus et racine

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}[1-cos(1/sqrt(n))].

**Référence réservée à l'évaluateur :** 1-cos x~x^2/2, donc terme positif ~1/(2n) ; divergence vers +infini.

**Première réponse de l'élève :** Le cosinus est borné, donc la série converge.

**Statut interne :** incorrecte

**Défi attendu :** Faire suivre correctement la puissance lors de la composition d'un DL.

**Exemple de relance, pas une phrase imposée :** Quel est l'ordre de 1-cos x près de zéro après substitution x=1/sqrt(n) ?

### Réaction : justifiee

Élève : Il est de l'ordre de 1/(2n), donc la série diverge par comparaison harmonique.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un terme borné suffit à faire converger une série.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je confonds 1/n et 1/n^2 après la substitution.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K055 — Racine moins racine

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}(sqrt(n+1)-sqrt(n)).

**Référence réservée à l'évaluateur :** Le terme est 1/(sqrt(n+1)+sqrt n)~1/(2sqrt n) ; ou S_N=sqrt(N+1)-1. Divergence vers +infini.

**Première réponse de l'élève :** Les deux racines sont équivalentes donc leur différence tend vite vers zéro et la série converge.

**Statut interne :** incorrecte

**Défi attendu :** Faire exploiter une identité exacte et rejeter la soustraction d'équivalents.

**Exemple de relance, pas une phrase imposée :** Pouvez-vous rationaliser le terme ou calculer directement la somme partielle ?

### Réaction : justifiee

Élève : S_N=sqrt(N+1)-1, qui diverge ; le terme seul tend pourtant vers zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : sqrt(n+1)-sqrt n est égal à sqrt(1)=1.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas le conjugué à multiplier.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K056 — Arctangente corrigée

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}[arctan(1/n)-1/n].

**Référence réservée à l'évaluateur :** arctan x-x=-x^3/3+O(x^5), donc convergence absolue.

**Première réponse de l'élève :** C'est du même ordre que 1/n, donc divergence.

**Statut interne :** incorrecte

**Défi attendu :** Faire déterminer le premier terme non nul, éventuellement par intégration du DL de 1/(1+x^2).

**Exemple de relance, pas une phrase imposée :** Que devient le terme linéaire lorsque vous soustrayez 1/n ?

### Réaction : justifiee

Élève : Il disparaît ; le premier terme est -1/(3n^3), sommable en module.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le premier terme du DL reste 1/n malgré la soustraction.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je peux dériver arctan, mais je ne connais pas son DL.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K057 — Logarithme alterné au seuil

Famille : developpements

**Question / contexte :** Étudier sum_{n>=2} log(1+(-1)^n/sqrt(n)).

**Référence réservée à l'évaluateur :** DL : (-1)^n/sqrt n-1/(2n)+O(n^{-3/2}). La première série converge, la troisième absolument, la dérive harmonique fait tendre les sommes vers -infini.

**Première réponse de l'élève :** Équivalent à une alternée convergente, donc convergence.

**Statut interne :** incorrecte

**Défi attendu :** Faire isoler la dérive et justifier la sommabilité du reste.

**Exemple de relance, pas une phrase imposée :** Quel terme non alterné apparaît au deuxième ordre du logarithme ?

### Réaction : justifiee

Élève : -1/(2n), dont la somme tend vers -infini ; le reste d'ordre n^{-3/2} est sommable.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le carré de (-1)^n alterne encore.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas contrôler le reste après le deuxième ordre.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K058 — Reste grand O non sommable

Famille : developpements

**Question / contexte :** Si u_n=1/n+O(1/n^2), sum(u_n-1/n) converge-t-elle ?

**Référence réservée à l'évaluateur :** Oui, |u_n-1/n|<=C/n^2 finalement, donc convergence absolue de la différence ; sum u_n diverge comme l'harmonique si u_n réel.

**Première réponse de l'élève :** Non, car sum u_n diverge.

**Statut interne :** incorrecte

**Défi attendu :** Faire répondre sur l'objet demandé et utiliser le contrôle du reste.

**Exemple de relance, pas une phrase imposée :** Quelle majoration porte directement sur la différence demandée ?

### Réaction : justifiee

Élève : Son module est majoré par C/n^2 ; c'est la différence qui converge absolument, pas sum u_n.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : O(1/n^2) signifie seulement que le terme tend vers zéro.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas passer du O à une inégalité.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K059 — Petit o harmonique et compensation

Famille : developpements

**Question / contexte :** Si u_n=1/n+o(1/n), la série sum(u_n-1/n) converge-t-elle nécessairement ?

**Référence réservée à l'évaluateur :** Non : choisir u_n=1/n+1/(n log n) pour n>=2 ; la différence est o(1/n) mais de série divergente.

**Première réponse de l'élève :** Oui, l'erreur est négligeable.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer négligeabilité locale et sommabilité globale.

**Exemple de relance, pas une phrase imposée :** Un reste 1/(n log n) satisfait-il votre hypothèse et est-il sommable ?

### Réaction : justifiee

Élève : Il satisfait le petit o mais sa série diverge ; l'hypothèse ne suffit pas.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Tout petit o possède une série absolument convergente.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas tester un petit o par un quotient.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K060 — Différence exponentielle symétrique

Famille : developpements

**Question / contexte :** Étudier sum_{n>=1}[exp(1/sqrt(n))+exp(-1/sqrt(n))-2].

**Référence réservée à l'évaluateur :** exp x+exp(-x)-2=x^2+O(x^4), donc terme positif ~1/n : divergence.

**Première réponse de l'élève :** Les deux exponentielles se compensent.

**Statut interne :** incorrecte

**Défi attendu :** Faire vérifier une annulation annoncée en conservant le premier ordre pair non nul.

**Exemple de relance, pas une phrase imposée :** Quels ordres s'annulent par symétrie, et quels ordres s'additionnent ?

### Réaction : justifiee

Élève : Les ordres impairs s'annulent mais les termes quadratiques s'ajoutent : terme ~1/n.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : exp(x)+exp(-x)=2 pour tout x.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas additionner les deux DL.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K061 — Reste alterné : valeur absolue

Famille : restes

**Question / contexte :** Majorer le reste après N termes de sum_{n>=1}(-1)^{n-1}/n.

**Référence réservée à l'évaluateur :** |R_N|<=1/(N+1) ; le signe est celui du premier terme omis, (-1)^N.

**Première réponse de l'élève :** R_N<=1/N, cela suffit pour borner l'erreur.

**Statut interne :** incomplete

**Défi attendu :** Faire formuler une borne d'erreur bilatérale avec le bon indice.

**Exemple de relance, pas une phrase imposée :** Une borne supérieure sur un nombre négatif contrôle-t-elle sa distance à zéro ?

### Réaction : justifiee

Élève : Il faut |R_N|<=1/(N+1), avec le premier indice omis N+1.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Si R_N est négatif, l'erreur est forcément nulle.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas pourquoi mettre une valeur absolue.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K062 — Nombre de termes et précision

Famille : restes

**Question / contexte :** Combien de termes suffisent pour une erreur <=0,001 dans l'harmonique alternée ?

**Référence réservée à l'évaluateur :** Le critère |R_N|<=1/(N+1) donne N>=999 comme condition suffisante, sans prétendre à une minimalité exacte.

**Première réponse de l'élève :** Il faut exactement 1000 termes, c'est minimal.

**Statut interne :** incomplete

**Défi attendu :** Accepter 1000 comme suffisant mais faire corriger la revendication de minimalité.

**Exemple de relance, pas une phrase imposée :** Résolvez 1/(N+1)<=0,001. Cette borne prouve-t-elle une minimalité ?

### Réaction : justifiee

Élève : N>=999 suffit ; cette estimation seule ne prouve pas que 999 est le nombre minimal réel.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Toute majoration de l'erreur donne le nombre minimal exact.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas distinguer suffisant et minimal.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K063 — Signe du reste alterné

Famille : restes

**Question / contexte :** Pour l'harmonique alternée commençant par +1, S_{2m} est-il au-dessus ou en dessous de la somme ?

**Référence réservée à l'évaluateur :** Le premier terme omis a un signe positif, donc R_{2m}>=0 et S_{2m} est en dessous de la somme.

**Première réponse de l'élève :** Au-dessus puisque le dernier terme ajouté est négatif.

**Statut interne :** incorrecte

**Défi attendu :** Faire utiliser le premier terme omis et non le dernier terme gardé.

**Exemple de relance, pas une phrase imposée :** Quel est le signe du premier terme qui manque après 2m termes ?

### Réaction : justifiee

Élève : Il est positif ; le reste est positif, donc S_{2m} sous-estime la somme.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le signe du reste est toujours celui du dernier terme ajouté.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je me perds dans (-1)^{n-1}.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K064 — Reste géométrique exact

Famille : restes

**Question / contexte :** Donner le reste après les termes n=0,...,N de sum (1/3)^n.

**Référence réservée à l'évaluateur :** R_N=(1/3)^{N+1}/(1-1/3)=1/(2*3^N), strictement positif.

**Première réponse de l'élève :** R_N=(1/3)^N.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer premier terme omis et somme de la queue.

**Exemple de relance, pas une phrase imposée :** Le reste contient un seul terme ou toute une nouvelle série géométrique ?

### Réaction : justifiee

Élève : Toute la queue, de premier terme 3^{-(N+1)} ; sa somme vaut 1/(2*3^N).

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Tous les termes suivants sont nuls puisqu'ils sont très petits.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas factoriser le premier terme de la queue.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K065 — Reste de Riemann général

Famille : restes

**Question / contexte :** Pour p>1, établir un équivalent de R_N=sum_{n>N}1/n^p.

**Référence réservée à l'évaluateur :** Comparaison intégrale : (N+1)^{1-p}/(p-1)<=R_N<=N^{1-p}/(p-1), donc R_N~N^{1-p}/(p-1).

**Première réponse de l'élève :** Le reste est équivalent au premier terme 1/N^p.

**Statut interne :** incorrecte

**Défi attendu :** Faire retrouver la puissance et la constante correctes du reste.

**Exemple de relance, pas une phrase imposée :** Quelle intégrale compare la somme de toute la queue, et quelle puissance donne sa primitive ?

### Réaction : justifiee

Élève : L'intégrale de N à l'infini vaut N^{1-p}/(p-1), et les deux bornes sont équivalentes.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La somme de termes décroissants est toujours équivalente au premier.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas calculer la borne à l'infini de la primitive.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K066 — Équivalent de restes positifs

Famille : restes

**Question / contexte :** Si a_n~b_n>0 et sum b_n converge, comparer les restes des deux séries.

**Référence réservée à l'évaluateur :** Pour tout epsilon>0, (1-epsilon)b_n<=a_n<=(1+epsilon)b_n finalement ; sommer sur n>N donne R_N(a)~R_N(b).

**Première réponse de l'élève :** Les restes sont équivalents parce qu'on peut toujours sommer un équivalent.

**Statut interne :** incomplete

**Défi attendu :** Faire justifier le passage aux restes par un contrôle uniforme sur la queue positive.

**Exemple de relance, pas une phrase imposée :** Écrivez un encadrement qui reste valable pour tous les indices de la queue.

### Réaction : justifiee

Élève : Pour N assez grand les inégalités relatives valent pour tout n>N ; on les somme et on laisse epsilon tendre vers zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Cela marche aussi sans signe et sans convergence des queues.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment choisir un rang commun pour toute la queue ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K067 — Sommes divergentes équivalentes

Famille : restes

**Question / contexte :** Si a_n~b_n>0 et sum b_n diverge, comparer leurs sommes partielles.

**Référence réservée à l'évaluateur :** Les sommes partielles sont équivalentes : encadrer les termes à partir d'un rang, puis les débuts finis sont négligeables devant les sommes divergentes.

**Première réponse de l'élève :** Les premiers termes empêchent d'obtenir un équivalent.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer influence sur une somme finie et sur un équivalent divergent.

**Exemple de relance, pas une phrase imposée :** Que devient une constante fixe divisée par une somme positive qui tend vers +infini ?

### Réaction : justifiee

Élève : Elle tend vers zéro ; les débuts finis disparaissent dans le rapport et l'encadrement donne l'équivalent.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Les premiers termes gardent toujours une proportion non nulle de la somme.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas isoler la partie finie.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K068 — Erreur relative et absolue

Famille : restes

**Question / contexte :** Si S_N~log N, peut-on conclure S_N-log N tend vers zéro ?

**Référence réservée à l'évaluateur :** Non : S_N=log N+1 donne un rapport tendant vers 1 mais une différence égale à 1 ; une erreur peut même être o(log N) et non bornée.

**Première réponse de l'élève :** Oui, c'est la définition de l'équivalence.

**Statut interne :** incorrecte

**Défi attendu :** Faire identifier précisément la quantité contrôlée par un équivalent.

**Exemple de relance, pas une phrase imposée :** Testez S_N=log N+1 : que donnent le rapport et la différence ?

### Réaction : justifiee

Élève : Le rapport tend vers 1 et la différence vaut 1 ; seule l'erreur relative tend vers zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Diviser par log N ne change pas une limite.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je confonds a_n~b_n et a_n-b_n tend vers zéro.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K069 — Calcul numérique et preuve

Famille : restes

**Question / contexte :** Les 100000 premiers termes d'une série donnent des sommes proches : est-ce une preuve de convergence ?

**Référence réservée à l'évaluateur :** Non : un calcul fini ne contrôle pas toute la queue. Il faut un critère ou une borne de reste ; l'harmonique peut paraître lente mais diverge.

**Première réponse de l'élève :** Oui, autant de termes garantissent la convergence.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer observation expérimentale et preuve, sans dévaloriser l'expérimentation.

**Exemple de relance, pas une phrase imposée :** Quelle information mathématique votre calcul fournit-il sur tous les termes non calculés ?

### Réaction : justifiee

Élève : Aucune borne générale ; il faut démontrer un contrôle de la queue ou appliquer un critère.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un ordinateur qui ne voit pas de divergence prouve la convergence.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment obtenir une borne plutôt qu'un graphique ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K070 — Accélération par soustraction

Famille : restes

**Question / contexte :** Pourquoi soustraire 1/n à log(1+1/n) change-t-il radicalement la sommabilité ?

**Référence réservée à l'évaluateur :** Le premier ordre harmonique s'annule ; la différence est -1/(2n^2)+O(n^{-3}), absolument sommable.

**Première réponse de l'élève :** Parce que la différence est plus petite.

**Statut interne :** incomplete

**Défi attendu :** Faire passer d'une intuition de petitesse à un ordre quantitativement sommable.

**Exemple de relance, pas une phrase imposée :** Quelle taille précise de la différence permet d'appliquer une série de comparaison convergente ?

### Réaction : justifiee

Élève : Elle est de l'ordre de n^{-2}, avec coefficient -1/2 ; son module est O(n^{-2}).

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : N'importe quelle différence tendant vers zéro serait sommable.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas quel ordre suffit.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K071 — Rapport limite strictement inférieur à un

Famille : parametres

**Question / contexte :** Pour u_n>0, que conclure si u_{n+1}/u_n tend vers 1/2 ?

**Référence réservée à l'évaluateur :** Choisir r entre 1/2 et 1 ; le rapport est finalement <=r, donc u_n est dominé par une géométrique sommable.

**Première réponse de l'élève :** La série converge par d'Alembert.

**Statut interne :** correcte

**Défi attendu :** Faire reconstruire la comparaison géométrique derrière le nom du critère.

**Exemple de relance, pas une phrase imposée :** Retrouvez la preuve en majorant les rapports par un nombre fixe inférieur à 1.

### Réaction : justifiee

Élève : Finalement le rapport est <=3/4, donc u_{N+k}<=u_N(3/4)^k.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Les rapports valent exactement 1/2 dès un certain rang.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas comment itérer l'inégalité.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K072 — Rapport limite égal à un

Famille : parametres

**Question / contexte :** Que conclure si u_{n+1}/u_n tend vers 1 ?

**Référence réservée à l'évaluateur :** Aucune conclusion générale : 1/n et 1/n^2 ont tous deux ce rapport limite, avec des séries de natures différentes.

**Première réponse de l'élève :** La série diverge.

**Statut interne :** incorrecte

**Défi attendu :** Faire reconnaître un critère non concluant sans transformer l'absence de conclusion en divergence.

**Exemple de relance, pas une phrase imposée :** Calculez cette limite pour 1/n et pour 1/n^2.

### Réaction : justifiee

Élève : Elle vaut 1 dans les deux cas ; le critère est muet à ce seuil.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 1/n^2 diverge aussi car son rapport tend vers 1.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas calculer u_{n+1}/u_n pour 1/n^2.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K073 — Factorielle

Famille : parametres

**Question / contexte :** Étudier sum_{n>=0} 1/n!.

**Référence réservée à l'évaluateur :** u_{n+1}/u_n=1/(n+1) tend vers zéro, donc convergence ; la valeur e n'est pas nécessaire pour conclure.

**Première réponse de l'élève :** Je connais la somme e, donc je n'ai pas besoin de preuve de convergence.

**Statut interne :** incomplete

**Défi attendu :** Faire justifier la convergence indépendamment d'une identité mémorisée.

**Exemple de relance, pas une phrase imposée :** Sans utiliser la valeur de la somme, quelle relation lie deux termes consécutifs ?

### Réaction : justifiee

Élève : Le rapport vaut 1/(n+1), finalement inférieur à 1/2 ; la série converge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 1/(n+1)!=(1/n!)/(n!) .

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas simplifier deux factorielles consécutives.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K074 — Exponentielle contre factorielle

Famille : parametres

**Question / contexte :** Pour a réel fixé, étudier sum_{n>=0} a^n/n!.

**Référence réservée à l'évaluateur :** Pour a=0, seul le terme n=0 vaut 1 avec a^0=1. Pour a non nul, rapport des modules |a|/(n+1) tend vers zéro : convergence absolue pour tout a.

**Première réponse de l'élève :** Il faut |a|<1 comme pour une géométrique.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer géométrique et série avec facteur factoriel, en traitant séparément a=0.

**Exemple de relance, pas une phrase imposée :** Quel rôle joue n! dans le rapport des modules de deux termes consécutifs ?

### Réaction : justifiee

Élève : Le rapport vaut |a|/(n+1), donc tend vers zéro pour tout a fixé.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : n! peut être ignoré dans le critère du rapport.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Et si a=0, le quotient est-il défini ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K075 — Puissance n^a et géométrique

Famille : parametres

**Question / contexte :** Pour a réel fixé, étudier sum_{n>=1} n^a/2^n.

**Référence réservée à l'évaluateur :** Rapport =((n+1)/n)^a/2 tend vers 1/2, donc convergence pour tout a réel.

**Première réponse de l'élève :** Elle converge seulement si a<0.

**Statut interne :** incorrecte

**Défi attendu :** Faire décider tous les paramètres fixes par le rapport plutôt que par une impression de croissance.

**Exemple de relance, pas une phrase imposée :** Quand a est fixé, vers quoi tend (1+1/n)^a ?

### Réaction : justifiee

Élève : Vers 1, donc le rapport tend vers 1/2 même si a est positif.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Pour a>0, n^a domine toujours 2^n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas comparer une puissance et une exponentielle.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K076 — Géométrique divisée par n

Famille : parametres

**Question / contexte :** Pour a réel, étudier sum_{n>=1} a^n/n.

**Référence réservée à l'évaluateur :** Convergence absolue pour |a|<1 ; a=-1 : convergence conditionnelle ; a=1 : divergence harmonique ; |a|>1 : terme ne tend pas vers zéro.

**Première réponse de l'élève :** Le rayon est 1 donc les deux bords ont le même comportement.

**Statut interne :** incorrecte

**Défi attendu :** Faire traiter séparément chaque extrémité après un critère intérieur.

**Exemple de relance, pas une phrase imposée :** Écrivez les deux séries obtenues pour a=1 et a=-1.

### Réaction : justifiee

Élève : À 1 c'est l'harmonique divergente ; à -1 l'harmonique alternée convergente non absolument.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le signe du paramètre ne peut pas changer la nature aux bords.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Le critère du rapport donne 1 aux deux bords, je suis bloqué.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K077 — Paramètre dans le dénominateur

Famille : parametres

**Question / contexte :** Pour t>=0, étudier sum_{n>=1}1/[n(1+tn)].

**Référence réservée à l'évaluateur :** À t=0 la série harmonique diverge ; pour t>0, le terme est <=1/(tn^2), donc convergence.

**Première réponse de l'élève :** La série converge pour tout t>=0 par comparaison à 1/(tn^2).

**Statut interne :** incorrecte

**Défi attendu :** Faire contrôler les hypothèses en fonction du paramètre avant une estimation.

**Exemple de relance, pas une phrase imposée :** Votre majorant est-il défini pour t=0 ? Quelle série obtenez-vous alors directement ?

### Réaction : justifiee

Élève : À zéro il n'est pas défini et la série est harmonique ; pour t>0 la comparaison convient.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Diviser par zéro ne pose pas de problème dans une majoration.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas s'il faut isoler une valeur du paramètre.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K078 — Alternée avec exposant

Famille : parametres

**Question / contexte :** Pour a réel, étudier sum_{n>=1}(-1)^n/n^a.

**Référence réservée à l'évaluateur :** Pour a<=0 le terme ne tend pas vers zéro ; pour a>0 alternance convergente ; convergence absolue exactement pour a>1.

**Première réponse de l'élève :** Elle converge pour tout a car elle est alternée.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer domaine de convergence et domaine de convergence absolue.

**Exemple de relance, pas une phrase imposée :** Que devient l'amplitude pour a=0, puis pour a<0 ?

### Réaction : justifiee

Élève : Elle vaut 1 ou croît ; il faut a>0 pour converger, et a>1 pour converger absolument.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un terme de module croissant peut passer le critère alterné.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas distinguer les deux seuils 0 et 1.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K079 — Test de la racine

Famille : parametres

**Question / contexte :** Étudier sum_{n>=1}(n/(2n+1))^n.

**Référence réservée à l'évaluateur :** La racine n-ième du terme est n/(2n+1), qui tend vers 1/2<1 ; convergence. On peut directement majorer par (1/2)^n.

**Première réponse de l'élève :** La base tend vers 1/2 donc le terme tend vers 1/2.

**Statut interne :** incorrecte

**Défi attendu :** Faire éviter un passage à la limite abusif et construire une majoration directe.

**Exemple de relance, pas une phrase imposée :** L'exposant reste-t-il fixe quand n grandit ? Pouvez-vous majorer chaque base par 1/2 ?

### Réaction : justifiee

Élève : L'exposant croît ; le terme est <=(1/2)^n, donc la série converge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La limite d'une base suffit toujours sans regarder l'exposant.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment interpréter une puissance dont l'exposant varie ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K080 — Rapport : utiliser le module

Famille : parametres

**Question / contexte :** Étudier sum_{n>=0}(-2)^n.

**Référence réservée à l'évaluateur :** Le terme général ne tend pas vers zéro. Le rapport signé vaut -2 mais le critère exige le module, ici 2>1.

**Première réponse de l'élève :** Le rapport vaut -2<1, donc convergence.

**Statut interne :** incorrecte

**Défi attendu :** Faire vérifier la formulation du critère plutôt qu'appliquer une inégalité signée.

**Exemple de relance, pas une phrase imposée :** Le critère compare-t-il le rapport signé ou le rapport des modules ?

### Réaction : justifiee

Élève : Celui des modules, égal à 2 ; de plus le terme général ne tend pas vers zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Un rapport négatif est toujours favorable à la convergence.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas pourquoi le module est indispensable.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K081 — Limite d'une récurrence

Famille : raisonnements

**Question / contexte :** x_0>0 et x_{n+1}=x_n/(1+x_n). Montrer que x_n tend vers zéro.

**Référence réservée à l'évaluateur :** Suite positive strictement décroissante, donc limite l>=0 ; par continuité l=l/(1+l), donc l=0. Aussi 1/x_n=1/x_0+n.

**Première réponse de l'élève :** Elle décroît, donc sa limite est zéro.

**Statut interne :** incomplete

**Défi attendu :** Faire compléter une conclusion correcte obtenue par un argument incomplet.

**Exemple de relance, pas une phrase imposée :** Une suite positive décroissante peut-elle tendre vers 2 ? Quelle équation doit vérifier la limite ici ?

### Réaction : justifiee

Élève : La décroissance seule ne suffit pas ; l=l/(1+l) impose l=0.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Toute décroissance stricte force une limite nulle.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas passer à la limite dans la récurrence.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K082 — Récurrence harmonique exacte

Famille : raisonnements

**Question / contexte :** Pour x_{n+1}=x_n/(1+x_n), x_0>0, étudier sum x_n.

**Référence réservée à l'évaluateur :** 1/x_{n+1}=1/x_n+1, donc x_n=1/(n+1/x_0)~1/n ; la série positive diverge.

**Première réponse de l'élève :** x_n tend vers zéro, donc sa série converge.

**Statut interne :** incorrecte

**Défi attendu :** Faire trouver la bonne transformation de suite avant de décider de la série.

**Exemple de relance, pas une phrase imposée :** Que devient la récurrence après passage aux inverses ?

### Réaction : justifiee

Élève : Les inverses augmentent de 1, donc x_n~1/n et la série diverge.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 1/(x_n/(1+x_n))=1/x_n+x_n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas calculer l'inverse de ce quotient.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K083 — Cesàro sur les accroissements

Famille : raisonnements

**Question / contexte :** Si y_{n+1}-y_n tend vers p>0, que peut-on conclure sur y_n/n ?

**Référence réservée à l'évaluateur :** y_n/n=y_0/n+(1/n)sum_{k=0}^{n-1}(y_{k+1}-y_k) tend vers p par Cesàro. Cela n'impose pas y_n-pn tend vers zéro.

**Première réponse de l'élève :** y_n-pn tend vers zéro.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer équivalent linéaire et erreur additive tendant vers zéro.

**Exemple de relance, pas une phrase imposée :** Testez y_n=pn+sqrt(n). Quelle conclusion plus faible reste toujours valable ?

### Réaction : justifiee

Élève : Les accroissements tendent vers p mais l'écart croît ; en revanche y_n/n tend vers p par Cesàro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une somme de termes qui tendent vers zéro tend forcément vers zéro.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment écrire y_n comme une somme d'accroissements ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K084 — Sommes et limites interverties

Famille : raisonnements

**Question / contexte :** Peut-on écrire lim_N sum_{n=1}^N 1/N = sum_{n>=1} lim_N 1/N = 0 ?

**Référence réservée à l'évaluateur :** Non : la somme de N termes 1/N vaut 1. Avec u_{N,n}=1/N pour n<=N et 0 sinon, chaque terme tend vers zéro mais la masse se déplace ; aucune domination sommable fournie.

**Première réponse de l'élève :** Oui, chaque terme tend vers zéro.

**Statut interne :** incorrecte

**Défi attendu :** Faire identifier un échange de limites injustifié à partir d'un calcul exact.

**Exemple de relance, pas une phrase imposée :** Calculez la somme finie avant de prendre sa limite.

### Réaction : justifiee

Élève : Elle vaut 1 pour chaque N ; l'échange n'est donc pas justifié par la seule convergence terme à terme.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une infinité de zéros doit donner zéro même si le nombre de termes change avant la limite.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas distinguer les deux indices N et n.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K085 — Reste d'un développement sous une somme

Famille : raisonnements

**Question / contexte :** Pour t>0, justifier une expansion de F(t)=sum_{n>=1}1/[n(1+tn)] quand t tend vers +infini.

**Référence réservée à l'évaluateur :** Identité : terme=1/(tn^2)-1/(t^2n^3)+1/[t^2n^3(1+tn)]. Le reste est entre 0 et 1/(t^3n^4), donc F(t)=Z_2/t-Z_3/t^2+O(t^{-3}).

**Première réponse de l'élève :** Je somme un reste O(t^{-3}) pour chaque n.

**Statut interne :** incomplete

**Défi attendu :** Faire contrôler la dépendance en l'indice avant de sommer un développement.

**Exemple de relance, pas une phrase imposée :** Votre constante dans le O dépend-elle de n ? Quelle majoration sommable en n pouvez-vous donner ?

### Réaction : justifiee

Élève : Le reste exact est <=1/(t^3n^4), donc la somme des restes est <=Z_4/t^3.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Une infinité de O(t^{-3}) est encore O(t^{-3}) sans autre hypothèse.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne trouve pas l'identité algébrique avec reste.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K086 — Sous-suite de sommes convergente

Famille : raisonnements

**Question / contexte :** Si les sommes S_{2N} convergent, la série converge-t-elle forcément ?

**Référence réservée à l'évaluateur :** Pas sans autre hypothèse, exemple sum_{n>=1}(-1)^n avec S_{2N}=0. Si u_n tend vers zéro, S_{2N+1}=S_{2N}+u_{2N+1} a la même limite, donc oui.

**Première réponse de l'élève :** Oui, une sous-suite suffit.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer l'assertion fausse de sa version complétée par u_n tendant vers zéro.

**Exemple de relance, pas une phrase imposée :** Quelle information sur u_{2N+1} permettrait de contrôler les sommes impaires ?

### Réaction : justifiee

Élève : S'il tend vers zéro, elles ont la même limite ; sans cela, (-1)^n donne un contre-exemple.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Les sommes impaires peuvent être ignorées dans la définition.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Comment relier S_{2N+1} à S_{2N} ?

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K087 — Série des carrés

Famille : raisonnements

**Question / contexte :** Si sum u_n converge, doit-on avoir sum u_n^2 convergente pour u_n réel ?

**Référence réservée à l'évaluateur :** Non : u_n=(-1)^n/sqrt n donne une série convergente, tandis que u_n^2=1/n a une série divergente.

**Première réponse de l'élève :** Oui, le carré rend les petits termes plus petits.

**Statut interne :** incorrecte

**Défi attendu :** Faire voir qu'une comparaison terme à terme en module demande déjà une série majorante sommable.

**Exemple de relance, pas une phrase imposée :** Testez une alternée d'amplitude 1/sqrt(n) : que devient le carré ?

### Réaction : justifiee

Élève : Le carré enlève l'alternance et donne l'harmonique, donc la conclusion est fausse.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La convergence conditionnelle implique la sommabilité de tous les modules plus petits.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne vois pas l'effet de supprimer les signes.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K088 — Sommabilité absolue et carrés

Famille : raisonnements

**Question / contexte :** Si sum |u_n| converge, montrer que sum |u_n|^2 converge.

**Référence réservée à l'évaluateur :** u_n tend vers zéro, donc |u_n|<=1 finalement ; alors |u_n|^2<=|u_n| et la comparaison s'applique.

**Première réponse de l'élève :** Parce que x^2<=x pour tout x positif.

**Statut interne :** incomplete

**Défi attendu :** Faire réparer une preuve de résultat vrai en précisant la validité finale de l'inégalité.

**Exemple de relance, pas une phrase imposée :** Votre inégalité vaut-elle pour x=2 ? Pourquoi devient-elle valable ici à partir d'un certain rang ?

### Réaction : justifiee

Élève : Elle vaut pour 0<=x<=1 ; comme u_n tend vers zéro, elle est vraie finalement.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 2^2<=2, donc il n'y a pas d'hypothèse supplémentaire.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je n'ai pas utilisé le fait que u_n tend vers zéro.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K089 — Logarithme d'un équivalent

Famille : raisonnements

**Question / contexte :** Si x_n~1/n avec x_n>0, que peut-on dire de log x_n+log n ?

**Référence réservée à l'évaluateur :** n x_n tend vers 1, donc log x_n+log n=log(n x_n) tend vers zéro par continuité du logarithme en 1.

**Première réponse de l'élève :** Je prends le logarithme des équivalents et j'obtiens une égalité exacte.

**Statut interne :** incomplete

**Défi attendu :** Faire justifier l'erreur additive par la continuité plutôt que par une égalité abusive.

**Exemple de relance, pas une phrase imposée :** Écrivez la somme des logarithmes comme le logarithme d'un produit dont vous connaissez la limite.

### Réaction : justifiee

Élève : C'est log(n x_n), qui tend vers log 1=0 ; ce n'est pas une égalité avec zéro pour chaque n.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : log(a_n/b_n)=0 dès que a_n~b_n.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas pourquoi le logarithme passe à la limite.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K090 — Produit terme à terme

Famille : raisonnements

**Question / contexte :** Si sum a_n et sum b_n convergent, sum a_n b_n converge-t-elle toujours ?

**Référence réservée à l'évaluateur :** Non : a_n=b_n=(-1)^n/sqrt n donnent deux séries convergentes et produit 1/n divergent. Ce n'est pas le produit de Cauchy.

**Première réponse de l'élève :** Oui, c'est le produit de deux nombres finis.

**Statut interne :** incorrecte

**Défi attendu :** Faire distinguer trois objets : produit des sommes, produit de Cauchy et produit terme à terme.

**Exemple de relance, pas une phrase imposée :** Le produit des sommes correspond-il au produit terme à terme ? Essayez a_n=b_n=(-1)^n/sqrt(n).

### Réaction : justifiee

Élève : Le produit terme à terme vaut 1/n, divergent ; je l'avais confondu avec le produit des sommes.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : (sum a_n)(sum b_n)=sum a_n b_n dans tous les cas.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas distinguer produit de Cauchy et produit terme à terme.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K091 — Réponse correcte hésitante

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/n^2.

**Référence réservée à l'évaluateur :** Convergence positive par Riemann p=2>1. L'hésitation de l'élève ne change pas la validité de cet argument.

**Première réponse de l'élève :** Je crois que ça converge, c'est Riemann avec p=2, mais je suis pas sûr.

**Statut interne :** correcte

**Défi attendu :** Ne pas confondre manque d'assurance et erreur ; challenger sobrement sans ajouter de pression.

**Exemple de relance, pas une phrase imposée :** Quel est le seuil exact sur p, et de quel côté se trouve 2 ?

### Réaction : justifiee

Élève : Le seuil est p>1 ; 2 est strictement au-dessus, donc le critère s'applique.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le seuil est p<1, mais 2 devrait marcher aussi.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je panique alors que je connais la formule.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K092 — Mauvaise réponse très assurée

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/n.

**Référence réservée à l'évaluateur :** L'harmonique diverge ; les blocs de 2^k à 2^{k+1}-1 valent au moins 1/2.

**Première réponse de l'élève :** Évidemment ça converge, aucun doute, les termes vont vers zéro.

**Statut interne :** incorrecte

**Défi attendu :** Ne pas se laisser guider par l'assurance de l'élève ; proposer un test concret sans humiliation.

**Exemple de relance, pas une phrase imposée :** Combien vaut au moins la somme des termes entre 2^k et 2^{k+1}-1 ?

### Réaction : justifiee

Élève : Elle vaut au moins 1/2 ; ma justification initiale ne suffit pas, et les sommes divergent.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Je suis certain d'avoir raison, pas besoin de vérifier les blocs.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne comprends pas pourquoi vous choisissez ces bornes.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K093 — Réaction trop brève : compris

Famille : interaction

**Question / contexte :** Justifier la convergence d'une série alternée dont les amplitudes décroissent vers zéro.

**Référence réservée à l'évaluateur :** La justification doit mentionner monotonie des amplitudes et limite nulle ; « compris » ne démontre pas la compréhension.

**Première réponse de l'élève :** Ça marche grâce aux signes.

**Statut interne :** incomplete

**Défi attendu :** Ne pas enregistrer une reformulation acquise sur un simple acquiescement ; demander un contenu précis.

**Exemple de relance, pas une phrase imposée :** Pouvez-vous reformuler les deux propriétés à vérifier sur les amplitudes ?

### Réaction : justifiee

Élève : Elles doivent décroître et tendre vers zéro ; l'alternance seule ne suffit pas.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Compris, les signes seuls suffisent.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Compris... mais je n'arrive pas à l'expliquer.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K094 — Demande d'un indice minimal

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/[n(n+1)].

**Référence réservée à l'évaluateur :** Décomposition en 1/n-1/(n+1), télescopage, somme 1. Un premier indice peut inviter à décomposer sans donner la somme.

**Première réponse de l'élève :** Donnez-moi juste une piste, pas le corrigé.

**Statut interne :** aide

**Défi attendu :** Donner un indice proportionné, puis le réduire au calcul d'une fraction si l'élève reste bloqué.

**Exemple de relance, pas une phrase imposée :** Quelle différence de deux fractions simples pourrait avoir n(n+1) pour dénominateur ?

### Réaction : justifiee

Élève : 1/n-1/(n+1) convient ; la somme finie vaut 1-1/(N+1), donc la série converge vers 1.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : 1/n+1/(n+1) est égal à 1/[n(n+1)].

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais même pas mettre ces deux fractions au même dénominateur.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K095 — Corrigé explicitement demandé

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/n^2 par comparaison intégrale.

**Référence réservée à l'évaluateur :** La positivité et décroissance donnent sum_{n=1}^N1/n^2<=1+int_1^N dx/x^2<=2 ; les sommes sont croissantes majorées.

**Première réponse de l'élève :** Je bloque, expliquez-moi la correction complète puis vérifiez que j'ai compris.

**Statut interne :** correction

**Défi attendu :** Une correction explicitement demandée autorise l'explication ; terminer par une vérification et ne pas refuser au nom du challenge.

**Exemple de relance, pas une phrase imposée :** Après l'encadrement par l'intégrale, quelle propriété des sommes partielles permet de conclure ?

### Réaction : justifiee

Élève : Elles sont croissantes par positivité et majorées par 2, donc convergentes.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : La majoration seule fait converger toute suite.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas relier les rectangles à l'intégrale.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

**Correction fournie avant la relance dans les sondes de réaction :**

Pour f(x)=1/x^2, positive et décroissante, chaque terme 1/n^2 avec n>=2 est au plus l'intégrale de n-1 à n de f. Donc S_N<=1+int_1^N dx/x^2<=2. Les sommes partielles sont croissantes par positivité et majorées, donc la série converge.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K096 — Contestation mathématique fondée

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}(-1)^{n-1}/n. Le khôlleur a affirmé à tort que la série diverge parce que les modules divergent.

**Référence réservée à l'évaluateur :** La série converge conditionnellement par le critère alterné. Le khôlleur doit rectifier sa confusion avec la convergence absolue.

**Première réponse de l'élève :** Votre objection me semble fausse : la convergence absolue est suffisante mais pas nécessaire.

**Statut interne :** correcte

**Défi attendu :** Rectifier explicitement l'erreur du khôlleur puis faire justifier, au lieu de défendre sa première affirmation.

**Exemple de relance, pas une phrase imposée :** Reprenons : quelles hypothèses du critère alterné pouvez-vous vérifier ici ?

### Réaction : justifiee

Élève : Les amplitudes 1/n décroissent vers zéro ; la série converge même si elle ne converge pas absolument.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Finalement, toute série alternée converge, quelle que soit l'amplitude.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je sais que l'absolue n'est pas nécessaire, mais je ne retrouve pas le critère.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

**Historique préalable injecté pour ce cas :**

- assistant : La série diverge puisque la série des modules diverge.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K097 — Notation orale équivalente

Famille : interaction

**Question / contexte :** Définir la convergence de sum_{k>=1}u_k.

**Référence réservée à l'évaluateur :** Il suffit que les sommes finies des termes d'indice 1 à N tendent vers un réel fini ; une formulation orale correcte est recevable.

**Première réponse de l'élève :** Quand j'additionne de plus en plus de termes, le total a une limite réelle finie.

**Statut interne :** correcte

**Défi attendu :** Accepter le sens mathématique de la formulation orale plutôt qu'exiger le vocabulaire exact.

**Exemple de relance, pas une phrase imposée :** Si vous appelez ce total S_N, quel lien permet d'en déduire la limite de u_N ?

### Réaction : justifiee

Élève : u_N=S_N-S_{N-1}, donc sa limite est zéro.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : u_N a la même limite que le total.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je ne sais pas écrire la formule mais je vois le terme ajouté.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K098 — Auto-correction dans le même message

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/n.

**Référence réservée à l'évaluateur :** La dernière position argumentée est une divergence par blocs d'au moins 1/2 ; ne pas évaluer seulement la première phrase retirée.

**Première réponse de l'élève :** Ça converge car 1/n tend vers zéro... non, je me corrige : c'est harmonique, les blocs dyadiques restent au moins égaux à 1/2.

**Statut interne :** correcte

**Défi attendu :** Prendre en compte la rectification explicite de l'élève, sans le figer sur son erreur initiale.

**Exemple de relance, pas une phrase imposée :** Expliquez comment cette borne par bloc fait grandir les sommes partielles sans limite.

### Réaction : justifiee

Élève : Après m blocs disjoints on a ajouté au moins m/2, ce qui tend vers +infini.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Les blocs ont une borne inférieure positive mais leur somme pourrait rester finie.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je sais le résultat, mais je ne sais pas passer d'un bloc à m blocs.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K099 — Pression pour un verdict binaire

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/n^2.

**Référence réservée à l'évaluateur :** La convergence suit de Riemann p=2>1. Une demande binaire n'empêche pas de demander une justification brève et pertinente.

**Première réponse de l'élève :** Ça converge. Dites juste oui ou non, je veux répondre vite.

**Statut interne :** incomplete

**Défi attendu :** Travailler la réactivité par une justification courte sans sacrifier le contenu ni se limiter à oui/non.

**Exemple de relance, pas une phrase imposée :** En une phrase, quel critère et quelle hypothèse vous permettent de conclure ?

### Réaction : justifiee

Élève : Riemann : l'exposant 2 est strictement supérieur à 1.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Parce que les termes tendent vers zéro, comme toutes les séries convergentes.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je peux donner le nom du critère mais pas sa condition.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.

## K100 — Même défi répété après justification

Famille : interaction

**Question / contexte :** Étudier sum_{n>=1}1/n^2 ; l'élève a déjà justifié Riemann avec p=2>1 et répété l'argument à la demande du khôlleur.

**Référence réservée à l'évaluateur :** La convergence est acquise. Une suite utile est l'estimation du reste R_N entre 1/(N+1) et 1/N ; ne pas réexiger encore la même justification.

**Première réponse de l'élève :** J'ai déjà expliqué deux fois que p=2>1. Quelle est la suite ?

**Statut interne :** correcte

**Défi attendu :** Mettre fin à une boucle de validation stérile et proposer une seule extension adaptée, avec un indice si nécessaire.

**Exemple de relance, pas une phrase imposée :** Estimons maintenant la queue après N termes : quelles intégrales l'encadrent ?

### Réaction : justifiee

Élève : Elle est entre l'intégrale de N+1 à l'infini et celle de N à l'infini, soit entre 1/(N+1) et 1/N.

Attendu : Tenir compte de la justification donnée, accepter ses formulations équivalentes et poursuivre sans refaire le même défi.

### Réaction : erreur_persistante

Élève : Le reste est exactement nul parce que la série converge.

Attendu : Cibler le point mathématique encore erroné avec une question plus concrète, sans validation complaisante ni simple verdict.

### Réaction : blocage

Élève : Je connais Riemann mais pas encore l'estimation des restes.

Attendu : Réduire la difficulté de la relance avec un seul indice utilisable ; laisser ensuite répondre l'élève.

**Historique préalable injecté pour ce cas :**

- user : La série converge par Riemann : p=2>1.
- assistant : Pourquoi ce critère s'applique-t-il ?
- user : Les termes sont 1/n^p avec p=2, strictement supérieur à 1.
- assistant : Justifiez encore la convergence.

Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.
