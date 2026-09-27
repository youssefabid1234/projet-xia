# Comparaison Pipelex du 27 septembre 2026

Configuration retenue : gpt-4o-mini. Validation Pipelex : valide, executable, un seul PipeLLM, aucune signature en attente. Contrat inchange : enonce, reponse_eleve, corrige -> Evaluation.

La comparaison directe au corrige etait deja en place avant cette intervention. Aucun calcul de reference a supprimer. Le seul changement de la methode est son modele explicite.

La progression depend de verdict, type_erreur et historique actualise par evaluation. Aucune parallelisation entre ces deux appels : la rendre possible demanderait un autre contrat (par exemple des decisions conditionnelles), donc un changement du fonctionnement pedagogique. Les reponses de cours correctes evitent deja la progression.

## Protocole et limites

Trois messages reels par configuration, via HTTP et services OpenAI/Pipelex, profils isoles. Les selections initiales de chapitre sont exclues. La reference initiale utilise le premier essai APRES correction de observer_tour (24,53 s), et non celui en echec a 34,57 s. Les deux premiers messages et questions sont identiques entre configurations. Le troisieme differe avec gpt-4o-mini : le tuteur a demande la definition de convergence absolue plutot que le theoreme ; pas de gain causal calculable sur ce cas. Une seule mesure par cas ne permet pas de separer variation reseau/serveur et effet du modele. Les selections de chapitre des sessions ont pu se chevaucher ; les trois messages mesures de chaque configuration ont ete envoyes successivement.

Les verdicts des essais Luna et gpt-4o-mini sont incorrecte, correcte, correcte, conformes aux reponses saisies. Ce petit echantillon ne valide pas la qualite sur tout le catalogue.

## initial

| Cas | Evaluation | Progression | Dialogue | Cours | Autres | Total | HTTP |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8.967 s | 12.151 s | 2.521 s | 0.000 s | 0.890 s | 24.528 s | 200 |
| 2 | 7.283 s | 0.000 s | 2.866 s | 0.249 s | 0.663 s | 11.061 s | 200 |
| 3 | 8.547 s | 0.000 s | 2.961 s | 0.183 s | 0.688 s | 12.378 s | 200 |

Cas 1, 37fbbbe9e082 : Une serie converge si son terme general tend vers zero. C'est ma reponse finale.

[Logs serveur](session-reelle-20260927-114527/serveur.log) / [Dialogue HTTP](session-reelle-20260927-114527/session.json)

Cas 2, 8a94e2b5ae52 : La serie de terme general u_n converge lorsque la suite S_n = somme des u_k pour k de 0 a n admet une limite finie. Cette limite est la somme de la serie.

[Logs serveur](session-reelle-20260927-113834/serveur.log) / [Dialogue HTTP](session-reelle-20260927-113834/session.json)

Cas 3, 79efb54cbde5 : Soit (u_n) une suite de nombres reels ou complexes. Si la serie de terme general |u_n| converge, alors la serie de terme general u_n converge. De plus, la valeur absolue de sa somme est inferieure ou egale a la somme des |u_n|.

[Logs serveur](session-reelle-20260927-113834/serveur.log) / [Dialogue HTTP](session-reelle-20260927-113834/session.json)

## gpt-5.6-luna

| Cas | Evaluation | Progression | Dialogue | Cours | Autres | Total | HTTP |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 13.978 s | 9.756 s | 2.312 s | 0.000 s | 1.068 s | 27.114 s | 200 |
| 2 | 19.153 s | 0.000 s | 4.543 s | 0.453 s | 1.023 s | 25.173 s | 200 |
| 3 | 27.358 s | 0.000 s | 7.645 s | 0.243 s | 1.279 s | 36.525 s | 200 |

Cas 1, 4439561c61d9 : Une serie converge si son terme general tend vers zero. C'est ma reponse finale.

[Logs serveur](session-reelle-20260927-115146/serveur.log) / [Dialogue HTTP](session-reelle-20260927-115146/session.json)

Cas 2, 1df199c17347 : La serie de terme general u_n converge lorsque la suite S_n = somme des u_k pour k de 0 a n admet une limite finie. Cette limite est la somme de la serie.

[Logs serveur](session-reelle-20260927-115207/serveur.log) / [Dialogue HTTP](session-reelle-20260927-115207/session.json)

Cas 3, 5ad436fdd11e : Soit (u_n) une suite de nombres reels ou complexes. Si la serie de terme general |u_n| converge, alors la serie de terme general u_n converge. De plus, la valeur absolue de sa somme est inferieure ou egale a la somme des |u_n|.

[Logs serveur](session-reelle-20260927-115207/serveur.log) / [Dialogue HTTP](session-reelle-20260927-115207/session.json)

## gpt-4o-mini

| Cas | Evaluation | Progression | Dialogue | Cours | Autres | Total | HTTP |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6.859 s | 13.728 s | 2.243 s | 0.000 s | 1.088 s | 23.918 s | 200 |
| 2 | 8.648 s | 0.000 s | 2.878 s | 0.203 s | 1.138 s | 12.868 s | 200 |
| 3 | 8.561 s | 0.000 s | 3.402 s | 0.357 s | 1.166 s | 13.486 s | 200 |

Cas 1, d88aafc0f12a : Une serie converge si son terme general tend vers zero. C'est ma reponse finale.

[Logs serveur](session-reelle-20260927-115502/serveur.log) / [Dialogue HTTP](session-reelle-20260927-115502/session.json)

Cas 2, 728de0cdcf5f : La serie de terme general u_n converge lorsque la suite S_n = somme des u_k pour k de 0 a n admet une limite finie. Cette limite est la somme de la serie.

[Logs serveur](session-reelle-20260927-115519/serveur.log) / [Dialogue HTTP](session-reelle-20260927-115519/session.json)

Cas 3, 57dc8567723d : Une serie de terme general u_n est absolument convergente si la serie de terme general |u_n| converge. Pour une suite reelle ou complexe, la convergence absolue implique la convergence de la serie de terme general u_n.

[Logs serveur](session-reelle-20260927-115519/serveur.log) / [Dialogue HTTP](session-reelle-20260927-115519/session.json)

## Gain observe sur les deux cas comparables

Cas 1 : gain evaluation +2.108 s (+23.5 %), gain total +0.611 s.
Cas 2 : gain evaluation -1.365 s (-18.7 %), gain total -1.807 s.

Conclusion : gpt-4o-mini est plus rapide que Luna sur ces essais, mais aucun gain global reproductible par rapport a la configuration initiale n'est demontre. Ne pas presenter ce changement comme une acceleration garantie.

42 tests hors ligne passes ; validation distante finale passee. Les types generes de progression restent inchanges car leur methode et son contrat ne changent pas.

Reference technique consultee : [PipeLLM, sortie structuree directe en un appel](https://docs.pipelex.com/latest/building-methods/pipes/pipe-operators/PipeLLM/).