# Note de livraison — Chaîne fonctionnelle : cours et exercices interactifs

## Construction reprise du dépôt RDM

**Sources** : le dépôt RDM (construction : générateur, gabarit, accueil, pastilles, tests), le portail animé
(ancien `index.html` de ce dépôt), l'exercice du dépôt « schema_chaine-energie-information », le cours Word
« Chaîne d'énergie des produits » et la page « Chaîne de puissance : formulaire et exercices ».

**Dépôts non modifiés** : RDM et schema_chaine-energie-information. Le gabarit du dépôt RDM est copié tel quel dans
`src/gabarit-exercice-interactif.html` (fichier identique, vérifié octet par octet).

**Accueil** (`index.html`), sur le modèle de l'accueil RDM : en-tête et montage d'illustration (les quatre systèmes de
l'exercice 1.1), puis les rubriques **Les cours** (Cours 1, pastille verte Niveau 1 ; Cours 2 et Cours 3, chaîne
d'énergie et chaîne d'information côte à côte, pastille bleue Niveau 2), **Le formulaire** (une carte, comme les autres, vers le formulaire en carte mentale), **Les
exercices** (Exercice 1.1, Niveau 1 ; QCM 2.1, Niveau 2 ; la carte « Exercices de calcul » du formulaire) et **Études de cas** (une carte « En cours d'édition », remplacée d'elle-même
par les études décrites dans `EXO_DEFS` avec `"etude": True`). Les numéros suivent la logique RDM : le premier
chiffre d'un exercice donne son niveau (1.1, puis 1.2… et 2.1… au niveau 2).

**Cartes de l'accueil** : plus de texte ; chaque carte montre une image, son étiquette, son titre, 3 à 5 mots-clés et
son bouton, et toutes ont la même taille, d'une rubrique à l'autre (test navigateur). Les images, recadrées au même format 480 × 270 par
`outils/preparer-images.sh` : portail (cours 1), moteur électrique seul, sans texte ni flèches (cours 2), capteur à
ultrasons et antenne dessinés pour le site (cours 3, `src/images/originaux/carte-capteur.svg` : le réseau de la
session ne permettait pas de télécharger une photo libre de droits), carte mentale du formulaire dépliée, vue de
loin, RAV4 (exercice 1.1), panneau photovoltaïque (QCM), photo fournie d'une calculatrice sur un brouillon
(exercices de calcul), ascenseur grisé (étude à venir). **À vérifier** : la photo de la calculatrice porte un
filigrane de banque d'images (« dreamstime ») ; sa publication suppose une licence.

**Cours** : le texte occupe toute la largeur de la section (le gabarit limite les paragraphes à 72 caractères, ce qui
convient à un sujet mais pas à un cours). Les tableaux « Compétences travaillées » des cours 2 et 3 sont retirés :
les cours ne visent pas une seule filière ; restent les objectifs et les prérequis.

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

## Cours 3 — Chaîne d'information des produits (Niveau 2, `?ex=cours-chaine-information`)

**Source** : le cours Word « Thème 3 — Chaîne d'information des produits » (leçon de référence, environ 3 h). Mis en
parallèle du cours 2 : même niveau, même présentation (objectifs, compétences, prérequis, sommaire, sections
numérotées, synthèse, quiz), liens croisés en pied de page.

Le texte du Word est repris section par section (constitution d'un produit, Acquérir, chaîne d'acquisition, Traiter,
Communiquer, encodage). Ses 22 figures sont des captures de manuel, souvent rognées ou peu lisibles : aucune n'est
reprise telle quelle, toutes sont **redessinées en SVG** et rendues interactives (`src/cours_information.py`) :
- **machine à café** (figures 1 et 2 réunies) : « Préparer un espresso » déroule six étapes, du bouton à la sonnerie ;
  les flux d'information, d'énergie et de matière circulent, la tasse se remplit ; la chaîne d'information se montre
  d'un seul bloc ou détaillée (acquérir, traiter, communiquer) ;
- **diagramme de blocs internes** : chaque bloc touché affiche sa fonction, son rôle et ses échanges, et éclaire ses
  flux ;
- **laboratoire des capteurs** : une même température, qui varie ou se règle, mesurée par un détecteur de seuil
  (signal logique), un capteur analogique (10 mV par degré) et un capteur numérique (trame de 10 bits décodée) ;
