# Note de livraison — Chaîne fonctionnelle : cours et exercices interactifs

## Construction reprise du dépôt RDM

**Sources** : le dépôt RDM (construction : générateur, gabarit, accueil, pastilles, tests), le portail animé
(ancien `index.html` de ce dépôt), l'exercice du dépôt « schema_chaine-energie-information », le cours Word
« Chaîne d'énergie des produits » et la page « Chaîne de puissance : formulaire et exercices ».

**Dépôts non modifiés** : RDM et schema_chaine-energie-information. Le gabarit du dépôt RDM est copié tel quel dans
`src/gabarit-exercice-interactif.html` (fichier identique, vérifié octet par octet).

**Accueil** (`index.html`), sur le modèle de l'accueil RDM : en-tête et montage d'illustration (les quatre systèmes de
l'exercice 1.1), puis les rubriques **Les cours** (Cours 1, pastille verte Niveau 1 ; Cours 2, pastille bleue
Niveau 2), **Le formulaire** (bandeau menant au formulaire en carte mentale et aux exercices de calcul), **Les
exercices** (Exercice 1.1, Niveau 1) et **Études de cas** (une carte « En cours d'édition », remplacée d'elle-même
par les études décrites dans `EXO_DEFS` avec `"etude": True`). Les numéros suivent la logique RDM : le premier
chiffre d'un exercice donne son niveau (1.1, puis 1.2… et 2.1… au niveau 2).

**Moteur applicatif** : seules les entrées réservées au sujet sont remplacées, chaque remplacement étant vérifié :
`CONSEIL_MIN` (lue dans `window.__CONSEIL_MIN__`), `DECOR` et `DR_NAMES` (vides : aucun tracé pour l'instant), le
texte de la fenêtre « Imprimer les DR », et le libellé « Diagramme validé » des questions à plusieurs cases, devenu
« Réponses validées ». Le correctif d'impression des tracés relevé dans le dépôt RDM est repris. Les consignes sont
propres à chaque exercice (modèle `tpl-consignes-…`), puisque l'exercice 1.1 ne comporte ni calcul ni unité.

## Cours 1 — La chaîne fonctionnelle (Niveau 1, `?ex=cours-chaine-fonctionnelle`)

Le portail interactif fait office de cours. Son schéma SVG et son script sont **extraits de
`src/portail-anime.html`** à chaque génération (remplacements vérifiés) ; le fichier d'origine reste une page autonome
que l'on peut ouvrir seule.

- Remplacements : classe `part` → `cp-part` (évite la classe homonyme du gabarit) ; titres `h1`/`h2` de l'animation →
  `h3` (le titre du cours est le seul `h1`) ; raccourcis clavier (← → espace) limités à l'animation, qui prend le focus
  quand on clique sur la scène, pour ne pas gêner le reste de la page.
- Style repris dans `generer.py`, préfixé par `.cp`. Dans le cours, l'animation et son panneau d'explication sont côte
  à côte (au-delà de 1 000 px) ; le bouton **Plein écran** restitue la mise en page d'origine, qui tient dans la
  hauteur de l'écran (vidéoprojecteur), sans perdre le scénario ni l'étape en cours ; Échap en sort.
- Ajouts : « L'essentiel à retenir » (huit cartes à retourner : rôle de chaque fonction et composants du portail qui la
  réalisent, ce qui relie les deux chaînes, ce qui circule), deux jeux (« Information ou énergie ? », 8 lignes ;
  « Quelle fonction réalise ce composant ? », 10 lignes) et un quiz de 8 questions noté avec étoiles. Tous reprennent
  le vocabulaire et les composants de l'animation.

## Cours 2 — Chaîne d'énergie des produits (Niveau 2, `?ex=cours-chaine-energie`)

Le cours Word est rendu « vivant » : tout son texte est conservé, ses huit parties deviennent des sections avec
navigation, complétées d'une synthèse et d'un quiz.

- **En-tête** : objectifs, compétences travaillées (CO3.1, CO3.2, CO4.2, taxonomie 2) et prérequis, comme dans le Word.
- **Figure 1** (chaînes de la trottinette) **redessinée** : six flux cliquables (consignes, informations restituées,
  commandes, états de la trottinette, puissance entrante, puissance utile), animés et expliqués.
