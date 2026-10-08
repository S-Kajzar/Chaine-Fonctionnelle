# Chaîne fonctionnelle : cours et exercices interactifs

Construction reprise du dépôt « Résistance des matériaux » (RDM) : une page autonome (un seul fichier HTML, aucune
dépendance externe, utilisable hors ligne), publiée par GitHub Pages depuis `index.html`, et la page
`formulaire.html` (formulaire de la chaîne de puissance), présentée sur l'accueil. L'accueil mène à :

| Adresse | Contenu |
|---|---|
| `index.html` | accueil : les cours (pastilles Niveau 1 / Niveau 2), le formulaire, les exercices (dont les exercices de calcul du formulaire), les études de cas |
| `?ex=cours-chaine-fonctionnelle` | Cours 1 — La chaîne fonctionnelle (Niveau 1) : portail automatique animé pas à pas (deux scénarios, plein écran pour vidéoprojecteur), cartes des huit fonctions, deux jeux, quiz |
| `?ex=cours-chaine-energie` | Cours 2 — Chaîne d'énergie des produits (Niveau 2) : figures animées, 25 fiches de composants, oscilloscope, hacheur, transmissions, ordres de grandeur, énergie, effort et flux, rendements, autonomie, deux jeux, quiz |
| `?ex=cours-chaine-information` | Cours 3 — Chaîne d'information des produits (Niveau 2) : machine à café animée, blocs internes, laboratoire des capteurs, chaîne d'acquisition, filtre, CAN, programme exécuté pas à pas, optocoupleur, trames, octet, hexadécimal, ASCII, trois jeux, quiz |
| `?ex=chaines-information-energie` | Exercice 1.1 — Chaînes d'information et d'énergie (Niveau 1) : 4 parties, 14 questions, 57 cases à remplir en y glissant des étiquettes, 1 h |
| `formulaire.html#formulaire` | formulaire de la chaîne de puissance en carte mentale |
| `formulaire.html#exercices` | séries d'exercices de calcul à valeurs aléatoires |

La rubrique « Études de cas » annonce une étude « En cours d'édition » tant qu'aucune étude n'est décrite.
Chaque exercice propose le mode entraînement ou le mode examen, avec sa propre note pondérée par la durée de ses
parties. Corrections apportées aux contenus d'origine et décisions : [`NOTE-DE-LIVRAISON.md`](NOTE-DE-LIVRAISON.md).

**Ajouter un exercice** : décrire ses parties dans `src/generer.py` (sur le modèle de `PARTS_EX1`, chaque question
à cases recevant sa liste d'étiquettes comme dans `EX1_ETIQUETTES`), puis l'ajouter à `EXO_DEFS` ; **ajouter une étude de cas** : même chose avec `"etude": True`. La carte apparaît d'elle-même sur
l'accueil (et remplace l'annonce « En cours d'édition »).

## Régénérer les pages

Les pages sont produites par un script, à partir du gabarit (`src/gabarit-exercice-interactif.html`, copie conforme de
celui du dépôt RDM, recopié sans modification de son style ni de ses moteurs), de l'animation du portail
(`src/portail-anime.html`, qui s'ouvre aussi seule dans un navigateur), du formulaire
(`src/formulaire-chaine-de-puissance.html`) et du contenu décrit dans `src/generer.py`.

```sh
bash outils/preparer-images.sh   # seulement si les images de src/images/originaux changent (ImageMagick 6)
python3 src/generer.py           # écrit index.html et formulaire.html
```

## Tester

```sh
node --test tests/correction.test.js                          # moteur de correction : 57 cases, 270 formulations d'origine, étiquettes
NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js # accueil, cours, entraînement, examen, étiquettes, documents, formulaire
```

`tests/reponses.js` contient la bonne étiquette de chaque case ; le parcours navigateur vérifie qu'un sujet entièrement
juste donne 20/20, sans erreur JavaScript.

## Organisation

| Chemin | Rôle |
|---|---|
| `src/gabarit-exercice-interactif.html` | gabarit de référence (charte, moteurs de correction et d'application), repris du dépôt RDM |
| `src/generer.py` | contenu (exercice, documents, cours interactifs), accueil, aiguillage et assemblage |
| `src/cours_information.py` | cours 3 : contenu, figures SVG, comportement et style |
| `src/rav4.py` | exercice 1.1, partie 2 : figures animées du Toyota RAV4 hybride (motorisation, chaîne d'énergie) |
| `src/portail-anime.html` | animation d'origine du portail automatique (source du cours 1) |
| `src/formulaire-chaine-de-puissance.html` | formulaire d'origine (source de `formulaire.html`) |
| `src/images/originaux/` | figures d'origine : exercice (`ex1-*`), cours Word (`ce-fig-*`, tableaux `ce-tab-*`) |
| `src/images/` | figures quantifiées intégrées en data URI, photos (`ce-ph-*`) et symboles (`ce-sy-*`) découpés dans les tableaux du cours, montage de la page d'accueil |
| `outils/preparer-images.sh` | quantification, découpes, correction du schéma de l'ascenseur, photo du RAV4, montage d'accueil |
| `outils/vignette-rav4.js` | vignette de la motorisation du RAV4 pour le montage d'accueil (Playwright) |
| `tests/` | tests Node et Playwright |
| `.github/workflows/static.yml` | publication GitHub Pages (déclenchée sur la branche `main`) |