- **chaîne d'acquisition en direct** : gain, fréquence de coupure et résolution réglables, allure du signal à chaque
  étape, diagnostic (écrêtage, parasites, escalier grossier) ; calculateur d'amplification (exemple du cours) ;
- **filtre passe-bas** : signal recomposé en direct à partir de ses composantes (fondamental, harmoniques 3, 5, 7,
  bruit) et spectre avec le gabarit ;
- **CAN** : caractéristique en escalier selon n et Vref, quantum, N en décimal et en binaire, balayage animé ;
- **système programmable** animé ; **programme « bouton → LED »** qui s'exécute vraiment : on maintient le bouton,
  l'étape active s'éclaire dans l'algorigramme et la ligne correspondante dans le pseudo-code, les blocs, Python et
  C++/Arduino ; mode pas à pas ; table des symboles redessinée ;
- **restitution** logique, analogique, numérique (voyant, son, afficheur LCD qui montre les codes envoyés) ;
  **optocoupleur** animé ; **trame** envoyée en Wi-Fi, Bluetooth, Ethernet ou bus CAN ;
- **octet** à bits cliquables (décimal, binaire, hexadécimal par quartets), **défi de conversion** à nombres
  aléatoires, **ASCII** : un mot tapé donne ses codes, la table complète surligne ses caractères ;
- trois jeux (filaire ou sans fil ; Acquérir, Traiter ou Communiquer ; type de signal) et un quiz de 10 questions.

Corrections et décisions :
- **Valeur N d'un CAN** : le Word la donne « entre 0 et 2ⁿ » ; elle va de 0 à 2ⁿ − 1 (de 000 à 111 pour 3 bits).
- **Caractéristique du CAN** : la figure du Word montrait des marches décalées d'un demi-quantum, alors que le texte
  dit de prendre la partie entière de V / q ; la caractéristique redessinée suit le texte (marches à 1 V, 2 V…).
- **Capteur numérique** : le Word dit qu'il faut connaître le codage, sans en donner ; le laboratoire en fixe un
  (dixièmes de degré sur 10 bits), annoncé sous le graphique, qui donne 55,8 °C pour la trame du cours.
- Les blocs « Nom / Prénom / Groupe », « Documents ressources » (pages de manuel) et « Modalités » (consignes
  d'enseignant) ne sont pas repris, comme pour le cours 2. Le « bac » de la machine à café devient le « tiroir à
  marc », pour ne pas prêter à confusion.

## Exercice 1.1 — Chaînes d'information et d'énergie (Niveau 1, `?ex=chaines-information-energie`)

**Source** : l'exercice du dépôt « schema_chaine-energie-information » (ascenseur, Toyota Prius devenue Toyota RAV4 hybride, chauffage
géothermique, portail automatisé ; 14 questions, 57 champs).

- Chaque système devient une **partie** : 15, 12, 18 et 15 min (1 h), 15, 11, 19 et 12 points. Les 14 questions
  d'origine gardent leurs cases, **validées ensemble** (mécanisme « fast-q » du gabarit) : un bouton par question, une
  correction commune avec le tableau des réponses attendues et la démarche d'origine ; chaque case vaut un point.
- **Des étiquettes à glisser, plus rien à recopier** : chaque question propose sa liste d'étiquettes (les huit
  fonctions, ou les composants et énergies du système, avec des intrus : 7 à 12 étiquettes, triées par ordre
  alphabétique pour ne pas souffler la réponse). On glisse une étiquette sur une case, ou on la touche puis on touche
  la case (téléphone, tablette) ; au clavier, Entrée sur l'étiquette puis Entrée sur la case. Une étiquette sert
  plusieurs fois ; glisser une case sur une autre échange leurs étiquettes ; ramener une étiquette dans la liste ou
  toucher une case remplie la vide. La case garde, masqué, le champ que lit le moteur du gabarit : correction, modes
  entraînement et examen, impression et notes sont inchangés.
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
- **Partie 2 : la Toyota Prius devient le Toyota RAV4 hybride** (maquette validée), photo fournie, recadrée, plaque
  d'immatriculation floutée. Les figures 3 et 4 sont redessinées en SVG et « vivantes » (`src/rav4.py`) :
  - figure 3, la motorisation : cinq situations de conduite (arrêt, démarrage, accélération, croisière, freinage) et
    un trajet qui les enchaîne ; l'énergie circule (chimique en pointillés orange, électrique en tirets bleus,
    mécanique en vert), les pistons s'allument, engrenages et roues tournent, la jauge de batterie se vide ou se
    remplit ; option 4 roues motrices (AWD-i, moteur électrique arrière) ; un composant touché affiche son rôle ;
  - figure 4, la chaîne à compléter (mêmes repères 1 à 11) : ses blocs s'éclairent au rythme de la figure 3, et au
    freinage le flux remonte des roues vers la batterie ;
  - les fonctions des composants (Alimenter, Convertir…) ne s'affichent qu'une fois la partie corrigée (questions
    validées, ou copie remise en examen) : la figure ne souffle pas les réponses.