- **Figure 2** (chaîne de puissance en blocs) **redessinée** : blocs cliquables (rôle, préactionneur / actionneur /
  effecteur, composant de la trottinette), flux d'énergie animé. **Figure 3** (ibd) conservée, avec un défi corrigé.
- **Tableaux de composants** (figures 4 à 11 du Word) → **25 fiches** (6 Alimenter, 5 Distribuer, 5 Convertir,
  9 Transmettre) : photo et symbole découpés dans les tableaux (`outils/preparer-images.sh`), fonction,
  caractéristiques et, pour Convertir, fonctionnement retranscrits en texte. Les exemples d'effecteurs (Agir) gardent
  leurs photos. À l'impression, toutes les fiches sont imprimées.
- **Simulateurs** : oscilloscope (réseau monophasé, triphasé, batterie, éolienne ; lecture au survol ou au clavier) ;
  hacheur et moteur à courant continu (rapport cyclique, tension moyenne, vitesse, inversion des polarités) ;
  engrenage, pignon-crémaillère et vis-écrou animés ; ordres de grandeur sur une échelle logarithmique ;
  calculateurs d'énergie, de puissance (effort × flux), de rendement d'un chargeur, de rendement global de la chaîne
  de la trottinette et d'autonomie d'une batterie. Deux jeux (« Quelle énergie à la sortie ? », 8 lignes ; synthèse
  « Range chaque composant dans sa fonction », 12 lignes) et un quiz de 10 questions.
- **Figures 12 et 13** du Word (voiture électrique, chargeur de téléphone) conservées ; les figures du cours sont
  renumérotées de 1 à 5.
- Graphiques : couleurs vérifiées pour les daltonismes (V1, V2, V3 en bleu, orange et vert d'eau ; signal et valeur
  moyenne en bleu et orange), étiquettes directes, légendes, valeurs reprises sous chaque graphique ou dans un tableau
  dépliable ; animations suspendues si le système demande de réduire les mouvements.

Corrections, interprétations et compléments :
- **Cases tronquées du Word complétées** : « à partir d'une [source renouvelable (soleil, vent)] », « variables suivant
  [le soleil ou le vent] », « utiliser son énergie pour [alimenter le produit] ».
- **Fusibles** : « gI » devient « gG — anciennement gI — » (désignation actuelle).
- **« Écrou/Vis sans fin »** devient **« Système vis-écrou »** (une vis sans fin désigne la vis d'un engrenage roue
  et vis) ; **« Pignon/Vis sans fin »** devient **« Roue et vis sans fin »** ; « r = Ns/Ne = Nombre filet/D2 » devient
  « nombre de filets de la vis / nombre de dents de la roue Z2 » (un rapport de dents, pas un diamètre).
- **Poulies et pignons-chaîne** : D1 roue menante (le pignon), D2 roue menée, comme sur le symbole du Word.
- **Batterie « d'iPhone 6 »** devient « batterie de téléphone » (pas de nom de marque, comme dans le dépôt RDM).
- « Ce thème permettra d'étudier » devient « Ce thème permet d'étudier ».
- **Valeurs des simulateurs** : batterie de la trottinette 36 V et 7,8 Ah (lues sur la figure 3) ; moteur à vide :
  3 000 tr/min sous 36 V ; éolienne : fréquence et tension proportionnelles au vent (valeurs indicatives) ; rendements
  par défaut de la chaîne de la trottinette 0,90 ; 0,95 ; 0,85 ; 0,90. Ces hypothèses sont écrites à côté de chaque
  simulateur.

## Exercice 1.1 — Chaînes d'information et d'énergie (Niveau 1, `?ex=chaines-information-energie`)

**Source** : l'exercice du dépôt « schema_chaine-energie-information » (ascenseur, Toyota Prius, chauffage
géothermique, portail automatisé ; 14 questions, 57 champs).

- Chaque système devient une **partie** : 15, 12, 18 et 15 min (1 h), 15, 11, 19 et 12 points. Les 14 questions
  d'origine gardent leurs cases, **validées ensemble** (mécanisme « fast-q » du gabarit) : un bouton par question, une
  correction commune avec le tableau des réponses attendues et la démarche d'origine ; chaque case vaut un point.
