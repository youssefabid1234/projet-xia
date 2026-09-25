# Extraction du polycopié

Dépendance : `pymupdf==1.28.2`.

```powershell
.\.venv-extraction\Scripts\python.exe scripts/extract_topologie.py --chapitre 2 --enonces 10 12 --corriges 99 106
```

`extract_topologie.py` appelle désormais le moteur général `extract_chapitre.py`.
Les bornes désignent des pages PDF inclusives, à partir de 1. Le chapitre est
fusionné par identifiant avec le fichier existant : relancer la commande ne crée
pas de doublons et conserve les autres chapitres. Le champ `page_source` donne
les pages PDF et imprimées, sous forme de liste pour les passages sur plusieurs pages.

Le moteur extrait et segmente le texte, retire les titres courants et pieds de
page, puis applique les transcriptions relues disponibles dans `transcriptions/`.
Elles sont liées à l'empreinte du PDF. Pour un nouveau chapitre sans transcription,
le résultat est du texte PDF brut, dont les formules doivent être relues ; le
fichier d'audit indique explicitement cette absence de contrôle. Il ne s'agit
pas d'un convertisseur automatique de mathématiques en LaTeX.

Pour le chapitre 2, les transcriptions LaTeX conservent les coquilles originales.
Les corrigés 2.9, 2.10, 2.13 et 2.20 incluent aussi des liens Markdown vers des
fac-similés (relatifs au dossier `data`) afin de conserver les figures, tableaux
et mises en page défectueuses. La ligne débordant de la page dans le corrigé 2.20
n'est pas complétée. Les corrigés 2.4, 2.6, 2.8 et 2.24 sont des chaînes vides,
comme dans le PDF ; les corrigés partiels ne sont pas complétés.

Vérification du moteur : `python scripts/test_extract_chapitre.py`.

La difficulté est extraite automatiquement pour chaque nouvelle entrée. Le
champ `difficulte` compte les étoiles noires : de 0 à 5 dans ce polycopié,
car certains exercices ne portent que des étoiles vides. Zéro n'est pas une
valeur de remplacement pour une notation absente : une notation inconnue
interrompt l'extraction avant l'écriture du JSON.

Pour compléter uniquement les entrées déjà présentes, sans réextraire leur contenu :

```powershell
.\.venv-extraction\Scripts\python.exe scripts/extract_topologie.py --difficultes-seulement
```

Les étoiles pleines et vides partagent le caractère Unicode `⋆` dans le PDF.
Le moteur utilise donc les identifiants de glyphes de la police FontAwesome
embarquée, contrôlée par empreinte SHA-256, et leur position près du titre.