- **Repère 8** : sur le RAV4, la chaîne silencieuse de la Prius laisse la place à l'arbre de sortie et aux pignons de
  renvoi (étiquette et correcteur changés ; « chaîne silencieuse » est désormais refusée).
- **Repère 4, la génératrice** : la source en faisait l'organe de récupération au freinage. C'est en réalité le moteur
  électrique, entraîné par les roues, qui fonctionne alors en génératrice ; la génératrice transforme une partie de
  la puissance du moteur thermique en électricité. L'indice et la démarche de Q2.3 sont corrigés, la figure 3 le
  montre. La flèche du repère 4 rejoint le répartiteur (repère 2), qui recharge la batterie (repère 1).
- **Version 4 roues motrices** : présentée dans la figure et en « pour aller plus loin », sans case notée (la partie
  garde ses 11 points).
- **Étiquettes et correction** : pour chaque case, la bonne étiquette est la seule acceptée de sa liste (test
  unitaire), sauf le plancher chauffant, où Transmettre et Agir restent justes comme dans la correction d'origine.
  Portail, repère 7 : « alimentation électrique » n'est plus accepté comme source d'énergie (l'exercice d'origine ne
  l'acceptait pas ; c'est l'étiquette du repère 8).
- **Tolérance de saisie** : les 270 formulations acceptées par l'exercice d'origine restent toutes justes (test
  unitaire). Ajouts : « carte électronique » et « microcontrôleur » pour la fonction Traiter du portail (vocabulaire du
  cours 1). Refus explicites des confusions : « moteur à bras » pour Transmettre, « moteur actionnant des câbles » pour
  Transmettre, sondes intérieure et extérieure inversées, « capteur de température » pour le capteur géothermique,
  « télécommande » pour le boîtier de commande, moteur électrique et moteur thermique inversés.
- Les noms des systèmes réels (Toyota RAV4, réseau EDF sur la figure) sont conservés comme dans l'exercice d'origine.

## QCM 2.1 — Énergie et chaîne d'énergie (Niveau 2, `?ex=qcm-energie`)

**Source** : la page « QCM — Chaînes d'information et d'énergie » fournie (`src/qcm-energie-source.html`, conservée
telle quelle ; ses images sont extraites dans `src/images/originaux/qcm-*`). Mise aux normes du gabarit
(`src/qcm.py`) :
- chaque question devient une question du gabarit à une case, masquée, qui reçoit le repère de la ou des propositions
  choisies ; le moteur Grading la corrige (« code » pour une réponse unique, « intset » pour plusieurs) : modes
  entraînement et examen, chronomètre, note pondérée, récapitulatif et impression sont ceux des autres exercices ;
- six parties pondérées par leur durée (1 h 20 en tout) : conversions et sources d'énergie, unités, puissance et
  rendement, signaux et moteur à courant continu, énergie thermique, photovoltaïque et batteries, fonctions de la
  chaîne d'énergie et stockage ; 76 questions d'un point ;
- après validation : bonne réponse en vert, réponse fausse en rouge, réponse attendue et explication de la source ;
- les figures partagées par plusieurs questions (oscillogrammes, courbes du panneau) ne sont écrites qu'une fois dans
  la page.

Corrections et décisions :
- **Titre** : la source s'intitule « Chaînes d'information et d'énergie », mais toutes ses questions portent sur
  l'énergie ; le QCM s'appelle « Énergie et chaîne d'énergie » (l'exercice 1.1 porte déjà l'autre titre).
- **Q46** retirée : doublon exact de Q45. **Q15** : l'explication acceptait « la chaleur », la liste des bonnes
  réponses l'oubliait ; elle est ajoutée.
- **Q59** (bouton poussoir → DISTRIBUER) : dans un système automatisé, un bouton poussoir réalise la fonction
  ACQUÉRIR (cours 3) ; la question précise désormais le cas d'une commande directe, où il coupe lui-même le courant.
- **Q42C** : la « puissance crête » se définit à 1000 W·m⁻² ; la question demande la puissance maximale à 600 W·m⁻².
- **Unités** : « KW », « KJ » deviennent « kW », « kJ ». Les explications ne renvoient plus à une note extérieure.
- **Q32C** : la formule R = e / (λ × S), donnée en image, reste écrite dans l'énoncé ; l'image est retirée.
- Pas de documents à consulter : un formulaire donnerait plusieurs réponses (formules de puissance, de rendement).

## Formulaire de la chaîne de puissance (`formulaire.html`)

La page fournie est publiée avec deux retouches, par remplacements vérifiés (la source n'est pas modifiée) : trois
liens « Accueil : chaîne fonctionnelle » (menu, carte mentale, réglages des exercices), et la fiche d'une formule
n'affiche plus les pastilles « Vu dans » (Cours, TD, A1…), qui renvoyaient à des séances extérieures au site. Sur
l'accueil, la carte « Formulaire de la chaîne de puissance » ouvre la carte mentale (`#formulaire`) et la carte
« Exercices de calcul », rangée avec les exercices, ouvre les séries de calcul (`#exercices`). Le cours 2 y renvoie
aussi.

## Points signalés sans modification

- Les figures de l'exercice sont de faible définition (282 à 900 px de large) ; elles sont intégrées telles quelles
  (PNG quantifiés). La figure 3 du cours (ibd) est coupée en bas, comme dans le Word.
- Quelques photos des tableaux du Word portent un logo de fabricant ; elles ne sont pas retouchées.
- Poids : `index.html` 2,5 Mio (1,7 Mio d'images), `formulaire.html` 150 Kio.

## Vérifications effectuées

- `node --test tests/correction.test.js` : 7 tests — configuration (4 parties, 57 cases, 60 min), réponse de référence
  juste pour chaque case, 270 formulations d'origine acceptées, confusions et fautes de frappe, aucune fonction
  acceptée à la place d'une autre, saisie vide refusée, étiquettes (la bonne est proposée, les autres de la liste
  sont refusées).
- `node --test tests/qcm.test.js` : 4 tests — 6 parties, 76 questions, 1 h 20 ; pour chaque question à réponse
  unique, chaque bonne proposition acceptée et toutes les autres refusées (plus de 300 propositions) ; réponses
  multiples exigées complètes et sans intrus ; corrections de la source.
- `tests/navigateur.test.js` (Playwright, Chromium) : 12 parcours, tous réussis — accueil (cartes illustrées à 3 à 5
  mots-clés et sans texte, annonce de l'étude, téléphone, aucune mention de diplôme ou d'épreuve) ; adresse inconnue ; cours 1
  (étapes, scénarios, clavier, plein écran, cartes, jeux, quiz) ; cours 2 (figures, fiches, oscilloscope, hacheur,
  transmissions, puissances, énergie, effort et flux, rendements, autonomie, jeux, quiz, impression, téléphone) ;
  cours 3 (machine à café, blocs internes, laboratoire, acquisition, amplification, CAN, programme exécuté, onglets,
  restitution, trame, octet, défi, ASCII, trois jeux, quiz 10/10, impression, téléphone) ; RAV4 (situations de
  conduite, chaîne synchronisée, version 4 roues motrices, fonctions dévoilées après correction, trajet) ; exercice en entraînement (cases vides, confirmation, verrouillage, 19,7 puis 20,0/20) ; exercice en examen (rien ne
  filtre avant la remise, y compris à l'impression ; remise en deux temps ; chronomètre arrêté ; 18,6/20) ;
  étiquettes (toucher puis toucher, clavier, glisser-déposer, réutilisation, échange, retour dans la liste, verrouillage
  après validation, téléphone) ; QCM (choix unique ou multiple, marques et explications, 20/20 en entraînement,
  examen avec réponses vides 2,0/20, figures chargées) ; documents et téléphone ; formulaire (liens vers l'accueil, fiche sans « Vu dans »,
  vues ouvertes depuis l'accueil).
- Aucune erreur JavaScript dans aucun parcours.