- La note n'est plus « bonnes réponses / 57 × 20 » : comme dans le dépôt RDM, chaque partie est notée sur 20 puis
  pondérée par sa durée ; modes entraînement et examen, chronomètre, impression, récapitulatif.
- Documents rédigés : **DP1** (rappel de cours de la source et schéma général des deux chaînes) et **DT1** (rôle de
  chaque fonction, exemple de la trottinette, indices pour repérer une case). Ils ne citent pas les composants des
  quatre systèmes.
- Champs « Nom, prénom / Classe / Date » remplacés par le champ « Nom et prénom » du gabarit (la date est imprimée).

Corrections et décisions :
- **Schéma de l'ascenseur** : il reprenait les légendes du portail (« Vantail en position initiale / finale ») ; elles
  deviennent « Usager à l'étage de départ / d'arrivée » (image corrigée par `outils/preparer-images.sh`, l'original
  reste dans `src/images/originaux`). La démarche de la question Q1.2 le mentionne.
- **Prius, repère 4** : la flèche qui part de la génératrice rejoint le répartiteur (repère 2), qui recharge la
  batterie (repère 1) ; la démarche le précise (la source la faisait aller directement au repère 1).
- **Tolérance de saisie** : les 270 formulations acceptées par l'exercice d'origine restent toutes justes (test
  unitaire). Ajouts : « carte électronique » et « microcontrôleur » pour la fonction Traiter du portail (vocabulaire du
  cours 1). Refus explicites des confusions : « moteur à bras » pour Transmettre, « moteur actionnant des câbles » pour
  Transmettre, sondes intérieure et extérieure inversées, « capteur de température » pour le capteur géothermique,
  « télécommande » pour le boîtier de commande, moteur électrique et moteur thermique inversés.
- Les noms des systèmes réels (Toyota Prius, réseau EDF sur la figure) sont conservés comme dans l'exercice d'origine.

## Formulaire de la chaîne de puissance (`formulaire.html`)

La page fournie est publiée telle quelle, avec trois liens « Accueil : chaîne fonctionnelle » ajoutés (menu, carte
mentale, réglages des exercices), par remplacements vérifiés. Sur l'accueil, le bandeau « Formulaire de la chaîne de
puissance » rappelle la chaîne des formules (P = U × I, η = Pu / Pa, Ns = r × Ne, P = F × v) et ouvre directement la
carte mentale (`#formulaire`) ou les exercices de calcul (`#exercices`). Le cours 2 y renvoie aussi.

## Points signalés sans modification

- Les figures de l'exercice sont de faible définition (282 à 900 px de large) ; elles sont intégrées telles quelles
  (PNG quantifiés). La figure 3 du cours (ibd) est coupée en bas, comme dans le Word.
- Quelques photos des tableaux du Word portent un logo de fabricant ; elles ne sont pas retouchées.
- Poids : `index.html` 1,7 Mio (1,3 Mio d'images), `formulaire.html` 150 Kio.

## Vérifications effectuées

- `node --test tests/correction.test.js` : 6 tests — configuration (4 parties, 57 cases, 60 min), réponse de référence
  juste pour chaque case, 270 formulations d'origine acceptées, confusions et fautes de frappe, aucune fonction
  acceptée à la place d'une autre, saisie vide refusée.
- `tests/navigateur.test.js` (Playwright, Chromium) : 8 parcours, tous réussis — accueil (cartes, bandeau du
  formulaire, annonce de l'étude, téléphone, aucune mention de diplôme ou d'épreuve) ; adresse inconnue ; cours 1
  (étapes, scénarios, clavier, plein écran, cartes, jeux, quiz) ; cours 2 (figures, fiches, oscilloscope, hacheur,
  transmissions, puissances, énergie, effort et flux, rendements, autonomie, jeux, quiz, impression, téléphone) ;
  exercice en entraînement (cases vides, confirmation, verrouillage, 19,7 puis 20,0/20) ; exercice en examen (rien ne
  filtre avant la remise, y compris à l'impression ; remise en deux temps ; chronomètre arrêté ; 18,6/20) ;
  documents et téléphone ; formulaire (liens vers l'accueil, vues ouvertes depuis l'accueil).
- Aucune erreur JavaScript dans aucun parcours.
