#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la page « Chaîne fonctionnelle » (index.html) : un accueil sur le modèle du dépôt « Résistance des
matériaux », deux cours interactifs (niveaux 1 et 2), l'exercice 1.1 et la rubrique « Études de cas », chacun
ouvert par ?ex=…, ainsi que la page formulaire.html (formulaire de la chaîne de puissance) présentée sur l'accueil.

    python3 src/generer.py

Le bloc <style> du gabarit, le moteur de correction (Grading) et le moteur applicatif sont recopiés tels quels ;
seules les entrées propres au sujet du moteur applicatif sont remplacées, chaque remplacement étant vérifié :
DECOR, DR_NAMES, le texte de la fenêtre « Imprimer les DR », le libellé « Diagramme validé » des questions à
plusieurs cases et CONSEIL_MIN, lu dans window.__CONSEIL_MIN__ puisque la durée conseillée dépend de l'exercice
ouvert. Un petit script d'aiguillage, exécuté avant les moteurs, installe le contenu demandé par l'adresse.

Le cours 1 reprend l'animation du portail (src/portail-anime.html, page autonome que l'on peut ouvrir seule) : son
schéma et son script en sont extraits, chaque remplacement étant vérifié ; son style est repris ici, préfixé par
.cp. La page formulaire.html est la copie de src/formulaire-chaine-de-puissance.html, augmentée de liens vers
l'accueil.
"""
import base64
import copy
import html
import json
import pathlib
import re
import struct
import types
import unicodedata

import cours_information
import rav4

ROOT = pathlib.Path(__file__).resolve().parent.parent
GABARIT = ROOT / "src" / "gabarit-exercice-interactif.html"
PORTAIL = ROOT / "src" / "portail-anime.html"
FORMULAIRE_SRC = ROOT / "src" / "formulaire-chaine-de-puissance.html"
IMAGES = ROOT / "src" / "images"
SORTIE = ROOT / "index.html"
FORMULAIRE = ROOT / "formulaire.html"
TITRE = "Chaîne fonctionnelle"


# ============================================================ outils
def png(name):
    data = (IMAGES / f"{name}.png").read_bytes()
    w, h = struct.unpack(">II", data[16:24])
    return "data:image/png;base64," + base64.b64encode(data).decode(), w, h


def esc(s):
    return html.escape(s, quote=True)


def frac(a, b):
    return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'


def fr(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def figure(name, alt, caption, maxw, cls="fig"):
    src, w, h = png(name)
    return (f'<figure class="{cls}" style="max-width:{maxw}px"><img src="{src}" alt="{esc(alt)}" '
            f'width="{w}" height="{h}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def jpg(name):
    """Photo JPEG intégrée en data URI ; dimensions lues dans le segment SOF."""
    data = (IMAGES / f"{name}.jpg").read_bytes()
    i = 2
    while i < len(data):
        marker, size = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return "data:image/jpeg;base64," + base64.b64encode(data).decode(), w, h
        i += 2 + size
    raise ValueError(f"{name}.jpg : dimensions introuvables")


def photo(name, alt, caption, maxw, cls="fig"):
    src, w, h = jpg(name)
    return (f'<figure class="{cls}" style="max-width:{maxw}px"><img src="{src}" alt="{esc(alt)}" '
            f'width="{w}" height="{h}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def sub_once(text, pattern, repl, flags=0):
    """Remplacement vérifié : le motif doit apparaître exactement une fois."""
    new, n = re.subn(pattern, lambda m: repl, text, flags=flags)
    assert n == 1, f"motif introuvable ou multiple : {pattern!r} ({n})"
    return new


# ============================================================ correcteurs (moteur Grading du gabarit)
def P(*alts):
    """Motif de mots-clés : chaque argument liste des mots équivalents séparés par « | », en minuscules et sans
    accents ; la réponse doit contenir un mot de chaque argument (une petite faute de frappe est tolérée)."""
    return [a.split("|") for a in alts]


def KW(*motifs, forbid=""):
    # forbid : mots qui rendent la réponse fausse ; ils sont comparés avec la même tolérance aux fautes de frappe
    # (« interieure » refuserait aussi « exterieure », à deux lettres près : on écrit « interieur »).
    g = {"type": "kw", "any": list(motifs)}
    if forbid:
        g["forbid"] = forbid.split("|")
    return g


ACQUERIR = KW(P("acquerir|acquisition"))
TRAITER = KW(P("traiter|traitement"))
COMMUNIQUER = KW(P("communiquer|communication|restituer"))
ALIMENTER = KW(P("alimenter|alimentation"))
DISTRIBUER = KW(P("distribuer|distribution"))
CONVERTIR = KW(P("convertir|conversion"))
TRANSMETTRE = KW(P("transmettre|transmission"))
AGIR = KW(P("agir|action"))
RESEAU = KW(P("reseau"), P("energie", "electrique"), P("alimentation", "electrique"), P("electricite"),
            P("secteur"), P("courant", "electrique"), P("230"), forbid="thermique|chimique|mecanique")
# portail, repère 7 : la source extérieure seule (« alimentation électrique » est l'étiquette du repère 8)
RESEAU_SOURCE = KW(P("reseau"), P("energie", "electrique"), P("electricite"), P("secteur"), P("courant", "electrique"),
                   P("230"), forbid="thermique|chimique|mecanique|alimentation")
MESSAGES = KW(P("message|messages|signalisation|information|informations|affichage"), P("signal", "lumineux"))


# ============================================================ blocs de contenu
def HTML(raw):
    return {"kind": "html", "html": raw}


def QBAR(docs, ans="ci-dessous"):
    return {"kind": "qbar", "docs": list(docs), "ans": ans}


def GRP(stem, hint, fields, why):
    """Question à plusieurs cases validées ensemble (mécanisme « fast-q » du gabarit), une case = un point.
    fields : liste de (libellé de la case, correcteur, réponse attendue affichée dans la correction)."""
    return {"kind": "grp", "stem": stem, "hint": hint, "fields": fields, "why": why}


def calc(s):
    return f'<span class="calc">{s}</span>'


H_VERBE = "Une fonction par case."
H_COMPO = "Un composant par case, tiré de la présentation."


# ============================================================ EXERCICE 1.1 — CHAÎNES D'INFORMATION ET D'ÉNERGIE
# Source : dépôt « schema_chaine-energie-information » (quatre systèmes, 14 questions, 57 cases).
# Chaque question d'origine garde ses cases, validées ensemble ; la démarche corrigée est celle de la source.
PARTS_EX1 = []

# ------------------------------------------------------------ Partie 1 : l'ascenseur
PARTS_EX1.append({"title": "L'ascenseur", "minutes": 15, "intro": [
    '<div class="cours-split">' +
    figure("ex1-ascenseur", "Vue en coupe d'un ascenseur avec ses six ensembles repérés", "Figure 1 — Les six "
           "ensembles de l'ascenseur.", 230) +
    "<div><p><strong>Les différentes parties d'un ascenseur :</strong></p><ol>"
    "<li>Une <strong>gaine</strong> (ou trémie) comprenant l'espace de déplacement, les rails de guidage des "
    "éléments mobiles (cabine et contrepoids) et le réseau des câbles des systèmes permettant le fonctionnement de "
    "l'installation.</li>"
    "<li>Une <strong>cabine</strong>, comprenant un système de porte intérieure, un tableau de commande, un "
    "éclairage, un dispositif de ventilation et un système de freinage de sécurité. Les systèmes de la cabine sont "
    "alimentés et reliés au système de commande par un câble souple pendentif.</li>"
    "<li>Une <strong>machinerie</strong> permettant le mouvement de la cabine : moteur actionnant des câbles.</li>"
    "<li>Un <strong>système de transmission du mouvement</strong> : boîte de réduction, poulie et natte de câbles "
    "avec contrepoids.</li>"
    "<li>Des <strong>portes palières</strong> et leurs dispositifs d'ouverture et de fermeture ainsi que les "
    "verrouillages de sécurité, actionnés par l'arrivée et le départ de la cabine.</li>"
    "<li>Un <strong>système de commande</strong> des systèmes d'ouverture et de fermeture des portes palières "
    "ainsi que des déplacements et des arrêts de la cabine, avec un dispositif d'arrêt d'urgence.</li></ol></div></div>",
    "<p>À l'aide de la présentation et de vos connaissances, complétez les chaînes d'information et d'énergie "
    "(puissance) du système.</p>",
    figure("ex1-ascenseur-chaines", "Schéma des chaînes d'information et d'énergie de l'ascenseur, cases numérotées "
           "de 1 à 12", "Figure 2 — Chaînes d'information et d'énergie de l'ascenseur : les 12 cases à compléter "
           "sont repérées en rouge.", 760)], "blocks": [
    QBAR(["DP1"]),
    GRP("Nommez les trois fonctions de la chaîne d'information, dans l'ordre (repères 3, 4 et 5).", H_VERBE, [
        ("Repère 3 (1<sup>re</sup> fonction)", ACQUERIR, "Acquérir"),
        ("Repère 4 (2<sup>e</sup> fonction)", TRAITER, "Traiter"),
        ("Repère 5 (3<sup>e</sup> fonction)", COMMUNIQUER, "Communiquer (ou restituer)")],
        "<p>La chaîne d'information suit toujours le même parcours, quel que soit le système : "
        + calc("ACQUÉRIR → TRAITER → COMMUNIQUER") + "</p><ul>"
        "<li><strong>Acquérir</strong> (repère 3) : capter les consignes de l'utilisateur (boutons d'appel, tableau "
        "de commande) et l'état du système (capteurs de position, de charge, de porte).</li>"
        "<li><strong>Traiter</strong> (repère 4) : le système de commande de l'ascenseur (partie 6 de la "
        "présentation) compare la consigne et l'état réel, puis décide de l'ordre à donner. C'est de cette case que "
        "part la flèche rouge vers la chaîne d'énergie.</li>"
        "<li><strong>Communiquer</strong> (repère 5) : restituer l'information à l'utilisateur (afficheur d'étage, "
        "voyants, signal sonore).</li></ul>"),
    GRP("Nommez les cinq fonctions de la chaîne d'énergie, dans l'ordre (repères 8 à 12).", H_VERBE, [
        ("Repère 8", ALIMENTER, "Alimenter"), ("Repère 9", DISTRIBUER, "Distribuer"),
        ("Repère 10", CONVERTIR, "Convertir"), ("Repère 11", TRANSMETTRE, "Transmettre"),
        ("Repère 12", AGIR, "Agir")],
        "<p>La chaîne d'énergie décrit le trajet de l'énergie depuis la source jusqu'à la matière d'œuvre : "
        + calc("ALIMENTER → DISTRIBUER → CONVERTIR → TRANSMETTRE → AGIR") + "</p>"
        "<p>On reconnaît la case <strong>AGIR</strong> (repère 12) au fait qu'elle est la seule traversée par les "
        "flèches vertes de la matière d'œuvre : l'usager entre à l'étage de départ et sort à l'étage d'arrivée. La "
        "case <strong>DISTRIBUER</strong> (repère 9) est celle qui reçoit la flèche rouge venant de la fonction "
        "<em>Traiter</em> : c'est elle qui laisse ou non passer l'énergie vers le moteur.</p>"),
    GRP("Identifiez les entrées et la sortie du système : repères 1, 2, 6 et 7.",
        "Ces cases ne sont pas des fonctions : elles décrivent ce qui entre dans le système ou ce qui en sort.", [
        ("Repère 1 (venant de l'utilisateur)",
         KW(P("consigne|consignes|ordre|ordres|commande|commandes")), "Consigne (de l'utilisateur)"),
        ("Repère 2 (venant de la chaîne d'énergie)",
         KW(P("compte|comptes", "rendu|rendus"), P("information|informations|info|infos", "capteur|capteurs"),
            P("etat", "systeme"), P("retour", "information|informations"), P("retour", "capteur|capteurs")),
         "Compte rendu (informations des capteurs)"),
        ("Repère 6 (allant vers l'utilisateur)", MESSAGES, "Messages (informations restituées)"),
        ("Repère 7 (entrée de la chaîne d'énergie)", RESEAU, "Réseau électrique (énergie électrique)")],
        "<ul><li><strong>Repère 1 — la consigne</strong> : la flèche part du pictogramme « utilisateur ». C'est "
        "l'ordre donné au système (appuyer sur le bouton d'appel d'un étage).</li>"
        "<li><strong>Repère 2 — le compte rendu</strong> : la longue flèche rouge remonte depuis la chaîne "
        "d'énergie. Ce sont les informations renvoyées par les capteurs (position de la cabine, état des portes) et "
        "réinjectées dans la fonction <em>Acquérir</em>. C'est ce retour qui rend le système <em>asservi</em>.</li>"
        "<li><strong>Repère 6 — les messages</strong> : la flèche repart vers l'utilisateur. Ce sont les "
        "informations restituées (numéro d'étage affiché, voyant d'appel allumé, bip de fermeture).</li>"
        "<li><strong>Repère 7 — l'énergie d'entrée</strong> : la case verte placée <em>avant</em> la fonction "
        "<em>Alimenter</em> représente la source extérieure, ici le réseau électrique (énergie électrique).</li></ul>"),
    GRP("À l'aide de la présentation de l'ascenseur, citez le composant qui réalise chacune des fonctions suivantes.",
        H_COMPO, [
        ("CONVERTIR (repère 10)", KW(P("moteur|moteurs|machinerie")), "Le moteur (de la machinerie)"),
        ("TRANSMETTRE (repère 11)",
         KW(P("poulie|poulies"), P("cable|cables"), P("reduction"), P("reducteur"), P("systeme", "transmission"),
            forbid="moteur|machinerie|cabine"),
         "La boîte de réduction, la poulie et la natte de câbles"),
        ("AGIR (repère 12)", KW(P("cabine")), "La cabine")],
        "<p>On relie chaque fonction au matériel décrit dans la présentation :</p><ul>"
        "<li><strong>Convertir → le moteur</strong> (partie 3, « une machinerie… : moteur actionnant des câbles »). "
        "Il convertit l'énergie électrique en énergie mécanique de rotation.</li>"
        "<li><strong>Transmettre → la boîte de réduction, la poulie et la natte de câbles</strong> (partie 4). Elles "
        "adaptent le mouvement de rotation du moteur en mouvement de translation de la cabine, avec l'aide du "
        "contrepoids.</li>"
        "<li><strong>Agir → la cabine</strong> (partie 2). C'est l'élément qui agit sur la matière d'œuvre : l'usager "
        "passe de l'étage de départ à l'étage d'arrivée.</li></ul>"
        "<p>Remarque : la fonction <em>Alimenter</em> correspond au réseau électrique et à l'armoire électrique de la "
        "machinerie, et la fonction <em>Traiter</em> au système de commande (partie 6).</p>"),
]})

# ------------------------------------------------------------ Partie 2 : le Toyota RAV4 hybride
# Figures 3 et 4 animées (src/rav4.py) ; la Prius de l'exercice d'origine est remplacée par le RAV4.
PARTS_EX1.append({"title": "Toyota RAV4 hybride", "minutes": 12, "intro": [
    '<div class="cours-split">' +
    photo("ex1-rav4", "Toyota RAV4 hybride gris dans un champ labouré", "", 420) +
    "<div><p>Le Toyota RAV4 est un SUV <strong>hybride</strong> : un moteur thermique et deux machines électriques se "
    "partagent l'entraînement des roues. Sa motorisation a pour fonction principale d'entraîner et de freiner les "
    "roues, mais aussi de <strong>récupérer de l'énergie lors de la phase de freinage</strong> : le moteur électrique "
    "fonctionne alors en génératrice et recharge la batterie.</p><p>À l'aide du schéma simplifié du système technique "
    "ci-dessous, complétez la représentation schématique de la chaîne d'énergie (dite aussi de puissance).</p>"
    "</div></div>",
    rav4.figure_tech(),
    rav4.figure_chaine()], "blocks": [
    QBAR(["DP1", "DT1"]),
    GRP("Complétez la branche thermique de la chaîne d'énergie (repères 5, 6 et 7) avec les composants du schéma.",
        "C'est la branche du bas à gauche : ALIMENTER → DISTRIBUER → CONVERTIR.", [
        ("Repère 5 — ALIMENTER", KW(P("reservoir|carburant|combustible")), "Le réservoir de carburant"),
        ("Repère 6 — DISTRIBUER", KW(P("injection|injecteur|injecteurs")), "Le système d'injection"),
        ("Repère 7 — CONVERTIR", KW(P("moteur", "thermique|combustion|essence|explosion"), forbid="electrique"),
         "Le moteur thermique")],
        "<p>On suit l'énergie <em>chimique</em> du carburant sur le schéma technique, de gauche à droite : "
        + calc("réservoir → système d'injection → moteur thermique") + "</p><ul>"
        "<li>Le <strong>réservoir de carburant</strong> stocke l'énergie : il <em>alimente</em>.</li>"
        "<li>Le <strong>système d'injection</strong> dose la quantité de carburant envoyée dans les cylindres : il "
        "<em>distribue</em> l'énergie.</li>"
        "<li>Le <strong>moteur thermique</strong> transforme l'énergie chimique en énergie mécanique de rotation : il "
        "<em>convertit</em>.</li></ul><p>Sur la figure 3, choisissez « Croisière » : c'est cette branche qui travaille.</p>"),
    GRP("Complétez la branche électrique de la chaîne d'énergie (repères 1, 2 et 3) avec les composants du schéma.",
        "C'est la branche du haut : ALIMENTER → DISTRIBUER → CONVERTIR.", [
        ("Repère 1 — ALIMENTER", KW(P("batterie|batteries|accumulateur|accumulateurs")), "La batterie"),
        ("Repère 2 — DISTRIBUER", KW(P("repartiteur|onduleur")), "Le répartiteur de puissance"),
        ("Repère 3 — CONVERTIR", KW(P("moteur", "electrique"), forbid="thermique|arriere"), "Le moteur électrique")],
        "<p>Même raisonnement pour l'énergie <em>électrique</em> : "
        + calc("batterie → répartiteur de puissance → moteur électrique") + "</p><ul>"
        "<li>La <strong>batterie</strong> stocke l'énergie électrique : elle <em>alimente</em>.</li>"
        "<li>Le <strong>répartiteur de puissance</strong> (un onduleur) oriente le courant vers le moteur électrique ou "
        "vers la batterie selon la phase de roulage : il <em>distribue</em>.</li>"
        "<li>Le <strong>moteur électrique</strong> transforme l'énergie électrique en énergie mécanique : il "
        "<em>convertit</em>.</li></ul><p>C'est bien la même structure que la branche thermique : c'est ce qui fait du "
        "RAV4 un véhicule <em>hybride</em>, avec deux chaînes d'alimentation qui se rejoignent pour entraîner les "
        "roues. Situation « Démarrage » de la figure 3 : seule cette branche travaille.</p>"),
    GRP("Le repère 4 est un second CONVERTIR, entraîné par le train épicycloïdal. Quel composant du schéma occupe "
        "cette case ?", "C'est le composant qui transforme une partie de la puissance du moteur thermique en "
        "électricité.", [
        ("Repère 4 — CONVERTIR", KW(P("generatrice|generateur|alternateur")), "La génératrice")],
        "<p>Le train épicycloïdal partage la puissance du moteur thermique : une partie va aux roues, l'autre entraîne "
        "la <strong>génératrice</strong>. Elle fait l'opération inverse d'un moteur : elle reçoit de l'énergie "
        "<em>mécanique</em> et la convertit en énergie <em>électrique</em>.</p><p>C'est pour cela que la flèche qui sort "
        "du repère 4 remonte vers le repère 2 : le répartiteur envoie ce courant <strong>recharger la batterie</strong> "
        "(repère 1) ou alimenter le moteur électrique (repère 3). Situation « Croisière » de la figure 3.</p>"
        "<p><em>Attention</em> : au freinage, ce n'est pas la génératrice qui récupère l'énergie, mais le <strong>moteur "
        "électrique</strong>, entraîné par les roues, qui fonctionne alors en génératrice (situation « Freinage »).</p>"),
    GRP("Complétez la fin de la chaîne d'énergie (repères 8, 9, 10 et 11) : les trois TRANSMETTRE puis AGIR.",
        "Suivez le schéma technique depuis le train épicycloïdal jusqu'aux roues.", [
        ("Repère 8 — TRANSMETTRE", KW(P("pignon|pignons|engrenage|engrenages"), P("arbre", "sortie"), P("renvoi"),
                                      forbid="reducteur"), "L'arbre de sortie et les pignons de renvoi"),
        ("Repère 9 — TRANSMETTRE", KW(P("reducteur")), "Le réducteur"),
        ("Repère 10 — TRANSMETTRE", KW(P("differentiel")), "Le différentiel"),
        ("Repère 11 — AGIR", KW(P("roue|roues"), forbid="arriere"), "Les roues motrices")],
        "<p>On lit le schéma technique de haut en bas, en partant du train épicycloïdal : "
        + calc("arbre de sortie et pignons de renvoi → réducteur → différentiel → roues motrices") + "</p><ul>"
        "<li>L'<strong>arbre de sortie</strong> reçoit la rotation du train épicycloïdal et du moteur électrique ; les "
        "<strong>pignons de renvoi</strong> la reportent vers le bas.</li>"
        "<li>Le <strong>réducteur</strong> diminue la vitesse de rotation et augmente le couple.</li>"
        "<li>Le <strong>différentiel</strong> répartit le couple entre les deux roues et leur permet de tourner à des "
        "vitesses différentes en virage.</li>"
        "<li>Les <strong>roues motrices</strong> réalisent la fonction <em>Agir</em> : elles font passer la matière "
        "d'œuvre de « roues immobiles » à « roues entraînées ».</li></ul><p><em>Pour aller plus loin</em> : la "
        "version 4 roues motrices (AWD-i, à cocher sur la figure 3) ajoute un moteur électrique sur l'essieu arrière, "
        "sans arbre de transmission ; il forme une seconde branche Convertir → Transmettre → Agir.</p>"),
]})

# ------------------------------------------------------------ Partie 3 : le chauffage géothermique
PARTS_EX1.append({"title": "Chauffage géothermique", "minutes": 18, "intro": [
    "<p>Le chauffage géothermique consiste à capter les calories présentes dans le sol pour les restituer dans la "
    "maison via une <strong>pompe à chaleur</strong>. Cette technique connaît un développement important en raison "
    "de son intérêt économique et écologique.</p>",
    figure("ex1-geothermie", "Schéma d'installation d'un chauffage géothermique dans une maison", "Figure 5 — "
           "Installation : capteur géothermique, pompe à chaleur, plancher chauffant, régulateur, clavier, écran "
           "rétro-éclairé, sondes de température intérieure (TI) et extérieure (TE), armoire électrique.", 560),
    figure("ex1-geothermie-chaines", "Chaînes d'information et d'énergie du chauffage géothermique, cases numérotées "
           "de 1 à 10", "Figure 6 — Représentation schématique à compléter : les 10 cases à remplir sont repérées "
           "en rouge. Les cases « Conversion numérique analogique » et « Chauffer la maison » sont déjà données.",
           620)], "blocks": [
    QBAR(["DP1", "DT1"]),
    GRP("Identifiez, pour chacun des neuf composants ci-dessous, le groupe fonctionnel auquel il appartient.",
        "Une fonction par case : une même fonction peut servir pour plusieurs composants.", [
        ("Réseau EDF / armoire électrique", ALIMENTER, "Alimenter"),
        ("Régulateur", TRAITER, "Traiter"),
        ("Pilote des moteurs", DISTRIBUER, "Distribuer"),
        ("Capteur géothermique", ALIMENTER, "Alimenter"),
        ("Plancher chauffant", KW(P("transmettre|transmission"), P("agir|action")), "Transmettre (Agir accepté)"),
        ("Pompe à chaleur", CONVERTIR, "Convertir"),
        ("Sonde de température", ACQUERIR, "Acquérir"),
        ("Clavier", ACQUERIR, "Acquérir"),
        ("Écran rétro-éclairé", COMMUNIQUER, "Communiquer")],
        "<p>On classe d'abord chaque composant dans sa chaîne, puis on lui attribue sa fonction.</p>"
        '<table class="t compo"><thead><tr><th>Composant</th><th>Chaîne</th><th>Groupe fonctionnel</th></tr></thead>'
        "<tbody><tr><td>Réseau EDF / armoire électrique</td><td>Énergie</td><td>Alimenter</td></tr>"
        "<tr><td>Régulateur</td><td>Information</td><td>Traiter</td></tr>"
        "<tr><td>Pilote des moteurs</td><td>Énergie</td><td>Distribuer</td></tr>"
        "<tr><td>Capteur géothermique</td><td>Énergie</td><td>Alimenter</td></tr>"
        "<tr><td>Plancher chauffant</td><td>Énergie</td><td>Transmettre</td></tr>"
        "<tr><td>Pompe à chaleur</td><td>Énergie</td><td>Convertir</td></tr>"
        "<tr><td>Sonde de température</td><td>Information</td><td>Acquérir</td></tr>"
        "<tr><td>Clavier</td><td>Information</td><td>Acquérir</td></tr>"
        "<tr><td>Écran rétro-éclairé</td><td>Information</td><td>Communiquer</td></tr></tbody></table>"
        "<p>Points d'attention :</p><ul>"
        "<li>Il y a <strong>deux alimentations</strong> : l'armoire électrique fournit l'énergie <em>électrique</em>, "
        "le capteur géothermique fournit l'énergie <em>thermique du sol</em>. Les deux entrent dans la chaîne "
        "d'énergie.</li>"
        "<li>Le <strong>clavier</strong> acquiert les consignes de l'habitant ; les <strong>sondes</strong> acquièrent "
        "des grandeurs physiques (températures intérieure et extérieure). Les deux réalisent donc la même fonction : "
        "<em>Acquérir</em>.</li>"
        "<li>Pour le <strong>plancher chauffant</strong>, les deux réponses <em>Transmettre</em> et <em>Agir</em> sont "
        "acceptées : il transmet la chaleur produite par la pompe à chaleur, mais on peut aussi considérer qu'il agit "
        "directement sur la matière d'œuvre (l'air de la maison). Sur le schéma, l'action « Chauffer la maison » est "
        "représentée à part, dans le rectangle noir.</li></ul>"),
    GRP("Complétez la chaîne d'information du schéma (repères 1 à 5) avec les composants de l'installation.",
        "Aidez-vous des flèches d'entrée : « Consignes / Commandes », « Climat », et le retour « Information "
        "température intérieur ».", [
        ("Repère 1 (entrée : consignes, commandes)", KW(P("clavier")), "Le clavier"),
        ("Repère 2 (entrée : climat)", KW(P("sonde|sondes|capteur", "temperature|exterieure|exterieur|te"),
                                         forbid="interieur|ti|geothermique"),
         "La sonde de température extérieure (TE)"),
        ("Repère 3 (entrée : information température intérieur)",
         KW(P("sonde|sondes|capteur", "temperature|interieure|interieur|ti"),
            forbid="exterieur|te|geothermique"), "La sonde de température intérieure (TI)"),
        ("Repère 4 (case centrale)", KW(P("regulateur")), "Le régulateur"),
        ("Repère 5 (sortie : messages)", KW(P("ecran|afficheur")), "L'écran rétro-éclairé")],
        "<p>On identifie chaque case à partir de la flèche qui y entre ou qui en sort :</p><ul>"
        "<li><strong>Repère 1</strong> : la flèche « Consignes / Commandes » vient de l'habitant → c'est le "
        "<strong>clavier</strong> (fonction <em>Acquérir</em>).</li>"
        "<li><strong>Repère 2</strong> : la flèche « Climat » correspond à la température extérieure → c'est la "
        "<strong>sonde de température extérieure</strong> (notée TE sur le schéma de la maison).</li>"
        "<li><strong>Repère 3</strong> : la flèche vient du bas, du retour « Information température intérieur » → "
        "c'est la <strong>sonde de température intérieure</strong> (notée TI). C'est le compte rendu de la chaîne "
        "d'énergie.</li>"
        "<li><strong>Repère 4</strong> : les trois entrées convergent vers une seule case, celle qui décide → c'est le "
        "<strong>régulateur</strong> (fonction <em>Traiter</em>). Il compare la température mesurée à la "
        "consigne.</li>"
        "<li><strong>Repère 5</strong> : la flèche sort vers « Messages » → c'est l'<strong>écran rétro-éclairé</strong> "
        "(fonction <em>Communiquer</em>).</li></ul>"
        "<p>La seconde sortie du régulateur passe par la « Conversion numérique analogique » puis devient la « Consigne "
        "marche arrêt » envoyée à la chaîne d'énergie : c'est le lien classique <em>Traiter → Distribuer</em>.</p>"),
    GRP("Complétez la chaîne d'énergie du schéma (repères 6 à 10) avec les composants de l'installation.",
        "Le repère 10 est la case alimentée par « Énergie thermique du sol ».", [
        ("Repère 6", KW(P("armoire"), P("reseau"), P("edf"), P("alimentation", "electrique")),
         "L'armoire électrique (réseau EDF)"),
        ("Repère 7", KW(P("pilote|pilotes")), "Le pilote des moteurs de la pompe à chaleur"),
        ("Repère 8", KW(P("pompe", "chaleur"), P("pac")), "La pompe à chaleur"),
        ("Repère 9", KW(P("plancher")), "Le plancher chauffant"),
        ("Repère 10", KW(P("capteur|sonde", "geothermique|sol"), P("geothermique"), P("capteur"),
                         forbid="temperature|interieure|exterieure"), "Le capteur géothermique")],
        "<p>On suit le sens des flèches, de la source vers la matière d'œuvre : "
        + calc("armoire électrique → pilote des moteurs → pompe à chaleur → plancher chauffant → chauffer la maison")
        + "</p><ul>"
        "<li><strong>Repère 6 — armoire électrique (réseau EDF)</strong> : première case de la ligne, elle "
        "<em>alimente</em> l'installation en énergie électrique.</li>"
        "<li><strong>Repère 7 — pilote des moteurs</strong> : c'est la case qui reçoit la « Consigne marche arrêt » "
        "venant de la chaîne d'information ; elle <em>distribue</em> l'énergie électrique vers la pompe à chaleur.</li>"
        "<li><strong>Repère 8 — pompe à chaleur</strong> : elle <em>convertit</em>. Elle reçoit deux entrées "
        "(l'électricité et l'énergie thermique du sol) et produit la chaleur utile.</li>"
        "<li><strong>Repère 9 — plancher chauffant</strong> : il <em>transmet</em> la chaleur à l'air de la maison, "
        "jusqu'à la case noire « Chauffer la maison ».</li>"
        "<li><strong>Repère 10 — capteur géothermique</strong> : c'est la case reliée à « Énergie thermique du sol ». "
        "Il constitue la seconde <em>alimentation</em> de la chaîne d'énergie.</li></ul>"),
]})

# ------------------------------------------------------------ Partie 4 : le portail automatisé
PARTS_EX1.append({"title": "Portail automatisé", "minutes": 15, "intro": [
    "<p>À l'aide du schéma ci-dessous et de vos connaissances, complétez les chaînes d'information et d'énergie "
    "(puissance) du système.</p>",
    figure("ex1-portail", "Schéma d'un portail automatisé avec ses huit composants numérotés", "Figure 7 — "
           "Composants du portail : 1 feu clignotant, 2 antenne réceptrice, 3 boîtier de commande, 4 vantail, "
           "5 moteur à bras, 6 alimentation électrique, 7 cellule optique, 8 télécommande.", 620),
    figure("ex1-portail-chaines", "Chaînes d'information et d'énergie du portail, cases numérotées de 1 à 12",
           "Figure 8 — Chaînes à compléter : les 12 cases sont repérées en rouge. Attention : cette numérotation "
           "rouge est indépendante de celle du schéma du portail ci-dessus.", 700)], "blocks": [
    QBAR(["DP1", "DT1"]),
    GRP("Complétez les trois cases de la chaîne d'information (repères 3, 4 et 5) avec les composants du portail.",
        "Les fonctions sont, dans l'ordre : Acquérir, Traiter, Communiquer.", [
        ("Repère 3 — ACQUÉRIR", KW(P("antenne|antennes|recepteur|reception")), "L'antenne réceptrice"),
        ("Repère 4 — TRAITER", KW(P("boitier|platine|microcontroleur"), P("carte", "commande|electronique"),
                                  P("unite", "commande"), forbid="telecommande"), "Le boîtier de commande"),
        ("Repère 5 — COMMUNIQUER", KW(P("feu|feux|clignotant|clignotants|gyrophare")), "Le feu clignotant")],
        "<p>On associe chaque composant de la légende à la fonction correspondante :</p><ul>"
        "<li><strong>Acquérir → l'antenne réceptrice</strong> (repère 2 de la légende). Elle capte le signal radio "
        "émis par la télécommande. La <em>cellule optique</em> réalise également une acquisition, mais pour la "
        "sécurité : elle détecte un obstacle entre les piliers.</li>"
        "<li><strong>Traiter → le boîtier de commande</strong> (repère 3 de la légende). C'est le « cerveau » du "
        "portail : il reçoit les informations, décide de l'ouverture ou de la fermeture, et envoie les ordres à la "
        "chaîne d'énergie.</li>"
        "<li><strong>Communiquer → le feu clignotant</strong> (repère 1 de la légende). Il prévient l'usager et les "
        "passants que le portail est en mouvement.</li></ul>"),
    GRP("Identifiez les entrées et la sortie de la chaîne d'information (repères 1, 2 et 6).",
        "Le repère 1 vient de l'utilisateur, le repère 2 vient de la chaîne d'énergie, le repère 6 repart vers "
        "l'utilisateur.", [
        ("Repère 1 (l'objet qui donne la consigne)", KW(P("telecommande|emetteur")), "La télécommande"),
        ("Repère 2 (le capteur de sécurité qui renvoie l'information)",
         KW(P("cellule|cellules|photoelectrique|capteur|capteurs")), "La cellule optique"),
        ("Repère 6 (ce qui est envoyé à l'utilisateur)", MESSAGES, "Les messages (signalisation lumineuse)")],
        "<ul><li><strong>Repère 1</strong> : la flèche part du pictogramme « utilisateur ». La consigne d'ouverture "
        "est donnée par la <strong>télécommande</strong> (repère 8 de la légende), dont le signal est ensuite capté "
        "par l'antenne réceptrice.</li>"
        "<li><strong>Repère 2</strong> : la longue flèche rouge remonte de la chaîne d'énergie : c'est le compte rendu. "
        "Sur ce portail, il est fourni par la <strong>cellule optique</strong> (repère 7 de la légende), qui détecte "
        "la présence d'un obstacle, ainsi que par les capteurs de fin de course qui indiquent que le vantail est "
        "ouvert ou fermé.</li>"
        "<li><strong>Repère 6</strong> : la flèche repart vers l'utilisateur : ce sont les <strong>messages</strong>, "
        "c'est-à-dire ici la signalisation lumineuse produite par le feu clignotant.</li></ul>"),
    GRP("Complétez la chaîne d'énergie du portail (repères 7 à 12) avec les composants ou les énergies mises en "
        "jeu.", "Le repère 7 est la source d'énergie extérieure ; les repères 8 à 12 sont Alimenter, Distribuer, "
        "Convertir, Transmettre, Agir.", [
        ("Repère 7 (source d'énergie extérieure)", RESEAU_SOURCE, "Le réseau électrique (230 V)"),
        ("Repère 8 — ALIMENTER", KW(P("alimentation|transformateur"), P("armoire")), "L'alimentation électrique"),
        ("Repère 9 — DISTRIBUER", KW(P("boitier|relais|variateur|platine|contacteur"), P("carte", "puissance|commande"),
                                     forbid="telecommande"), "Le boîtier de commande (partie puissance)"),
        ("Repère 10 — CONVERTIR", KW(P("moteur|moteurs|motoreducteur")), "Le moteur à bras"),
        ("Repère 11 — TRANSMETTRE", KW(P("bras|reducteur"), forbid="moteur|moteurs|motoreducteur"),
         "Le bras articulé (avec son réducteur)"),
        ("Repère 12 — AGIR", KW(P("vantail|vantaux|portail|battant|battants")), "Le vantail")],
        "<p>On suit l'énergie depuis la prise de courant jusqu'au mouvement du portail : "
        + calc("réseau électrique → alimentation → boîtier de commande → moteur → bras → vantail") + "</p><ul>"
        "<li><strong>Repère 7</strong> : la case verte placée avant la chaîne est la source extérieure, le "
        "<strong>réseau électrique</strong> (230 V).</li>"
        "<li><strong>Repère 8 — Alimenter</strong> : l'<strong>alimentation électrique</strong> (repère 6 de la "
        "légende) met l'installation sous tension, en basse tension.</li>"
        "<li><strong>Repère 9 — Distribuer</strong> : c'est la case qui reçoit la flèche rouge venant de "
        "<em>Traiter</em>. La partie puissance du <strong>boîtier de commande</strong> (relais, carte de puissance) "
        "laisse passer le courant vers le moteur, dans un sens ou dans l'autre selon qu'il faut ouvrir ou fermer.</li>"
        "<li><strong>Repère 10 — Convertir</strong> : le <strong>moteur à bras</strong> (repère 5 de la légende) "
        "transforme l'énergie électrique en énergie mécanique.</li>"
        "<li><strong>Repère 11 — Transmettre</strong> : le <strong>bras articulé</strong> (avec son réducteur) "
        "transmet le mouvement du moteur au vantail en l'adaptant.</li>"
        "<li><strong>Repère 12 — Agir</strong> : le <strong>vantail</strong> (repère 4 de la légende) est l'élément "
        "qui agit : il passe de la position initiale à la position finale, ce qui correspond bien aux deux flèches "
        "vertes du schéma.</li></ul>"
        "<p><em>Remarque</em> : le boîtier de commande apparaît deux fois, dans les deux chaînes. C'est fréquent : il "
        "contient à la fois la partie <em>commande</em> (Traiter) et la partie <em>puissance</em> (Distribuer).</p>"),
]})


# ------------------------------------------------------------ étiquettes à glisser dans les cases
# Chaque question propose une liste d'étiquettes (réutilisables, avec des intrus) : on glisse, on ne recopie plus.
# La correction reste celle du moteur à mots-clés : tests/correction.test.js vérifie, pour chaque case, quelles
# étiquettes de sa liste sont acceptées.
E_FONCTIONS = ["Acquérir", "Traiter", "Communiquer", "Alimenter", "Distribuer", "Convertir", "Transmettre", "Agir"]
E_ASC_FLUX = ["Consigne", "Compte rendu", "Messages", "Réseau électrique", "Énergie mécanique", "Énergie thermique",
              "Usager à l'étage d'arrivée"]
E_ASC_COMPO = ["Le moteur", "La boîte de réduction, la poulie et les câbles", "La cabine", "Le système de commande",
               "Les portes palières", "La gaine"]
E_RAV4 = ["Le réservoir de carburant", "Le système d'injection", "Le moteur thermique", "La batterie",
           "Le répartiteur de puissance", "Le moteur électrique", "La génératrice", "Le train épicycloïdal",
           "L'arbre de sortie et les pignons de renvoi", "Le réducteur", "Le différentiel", "Les roues motrices"]
E_GEO = ["Le clavier", "La sonde de température extérieure (TE)", "La sonde de température intérieure (TI)",
         "Le régulateur", "L'écran rétro-éclairé", "L'armoire électrique (réseau EDF)", "Le pilote des moteurs",
         "La pompe à chaleur", "Le plancher chauffant", "Le capteur géothermique"]
E_PORTAIL = ["La télécommande", "L'antenne réceptrice", "Le boîtier de commande", "Le feu clignotant",
             "La cellule optique", "Les messages (signalisation lumineuse)", "Le réseau électrique (230 V)",
             "L'alimentation électrique", "Le moteur à bras", "Le bras articulé", "Le vantail"]
EX1_ETIQUETTES = [[E_FONCTIONS, E_FONCTIONS, E_ASC_FLUX, E_ASC_COMPO], [E_RAV4] * 4, [E_FONCTIONS, E_GEO, E_GEO],
                  [E_PORTAIL] * 3]


def ordre_etiquettes(e):
    """Ordre alphabétique, sans tenir compte de l'article ni des accents : la liste ne souffle pas la réponse."""
    sans = re.sub(r"^(le |la |les |l')", "", e.lower())
    return unicodedata.normalize("NFD", sans).encode("ascii", "ignore").decode()


for _p, _banks in zip(PARTS_EX1, EX1_ETIQUETTES):
    _grps = [b for b in _p["blocks"] if b["kind"] == "grp"]
    assert len(_grps) == len(_banks), _p["title"]
    for _g, _bank in zip(_grps, _banks):
        _g["bank"] = sorted(_bank, key=ordre_etiquettes)


# ============================================================ DOCUMENTS DE L'EXERCICE 1.1
def _schema_chaines():
    """Structure générale d'une chaîne fonctionnelle (DP1) : chaîne d'information au-dessus de la chaîne d'énergie."""
    def bloc(x, y, w, t, k):
        c, f = ("#1F5FA8", "#E6EEF8") if k == "i" else ("#B26A00", "#FCEFD8")
        return (f'<rect x="{x}" y="{y}" width="{w}" height="54" fill="{f}" stroke="{c}" stroke-width="2"/>'
                f'<text x="{x + w / 2}" y="{y + 33}" text-anchor="middle" font-weight="700" font-size="15" '
                f'fill="{c}" letter-spacing=".5">{t}</text>')
    fl = 'fill="none" stroke-width="2.2"'
    info = 'stroke="#1F5FA8" marker-end="url(#dp-ai)"'
    ener = 'stroke="#B26A00" marker-end="url(#dp-ae)"'
    mo = 'stroke="#1B7A43" marker-end="url(#dp-am)"'
    t = 'font-size="13.5" font-weight="600"'
    return (
        '<svg class="dp-svg" viewBox="0 0 900 350" role="img" aria-labelledby="dp-svg-t">'
        '<title id="dp-svg-t">Structure d\'une chaîne fonctionnelle : la chaîne d\'information (acquérir, traiter, '
        'communiquer) envoie des ordres à la fonction distribuer de la chaîne d\'énergie (alimenter, distribuer, '
        'convertir, transmettre, agir) ; les capteurs rendent compte à la fonction acquérir.</title><defs>'
        '<marker id="dp-ai" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0 0L10 5L0 10Z" fill="#1F5FA8"/></marker>'
        '<marker id="dp-ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0 0L10 5L0 10Z" fill="#B26A00"/></marker>'
        '<marker id="dp-am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0 0L10 5L0 10Z" fill="#1B7A43"/></marker></defs>'
        '<rect x="150" y="34" width="580" height="104" fill="#F4F7FB" stroke="#9DB6D6" stroke-dasharray="6 4"/>'
        '<rect x="96" y="196" width="676" height="104" fill="#FDF8EF" stroke="#DDBB8A" stroke-dasharray="6 4"/>'
        '<text x="158" y="52" font-size="12" font-weight="700" fill="#1F5FA8" letter-spacing="1">CHAÎNE D\'INFORMATION</text>'
        '<text x="104" y="214" font-size="12" font-weight="700" fill="#B26A00" letter-spacing="1">CHAÎNE D\'ÉNERGIE</text>'
        + bloc(170, 64, 150, "ACQUÉRIR", "i") + bloc(360, 64, 150, "TRAITER", "i") + bloc(550, 64, 160, "COMMUNIQUER", "i")
        + bloc(110, 226, 118, "ALIMENTER", "e") + bloc(250, 226, 124, "DISTRIBUER", "e")
        + bloc(396, 226, 118, "CONVERTIR", "e") + bloc(536, 226, 130, "TRANSMETTRE", "e")
        + '<rect x="796" y="226" width="86" height="54" fill="#FFF3C4" stroke="#1C2530" stroke-width="2"/>'
        '<text x="839" y="259" text-anchor="middle" font-weight="700" font-size="15" fill="#1C2530">AGIR</text>'
        f'<path d="M18 91H168" {fl} {info}/><text x="22" y="82" {t} fill="#1F5FA8">consignes</text>'
        f'<path d="M320 91H358" {fl} {info}/><path d="M510 91H548" {fl} {info}/>'
        f'<path d="M710 91H880" {fl} {info}/><text x="734" y="82" {t} fill="#1F5FA8">messages</text>'
        f'<path d="M435 118V170H312V224" {fl} {info}/><text x="446" y="164" {t} fill="#1F5FA8" font-weight="800">ordres</text>'
        f'<path d="M601 280V322H70V111H168" {fl} stroke-dasharray="7 5" {info}/>'
        f'<text x="80" y="316" {t} fill="#1F5FA8">compte rendu (capteurs)</text>'
        f'<path d="M8 253H108" {fl} {ener}/><text x="8" y="274" {t} fill="#B26A00">énergie</text>'
        f'<path d="M228 253H248" {fl} {ener}/><path d="M374 253H394" {fl} {ener}/>'
        f'<path d="M514 253H534" {fl} {ener}/><path d="M666 253H794" {fl} {ener}/>'
        f'<path d="M839 176V224" {fl} {mo}/><path d="M839 280V330" {fl} {mo}/>'
        f'<text x="830" y="168" {t} fill="#1B7A43" text-anchor="end">matière d\'œuvre entrante</text>'
        f'<text x="830" y="344" {t} fill="#1B7A43" text-anchor="end">matière d\'œuvre sortante</text>'
        '</svg>')


DOCS = [
    ("DP1", "Chaîne d'information et chaîne d'énergie", "Dossier présentation", False,
     '<div class="doc-text"><h3>Rappel de cours</h3><p>Tout système technique se décrit avec deux chaînes couplées :</p>'
     "<ul><li><strong>Chaîne d'information</strong> : <em>ACQUÉRIR</em> → <em>TRAITER</em> → <em>COMMUNIQUER</em>. "
     "Elle reçoit les <em>consignes</em> de l'utilisateur et le <em>compte rendu</em> des capteurs, et elle renvoie "
     "des <em>messages</em> à l'utilisateur.</li>"
     "<li><strong>Chaîne d'énergie</strong> (ou de puissance) : <em>ALIMENTER</em> → <em>DISTRIBUER</em> → "
     "<em>CONVERTIR</em> → <em>TRANSMETTRE</em> → <em>AGIR</em>. Elle transforme l'énergie d'entrée pour agir sur "
     "la <em>matière d'œuvre</em>.</li></ul>"
     "<p>Le lien entre les deux : la fonction <em>TRAITER</em> envoie les ordres à la fonction <em>DISTRIBUER</em>, "
     "et la chaîne d'énergie renvoie un compte rendu (capteurs) vers la fonction <em>ACQUÉRIR</em>.</p>"
     + _schema_chaines() +
     "<h3>Lire un schéma à compléter</h3><ul>"
     "<li>Les cases sont numérotées en rouge ; une case reçoit soit une <strong>fonction</strong> (un verbe à "
     "l'infinitif), soit le <strong>composant</strong> qui la réalise, soit le nom d'une <strong>entrée</strong> ou "
     "d'une <strong>sortie</strong>, selon la question.</li>"
     "<li>Les flèches indiquent ce qui circule : informations (consignes, compte rendu, ordres, messages), énergie, "
     "matière d'œuvre.</li></ul></div>"),
    ("DT1", "Le rôle de chaque fonction", "Dossier technique", True,
     '<div class="doc-text"><h3>Ce que fait chaque fonction</h3>'
     '<table class="t"><thead><tr><th>Fonction</th><th>Rôle</th><th>Exemple : trottinette électrique</th></tr></thead><tbody>'
     '<tr class="dt-i"><td><b>Acquérir</b></td><td>Prélever une information : une consigne de l\'utilisateur ou l\'état '
     "du système (capteurs).</td><td>capteur d'accélérateur (potentiomètre)</td></tr>"
     '<tr class="dt-i"><td><b>Traiter</b></td><td>Élaborer une décision à partir des informations acquises, puis '
     "donner les ordres.</td><td>carte de traitement</td></tr>"
     '<tr class="dt-i"><td><b>Communiquer</b></td><td>Transmettre les ordres à la chaîne d\'énergie et restituer des '
     "informations à l'utilisateur.</td><td>affichage de la vitesse</td></tr>"
     '<tr class="dt-e"><td><b>Alimenter</b></td><td>Fournir l\'énergie au système ; elle peut être stockée.</td>'
     "<td>batterie (accumulateur)</td></tr>"
     '<tr class="dt-e"><td><b>Distribuer</b></td><td>Laisser passer ou non l\'énergie vers l\'actionneur, dans la '
     "bonne quantité et le bon sens, selon les ordres reçus (préactionneur).</td><td>hacheur (carte variateur)</td></tr>"
     '<tr class="dt-e"><td><b>Convertir</b></td><td>Changer la forme de l\'énergie (actionneur).</td>'
     "<td>moteur à courant continu</td></tr>"
     '<tr class="dt-e"><td><b>Transmettre</b></td><td>Acheminer l\'énergie mécanique jusqu\'à l\'effecteur en adaptant '
     "le mouvement (vitesse, couple, rotation ou translation).</td><td>poulies et courroie</td></tr>"
     '<tr class="dt-e"><td><b>Agir</b></td><td>Réaliser l\'action sur la matière d\'œuvre (effecteur).</td>'
     "<td>roue arrière</td></tr></tbody></table>"
     "<h3>Indices pour repérer une case</h3><ul>"
     "<li>La case qui reçoit les <strong>ordres</strong> venant de <em>Traiter</em> est <em>Distribuer</em>.</li>"
     "<li>La case traversée par la <strong>matière d'œuvre</strong> (état initial → état final) est <em>Agir</em>.</li>"
     "<li>La <strong>source d'énergie</strong> est placée avant <em>Alimenter</em>, hors des cases de fonction.</li>"
     "<li>Le <strong>compte rendu</strong> des capteurs remonte de la chaîne d'énergie vers <em>Acquérir</em>.</li>"
     "<li>Un même boîtier peut apparaître dans les deux chaînes : sa partie commande <em>traite</em>, sa partie "
     "puissance <em>distribue</em>.</li></ul></div>"),
]


# ============================================================ rendu HTML
def render_q(q, part):
    """Question à une case (non utilisée dans l'exercice 1.1, conservée pour les exercices à venir)."""
    qid, label = q["id"], q["label"]
    return f"""
        <div class="q" id="{qid}" data-q="{qid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{q['stem']}</strong></p>
          <p class="q-hint" id="h-{qid}">{q['hint']}</p>
          <div class="q-row">
            <input type="text" class="q-input" id="in-{qid}" aria-label="Réponse {label}" aria-describedby="h-{qid}" autocomplete="off" autocapitalize="off" spellcheck="false">
            <button type="button" class="btn btn-validate">Valider</button>
            <span class="q-status" aria-live="polite"></span>
            <span class="print-only pstat">Non validée : comptée fausse</span>
          </div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="q-unit-msg" hidden></p>
            <p class="q-expected"><span>Réponse attendue :</span> {q['expected']}</p>
            <div class="q-why">{q['why']}</div>
          </div>
        </div>"""


def render_grp(g, part):
    """Question à plusieurs cases : structure « fast-q » du gabarit (un bouton, une correction commune).
    Chaque case garde le champ lu par le moteur (masqué) ; on la remplit en y glissant une étiquette de la liste."""
    gid, label = g["id"], g["label"]
    rows = "".join(
        f'<div class="grp-l"><span class="grp-lab" id="lb-{fid}">{fl}</span><div class="sol">'
        f'<input type="hidden" id="in-{fid}" data-q="{fid}"><button type="button" class="dz" id="dz-{fid}" '
        f'aria-labelledby="lb-{fid} dzv-{fid}"><span class="dz-v" id="dzv-{fid}">case vide</span></button>'
        f'<span class="mark" aria-live="polite"></span></div></div>'
        for fid, (fl, _g, _e) in zip(g["fids"], g["fields"]))
    tags = "".join(f'<button type="button" class="etq" draggable="true" aria-pressed="false">{esc(t)}</button>'
                   for t in g["bank"])
    sol = "".join(f"<tr><td>{fl}</td><td>{e}</td></tr>" for fl, _g, e in g["fields"])
    n = len(g["fields"])
    return f"""
        <div class="fast-q grp" id="{gid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{g['stem']}</strong></p>
          <p class="q-hint">{g['hint']}</p>
          <div class="bank" role="group" aria-label="Étiquettes de la question {label}"><span class="bank-t">Étiquettes</span>{tags}</div>
          <div class="grp-fields" role="group" aria-label="Cases de la question {label}">{rows}</div>
          <div class="fast-foot"><button type="button" class="btn btn-fast">Valider {'les ' + str(n) + ' cases' if n > 1 else 'la case'}</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <table class="t grp-sol"><thead><tr><th>Case</th><th>Réponse attendue</th></tr></thead><tbody>{sol}</tbody></table>
            <div class="q-why"><p class="why-t">Démarche</p>{g['why']}</div>
          </div>
        </div>"""


def render_qbar(b):
    chips = " ".join(f'<button type="button" class="doc-chip" data-doc="{d}" aria-pressed="false">{d}</button>'
                     for d in b["docs"])
    return (f'\n      <div class="qbar" role="group" aria-label="{b["label"]}"><div class="qb-num">{b["label"]}</div>'
            f'<div class="qb-docs">Documents à consulter : {chips}</div><div class="qb-ans">Répondre : {b["ans"]}</div></div>')


def item_points(b):
    return {"q": 1, "grp": len(b.get("fields", ())), "sk": len(b.get("criteria", ()))}.get(b["kind"], 0)


def part_points(p):
    return sum(item_points(b) for b in p["blocks"])


def hm(minutes):
    h, m = divmod(minutes, 60)
    return f"{h}\u00a0h\u00a0{m:02d}" if h else f"{m}\u00a0min"


HOUSE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.3" '
         'stroke-linejoin="round" stroke-linecap="round"><path d="M3 11.5 12 4l9 7.5"/>'
         '<path d="M5.5 9.8V20h4.5v-5.5h4V20h4.5V9.8"/></svg>')

QLABEL = {}
CUR = {"total": 1}


def pct(minutes):
    return fr(minutes / CUR["total"] * 100, 1)


def render_part(p):
    pts = part_points(p)
    body = "\n      ".join(p["intro"])
    blocks = []
    for b in p["blocks"]:
        if b["kind"] == "q":
            blocks.append(render_q(b, p))
        elif b["kind"] == "grp":
            blocks.append(render_grp(b, p))
        elif b["kind"] == "qbar":
            blocks.append(render_qbar(b))
        else:
            blocks.append(b["html"])
    n = p["num"]
    return f"""
  <section class="part" id="partie-{n}" aria-labelledby="t-partie-{n}">
    <header class="part-head"><div class="part-num" aria-hidden="true">{n}</div>
      <div><h2 id="t-partie-{n}"><span class="sr-only">Partie {n} : </span>{p['title']}</h2>
        <div class="duree">Durée conseillée : {hm(p['minutes'])} · Barème : {pts} points, soit {pct(p['minutes'])} % de la note</div></div></header>
    <div class="part-body">
      {body}{''.join(blocks)}
    </div>
  </section>"""


def prepare_exo(e):
    """Copie et numérote les parties d'un exercice (Q1.1, Q1.2…) ; calcule sa configuration pour les moteurs."""
    parts = copy.deepcopy(e["parts"])
    for i, p in enumerate(parts):
        p["num"] = str(i + 1)
        k = 0
        for b in p["blocks"]:
            if b["kind"] in ("q", "grp"):
                k += 1
                b["id"] = f"{e['prefix']}{p['num']}_{k}"
                b["label"] = f"Q{p['num']}.{k}"
                QLABEL[b["id"]] = b["label"]
                if b["kind"] == "grp":
                    b["fids"] = [f"{b['id']}_{j + 1}" for j in range(len(b["fields"]))]
        # figures qui suivent la correction d'une partie (RAV4) : identifiants de ses questions
        grp_ids = " ".join(b["id"] for b in p["blocks"] if b["kind"] in ("q", "grp"))
        p["intro"] = [x.replace("__GRP__", grp_ids) for x in p["intro"]]
        # la barre de documents prend le numéro de la question qui la suit
        for j, b in enumerate(p["blocks"]):
            if b["kind"] == "qbar":
                nxt = next((x for x in p["blocks"][j + 1:] if x["kind"] in ("q", "grp")), None)
                b["label"] = nxt["label"] if nxt else f"Partie {p['num']}"
    e["P"] = parts
    e["minutes"] = sum(p["minutes"] for p in parts)
    e["n_q"] = sum(1 for p in parts for b in p["blocks"] if b["kind"] in ("q", "grp"))
    e["n_cases"] = sum(item_points(b) for p in parts for b in p["blocks"] if b["kind"] in ("q", "grp"))
    e["points"] = sum(part_points(p) for p in parts)
    qcfg, parts_cfg = {}, []
    for p in parts:
        parts_cfg.append({"num": p["num"], "title": p["title"], "minutes": p["minutes"],
                          "duration": hm(p["minutes"]), "points": part_points(p)})
        for b in p["blocks"]:
            if b["kind"] == "q":
                qcfg[b["id"]] = {"label": b["label"], "part": p["num"], "pts": 1, "grader": b["grader"]}
            elif b["kind"] == "grp":
                for fid, (fl, g, _x) in zip(b["fids"], b["fields"]):
                    qcfg[fid] = {"label": f"{b['label']} — {re.sub(r'<[^>]+>', '', fl)}", "part": p["num"],
                                 "pts": 1, "grader": g}
    np_ = len(parts)
    e["cfg"] = {"title": e["title"], "minutes": e["minutes"], "duree": hm(e["minutes"]),
                "cartouche": f"{e['n_q']} questions, {e['n_cases']} cases notées, réparties en {np_} partie"
                             f"{'s' if np_ > 1 else ''} pondérée{'s' if np_ > 1 else ''} par leur durée.",
                "parts": parts_cfg, "qcfg": qcfg, "skcfg": {}}


def render_docs(e):
    rail, tabs, secs = [], [], []
    first_dt = True
    for key, title, kind, is_dt, content in sorted((d for d in DOCS if d[0] in e["docs"]),
                                                   key=lambda d: (d[3], d[0])):
        if is_dt and first_dt:
            rail.append('<div class="grp" aria-hidden="true"></div>')
            first_dt = False
        cls = "tab dt" if is_dt else "tab"
        rail.append(f'<button type="button" class="{cls}" data-doc="{key}" aria-selected="false" title="{esc(title)}">{key}</button>')
        tabs.append(f'<button type="button" data-doc="{key}" aria-selected="false">{key}</button>')
        secs.append(f'<section class="doc" id="doc-{key}" data-title="{key} : {esc(title)}" data-kind="{kind}">{content}\n</section>')
    return "".join(rail), "".join(tabs), "\n".join(secs)


def pastille(level):
    if not level:
        return ""
    return f' <span class="pastille n{level.split()[-1]}">{level}</span>'


def render_exo_home(e):
    src, w, h = png(e["hero"][0])
    docs = sorted(e["docs"], key=lambda k: (k[:2] != "DP", k))
    docs_txt = (", ".join(docs[:-1]) + " et " + docs[-1]) if len(docs) > 1 else docs[0]
    facts = ('<div class="home-facts">'
             f'<div><b>{len(e["P"])} parties</b><span>{e["n_q"]} questions</span></div>'
             f'<div><b>{hm(e["minutes"])}</b><span>durée conseillée</span></div>'
             f'<div><b>{len(docs)} documents</b><span>{docs_txt}</span></div>'
             f'<div><b>{e["n_cases"]} cases</b><span>un point chacune</span></div></div>')
    return (f'<div class="home-top"><div class="home-top-l"><header class="home-head"><span class="mc-tag">{e["tag"]}</span>{pastille(e.get("level"))}'
            f'<h1 id="home-title">{e["title"]}</h1><p class="home-sub">{e["sub"]}</p></header>{facts}</div>'
            f'<figure class="home-hero"><img src="{src}" alt="{esc(e["hero"][1])}" width="{w}" height="{h}">'
            f'<figcaption class="small">{e["hero"][2]}</figcaption></figure></div>')


MODES_HTML = """<h2 class="home-choose">Choisis ton mode de travail</h2>
<div class="modes">
  <article class="mode-card">
    <div class="mc-head"><span class="mc-tag">Mode 1</span><h3>Mode entraînement</h3></div>
    <p class="mc-lead">Pour apprendre en avançant, question par question.</p>
    <ul><li>Chaque question se valide isolément ; la démarche corrigée s'affiche aussitôt.</li>
      <li>La note pondérée s'actualise en continu dans le bandeau.</li>
      <li>Les documents et le chronomètre restent disponibles, sans contrainte de temps.</li></ul>
    <button type="button" class="btn btn-mode" data-mode="training">Commencer l'entraînement</button>
  </article>
  <article class="mode-card exam">
    <div class="mc-head"><span class="mc-tag">Mode 2</span><h3>Mode examen</h3></div>
    <p class="mc-lead">Pour se placer dans les conditions d'une évaluation.</p>
    <ul><li>Aucune correction et aucune note pendant la composition ; les réponses restent modifiables.</li>
      <li>Le chronomètre tourne, à comparer à la durée conseillée.</li>
      <li>En fin de sujet, le bouton « J'ai fini, je fais corriger ma copie » dévoile d'un coup les corrections, les notes par partie et la note globale.</li></ul>
    <button type="button" class="btn btn-mode" data-mode="exam">Composer en mode examen</button>
  </article>
</div>
<p class="home-note small">Le mode se choisit une seule fois : pour en changer, reviens à l'accueil (onglet maison) et rouvre l'exercice. Rien n'est enregistré sur l'ordinateur.</p>
<p class="home-back"><a class="btn ghost" href="?">""" + HOUSE + """ Retour à l'accueil</a></p>"""

CONSIGNES_MOTS = """<p class="only-training"><strong>Mode entraînement.</strong> Remplis les cases d'une question puis clique sur « Valider » : une réponse validée est définitive et sa correction s'affiche aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Compose tout le sujet sans correction ni note : tes réponses restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections, les notes par partie et la note globale.</p>
    <p><strong>Des étiquettes, pas de calcul.</strong> Chaque question propose ses étiquettes : <strong>glisse</strong> une étiquette sur une case, ou <strong>touche</strong> une étiquette puis la case (au clavier : Entrée sur l'étiquette, puis Entrée sur la case). Une étiquette peut servir plusieurs fois, certaines ne servent pas. Pour vider une case, touche-la ou ramène son étiquette dans la liste.</p>
    <p><strong>Une question, plusieurs cases.</strong> Les cases d'une même question se valident ensemble ; chaque case vaut un point. Les schémas sont numérotés en rouge pour repérer chaque case à compléter.</p>
    <p>Le dossier de présentation (DP) et le dossier technique (DT) s'ouvrent avec les onglets sur le bord droit, ou avec les boutons des en-têtes de question.</p>
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque partie est notée sur 20, puis pèse au prorata de son temps. Le récapitulatif de fin de sujet donne le détail partie par partie.</p>"""


# ============================================================ EXERCICES ET ÉTUDES (accueil et configuration)
# Ajouter un exercice : décrire ses parties (comme PARTS_EX1), puis l'ajouter ici ; "etude": True le range dans
# la rubrique « Études de cas ». La carte apparaît d'elle-même sur l'accueil.
EXO_DEFS = [
    {"key": "chaines-information-energie", "prefix": "a", "tag": "Exercice 1.1", "level": "Niveau 1",
     "title": "Chaînes d'information et d'énergie", "parts": PARTS_EX1, "docs": ["DP1", "DT1"],
     "consignes": CONSIGNES_MOTS,
     "hero": ("ex1-portail", "Portail automatisé à deux vantaux et ses huit composants numérotés",
              "Quatre systèmes à décrire : ascenseur, voiture hybride, chauffage géothermique et portail."),
     "card": "Un ascenseur, une voiture hybride, un chauffage géothermique et un portail automatisé : nommer les "
             "fonctions, placer les composants, repérer les entrées et les sorties.",
     "sub": "Quatre systèmes techniques à analyser : compléter leurs chaînes d'information et d'énergie avec les "
            "fonctions, les composants qui les réalisent, les consignes, les comptes rendus et l'énergie d'entrée."},
]


# ============================================================ ACCUEIL
COURS = [
    {"key": "cours-chaine-fonctionnelle", "tag": "Cours 1", "level": "Niveau 1", "title": "La chaîne fonctionnelle",
     "desc": "Un portail automatique animé pas à pas : chaîne d'information, chaîne d'énergie et ce qui les relie ; "
             "avec un jeu et un quiz."},
    {"key": "cours-chaine-energie", "tag": "Cours 2", "level": "Niveau 2", "title": "Chaîne d'énergie des produits",
     "desc": "Alimenter, distribuer, convertir, transmettre, agir : composants, symboles, puissances et rendements ; "
             "avec des simulateurs, un jeu et un quiz."},
    {"key": "cours-chaine-information", "tag": "Cours 3", "level": "Niveau 2", "title": "Chaîne d'information des produits",
     "desc": "Acquérir, traiter, communiquer : capteurs et signaux, chaîne d'acquisition, programme, réseaux et "
             "encodage ; avec une machine à café animée, des laboratoires, des jeux et un quiz."},
]
# Rubrique « Études de cas » : tant qu'aucune étude n'est décrite dans EXO_DEFS, une carte l'annonce.
ETUDE_A_VENIR = ("Étude de cas", "Un système réel étudié de bout en bout : chaînes d'information et d'énergie, "
                 "choix des composants, puissances et rendements.")
OUVRIR = ("Ouvrir l'exercice", "Ouvrir l'étude")


def _exo_card(e):
    return (f'<article class="mode-card"><div class="mc-head"><span class="mc-tag">{e["tag"]}{pastille(e.get("level"))}'
            f'</span><h3>{e["title"]}</h3></div>'
            f'<p>{e["card"]}</p><p class="small ex-meta">{len(e["P"])} partie{"s" if len(e["P"]) > 1 else ""} · '
            f'{e["n_q"]} questions · {e["n_cases"]} cases · {hm(e["minutes"])}</p>'
            f'<a class="btn" href="?ex={e["key"]}">{OUVRIR[bool(e.get("etude"))]}</a></article>')


FORMULAIRE_CARTES = [
    ("Formulaire", "Formulaire de la chaîne de puissance",
     "Toutes les formules de la séquence en carte mentale : puissance, énergie, rendement, conversions, rotation et "
     "transmission, électrotechnique, stockage. Chaque formule avec ses grandeurs, leurs unités et ses autres "
     "écritures, une recherche par mot ou par symbole.",
     "Carte mentale · recherche · version imprimable", "formulaire.html#formulaire", "Ouvrir le formulaire"),
    ("Calculs", "Exercices de calcul",
     "Des séries de calculs courts à valeurs aléatoires : tu choisis les thèmes et le nombre de questions. Les données "
     "sont en clair, la formule est à retrouver, parfois à isoler.",
     "1 à 40 questions · correction détaillée · note sur 20", "formulaire.html#exercices", "Choisir mes exercices"),
]


def _lien_card(tag, title, desc, meta, href, bouton):
    return (f'<article class="mode-card lien-card"><div class="mc-head"><span class="mc-tag">{tag}</span>'
            f'<h3>{title}</h3></div><p>{desc}</p><p class="small ex-meta">{meta}</p>'
            f'<a class="btn" href="{href}">{bouton}</a></article>')


def render_hub():
    src, w, h = png("accueil")
    cards = "".join(_exo_card(e) for e in EXO_DEFS if not e.get("etude")) + _lien_card(*FORMULAIRE_CARTES[1])
    etudes = "".join(_exo_card(e) for e in EXO_DEFS if e.get("etude")) or (
        f'<article class="mode-card en-edition"><div class="mc-head"><span class="mc-tag">Étude 1</span>'
        f'<h3>{ETUDE_A_VENIR[0]}</h3></div><p>{ETUDE_A_VENIR[1]}</p>'
        '<p class="small ex-meta etat">En cours d\'édition</p></article>')
    cours = "".join(
        f'<article class="mode-card cours-card"><div class="mc-head">'
        f'<span class="mc-tag">{c["tag"]}{pastille(c.get("level"))}</span><h3>{c["title"]}</h3></div>'
        f'<p>{c["desc"]}</p><p class="small ex-meta">Disponible</p>'
        f'<a class="btn" href="?ex={c["key"]}">Lire le cours</a></article>' for c in COURS)
    return (f'<div class="home-top"><div class="home-top-l"><header class="home-head"><h1 id="home-title">{TITRE}</h1>'
            "<p class=\"home-sub\">Chaîne d'information et chaîne d'énergie : décrire un système automatisé, identifier "
            "ses fonctions et ses composants, suivre l'énergie de la source jusqu'à l'action, calculer puissances et "
            "rendements. Des cours, des exercices et des études de cas interactifs de deux niveaux, à faire en mode "
            "entraînement ou en mode examen, et le formulaire de la chaîne de puissance.</p></header></div>"
            f'<figure class="home-hero"><img src="{src}" alt="Quatre systèmes : un ascenseur en coupe, un portail '
            f'automatique à deux vantaux, un chauffage géothermique et une voiture hybride avec le schéma de sa '
            f'motorisation" width="{w}" height="{h}">'
            '<figcaption class="small">Les systèmes étudiés dans l\'exercice 1.1.</figcaption></figure></div>'
            f'<h2 class="home-choose">Les cours</h2><div class="ex-grid cours-grid">{cours}</div>'
            f'<h2 class="home-choose">Le formulaire</h2><div class="ex-grid form-grid">{_lien_card(*FORMULAIRE_CARTES[0])}</div>'
            f'<h2 class="home-choose">Les exercices</h2><div class="ex-grid exo-grid">{cards}</div>'
            f'<h2 class="home-choose">Études de cas</h2><div class="ex-grid etude-grid">{etudes}</div>'
            f'<p class="home-note small">Pastilles : {pastille("Niveau 1").strip()} premier niveau, '
            f'{pastille("Niveau 2").strip()} niveau approfondi. Les études de cas reprendront des systèmes réels et '
            "mobiliseront plusieurs notions. Chaque exercice propose le mode entraînement (correction question par "
            "question) ou le mode examen (correction à la remise de la copie). Rien n'est enregistré sur "
            "l'ordinateur.</p>")


def course_head(tag, level, title, sub):
    return (f'<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head">'
            f'<span class="mc-tag">{tag}</span>{pastille(level)}<h1 id="home-title">{title}</h1>'
            f'<p class="home-sub">{sub}</p></header></div></div>')


def course_section(n, ident, titre, body):
    return (f'<section class="part cours-sec" id="{ident}" aria-labelledby="{ident}-t"><header class="part-head">'
            f'<div class="part-num" aria-hidden="true">{n}</div><div><h2 id="{ident}-t" style="padding:14px 16px">{titre}'
            f'</h2></div></header><div class="part-body">{body}</div></section>')


def course_nav(items):
    return ('<nav class="cours-nav no-print" aria-label="Étapes du cours">' +
            "".join(f'<a href="#{a}">{n}. {t}</a>' for n, (a, t) in enumerate(items, 1)) + "</nav>")


def quiz_html(questions, name):
    """Quiz noté (moteur initQuiz) : questions = [(énoncé, [choix], indice juste, explication)]."""
    return "".join(
        f'<fieldset class="quiz-q" data-ok="{ok}"><legend><span class="q-num">{i + 1}</span> {q}</legend>' +
        "".join(f'<label><input type="radio" name="{name}{i}" value="{j}"> {o}</label>' for j, o in enumerate(opts)) +
        f'<p class="quiz-fb" aria-live="polite"></p><p class="quiz-why" hidden>{why}</p></fieldset>'
        for i, (q, opts, ok, why) in enumerate(questions))


def quiz_section(n, ident, questions, name):
    return course_section(n, ident, "Quiz : vérifie tes connaissances",
                          f'<p>Choisis une réponse : la correction s\'affiche aussitôt.</p><div class="quiz">'
                          f'{quiz_html(questions, name)}</div><div class="quiz-score" aria-live="polite">'
                          f'<span id="qz-score">0 / {len(questions)}</span><span id="qz-stars" aria-hidden="true"></span>'
                          '<button type="button" class="btn ghost" id="qz-reset">Recommencer</button></div>')


def jeu_html(lignes, choix, ident):
    """Jeu de classement : chaque ligne (libellé, clé juste) propose les mêmes boutons (clé, texte)."""
    rows = "".join(
        f'<div class="jeu-l" data-ok="{ok}"><span>{t}</span>' +
        "".join(f'<button type="button" class="btn ghost" data-v="{k}">{n}</button>' for k, n in choix) +
        '<b class="jeu-fb" aria-live="polite"></b></div>' for t, ok in lignes)
    return (f'<div class="jeu" id="{ident}">{rows}<p class="jeu-score" aria-live="polite">Score : '
            f'<span class="jeu-s">0 / {len(lignes)}</span> <button type="button" class="btn ghost jeu-reset">'
            'Recommencer</button></p></div>')


# ============================================================ COURS — éléments communs (quiz, jeux, cartes)
COURS_COMMUN_JS = r"""
  function initQuiz(root) {
    function q(s) { return root.querySelector(s); }
    function qa(s) { return Array.prototype.slice.call(root.querySelectorAll(s)); }
    var qs = qa(".quiz-q");
    function score() {
      var n = qs.filter(function (f) { return f.classList.contains("is-ok"); }).length;
      var done = qs.filter(function (f) { return f.classList.contains("done"); }).length;
      var st = n === qs.length ? 3 : n >= qs.length - 2 ? 2 : n >= 2 ? 1 : 0;
      q("#qz-score").textContent = n + " / " + qs.length;
      q("#qz-stars").textContent = done === qs.length ? "★★★".slice(0, st) + "☆☆☆".slice(0, 3 - st) : "";
    }
    qs.forEach(function (fs) {
      fs.addEventListener("change", function (e) {
        if (fs.classList.contains("done")) return;
        var ok = e.target.value === fs.getAttribute("data-ok");
        fs.classList.add("done", ok ? "is-ok" : "is-ko");
        fs.querySelector(".quiz-fb").textContent = ok ? "✔ Bonne réponse !" : "✘ Pas tout à fait.";
        fs.querySelector(".quiz-why").hidden = false;
        Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) {
          i.disabled = true;
          if (i.value === fs.getAttribute("data-ok")) i.parentNode.classList.add("good");
        });
        score();
      });
    });
    q("#qz-reset").addEventListener("click", function () {
      qs.forEach(function (fs) {
        fs.classList.remove("done", "is-ok", "is-ko");
        fs.querySelector(".quiz-fb").textContent = "";
        fs.querySelector(".quiz-why").hidden = true;
        Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) { i.disabled = false; i.checked = false; i.parentNode.classList.remove("good"); });
      });
      score();
    });
    score();
  }
  // jeu de classement : un clic par ligne, le bon bouton est montré en cas d'erreur
  function initJeu(box) {
    var lignes = Array.prototype.slice.call(box.querySelectorAll(".jeu-l"));
    function score() {
      box.querySelector(".jeu-s").textContent = lignes.filter(function (l) { return l.classList.contains("is-ok"); }).length + " / " + lignes.length;
    }
    lignes.forEach(function (l) {
      Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) {
        b.addEventListener("click", function () {
          if (l.classList.contains("is-ok") || l.classList.contains("is-ko")) return;
          var good = l.getAttribute("data-ok"), ok = b.getAttribute("data-v") === good;
          l.classList.add(ok ? "is-ok" : "is-ko");
          b.classList.add(ok ? "pick-ok" : "pick-ko");
          if (!ok) l.querySelector('button[data-v="' + good + '"]').classList.add("pick-good");
          l.querySelector(".jeu-fb").textContent = ok ? "✔" : "✘";
          score();
        });
      });
    });
    box.querySelector(".jeu-reset").addEventListener("click", function () {
      lignes.forEach(function (l) {
        l.classList.remove("is-ok", "is-ko");
        l.querySelector(".jeu-fb").textContent = "";
        Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) { b.classList.remove("pick-ok", "pick-ko", "pick-good"); });
      });
      score();
    });
    score();
  }
  // cartes à retourner
  function initCartes(root) {
    Array.prototype.forEach.call(root.querySelectorAll(".carte"), function (b) {
      b.addEventListener("click", function () { b.setAttribute("aria-expanded", b.getAttribute("aria-expanded") === "true" ? "false" : "true"); });
    });
  }
  function fr(x, d) { return x.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace(/^-/, "−"); }
"""

COURS_COMMUN_CSS = """
/* ---------- cours interactifs (repris du dépôt RDM) ---------- */
.cours .part{margin-bottom:22px}
.cours-nav{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 16px}
.cours-nav a{font:600 .92rem var(--f-titre); color:var(--encre); background:var(--papier); border:1.5px solid var(--encre); padding:5px 12px; text-decoration:none}
.cours-nav a:hover{background:var(--jaune-pale)}
.cours-defi{font-weight:700; color:var(--bleu)}
.cours .part-body h3{font:700 1.12rem var(--f-titre); margin:18px 0 6px}
.formule{display:flex; flex-wrap:wrap; gap:14px 28px; align-items:center; border:2px solid var(--rouge); background:#fff; padding:10px 18px; margin:12px 0; max-width:680px}
.formule .f-main{font:700 1.5rem var(--f-titre); line-height:2}
.formule .f-units{font-size:.9rem; color:var(--encre-2)}
.simu{border:2px solid var(--bleu); background:var(--bleu-pale); padding:12px 16px; margin:14px 0}
.simu h3{margin:0 0 8px!important; font:700 1.15rem var(--f-titre); color:var(--bleu)}
.simu-grid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px 18px}
@media (max-width:640px){ .simu-grid{grid-template-columns:1fr} }
.simu-grid label{display:flex; flex-direction:column; gap:4px; font-weight:600; font-size:.92rem}
.simu-grid output{font:700 1rem var(--f-titre); color:var(--bleu)}
.simu-grid input[type=range]{width:100%; accent-color:var(--bleu)}
.simu-grid select{padding:5px; border:1.5px solid var(--encre-2); background:#fff; font:inherit}
.simu-out{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin:12px 0 8px}
.simu-out div{background:var(--encre); color:#fff; padding:6px 10px}
.simu-out span{display:block; font-size:.78rem; color:#D7DDE2}
.simu-out b{font:700 1.1rem var(--f-titre); color:var(--jaune)}
.simu-out4{grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:760px){ .simu-out,.simu-out4{grid-template-columns:repeat(2,minmax(0,1fr))} }
.simu-verdict{font-weight:700; margin:8px 0 4px}
.simu-verdict.ok{color:var(--vert)} .simu-verdict.ko{color:var(--rouge)}
.simu-defi{margin-top:8px; background:#fff; border:1px dashed var(--bleu); padding:6px 10px}
.simu-defi summary{cursor:pointer; font-weight:600}
.exemple{background:#F6F7F4; border:1px solid var(--trait-fin); padding:6px 16px; margin-top:12px}
.exemple h3{font:700 1.05rem var(--f-titre); margin:10px 0 4px}
.remarque{border-left:6px solid var(--jaune); background:var(--jaune-pale); padding:8px 14px; margin:12px 0; max-width:80ch}
.remarque p{margin:.2rem 0}
.quiz{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px}
.quiz-q{border:1.5px solid var(--encre); background:#fff; padding:8px 14px 10px; margin:0}
.quiz-q legend{font-weight:700; padding:0 4px}
.quiz-q label{display:block; padding:3px 0; cursor:pointer}
.quiz-q.is-ok{border-color:var(--vert); background:var(--vert-pale)}
.quiz-q.is-ko{border-color:var(--rouge); background:var(--rouge-pale)}
.quiz-q label.good{font-weight:700; color:var(--vert)}
.quiz-fb{margin:4px 0 0; font-weight:700}
.quiz-q.is-ok .quiz-fb{color:var(--vert)} .quiz-q.is-ko .quiz-fb{color:var(--rouge)}
.quiz-why{margin:2px 0 0; font-size:.9rem}
.quiz-score{display:flex; align-items:center; gap:14px; margin:14px 0 0; font:700 1.3rem var(--f-titre)}
#qz-stars{color:var(--jaune); font-size:1.6rem; letter-spacing:2px}
.jeu{border:2px solid var(--encre); background:#fff; padding:10px 14px; margin:12px 0 0}
.jeu-l{display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; padding:6px 0; border-top:1px solid var(--trait-fin)}
.jeu-l>span{flex:1 1 240px; font-weight:600}
.jeu-l .btn{padding:4px 9px; font-size:.88rem}
.jeu-l .btn.pick-ok{background:var(--vert); border-color:var(--vert); color:#fff}
.jeu-l .btn.pick-ko{background:var(--rouge); border-color:var(--rouge); color:#fff}
.jeu-l .btn.pick-good{outline:3px solid var(--vert); outline-offset:1px}
.jeu-l.is-ok{background:var(--vert-pale)} .jeu-l.is-ko{background:var(--rouge-pale)}
.jeu-fb{min-width:1.5em; font-size:1.1rem} .jeu-l.is-ok .jeu-fb{color:var(--vert)} .jeu-l.is-ko .jeu-fb{color:var(--rouge)}
.jeu-score{display:flex; align-items:center; gap:12px; font:700 1.2rem var(--f-titre); margin:8px 0 0}
.jeu-score .btn{font-size:.9rem; padding:5px 12px}
.cartes{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin:8px 0 14px}
.carte{display:flex; flex-direction:column; gap:6px; align-items:flex-start; text-align:left; min-height:96px; padding:12px 14px; border:2px solid var(--encre); border-left-width:8px; background:var(--jaune-pale); font:inherit; cursor:pointer}
.carte.c-info{border-left-color:var(--bleu)} .carte.c-ener{border-left-color:var(--orange)}
.carte b{font:700 1.15rem var(--f-titre); letter-spacing:.03em}
.carte.c-info b{color:var(--bleu)} .carte.c-ener b{color:var(--orange)}
.carte .dos{display:none; font-size:.93rem}
.carte .dos i{display:block; margin-top:4px; font-style:normal; color:var(--encre-2)}
.carte[aria-expanded="true"]{background:#fff}
.carte[aria-expanded="true"] .dos{display:block}
.carte[aria-expanded="false"]::after{content:"Clique pour retourner"; font-size:.8rem; color:var(--encre-2)}
.cours-foot{display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 0}
.cours-foot .small{align-self:center}
@media print{
  body.cours-page #home{display:block!important; padding:0}
  .no-print,.cours-nav,.cours-foot{display:none!important}
  .quiz-why[hidden]{display:block!important}
  .carte .dos{display:block!important}
  .carte::after{display:none!important}
}
"""


# ============================================================ COURS 1 — LA CHAÎNE FONCTIONNELLE (niveau 1), interactif
# L'animation vient de src/portail-anime.html : schéma et script extraits, remplacements vérifiés.
def portail_source():
    src = PORTAIL.read_text(encoding="utf-8")
    markup = re.search(r'<div class="app">.*?\n</div>\n(?=\n<script>)', src, re.S).group(0)
    script = re.search(r'<script>\n\(function \(\) \{\n  "use strict";\n(.*)\n\}\)\(\);\n</script>', src, re.S).group(1)
    # classes et titres : pas de conflit avec la classe « part » du gabarit, titres sous le h1 du cours
    markup, n = re.subn(r' class="part"', ' class="cp-part"', markup)
    assert n == 9, n
    markup = sub_once(markup, r"<h1>Portail automatique : la chaîne fonctionnelle</h1>",
                      '<h3 class="cp-h">Portail automatique : la chaîne fonctionnelle</h3>')
    markup = sub_once(markup, r'<h2 id="t-chain">Chaîne fonctionnelle</h2>', '<h3 id="t-chain">Chaîne fonctionnelle</h3>')
    markup = sub_once(markup, r'<h2 id="ex-title"></h2>', '<h3 id="ex-title"></h3>')
    # bouton « Plein écran » hors du groupe des scénarios (le script lie chaque bouton de ce groupe à un scénario)
    markup = sub_once(markup, r'aria-selected="false">2\. Fermeture et sécurité</button>\n  </div>\n</header>',
                      'aria-selected="false">2. Fermeture et sécurité</button>\n  </div>\n  '
                      '<button type="button" class="cp-fs" id="cp-fs" aria-pressed="false" title="Afficher '
                      "l'animation sur tout l'écran (vidéoprojecteur)\">Plein écran</button>\n</header>")
    script = sub_once(script, r'\$\$\("#scene \.part, #scene \.in-cell"\)', '$$("#scene .cp-part, #scene .in-cell")')
    # raccourcis clavier limités à l'animation (la page du cours contient d'autres commandes)
    script = sub_once(script, r'document\.addEventListener\("keydown", function \(e\) \{',
                      'root.addEventListener("keydown", function (e) {')
    return markup, script


CARTES_PORTAIL = [
    ("info", "ACQUÉRIR", "Prélever une information sur l'utilisateur (consigne) ou sur le système (état).",
     "Portail : antenne et récepteur radio, capteurs de fin de course, cellules photoélectriques."),
    ("info", "TRAITER", "Élaborer une décision à partir des informations acquises.",
     "Portail : carte électronique (microcontrôleur)."),
    ("info", "COMMUNIQUER", "Transmettre des ordres à la chaîne d'énergie et des informations à l'utilisateur.",
     "Portail : carte électronique (ordres), feu clignotant (message)."),
    ("ener", "ALIMENTER", "Fournir au système l'énergie dont il a besoin.",
     "Portail : réseau 230 V, transformateur 230 V → 24 V."),
    ("ener", "DISTRIBUER", "Autoriser ou non le passage de l'énergie, et en choisir le sens, sur ordre.",
     "Portail : relais de la carte de puissance."),
    ("ener", "CONVERTIR", "Changer la forme de l'énergie.",
     "Portail : moteur électrique (électrique → mécanique de rotation)."),
    ("ener", "TRANSMETTRE", "Acheminer l'énergie mécanique jusqu'à l'objet à déplacer, en adaptant le mouvement.",
     "Portail : réducteur, pignon et crémaillère (rotation → translation)."),
    ("ener", "AGIR", "Réaliser l'action attendue sur la matière d'œuvre.",
     "Portail : le portail coulisse, de « fermé » à « ouvert »."),
]
JEU_CIRCULE = [("Le signal radio émis par la télécommande", "info"), ("Le courant du réseau 230 V", "ener"),
               ("L'ordre « ouvrir » envoyé au relais", "info"), ("La rotation de l'arbre du moteur", "ener"),
               ("Le signal du capteur de fin de course", "info"), ("La translation du portail sur son rail", "ener"),
               ("Le clignotement du feu", "info"), ("Le courant 24 V qui traverse le relais vers le moteur", "ener")]
FONCTIONS = [("acquerir", "Acquérir"), ("traiter", "Traiter"), ("communiquer", "Communiquer"),
             ("alimenter", "Alimenter"), ("distribuer", "Distribuer"), ("convertir", "Convertir"),
             ("transmettre", "Transmettre"), ("agir", "Agir")]
JEU_COMPOSANTS = [("Antenne et récepteur radio", "acquerir"), ("Cellules photoélectriques", "acquerir"),
                  ("Microcontrôleur de la carte électronique", "traiter"), ("Feu clignotant", "communiquer"),
                  ("Transformateur 230 V → 24 V", "alimenter"), ("Relais de la carte de puissance", "distribuer"),
                  ("Moteur électrique", "convertir"), ("Réducteur", "transmettre"),
                  ("Pignon et crémaillère", "transmettre"), ("Portail coulissant", "agir")]
QUIZ_1 = [
    ("Dans le portail, l'antenne et le récepteur radio réalisent la fonction…", ["Acquérir", "Traiter", "Distribuer"], 0,
     "Ils captent l'onde radio et la transforment en un signal électrique exploitable par la carte : c'est une "
     "acquisition."),
    ("Quel bloc de la chaîne d'énergie reçoit les ordres de la chaîne d'information ?",
     ["Alimenter", "Distribuer", "Convertir"], 1,
     "Le relais (Distribuer) est le seul bloc de la chaîne d'énergie qui reçoit des ordres : il laisse passer ou non "
     "l'énergie, dans un sens ou dans l'autre."),
    ("Le moteur électrique transforme l'énergie électrique en…",
     ["énergie mécanique de rotation", "énergie mécanique de translation", "information"], 0,
     "Convertir, c'est changer la forme de l'énergie : électrique → mécanique de rotation. C'est ensuite la "
     "transmission qui produit la translation."),
    ("Le système pignon-crémaillère…", ["convertit l'énergie électrique", "transforme une rotation en translation",
                                        "acquiert la position du portail"], 1,
     "Il appartient à Transmettre : la rotation du pignon devient la translation de la crémaillère fixée au portail."),
    ("À quoi sert le capteur de fin de course ?",
     ["À alimenter le moteur", "À rendre compte que le portail est arrivé en bout de course",
      "À faire clignoter le feu"], 1,
     "C'est un compte rendu : il remonte vers la chaîne d'information, qui ordonne alors l'arrêt."),
    ("Un ballon coupe le faisceau des cellules pendant la fermeture. Que fait la carte électronique ?",
     ["Rien : le portail continue", "Elle arrête le moteur, puis fait rouvrir le portail", "Elle coupe le réseau 230 V"],
     1, "La sécurité passe d'abord : arrêt immédiat, puis réouverture. Sans capteurs, la chaîne d'énergie poursuivrait "
        "aveuglément son mouvement."),
    ("Pour fermer le portail plutôt que l'ouvrir, qu'est-ce qui change dans la chaîne d'énergie ?",
     ["Les blocs utilisés", "Le sens dans lequel le relais distribue l'énergie", "La tension du réseau"], 1,
     "Les blocs sont les mêmes ; le relais inverse le sens du courant et le moteur tourne dans l'autre sens."),
    ("Le feu clignotant réalise la fonction…", ["Communiquer", "Agir", "Transmettre"], 0,
     "Il prévient l'utilisateur et les passants : c'est un message, rôle de la fonction Communiquer."),
]


def render_cours_portail():
    markup, _ = portail_source()
    cartes = "".join(
        f'<button type="button" class="carte c-{k}" aria-expanded="false"><b>{t}</b><span class="dos">{d}<i>{ex}</i>'
        "</span></button>" for k, t, d, ex in CARTES_PORTAIL)
    s1 = course_section(1, "c1-anim", "Le portail automatique, pas à pas",
                        "<p>Lance l'animation ou avance étape par étape (boutons ◀ ▶ ou flèches du clavier). Deux "
                        "scénarios : l'ouverture, puis la fermeture avec un obstacle. Les blocs de la chaîne "
                        "s'allument à mesure que l'information et l'énergie circulent ; le panneau de droite explique "
                        "chaque étape. Le bouton « Plein écran » adapte l'animation à un vidéoprojecteur.</p>"
                        f'<div class="cp" tabindex="-1">{markup}</div>')
    s2 = course_section(2, "c1-essentiel", "L'essentiel à retenir",
                        "<p>Tout système automatisé se décrit avec deux chaînes reliées : la <b class=\"ti\">chaîne "
                        "d'information</b>, qui <b>décide</b>, et la <b class=\"te\">chaîne d'énergie</b>, qui "
                        "<b>agit</b>.</p><p class=\"cours-defi\">À toi : retourne chaque carte pour lire le rôle de la "
                        f'fonction et les composants du portail qui la réalisent.</p><div class="cartes">{cartes}</div>'
                        '<div class="exemple"><h3>Ce qui relie les deux chaînes</h3><ul>'
                        "<li>Les <b>ordres</b> : la chaîne d'information les envoie au bloc <em>Distribuer</em>.</li>"
                        "<li>Les <b>comptes rendus</b> : les capteurs (fins de course, cellules) renvoient l'état du "
                        "système vers <em>Acquérir</em>.</li></ul><h3>Ce qui circule</h3><ul>"
                        "<li>Dans la chaîne d'information : des <b>informations</b> (signal radio, signal électrique, "
                        "ordres, messages).</li><li>Dans la chaîne d'énergie : de l'<b>énergie</b> qui change de forme "
                        "(électrique, puis mécanique de rotation, puis de translation).</li></ul></div>")
    s3 = course_section(3, "c1-jeux", "Jeux : classe ce qui circule et les composants",
                        "<h3>Information ou énergie ?</h3><p>Pour chaque élément, indique ce qui circule.</p>"
                        + jeu_html(JEU_CIRCULE, [("info", "Information"), ("ener", "Énergie")], "jeu-circule") +
                        "<h3>Quelle fonction réalise ce composant ?</h3>"
                        + jeu_html(JEU_COMPOSANTS, FONCTIONS, "jeu-compo"))
    s4 = quiz_section(4, "c1-quiz", QUIZ_1, "q1_")
    return f"""<div class="cours" id="cours-1">
{course_head("Cours 1", "Niveau 1", "La chaîne fonctionnelle",
             "Comment un portail automatique décide-t-il, puis agit-il ? Suis l'animation : étape par étape, la "
             "chaîne d'information décide et la chaîne d'énergie agit. Environ 25 minutes, avec des cartes à "
             "retourner, deux jeux et un quiz.")}
{course_nav([("c1-anim", "L'animation"), ("c1-essentiel", "L'essentiel"), ("c1-jeux", "Jeux"), ("c1-quiz", "Quiz")])}
{s1}{s2}{s3}{s4}
<div class="cours-foot no-print"><a class="btn" href="?ex=chaines-information-energie">S'entraîner : Exercice 1.1</a>
<a class="btn ghost" href="?ex=cours-chaine-energie">Cours 2 : chaîne d'énergie</a>
<button type="button" class="btn ghost cours-print">Imprimer le cours</button>
<a class="btn ghost" href="?">{HOUSE} Retour à l'accueil</a></div>
</div>"""


def cours_portail_js():
    _, script = portail_source()
    body = "\n".join("  " + l if l else l for l in script.split("\n"))
    return r"""
  function initCoursPortail(home) {
    var root = home.querySelector(".cp");
    (function () {
      "use strict";
""" + body + r"""
    })();
    // plein écran (vidéoprojecteur) : la mise en page d'origine, ajustée à la hauteur de l'écran
    var fs = root.querySelector("#cp-fs");
    function setFull(on) {
      root.classList.toggle("cp-full", on);
      document.body.classList.toggle("cp-full-open", on);
      fs.setAttribute("aria-pressed", on ? "true" : "false");
      fs.textContent = on ? "Quitter le plein écran" : "Plein écran";
      try {
        if (on && root.requestFullscreen && !document.fullscreenElement) root.requestFullscreen().catch(function () {});
        if (!on && document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {});
      } catch (e) { /* plein écran du navigateur refusé : la vue occupe tout de même la fenêtre */ }
    }
    fs.addEventListener("click", function () { setFull(!root.classList.contains("cp-full")); });
    document.addEventListener("fullscreenchange", function () {
      if (!document.fullscreenElement && root.classList.contains("cp-full")) setFull(false);
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && root.classList.contains("cp-full")) setFull(false); });
    // un clic sur l'animation lui donne le focus : les flèches et la barre d'espace la pilotent
    root.addEventListener("click", function (e) {
      if (!e.target.closest("button, select, input, label, a")) root.focus({ preventScroll: true });
    });
    initCartes(home);
    Array.prototype.forEach.call(home.querySelectorAll(".jeu"), initJeu);
    initQuiz(home);
    home.querySelector(".cours-print").addEventListener("click", function () { window.print(); });
  }
"""


PORTAIL_CSS = """
/* ---------- cours 1 : animation du portail (style de src/portail-anime.html, préfixé par .cp) ---------- */
body.page-cours-chaine-fonctionnelle .home-inner{max-width:1320px}
body.page-cours-chaine-fonctionnelle .part-body>p{max-width:86ch}
.cp{margin:6px 0 4px}
.cp:focus{outline:none}
.cp select{font:inherit; color:inherit}
.cp .app{display:flex; flex-direction:column; gap:10px}
.cp .topbar{display:flex; flex-wrap:wrap; align-items:stretch; background:var(--papier); border:2px solid var(--encre); border-left:10px solid var(--jaune); min-height:44px}
.cp .cp-h{margin:0; padding:7px 14px; font:700 clamp(1.05rem,1.5vw,1.5rem)/1.15 var(--f-titre); letter-spacing:-.01em;
  flex:1 1 260px; min-width:0; align-self:center}
.cp .scenarios{display:flex; flex:0 1 auto; flex-wrap:wrap}
.cp .scenarios button{border:0; border-left:2px solid var(--encre); background:#F4F5F2; padding:6px 16px; font:700 .95rem var(--f-titre); cursor:pointer; white-space:nowrap}
.cp .scenarios button[aria-selected="true"]{background:var(--encre); color:var(--jaune)}
.cp .cp-fs{border:0; border-left:2px solid var(--encre); background:var(--jaune); color:var(--encre); padding:6px 14px; font:700 .95rem var(--f-titre); cursor:pointer; white-space:nowrap}
.cp .cp-fs:hover{background:#FFD447}
@media (max-width:640px){ .cp .scenarios{flex:1 1 100%} .cp .scenarios button{flex:1 1 auto; border-top:2px solid var(--encre); padding:6px 10px} .cp .scenarios button:first-child{border-left:0}
  .cp .cp-fs{flex:1 1 100%; border-left:0; border-top:2px solid var(--encre)} }
.cp .main{display:grid; grid-template-columns:minmax(0,1fr); gap:10px}
@media (min-width:1000px){ .cp .main{grid-template-columns:minmax(0,1fr) minmax(320px,370px)} }
.cp .visuals{display:flex; flex-direction:column; gap:10px; min-width:0}
.cp .side{display:flex; flex-direction:column; gap:10px; min-width:0}
.cp .card{background:var(--papier); border:2px solid var(--encre)}
.cp .scene-card{padding:6px}
.cp .scene-card svg{display:block; width:100%; height:auto}
.cp .chain-card{padding:4px 6px 6px}
.cp .chain-head{display:flex; align-items:baseline; gap:6px 16px; flex-wrap:wrap; padding:0 4px 4px; min-height:22px}
.cp .chain-head h3{margin:0; font:700 1.05rem var(--f-titre)}
.cp .legend{display:flex; gap:14px; flex-wrap:wrap; font-size:.8rem; color:var(--encre-2)}
.cp .legend span{display:inline-flex; align-items:center; gap:6px}
.cp .legend i{display:inline-block; width:24px; height:0; border-top:3px solid}
.cp .chain-wrap{overflow-x:auto}
.cp .chain-wrap svg{display:block; width:100%; min-width:640px; height:auto}
.cp .explain{flex:1 1 auto; border-left:8px solid var(--trait); padding:12px 16px 14px; display:flex; flex-direction:column; transition:border-color .3s;
  font-size:clamp(15px,1.05vw,19px); line-height:1.5}
.cp .explain.k-info{border-left-color:var(--bleu)} .cp .explain.k-ener{border-left-color:var(--orange)}
.cp .explain.k-sys{border-left-color:var(--jaune)} .cp .explain.k-both{border-left-color:var(--encre)}
.cp .ex-head{display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:4px}
.cp .ex-step{font:700 .85em var(--f-titre); background:var(--encre); color:#fff; padding:2px 8px}
.cp .chip{font:700 .78em var(--f-titre); padding:2px 8px; border:1.5px solid}
.cp .chip.info{color:var(--bleu); border-color:var(--bleu); background:var(--bleu-pale)}
.cp .chip.ener{color:var(--orange); border-color:var(--orange); background:var(--orange-pale)}
.cp .chip.sys{color:var(--encre); border-color:var(--encre); background:var(--jaune-pale)}
.cp .explain h3{margin:2px 0 6px; font:700 1.38em/1.15 var(--f-titre)}
.cp .ex-text p{margin:.3em 0} .cp .ex-text ul{margin:.25em 0; padding-left:1.15em} .cp .ex-text li{margin:.2em 0}
.ti{color:var(--bleu)} .te{color:var(--orange)}
.cp .fiche{margin:auto 0 0; padding-top:10px; display:grid; grid-template-columns:auto 1fr; border-top:1px dashed var(--trait); font-size:.88em}
.cp .fiche dt{font:700 .85em/1.9 var(--f-titre); color:var(--encre-2); padding-right:12px; text-transform:uppercase; letter-spacing:.03em}
.cp .fiche dd{margin:0; padding:2px 0; font-weight:600}
.cp .controls{padding:8px 10px; display:flex; flex-direction:column; gap:8px}
.cp .ctl-row{display:flex; gap:6px; flex-wrap:wrap; align-items:center}
.cp .btn{padding:7px 12px; white-space:nowrap}
.cp .btn.ghost:disabled{background:#F2F3F1; color:#9AA2A8}
.cp .btn.play{background:var(--jaune); color:var(--encre); border-color:var(--encre); flex:1 1 8em}
.cp .btn.play:hover{background:#FFD447}
.cp .timeline{display:flex; flex-direction:column; gap:5px}
.cp .dots{display:flex; gap:4px; flex-wrap:wrap}
.cp .dots button{width:28px; height:26px; border:1.5px solid var(--encre); background:#fff; font:700 .8rem var(--f-titre); cursor:pointer; padding:0}
.cp .dots button.d-info{border-bottom:4px solid var(--bleu)} .cp .dots button.d-ener{border-bottom:4px solid var(--orange)}
.cp .dots button.d-sys{border-bottom:4px solid var(--jaune)} .cp .dots button.d-both{border-bottom:4px solid var(--encre)}
.cp .dots button.seen{background:#EEF0EC}
.cp .dots button[aria-current="step"]{background:var(--encre); color:var(--jaune)}
.cp .bar{height:5px; background:var(--trait-fin)} .cp .bar span{display:block; height:100%; width:0; background:var(--jaune)}
.cp .opts{display:flex; gap:6px 14px; flex-wrap:wrap; align-items:center; font-size:.85rem; color:var(--encre-2)}
.cp .opts label{display:inline-flex; gap:6px; align-items:center; cursor:pointer}
.cp .opts select{border:1.5px solid var(--encre-2); background:#fff; padding:3px 4px; color:var(--encre)}
.cp .opts .hint{margin-left:auto}
/* SVG — chaîne */
.cp .blk rect{fill:#fff; stroke-width:2; transition:fill .3s, stroke-width .3s}
.cp .blk.info rect{stroke:var(--bleu)} .cp .blk.ener rect{stroke:var(--orange)} .cp .blk.act rect{stroke:var(--encre); stroke-dasharray:6 4}
.cp .blk text{text-anchor:middle; fill:var(--encre)}
.cp .blk .verb{font:700 16px var(--f-titre); letter-spacing:.04em}
.cp .blk.info .verb{fill:var(--bleu)} .cp .blk.ener .verb{fill:var(--orange)}
.cp .blk .cmp{font:500 12.5px var(--f-texte)}
.cp .blk .frm{font:italic 600 11.5px var(--f-texte); fill:var(--encre-2)}
.cp .blk{transition:opacity .3s}
.cp .focus .blk:not(.on){opacity:.42}
.cp .blk.info.on rect{fill:var(--bleu-pale); stroke-width:4}
.cp .blk.ener.on rect{fill:var(--orange-pale); stroke-width:4}
.cp .blk.act.on rect{fill:var(--jaune-pale); stroke-width:3.5}
.cp .fl{fill:none; stroke-width:2; transition:stroke .3s, stroke-width .3s}
.cp .fl.k-info{stroke:#9DB6D6} .cp .fl.k-ener{stroke:#DDBB8A}
.cp .fl.k-info.on{stroke:var(--bleu); stroke-width:3.2} .cp .fl.k-ener.on{stroke:var(--orange); stroke-width:3.2}
.cp .fl.dash{stroke-dasharray:7 5}
.cp .clab{font:600 12.5px var(--f-texte); fill:var(--encre-2)}
.cp .clab.b{fill:var(--bleu)} .cp .clab.o{fill:var(--orange)}
.cp .rowtitle{font:700 13px var(--f-titre); letter-spacing:.06em}
/* SVG — scène */
.cp .lab{font:600 14px var(--f-texte); fill:var(--encre); paint-order:stroke; stroke:#fff; stroke-width:4px; stroke-linejoin:round}
.cp .lead-line{stroke:#6B7580; stroke-width:1.2; fill:none}
.cp .hide-labels .labels{display:none}
.cp .cp-part{transition:filter .3s}
.cp .cp-part.hl{animation:cp-glow 1.4s ease-in-out infinite}
@keyframes cp-glow{0%,100%{filter:drop-shadow(0 0 2px #F2B705) drop-shadow(0 0 5px #F2B705)}50%{filter:drop-shadow(0 0 4px #F2B705) drop-shadow(0 0 11px #F2B705)}}
.cp .in-cell rect.cell{fill:#F7F8F6; stroke:#A5ADAA; stroke-width:1.5; transition:fill .3s, stroke .3s}
.cp .in-cell.hl rect.cell{fill:var(--jaune-pale); stroke:var(--jaune); stroke-width:3.5}
.cp .in-cell text{font:600 11px var(--f-texte); fill:var(--encre); text-anchor:middle}
.cp .lamp{fill:#C08A2A}
.cp .glow{fill:#F2B705; opacity:0}
.cp .blink .lamp{animation:cp-lamp .6s steps(1) infinite}
.cp .blink .glow{animation:cp-lampglow .6s steps(1) infinite}
@keyframes cp-lamp{0%{fill:#FFB000}50%{fill:#9A6A16}}
@keyframes cp-lampglow{0%{opacity:.55}50%{opacity:0}}
.cp .wave{fill:none; stroke:var(--bleu); stroke-width:3; stroke-linecap:round; opacity:0}
.cp .waves-on .wave{animation:cp-wave 1.2s ease-out infinite}
.cp .waves-on .wave.w2{animation-delay:.2s} .cp .waves-on .wave.w3{animation-delay:.4s}
@keyframes cp-wave{0%{opacity:0}30%{opacity:1}100%{opacity:0}}
.cp #beam{stroke:#E06666; stroke-width:2; stroke-dasharray:6 5; opacity:.75; transition:stroke .2s}
.cp #beam.cut{stroke:var(--rouge); stroke-width:3.5; stroke-dasharray:none; opacity:1}
.cp #s-radio{stroke:var(--bleu); stroke-width:2; stroke-dasharray:4 6; fill:none; opacity:0; transition:opacity .3s}
.cp #s-radio.on{opacity:.8}
.cp #s-power{stroke:#59636C; stroke-width:4; fill:none; transition:stroke .3s}
.cp #s-power.on{stroke:var(--orange)}
.cp #ball{transition:transform 1.3s cubic-bezier(.3,.7,.4,1)}
.cp .ptc-info{fill:var(--bleu); stroke:#fff; stroke-width:1.5}
.cp .ptc-ener{fill:#E98A00; stroke:#fff; stroke-width:1.5}
@media (prefers-reduced-motion:reduce){ .cp .cp-part.hl,.cp .waves-on .wave{animation:none} .cp .cp-part.hl{filter:drop-shadow(0 0 5px #F2B705)} }
/* plein écran : la mise en page d'origine, qui tient dans la hauteur de l'écran */
.cp.cp-full{position:fixed; inset:0; z-index:80; margin:0; background:var(--beton); padding:10px; overflow:auto; display:flex; flex-direction:column}
.cp.cp-full .app{flex:1 1 auto; min-height:0}
body.cp-full-open{overflow:hidden}
body.cp-full-open .banner,body.cp-full-open .rail{display:none}
@media (min-width:900px) and (min-height:460px) and (orientation:landscape){
  .cp.cp-full{overflow:hidden}
  .cp.cp-full .main{flex:1 1 auto; min-height:0;
    grid-template-columns:min(calc((100vh - 150px) * 1.4545 + 16px), calc(100vw - 360px)) minmax(330px,1fr);
    grid-template-columns:min(calc((100dvh - 150px) * 1.4545 + 16px), calc(100vw - 360px)) minmax(330px,1fr)}
  .cp.cp-full .side{min-height:0}
  .cp.cp-full .explain{min-height:0; overflow-y:auto; font-size:clamp(15px,1.05vw,20px)}
  .cp.cp-full .chain-wrap{overflow:visible}
  .cp.cp-full .chain-wrap svg{min-width:0}
}
@media (min-width:900px) and (max-width:1180px) and (min-height:460px) and (orientation:landscape){
  .cp.cp-full .main{grid-template-columns:min(calc((100vh - 150px) * 1.4545 + 16px), calc(100vw - 440px)) minmax(420px,1fr);
    grid-template-columns:min(calc((100dvh - 150px) * 1.4545 + 16px), calc(100vw - 440px)) minmax(420px,1fr)}
  .cp.cp-full .explain{font-size:14.5px}
}
@media print{ .cp .controls,.cp .cp-fs{display:none!important} .cp .chain-wrap svg{min-width:0} }
"""


# ============================================================ COURS 2 — CHAÎNE D'ÉNERGIE DES PRODUITS (niveau 2), interactif
# Source : le cours Word « Chaîne d'énergie des produits ». Les tableaux de composants du Word deviennent des fiches
# (photos et symboles découpés par outils/preparer-images.sh) ; figures 1 et 2 redessinées et animées ; simulateurs.
def img(name, alt="", cls=""):
    src, w, h = png(name)
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{src}" alt="{esc(alt)}" width="{w}" height="{h}">'


OBJECTIFS = ["Identifier les constituants de la chaîne de puissance d'un produit mécatronique.",
             "Distinguer les fonctions Alimenter/Stocker, Distribuer, Convertir, Transmettre et Agir.",
             "Associer à chaque fonction ses principaux composants et symboles.",
             "Calculer les puissances et le rendement le long de la chaîne d'énergie."]
COMPETENCES = [("CO3.1", "Identifier et caractériser les fonctions et les constituants d'un produit ainsi que ses "
                         "entrées/sorties.", 2),
               ("CO3.2", "Identifier et caractériser l'agencement matériel et/ou logiciel d'un produit.", 2),
               ("CO4.2", "Décrire le fonctionnement et/ou l'exploitation d'un produit en utilisant l'outil de "
                         "description le plus pertinent.", 2)]
PREREQUIS = ["Notion de chaîne d'énergie et de chaîne d'information.", "Lecture de diagrammes SysML (blocs, flux)."]

# fiches : (clé de la photo, nom, fonction, caractéristiques principales, symbole ou None, fonctionnement ou None)
FICHES = {
    "alim": [
        ("monophase", "Réseau monophasé", "Alimenter en énergie électrique à partir du réseau de distribution.",
         "Alternatif monophasé ; <i>U</i> = 230 V ; fréquence 50 Hz : <i>f</i> = 1/<i>T</i> ; période <i>T</i> = 20 ms.",
         "ce-sy-monophase", None),
        ("triphase", "Réseau triphasé", "Alimenter en énergie électrique à partir du réseau de distribution.",
         "Alternatif triphasé 230/400 V – 50 Hz ; <i>V</i> : tension entre phase et neutre = 230 V ; <i>U</i> : "
         "tension entre phases = 400 V.", "ce-sy-triphase", None),
        ("batterie", "Batterie", "Alimenter en énergie électrique préalablement stockée.",
         "Continu ; tension <i>U</i> en V et capacité <i>Q</i> en Ah ; <i>Q</i> = <i>I</i> × <i>t</i> avec <i>I</i> "
         "en A et <i>t</i> en h.", "ce-sy-batterie", None),
        ("renouvelables", "Énergies renouvelables", "Alimenter localement en énergie électrique à partir d'une "
         "source renouvelable (soleil, vent).", "Photovoltaïque (PV) : continu ; éolien : continu ou alternatif ; "
         "production variable suivant le soleil ou le vent.", "ce-sy-renouvelables", None),
        ("chargeur", "Chargeur de batterie et régulateur de charge", "Charger les batteries à partir du réseau de "
         "distribution ou d'énergies renouvelables.", "Une tension continue fixe en sortie. Le régulateur de charge "
         "permet de charger la batterie ou d'utiliser son énergie pour alimenter le produit.", "ce-sy-chargeur", None),
        ("onduleur", "Onduleur et transformateur", "Adapter la tension de sortie.",
         "Sortie en alternatif, constante en valeur et en fréquence. L'onduleur fabrique de l'alternatif à partir du "
         "continu d'une batterie ; le transformateur change la valeur d'une tension alternative (<i>U</i><sub>1</sub> "
         "→ <i>U</i><sub>2</sub>, même fréquence <i>f</i>).", "ce-sy-onduleur", None),
    ],
    "dist": [
        ("disjoncteur", "Disjoncteur et relais thermique", "Protéger contre les surcharges et/ou les courts-circuits.",
         "Courant de déclenchement thermique <i>I</i><sub>r</sub> ; courant de déclenchement magnétique "
         "<i>I</i><sub>m</sub>.", "ce-sy-disjoncteur", None),
        ("fusibles", "Fusibles (dans un porte-fusible)", "Protéger contre les courts-circuits.",
         "Type (aM, gG — anciennement gI —, instantané, retardé…) ; calibre en A ; taille ; pouvoir de coupure.",
         "ce-sy-fusible", None),
        ("interrupteur", "Interrupteur", "Commuter manuellement l'énergie électrique.",
         "Nombre de pôles ; intensité nominale ; pouvoir de commutation.", "ce-sy-interrupteur", None),
        ("relais", "Relais et contacteur", "Commuter à distance l'énergie électrique.",
         "Tension de la bobine ; tension et courant assignés des contacts ; nombre et type de contacts.",
         "ce-sy-relais", None),
        ("modulateur", "Modulateur d'énergie (carte de puissance)", "Moduler l'énergie pour l'adapter au récepteur en "
         "fonction de la commande.", "Tension d'entrée ; puissance du récepteur associé ; plage de variation (vitesse, "
         "fréquence, tension…). Symboles : redresseur commandé (alternatif → continu réglable), hacheur (continu → "
         "continu réglable), gradateur ou MLI (alternatif → alternatif réglable).", "ce-sy-modulateur", None),
    ],
    "conv": [
        ("moteur-cc", "Moteur à courant continu", "Convertir l'énergie électrique reçue en énergie mécanique.",
         "Tension <i>U</i> en V ; intensité <i>I</i> en A ; puissance <i>P</i> en W ; couple <i>C</i> en N·m ; "
         "fréquence de rotation <i>N</i> en tr/min.", "ce-sy-moteur-cc",
         "Inversion du sens de rotation par inversion des polarités ; variation de la vitesse de rotation par "
         "variation de la tension moyenne reçue."),
        ("moteur-asynchrone", "Moteur asynchrone", "Convertir l'énergie électrique reçue en énergie mécanique.",
         "Tension <i>U</i> en V ; intensité <i>I</i> en A ; puissance <i>P</i> en W ; couple <i>C</i> en N·m ; "
         "fréquence de rotation <i>N</i> en tr/min.", "ce-sy-moteur-asynchrone",
         "Inversion du sens de rotation par inversion de 2 des 3 phases ; variation de la vitesse de rotation par "
         "modulation de la tension d'alimentation ou par MLI."),
        ("moteur-brushless", "Moteur brushless (sans balais)", "Convertir l'énergie électrique reçue en énergie "
         "mécanique.", "Tension <i>U</i> en V ; intensité <i>I</i> en A ; puissance <i>P</i> en W ; couple <i>C</i> "
         "en N·m ; fréquence de rotation <i>N</i> en tr/min.", "ce-sy-moteur-brushless",
         "Inversion du sens de rotation par inversion de 2 des 3 phases ; variation de la vitesse de rotation par "
         "modulation de la tension d'alimentation et/ou par MLI ; peut atteindre des vitesses de rotation élevées."),
        ("resistance", "Résistance", "Convertir l'énergie électrique reçue en énergie thermique.",
         "Tension <i>U</i> en V ; intensité <i>I</i> en A ; puissance <i>P</i> en W ; résistance <i>R</i> en Ω.",
         "ce-sy-resistance", "Variation de la température de chauffe par gradation de la tension ou par trains "
         "d'ondes."),
        ("eclairage", "Éclairage", "Convertir l'énergie électrique reçue en énergie lumineuse.",
         "Tension <i>U</i> en V ; intensité <i>I</i> en A ; puissance <i>P</i> en W ; éclairement.", "ce-sy-eclairage",
         "Variation de l'éclairage par gradation de la tension."),
    ],
    "trans": [
        ("accouplement", "Accouplement (permanent ou non)", "Transmettre la vitesse et le couple entre deux arbres.",
         "Angle ou décalage entre les axes ; <i>N</i><sub>s</sub> = <i>N</i><sub>e</sub>.", "ce-sy-accouplement", None),
        ("engrenage", "Engrenage droit à axes parallèles", "Adapter l'énergie mécanique de rotation en modifiant sa "
         "vitesse et son couple.", "Rapport de réduction <i>r</i> ; nombre de dents <i>Z</i> ; diamètres primitifs "
         "<i>D</i> ; <i>r</i> = <i>N</i><sub>s</sub> / <i>N</i><sub>e</sub> = <i>Z</i><sub>e</sub> / "
         "<i>Z</i><sub>s</sub>.", "ce-sy-engrenage", None),
        ("train", "Train d'engrenages", "Adapter l'énergie mécanique de rotation en modifiant sa vitesse et son "
         "couple, tout en déplaçant l'axe de rotation.", "Rapport de réduction <i>r</i> ; nombres de dents <i>Z</i> ; "
         "diamètres primitifs <i>D</i> ; <i>r</i> = <i>N</i><sub>s</sub> / <i>N</i><sub>e</sub> = produit des nombres "
         "de dents des roues menantes / produit des nombres de dents des roues menées.", "ce-sy-train", None),
        ("poulies", "Pignons et chaîne, poulies et courroie", "Adapter l'énergie mécanique de rotation en modifiant sa "
         "vitesse et son couple, tout en déplaçant l'axe de rotation.", "Diamètres primitifs des deux roues : "
         "<i>D</i><sub>1</sub> (roue menante, le pignon) et <i>D</i><sub>2</sub> (roue menée) ; <i>r</i> = "
         "<i>N</i><sub>s</sub> / <i>N</i><sub>e</sub> = <i>D</i><sub>1</sub> / <i>D</i><sub>2</sub>.",
         "ce-sy-poulies", None),
        ("cremaillere", "Pignon et crémaillère", "Transformer l'énergie mécanique de rotation en énergie mécanique de "
         "translation.", "Diamètre primitif de la roue <i>D</i> ; <i>V</i><sub>s</sub> = <i>ω</i><sub>e</sub> × "
         "<i>R</i> ; <i>ω</i><sub>e</sub> = 2π <i>N</i><sub>e</sub> / 60 avec <i>N</i><sub>e</sub> en tr/min ; "
         "<i>R</i> = rayon de la roue dentée.", "ce-sy-cremaillere", None),
        ("vis-ecrou", "Système vis-écrou", "Transformer l'énergie mécanique de rotation en énergie mécanique de "
         "translation.", "Pas de la vis <i>p</i> ; <i>V</i><sub>s</sub> = <i>p</i> × <i>N</i><sub>e</sub>.",
         "ce-sy-vis-ecrou", None),
        ("roue-vis", "Roue et vis sans fin", "Adapter l'énergie mécanique en modifiant sa vitesse, son couple et sa "
         "direction (axes orthogonaux).", "Nombre de filets de la vis ; <i>r</i> = <i>N</i><sub>s</sub> / "
         "<i>N</i><sub>e</sub> = nombre de filets de la vis / nombre de dents de la roue <i>Z</i><sub>2</sub>.",
         "ce-sy-roue-vis", None),
        ("echangeur", "Échangeur thermique", "Transmettre la chaleur d'un fluide à un autre sans aucun contact entre "
         "les deux.", "Débit en m³/h ; surface d'échange en m².", "ce-sy-echangeur", None),
        ("reflecteur", "Réflecteur de lumière", "Transmettre le maximum de luminosité.",
         "Forme et matière du réflecteur.", None, None),
    ],
}


def catalogue(cle, titre):
    items = FICHES[cle]
    btns = "".join(f'<button type="button" class="cata-it" data-fiche="{k}" aria-pressed="false">'
                   f'{img("ce-ph-" + k)}<span>{n}</span></button>' for k, n, *_r in items)
    fiches = []
    for k, n, fct, car, sy, fon in items:
        sym = (f'<figure class="fc-sy">{img(sy, "Symbole : " + n)}<figcaption>Symbole</figcaption></figure>' if sy
               else '<figure class="fc-sy fc-nosy"><span>Pas de symbole normalisé</span><figcaption>Symbole</figcaption></figure>')
        fiches.append(
            f'<article class="fiche-c" data-fiche="{k}" hidden><h4>{n}</h4><div class="fc-grid">'
            f'<figure class="fc-ph"><img alt="{esc(n)}"></figure><dl><dt>Fonction</dt><dd>{fct}</dd>'
            f'<dt>Caractéristiques principales</dt><dd>{car}</dd>'
            + (f"<dt>Fonctionnement</dt><dd>{fon}</dd>" if fon else "") + f"</dl>{sym}</div></article>")
    return (f'<div class="cata" data-cata="{cle}"><p class="cours-defi">À toi : clique sur chaque composant pour '
            f'ouvrir sa fiche.</p><div class="cata-list" role="group" aria-label="{titre}">{btns}</div>'
            f'<div class="cata-fiches">{"".join(fiches)}</div></div>')


# ---------- figure 1 : chaînes de puissance et d'information d'une trottinette (redessinée, flux cliquables)
F1_FLUX = [
    ("consignes", "Consignes", "info", "M160 150H328",
     "<b>Consignes</b> : l'utilisateur agit sur l'accélérateur ou sur le frein. La chaîne d'information reçoit ces "
     "consignes."),
    ("infos", "Informations restituées", "info", "M570 128H684V58H95V118",
     "<b>Informations restituées</b> : la chaîne d'information renseigne l'utilisateur sur l'état de la trottinette "
     "(vitesse, charge de la batterie…)."),
    ("commandes", "Commandes", "info", "M570 160H650V204H500V250",
     "<b>Commandes</b> : la chaîne d'information commande la chaîne de puissance, c'est-à-dire l'énergie à envoyer "
     "au moteur pour accélérer ou ralentir."),
    ("etats", "États de la trottinette", "info", "M640 268H704V230H300V172H328",
     "<b>États de la trottinette</b> : la chaîne de puissance renvoie son état à la chaîne d'information (comptes "
     "rendus des capteurs)."),
    ("entrante", "Puissance entrante", "ener", "M160 290H398",
     "<b>Puissance entrante</b> : le chargeur, branché sur le réseau, recharge la batterie : l'énergie est stockée "
     "puis embarquée."),
    ("utile", "Puissance utile", "ener", "M640 290H788",
     "<b>Puissance utile</b> : elle fait avancer la trottinette, qui passe de la position 1 à la position 2."),
]


def figure_trottinette():
    paths = "".join(f'<path id="f1-{k}" class="f1-fl k-{c}" data-k="k-{c}" d="{d}"/>' for k, _n, c, d, _t in F1_FLUX)
    btns = "".join(f'<button type="button" class="ce-fb ce-f1-b k-{c}" data-f="f1-{k}" data-t="{esc(t)}" '
                   f'aria-pressed="false">{n}</button>' for k, n, c, _d, t in F1_FLUX)
    def box(x, y, w, h, cls, lines):
        ty = y + h / 2 - (len(lines) - 1) * 9 + 5
        return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>' +
                "".join(f'<text class="bx-t" x="{x + w / 2}" y="{ty + i * 18}" text-anchor="middle">{l}</text>'
                        for i, l in enumerate(lines)))
    lab = ('<text class="fl-l i" x="244" y="142" text-anchor="middle">consignes</text>'
           '<text class="fl-l i" x="390" y="52" text-anchor="middle">informations restituées</text>'
           '<text class="fl-l i" x="604" y="196" text-anchor="middle">commandes</text>'
           '<text class="fl-l i" x="390" y="248" text-anchor="middle">états de la trottinette</text>'
           '<text class="fl-l e" x="280" y="282" text-anchor="middle">puissance entrante</text>'
           '<text class="fl-l e" x="714" y="282" text-anchor="middle">puissance utile</text>')
    return (
        f'<div class="ce-fig"><div class="ce-fbtns" role="group" aria-label="Flux de la trottinette">{btns}</div>'
        '<svg class="ce-svg" id="ce-f1" viewBox="0 0 1000 430" role="img" aria-labelledby="ce-f1-t">'
        "<title id=\"ce-f1-t\">Chaînes de puissance et d'information d'une trottinette électrique : l'utilisateur donne "
        "des consignes à la chaîne d'information, qui commande la chaîne de puissance ; le chargeur de batterie fournit "
        "la puissance entrante ; la puissance utile fait avancer la trottinette de la position 1 à la position 2.</title>"
        '<defs><marker id="f1-ai" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0 0L10 5L0 10Z" fill="#1F5FA8"/></marker><marker id="f1-ae" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#B26A00"/></marker>'
        '<marker id="f1-am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0 0L10 5L0 10Z" fill="#1B7A43"/></marker></defs>'
        '<rect class="bx-sys" x="232" y="30" width="512" height="372" rx="6"/>'
        '<text class="bx-cap" x="488" y="392" text-anchor="middle">Trottinette électrique</text>'
        + box(30, 124, 130, 52, "bx-u", ["Utilisateur"]) + box(30, 262, 130, 56, "bx-u", ["Chargeur", "de batterie"])
        + box(330, 106, 240, 72, "bx-i", ["Chaîne d'information", "de la trottinette"])
        + box(400, 250, 240, 72, "bx-e", ["Chaîne de puissance", "de la trottinette"])
        + box(790, 254, 180, 72, "bx-a", ["Faire avancer", "la trottinette"])
        + box(800, 150, 160, 50, "bx-mo", ["Trottinette en", "position 1"])
        + box(800, 368, 160, 50, "bx-mo", ["Trottinette en", "position 2"])
        + '<path class="f1-mo" d="M880 200V250"/><path class="f1-mo" d="M880 326V364"/>'
        + paths + lab + '<g class="ce-ptc"></g></svg>'
        '<p class="ce-ftxt" id="ce-f1-txt" aria-live="polite">Clique sur un flux pour savoir ce qui circule.</p></div>')


# ---------- figure 2 : chaîne de puissance de la trottinette (blocs fonctionnels, flux d'énergie animé)
F2_BLOCS = [
    ("alim", "Alimenter/Stocker", "Batterie",
     "<b>Alimenter</b> en énergie le produit ; cette énergie pouvant être <b>stockée</b>. Trottinette : la batterie "
     "(accumulateur lithium-ion) stocke l'énergie électrique apportée par le chargeur et l'embarque."),
    ("dist", "Distribuer", "Hacheur",
     "<b>Distribuer</b> l'énergie vers les principaux actionneurs, en assurant la sécurité des biens et des personnes "
     "et en adaptant l'énergie : ce sont les <b>préactionneurs</b>. Trottinette : le hacheur dose l'énergie électrique "
     "envoyée au moteur selon la commande de l'accélérateur."),
    ("conv", "Convertir", "Moteur à courant continu",
     "<b>Convertir</b> l'énergie distribuée en énergie utile au fonctionnement du produit : ce sont les "
     "<b>actionneurs</b>. Trottinette : le moteur à courant continu convertit l'énergie électrique en énergie "
     "mécanique de rotation."),
    ("trans", "Transmettre", "Poulie et courroie",
     "<b>Transmettre</b> l'énergie aux organes effecteurs. Trottinette : la poulie et la courroie transmettent la "
     "rotation du moteur à la roue en adaptant la vitesse."),
    ("agir", "Agir", "Roue",
     "<b>Agir</b> en effectuant l'action désirée : ce sont les <b>effecteurs</b>. Trottinette : la roue fait avancer "
     "la trottinette."),
]
F2_PUISS = ["Puissance entrante", "Puissance électrique", "Puissance électrique modulée", "Puissance mécanique",
            "Puissance utile"]


def figure_chaine_puissance():
    xs = [70, 250, 430, 610, 790]
    g = []
    for i, ((k, t, c, d), x) in enumerate(zip(F2_BLOCS, xs)):
        lines = t.split("/")
        ty = 86 - (len(lines) - 1) * 9
        g.append(f'<g class="ce-blk" data-b="{k}" data-t="{esc(d)}" tabindex="0" role="button" aria-label="{esc(t)} : '
                 f'{esc(c)}"><rect x="{x}" y="56" width="140" height="64" rx="5"/>' +
                 "".join(f'<text class="blk-t" x="{x + 70}" y="{ty + j * 18}" text-anchor="middle">'
                         f'{l + ("/" if j < len(lines) - 1 else "")}</text>' for j, l in enumerate(lines)) +
                 f'<text class="blk-c" x="{x + 70}" y="146" text-anchor="middle">{c}</text></g>')
    arrows, labels = [], []
    ends = [(4, 68)] + [(xs[i] + 140, xs[i + 1] - 2) for i in range(4)]
    for i, (a, b) in enumerate(ends):
        arrows.append(f'<path id="c2-p{i}" class="f2-fl" data-k="k-ener" d="M{a} 88H{b}"/>')
        cx = (a + b) / 2 if i else 36
        words = F2_PUISS[i].split(" ")
        lines = [" ".join(words[:1]), " ".join(words[1:])] if len(words) > 1 else words
        labels.append("".join(f'<text class="pw-l" x="{cx}" y="{176 + j * 16}" text-anchor="middle">{w}</text>'
                              for j, w in enumerate(lines)))
    # sortie : puissance utile vers la trottinette
    return (
        '<div class="ce-fig"><div class="ce-fbtns"><button type="button" class="ce-fb k-ener" id="ce-f2-go" '
        'aria-pressed="false">▶ Faire circuler l\'énergie</button><span class="small">Clique sur un bloc pour lire son '
        'rôle.</span></div>'
        '<svg class="ce-svg" id="ce-f2" viewBox="0 0 960 220" role="img" aria-labelledby="ce-f2-t">'
        "<title id=\"ce-f2-t\">Chaîne de puissance d'une trottinette en blocs fonctionnels : alimenter et stocker "
        "(batterie), distribuer (hacheur), convertir (moteur à courant continu), transmettre (poulie et courroie), agir "
        "(roue) ; la puissance entrante devient puissance électrique, puis électrique modulée, mécanique, et enfin "
        "utile.</title><defs><marker id=\"f2-ae\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"5\" "
        'markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#B26A00"/></marker></defs>'
        '<path class="f2-cmd" d="M320 6V52"/><text class="pw-l i" x="330" y="22">commandes (chaîne d\'information)</text>'
        + "".join(arrows) + "".join(g) + "".join(labels) + '<g class="ce-ptc"></g></svg>'
        '<p class="ce-ftxt" id="ce-f2-txt" aria-live="polite">Clique sur un bloc de la chaîne.</p></div>')


# ---------- jeux, quiz et données des simulateurs
JEU_CONVERTIR = [("Moteur à courant continu", "meca"), ("Résistance chauffante", "ther"), ("Lampe", "lum"),
                 ("Alternateur", "elec"), ("Pile", "elec"), ("Cuve d'électrolyse", "chim"),
                 ("Moteur à explosion", "meca"), ("Radiateur électrique", "ther")]
ENERGIES = [("meca", "Mécanique"), ("elec", "Électrique"), ("ther", "Thermique"), ("lum", "Lumineuse"),
            ("chim", "Chimique")]
JEU_SYNTHESE = [("Batterie lithium-ion", "alim"), ("Réseau triphasé 230/400 V", "alim"), ("Hacheur", "dist"),
                ("Contacteur", "dist"), ("Disjoncteur", "dist"), ("Moteur brushless", "conv"),
                ("Résistance chauffante", "conv"), ("Réducteur à engrenages", "trans"), ("Pignon et crémaillère", "trans"),
                ("Échangeur thermique", "trans"), ("Roue de trottinette", "agir"), ("Four de traitement thermique", "agir")]
FONCTIONS_E = [("alim", "Alimenter"), ("dist", "Distribuer"), ("conv", "Convertir"), ("trans", "Transmettre"),
               ("agir", "Agir")]
PUISSANCES = [("Télévision", 100), ("Vélo électrique", 250), ("Radiateur électrique", 2e3), ("Voiture citadine", 75e3),
              ("Camion semi-remorque", 350e3), ("Éolienne", 2e6), ("Train", 10e6), ("Avion", 80e6),
              ("Centrale nucléaire", 1e9)]
RENDEMENTS = [("Thermique", "Moteur à explosion", "Mécanique", 40), ("Thermique", "Turbine à vapeur", "Mécanique", 45),
              ("Thermique", "Chaudière", "Thermique", 80), ("Mécanique", "Alternateur", "Électrique", 95),
              ("Mécanique", "Dynamo", "Électrique", 90), ("Chimique", "Pile", "Électrique", 50),
              ("Chimique", "Accumulateur", "Électrique", 70), ("Électrique", "Moteur électrique", "Mécanique", 90),
              ("Électrique", "Radiateur", "Thermique", 100), ("Électrique", "Lampe à filament", "Lumineuse", 3),
              ("Électrique", "Cuve d'électrolyse", "Chimique", 70)]
EFFORT_FLUX = [("trans", "Mécanique de translation", "Force <i>F</i> en N (newton)", "Vitesse <i>v</i> en m/s",
                "<i>P</i> = <i>F</i> × <i>v</i>", ("F", "N", 500), ("v", "m/s", 2)),
               ("rot", "Mécanique de rotation", "Couple <i>C</i> en N·m (newton-mètre)",
                "Vitesse angulaire <i>ω</i> en rad/s", "<i>P</i> = <i>C</i> × <i>ω</i>", ("C", "N·m", 10), ("ω", "rad/s", 100)),
               ("elec", "Électricité", "Tension <i>U</i> en V (volt)", "Courant <i>I</i> en A (ampère)",
                "<i>P</i> = <i>U</i> × <i>I</i>", ("U", "V", 36), ("I", "A", 10)),
               ("hydr", "Hydraulique", "Pression <i>p</i> en Pa (pascal)", "Débit <i>Q</i> en m³/s",
                "<i>P</i> = <i>p</i> × <i>Q</i>", ("p", "Pa", 2e6), ("Q", "m³/s", 0.001))]
CHAINE_ETAGES = [("Alimenter", "batterie", 0.90), ("Distribuer", "hacheur", 0.95), ("Convertir", "moteur", 0.85),
                 ("Transmettre", "poulie-courroie", 0.90)]
QUIZ_2 = [
    ("Dans une trottinette électrique, le hacheur réalise la fonction…", ["Alimenter", "Distribuer", "Convertir"], 1,
     "Il dose l'énergie électrique envoyée au moteur selon la commande : c'est un préactionneur (Distribuer)."),
    ("Un préactionneur…", ["convertit l'énergie", "distribue l'énergie à l'actionneur selon les ordres",
                           "réalise l'action sur la matière d'œuvre"], 1,
     "Préactionneur → Distribuer ; actionneur → Convertir ; effecteur → Agir."),
    ("La tension efficace du réseau monophasé vaut 230 V. Sa tension maximale vaut environ…", ["230 V", "325 V", "400 V"],
     1, "Umax = U × √2 = 230 × 1,414 ≈ 325 V. 400 V est la tension entre deux phases du réseau triphasé."),
    ("La période d'une tension de fréquence 50 Hz vaut…", ["50 ms", "20 ms", "2 ms"], 1,
     "T = 1 / f = 1 / 50 = 0,02 s = 20 ms."),
    ("Pour inverser le sens de rotation d'un moteur asynchrone triphasé, on…",
     ["inverse deux des trois phases", "inverse les polarités", "augmente la fréquence"], 0,
     "Inverser deux phases suffit. Inverser les polarités, c'est la méthode du moteur à courant continu."),
    ("Un engrenage a <i>Z</i><sub>e</sub> = 20 dents et <i>Z</i><sub>s</sub> = 60 dents. Avec <i>N</i><sub>e</sub> = "
     "1 500 tr/min, <i>N</i><sub>s</sub> vaut…", ["4 500 tr/min", "500 tr/min", "1 500 tr/min"], 1,
     "r = Ze / Zs = 20 / 60 = 1/3 ; Ns = r × Ne = 1 500 / 3 = 500 tr/min. La vitesse baisse, le couple augmente."),
    ("Un radiateur de 2 kW fonctionne pendant 3 h. Il consomme…", ["6 kWh", "0,67 kWh", "6 000 kWh"], 0,
     "E = P × t = 2 kW × 3 h = 6 kWh, soit 6 000 Wh ou 21,6 MJ."),
    ("Un bloc absorbe 200 W et restitue 150 W. Son rendement vaut…", ["75 %", "133 %", "50 W"], 0,
     "η = Pu / Pa = 150 / 200 = 0,75 = 75 %. Les 50 W manquants sont des pertes (chaleur)."),
    ("Trois blocs en série ont pour rendements 0,9 ; 0,8 et 0,95. Le rendement global vaut environ…",
     ["0,68", "0,88", "0,80"], 0,
     "η global = 0,9 × 0,8 × 0,95 ≈ 0,68 : il est inférieur au plus faible des rendements (0,8)."),
    ("Une batterie de 2 Ah débite un courant de 4 A. Elle se décharge en…", ["8 h", "2 h", "30 min"], 2,
     "C = I × t donc t = C / I = 2 / 4 = 0,5 h = 30 min."),
]


def fmt_puissance(p):
    for u, k in (("GW", 1e9), ("MW", 1e6), ("kW", 1e3), ("W", 1)):
        if p >= k:
            v = p / k
            return f"{fr(v, 0) if v == int(v) else fr(v, 1)} {u}"


def render_cours_energie():
    obj = "".join(f"<li>{o}</li>" for o in OBJECTIFS)
    comp = "".join(f"<tr><td><b>{c}</b></td><td>{t}</td><td>{n}</td></tr>" for c, t, n in COMPETENCES)
    pre = "".join(f"<li>{p}</li>" for p in PREREQUIS)
    fiche = (f'<div class="c2-fiche"><div><h3>Objectifs</h3><ul>{obj}</ul></div><div><h3>Compétences travaillées</h3>'
             f'<table class="t"><thead><tr><th>Code</th><th>Compétence</th><th>Taxo.</th></tr></thead><tbody>{comp}'
             f"</tbody></table></div><div><h3>Prérequis</h3><ul>{pre}</ul></div></div>")
    s1 = course_section(1, "c2-meca", "Produits mécatroniques",
        "<p>Un produit mécatronique mêle des parties <b>mécaniques</b>, <b>électroniques</b> et <b>informatiques</b>. Des "
        "structures de contrôle permettent de piloter le produit, d'augmenter et d'optimiser ses fonctionnalités. Ce type "
        "de produit concerne de nombreux domaines (robotique, aérospatiale, transport, électroménager, loisirs…).</p>"
        "<p>Avec la fin des énergies fossiles polluantes, ces produits sont actuellement développés pour fonctionner "
        "avec l'énergie électrique. Ce thème permet d'étudier les systèmes <b>mono-source électriques</b>.</p>"
        '<div class="remarque"><p><b>Remarque :</b> pour se déplacer dans les villes, les consommateurs peuvent choisir '
        "différents moyens comme les trams et métros, les voitures électriques, les vélos à assistance, les "
        "trottinettes… La plupart de ces systèmes mécatroniques peuvent être modélisés sous la forme d'une chaîne de "
        "puissance et d'une chaîne d'information.</p></div>"
        '<div class="exemple"><h3>Exemple — la trottinette électrique</h3><p>La trottinette électrique est alimentée par '
        "une énergie embarquée stockée, rechargeable depuis le réseau électrique. L'énergie embarquée est distribuée "
        "jusqu'au moteur, qui la convertit en énergie mécanique et la transmet aux roues pour faire avancer la "
        "trottinette.</p></div><h3>Figure 1 — Chaînes de puissance et d'information d'une trottinette électrique</h3>"
        '<p class="cours-defi">À toi : clique sur chaque flux pour le voir circuler.</p>' + figure_trottinette())
    s2 = course_section(2, "c2-diag", "Diagrammes fonctionnels",
        "<h3>2.1 La chaîne de puissance</h3><p>La chaîne de puissance permet d'amener l'énergie en quantité suffisante et "
        "sous la bonne forme aux effecteurs afin de réaliser l'action désirée. Dans un produit, elle peut être découpée "
        "en blocs fonctionnels, dans l'ordre :</p><ul>"
        "<li><b>Alimenter</b> en énergie le produit ; cette énergie pouvant être <b>stockée</b>.</li>"
        "<li><b>Distribuer</b> l'énergie vers les principaux actionneurs, en assurant la sécurité des biens et des "
        "personnes et en adaptant l'énergie (<b>préactionneurs</b>).</li>"
        "<li><b>Convertir</b> l'énergie distribuée en énergie utile au fonctionnement du produit (<b>actionneurs</b>).</li>"
        "<li><b>Transmettre</b> l'énergie aux organes effecteurs.</li>"
        "<li><b>Agir</b> en effectuant l'action désirée (<b>effecteurs</b>).</li></ul>"
        "<h3>Figure 2 — Chaîne de puissance d'une trottinette (blocs fonctionnels)</h3>" + figure_chaine_puissance() +
        "<h3>2.2 Diagramme de blocs internes (ibd)</h3><p>Le diagramme SysML de blocs internes (ibd) représente "
        "graphiquement la structure interne d'un produit, avec ses composants et leurs interactions. La chaîne de "
        "puissance est identifiable à l'intérieur de ce diagramme.</p>"
        + figure("ce-fig-ibd", "Diagramme de blocs internes partiel d'une trottinette : accumulateur, carte variateur, "
                 "moteur, transmission et roue, reliés en vert ; capteur d'accélérateur et carte de traitement",
                 "Figure 3 — Diagramme ibd partiel d'une trottinette : composants et flux échangés (chaîne de puissance "
                 "en vert).", 820) +
        '<details class="simu-defi"><summary>Défi : quels blocs de ce diagramme forment la chaîne de puissance ? '
        "Et quelle fonction réalise chacun ?</summary><p>Les blocs reliés en vert : <b>accumulateur</b> Li-ion "
        "(Alimenter/Stocker, 7,8 Ah sous 36 V) → <b>carte variateur</b> (Distribuer : tension de sortie variable de 0 à "
        "36 V) → <b>moteur</b> à courant continu 36 V (Convertir) → <b>transmission</b> pignon-chaîne (Transmettre) → "
        "<b>roue</b> pneumatique (Agir). Le capteur d'accélérateur et la carte de traitement appartiennent à la chaîne "
        "d'information ; la « commande moteur » relie les deux chaînes.</p></details>"
        '<div class="remarque"><p><b>Conclusion :</b> la chaîne de puissance et le diagramme ibd mettent en évidence les '
        "échanges de flux d'information, d'énergie et/ou de matière entre les composants du produit étudié.</p></div>")
    s3 = course_section(3, "c2-alim", "Fonction Alimenter / Stocker",
        "<p>Ce bloc indique comment le produit est alimenté en énergie et permet de préciser si l'énergie est "
        "<b>stockée</b> et <b>embarquée</b>. Le produit peut aussi être alimenté par des <b>énergies renouvelables</b> "
        "(extérieures ou présentes sur le produit). Si le produit contient des batteries, celles-ci doivent être "
        "rechargées : soit en étant connectées à un chargeur externe, soit avec un régulateur de charge exploitant les "
        "énergies renouvelables. Parfois, l'énergie électrique doit être <b>adaptée</b> avant d'être distribuée "
        "(onduleur, transformateur).</p>" + catalogue("alim", "Composants de la fonction Alimenter") +
        '<div class="simu" id="ce-osc-box"><h3>Oscilloscope : l\'allure de la tension</h3>'
        '<div class="osc-src" role="radiogroup" aria-label="Source d\'énergie">'
        '<label><input type="radio" name="ce-src" value="mono" checked> Réseau monophasé</label>'
        '<label><input type="radio" name="ce-src" value="tri"> Réseau triphasé</label>'
        '<label><input type="radio" name="ce-src" value="bat"> Batterie</label>'
        '<label><input type="radio" name="ce-src" value="eol"> Éolienne</label></div>'
        '<label class="osc-vent" hidden>Vitesse du vent : <output id="ce-vent-o">10 m/s</output>'
        '<input type="range" id="ce-vent" min="3" max="15" step="1" value="10"></label>'
        '<div class="osc-wrap"><svg class="osc" id="ce-osc" viewBox="0 0 640 290" tabindex="0" role="img" '
        'aria-labelledby="ce-osc-t"><title id="ce-osc-t">Tension en fonction du temps pour la source choisie ; les '
        'valeurs caractéristiques sont données sous le graphique.</title><defs><clipPath id="osc-clip">'
        '<rect id="osc-clip-r" x="58" y="0" width="0" height="290"/></clipPath></defs><g class="osc-grid"></g>'
        '<g class="osc-curves"></g><g class="osc-ann"></g><g class="osc-hov"><line class="osc-x" y1="18" y2="246"/></g>'
        '<rect class="osc-hit" x="58" y="18" width="566" height="228"/></svg>'
        '<div class="osc-tip" id="ce-osc-tip" hidden></div></div><div class="osc-leg" id="ce-osc-leg"></div>'
        '<div class="simu-out simu-out4" id="ce-osc-out"></div>'
        '<p class="small">Survole le graphique (ou utilise les flèches du clavier) pour lire la tension à chaque '
        'instant. <button type="button" class="btn ghost" id="ce-osc-replay">Rebalayer l\'écran</button></p></div>')
    s4 = course_section(4, "c2-dist", "Fonction Distribuer",
        "<p>Ce bloc explique comment l'énergie est distribuée à l'actionneur (bloc Convertir). Suivant les "
        "<b>ordres</b> de la chaîne d'information, il distribue l'énergie sous la forme qui convient. Les éléments les "
        "plus courants sont les suivants.</p>" + catalogue("dist", "Composants de la fonction Distribuer") +
        '<div class="simu" id="ce-hach"><h3>Simulateur : un hacheur commande un moteur à courant continu</h3>'
        "<p>La batterie délivre <i>U</i> = 36 V. Le hacheur la découpe : pendant une fraction <i>α</i> de chaque période "
        "(le <b>rapport cyclique</b>), il laisse passer la tension, puis il la coupe. Le moteur « voit » la tension "
        "moyenne <i>U</i><sub>moy</sub> = <i>α</i> × <i>U</i>.</p>"
        '<div class="simu-grid"><label><span>Rapport cyclique <i>α</i> : <output id="ce-alpha-o">50 %</output></span>'
        '<input type="range" id="ce-alpha" min="0" max="100" step="5" value="50"></label>'
        '<label class="chk"><input type="checkbox" id="ce-inv"> Inverser les polarités</label></div>'
        '<div class="hach-row"><svg class="osc" id="ce-pwm" viewBox="0 0 640 230" role="img" aria-labelledby="ce-pwm-t">'
        '<title id="ce-pwm-t">Tension hachée aux bornes du moteur et sa valeur moyenne.</title><g class="pwm-g"></g>'
        '</svg><svg class="hach-mot" id="ce-mot" viewBox="0 0 120 140" role="img" aria-label="Moteur : le repère tourne '
        'à la vitesse calculée"><circle cx="60" cy="60" r="50"/><g id="ce-rotor"><line x1="60" y1="60" x2="60" y2="18"/>'
        '<circle cx="60" cy="22" r="6"/></g><circle class="axe" cx="60" cy="60" r="7"/><text x="60" y="134" '
        'text-anchor="middle">moteur M</text></svg></div><div class="osc-leg" id="ce-pwm-leg"></div>'
        '<div class="simu-out simu-out4"><div><span>Rapport cyclique α</span><b id="ce-h-a"></b></div>'
        '<div><span>Tension moyenne U<sub>moy</sub></span><b id="ce-h-u"></b></div><div><span>Fréquence de rotation N'
        '</span><b id="ce-h-n"></b></div><div><span>Sens de rotation</span><b id="ce-h-s"></b></div></div>'
        '<p class="small">Valeurs indicatives d\'un moteur à vide : 3 000 tr/min sous 36 V ; la vitesse est '
        "proportionnelle à la tension moyenne. Le hacheur <em>distribue</em> (préactionneur), le moteur "
        "<em>convertit</em> (actionneur).</p></div>")
    s5 = course_section(5, "c2-conv", "Fonction Convertir",
        "<p>Ce bloc décrit comment l'énergie est convertie d'une forme à une autre dans le système. Les éléments les "
        "plus courants sont les suivants.</p>" + catalogue("conv", "Composants de la fonction Convertir") +
        "<h3>Jeu : quelle énergie à la sortie ?</h3><p>Chaque convertisseur reçoit une énergie et en restitue une autre. "
        "Indique l'énergie restituée.</p>" + jeu_html(JEU_CONVERTIR, ENERGIES, "jeu-conv"))
    s6 = course_section(6, "c2-trans", "Fonction Transmettre",
        "<p>Ce bloc explique comment l'énergie fournie par l'actionneur est transmise au système. Les éléments les plus "
        "courants sont les suivants.</p>" + catalogue("trans", "Composants de la fonction Transmettre") +
        '<div class="simu" id="ce-tr"><h3>Simulateur : adapter ou transformer le mouvement</h3>'
        '<div class="ce-tabs" role="group" aria-label="Mécanisme"><button type="button" class="ce-tab" data-m="eng" '
        'aria-pressed="true">Engrenage</button><button type="button" class="ce-tab" data-m="cre" aria-pressed="false">'
        'Pignon-crémaillère</button><button type="button" class="ce-tab" data-m="vis" aria-pressed="false">Vis-écrou'
        '</button></div>'
        '<div class="ce-pane" data-m="eng"><div class="simu-grid">'
        '<label><span>Roue menante : <i>Z</i><sub>e</sub> = <output id="ce-ze-o">20</output> dents</span>'
        '<input type="range" id="ce-ze" min="10" max="40" step="1" value="20"></label>'
        '<label><span>Roue menée : <i>Z</i><sub>s</sub> = <output id="ce-zs-o">40</output> dents</span>'
        '<input type="range" id="ce-zs" min="10" max="60" step="1" value="40"></label>'
        '<label><span>Fréquence de rotation d\'entrée : <i>N</i><sub>e</sub> = <output id="ce-ne-o">1 500 tr/min</output>'
        '</span><input type="range" id="ce-ne" min="100" max="3000" step="100" value="1500"></label>'
        '<label><span>Couple d\'entrée : <i>C</i><sub>e</sub> = <output id="ce-ce-o">10 N·m</output></span>'
        '<input type="range" id="ce-ce" min="1" max="50" step="1" value="10"></label></div>'
        '<svg class="mec" id="ce-eng" viewBox="0 0 640 300" role="img" aria-label="Deux roues dentées qui engrènent : '
        'elles tournent en sens inverses, la plus petite plus vite"><g id="ce-g1"></g><g id="ce-g2"></g></svg>'
        '<div class="simu-out simu-out4"><div><span>Rapport r = Z<sub>e</sub> / Z<sub>s</sub></span><b id="ce-e-r"></b>'
        '</div><div><span>N<sub>s</sub> = r × N<sub>e</sub></span><b id="ce-e-n"></b></div><div><span>Couple de sortie '
        '(sans pertes)</span><b id="ce-e-c"></b></div><div><span>Réduction ou multiplication</span><b id="ce-e-t"></b>'
        '</div></div></div>'
        '<div class="ce-pane" data-m="cre" hidden><div class="simu-grid">'
        '<label><span>Rayon primitif du pignon : <i>R</i> = <output id="ce-r-o">20 mm</output></span>'
        '<input type="range" id="ce-r" min="10" max="50" step="1" value="20"></label>'
        '<label><span>Fréquence de rotation : <i>N</i><sub>e</sub> = <output id="ce-nr-o">60 tr/min</output></span>'
        '<input type="range" id="ce-nr" min="10" max="300" step="10" value="60"></label></div>'
        '<svg class="mec" id="ce-cre" viewBox="0 0 640 230" role="img" aria-label="Pignon qui tourne et crémaillère qui '
        'se déplace en translation"><g id="ce-rack"></g><g id="ce-pin"></g></svg>'
        '<div class="simu-out"><div><span>ω<sub>e</sub> = 2π N<sub>e</sub> / 60</span><b id="ce-c-w"></b></div>'
        '<div><span>V<sub>s</sub> = ω<sub>e</sub> × R</span><b id="ce-c-v"></b></div><div><span>Distance en 1 min</span>'
        '<b id="ce-c-d"></b></div></div></div>'
        '<div class="ce-pane" data-m="vis" hidden><div class="simu-grid">'
        '<label><span>Pas de la vis : <i>p</i> = <output id="ce-p-o">4 mm</output></span>'
        '<input type="range" id="ce-p" min="1" max="10" step="0.5" value="4"></label>'
        '<label><span>Fréquence de rotation : <i>N</i><sub>e</sub> = <output id="ce-nv-o">300 tr/min</output></span>'
        '<input type="range" id="ce-nv" min="30" max="1500" step="30" value="300"></label></div>'
        '<svg class="mec" id="ce-vis" viewBox="0 0 640 170" role="img" aria-label="Vis qui tourne et écrou qui avance">'
        '<defs><clipPath id="ce-screw-clip"><rect x="30" y="70" width="580" height="30"/></clipPath></defs>'
        '<g id="ce-screw"></g><g id="ce-nut"></g></svg>'
        '<div class="simu-out"><div><span>V<sub>s</sub> = p × N<sub>e</sub></span><b id="ce-v-v"></b></div>'
        '<div><span>Soit</span><b id="ce-v-s"></b></div><div><span>Avance pour 1 tour</span><b id="ce-v-t"></b></div>'
        "</div></div></div>")
    agir = "".join(f'<figure class="agir-c">{img("ce-ph-" + k, n)}<figcaption><b>{n}</b><span>{a}</span></figcaption>'
                   f"</figure>" for k, n, a in [("roues", "Roues de trottinette", "faire avancer la trottinette"),
                                               ("scene", "Éclairage de scène", "éclairer la scène"),
                                               ("four", "Four de traitement thermique", "chauffer les pièces à traiter")])
    s7 = course_section(7, "c2-agir", "Fonction Agir",
        "<p>Ce bloc explique comment est utilisée l'énergie transmise pour réaliser l'action demandée par le cahier des "
        "charges du produit. L'effecteur agit directement sur la matière d'œuvre.</p>"
        f'<p><b>Exemples :</b></p><div class="agir">{agir}</div>')
    ef_rows = "".join(f'<tr data-ef="{k}" tabindex="0"><td><b>{n}</b></td><td>{e}</td><td>{f}</td><td>{p}</td></tr>'
                      for k, n, e, f, p, *_x in EFFORT_FLUX)
    ef_cfg = esc(json.dumps({k: {"n": n, "p": p, "a": a, "b": b} for k, n, _e, _f, p, a, b in EFFORT_FLUX},
                            ensure_ascii=False))
    rd_rows = "".join(f"<tr><td>{a}</td><td>{m}</td><td>{r}</td><td>{v} %</td></tr>" for a, m, r, v in RENDEMENTS)
    pu_rows = "".join(f"<li>{n} : {fmt_puissance(p)}</li>" for n, p in PUISSANCES)
    etages = "".join(
        f'<label><span>{n} ({c}) : <i>η</i><sub>{i + 1}</sub> = <output id="ce-eta{i}-o"></output></span>'
        f'<input type="range" id="ce-eta{i}" min="0.5" max="1" step="0.01" value="{v}"></label>'
        for i, (n, c, v) in enumerate(CHAINE_ETAGES))
    s8 = course_section(8, "c2-puis", "Puissances et rendements",
        "<h3>8.1 La puissance</h3><p>La puissance caractérise la performance d'un système à un instant donné. Elle "
        "s'exprime en <b>watt (W)</b>, c'est-à-dire en joule par seconde (J/s).</p>"
        '<div class="simu" id="ce-pu"><h3>Quelques ordres de grandeur</h3><p class="small">Échelle logarithmique : '
        "chaque graduation vaut 10 fois la précédente. Clique sur un point pour comparer.</p>"
        '<div class="osc-wrap"><svg class="osc" id="ce-pu-svg" viewBox="0 0 640 352" role="img" aria-labelledby="ce-pu-t">'
        '<title id="ce-pu-t">Puissances de quelques systèmes, de la télévision (100 W) à la centrale nucléaire '
        '(1 GW), sur une échelle logarithmique.</title></svg><div class="osc-tip" id="ce-pu-tip" hidden></div></div>'
        f'<p class="ce-ftxt" id="ce-pu-txt" aria-live="polite"></p><details class="tview"><summary>Voir la liste</summary>'
        f"<ul class=\"cols\">{pu_rows}</ul></details></div>"
        "<h3>8.2 L'énergie</h3><p>L'énergie caractérise la consommation de ce système pendant une durée. Elle s'exprime "
        "en <b>joule (J)</b>. Puissance et énergie sont liées par la relation :</p>"
        f'<div class="formule"><span class="f-main"><i>E</i> = <i>P</i> × <i>t</i></span><span class="f-units"><i>E</i> '
        "énergie en joule (J)<br><i>P</i> puissance en watt (W)<br><i>t</i> temps en seconde (s)</span></div>"
        "<p>Le joule étant peu utilisé en ingénierie, on lui préfère souvent le <b>wattheure (Wh)</b>. Il faut alors veiller "
        "à la cohérence des unités : la puissance en watt et le temps en heures. De plus : <b>1 Wh = 3 600 J</b>.</p>"
        '<div class="simu" id="ce-en"><h3>Calculateur d\'énergie</h3><div class="ce-presets">'
        '<button type="button" class="btn ghost" data-p="2000" data-t="3">Radiateur 2 kW, 3 h</button>'
        '<button type="button" class="btn ghost" data-p="100" data-t="4">Télévision 100 W, 4 h</button>'
        '<button type="button" class="btn ghost" data-p="250" data-t="2">Vélo électrique 250 W, 2 h</button></div>'
        '<div class="simu-grid"><label><span>Puissance <i>P</i> (W)</span><input type="number" id="ce-en-p" min="0" '
        'step="any" value="2000"></label><label><span>Durée <i>t</i> (h)</span><input type="number" id="ce-en-t" min="0" '
        'step="any" value="3"></label></div><div class="simu-out"><div><span>Énergie en Wh</span><b id="ce-en-wh"></b>'
        '</div><div><span>Énergie en kWh</span><b id="ce-en-kwh"></b></div><div><span>Énergie en joules</span>'
        '<b id="ce-en-j"></b></div></div></div>'
        "<h3>8.3 Grandeurs d'effort et grandeurs de flux</h3><p>La puissance (en W) est le produit d'une <b>grandeur "
        "d'effort</b> et d'une <b>grandeur de flux</b>. Le tableau récapitule les grandeurs les plus courantes ; clique "
        "sur une ligne pour calculer une puissance.</p>"
        f'<div class="recap-wrap"><table class="t ef-table"><thead><tr><th>Énergie</th><th>Grandeur d\'effort</th>'
        f"<th>Grandeur de flux</th><th>Puissance</th></tr></thead><tbody>{ef_rows}</tbody></table></div>"
        f'<div class="simu" id="ce-ef" data-cfg="{ef_cfg}"><h3 id="ce-ef-t"></h3><div class="simu-grid">'
        '<label><span id="ce-ef-la"></span><input type="number" id="ce-ef-a" step="any"></label>'
        '<label><span id="ce-ef-lb"></span><input type="number" id="ce-ef-b" step="any"></label></div>'
        '<div class="simu-out"><div><span>Puissance P</span><b id="ce-ef-p"></b></div><div><span>Formule</span>'
        '<b id="ce-ef-f"></b></div><div><span>Soit</span><b id="ce-ef-k"></b></div></div>'
        '<p class="small" id="ce-ef-w"></p></div>'
        "<h3>8.4 Pourquoi parle-t-on de « chaîne de puissance » ?</h3><p>Jusqu'ici, les fonctions et leurs constituants "
        "sont représentés par des blocs, sans qu'aucune puissance n'apparaisse. En réalité, entre chaque bloc, il y a "
        "transfert d'énergie (mécanique, électrique, pneumatique…). En prenant l'exemple d'une voiture électrique, on "
        "peut faire apparaître ces transferts de puissance sur la chaîne, avec les grandeurs d'effort et de flux.</p>"
        + figure("ce-fig-voiture", "Chaîne de puissance d'une voiture électrique : énergie électrique (U, I, P = U × I) en "
                 "sortie de batterie et en sortie de variateur, énergie mécanique de rotation (C, ω, P = C × ω) en sortie "
                 "de moteur et de réducteur", "Figure 4 — Transferts de puissance sur la chaîne d'une voiture électrique "
                 "(grandeurs d'effort et de flux).", 660) +
        "<h3>8.5 Rendement d'un bloc</h3><p>Les transferts de puissance ne sont pas parfaits : à chaque passage d'un bloc "
        "à l'autre, une partie de l'énergie est perdue, dissipée sous forme de <b>chaleur</b>. Par exemple, la chaleur "
        "dégagée par un chargeur de téléphone provient des pertes liées à la transformation de tension (230 V → 5 V).</p>"
        + figure("ce-fig-chargeur", "Chaîne d'un chargeur de téléphone : le réseau alimente, le transformateur 230 V vers "
                 "5 V transmet avec des pertes en chaleur, la batterie du téléphone reçoit P2", "Figure 5 — Pertes dans un "
                 "chargeur de téléphone (bloc Transmettre).", 620) +
        "<p>Pour un chargeur de téléphone, les pertes représentent 20 à 40 % de l'énergie entrante (<i>P</i><sub>1</sub>). "
        "Le bloc restitue donc en sortie (<i>P</i><sub>2</sub>) moins d'énergie qu'il n'en reçoit. Avec 20 % de pertes, "
        "<i>P</i><sub>2</sub> vaut 80 % de <i>P</i><sub>1</sub> : ce pourcentage est le <b>rendement</b>, noté <i>η</i> "
        "(êta), rapport entre la puissance utile (sortie) et la puissance absorbée (entrée) :</p>"
        f'<div class="formule"><span class="f-main"><i>η</i> = {frac("<i>P</i><sub>u</sub>", "<i>P</i><sub>a</sub>")}'
        "</span><span class=\"f-units\"><i>P</i><sub>u</sub> puissance utile (W)<br><i>P</i><sub>a</sub> puissance "
        "absorbée (W)<br><i>η</i> rendement, sans unité ou en %</span></div>"
        '<div class="simu" id="ce-ch"><h3>Le chargeur de téléphone</h3><div class="simu-grid"><label><span>Puissance '
        'absorbée <i>P</i><sub>1</sub> : <output id="ce-ch-p-o"></output></span><input type="range" id="ce-ch-p" min="5" '
        'max="30" step="1" value="10"></label><label><span>Pertes : <output id="ce-ch-l-o"></output></span><input '
        'type="range" id="ce-ch-l" min="20" max="40" step="1" value="20"></label></div>'
        '<svg class="osc sk" id="ce-ch-svg" viewBox="0 0 640 192" role="img" aria-label="Bande d\'énergie dont la largeur '
        'est proportionnelle à la puissance : la bande de sortie est plus étroite, la différence part en chaleur"></svg>'
        '<div class="simu-out"><div><span>Puissance utile P<sub>2</sub></span><b id="ce-ch-u"></b></div><div><span>Pertes'
        '</span><b id="ce-ch-x"></b></div><div><span>Rendement η</span><b id="ce-ch-e"></b></div></div></div>'
        "<h3>Quelques machines et leur rendement</h3>"
        '<div class="simu" id="ce-rd"><div class="osc-wrap"><svg class="osc" id="ce-rd-svg" viewBox="0 0 640 420" '
        'role="img" aria-labelledby="ce-rd-t"><title id="ce-rd-t">Rendement de onze machines, classées du plus élevé '
        '(radiateur, 100 %) au plus faible (lampe à filament, 3 %).</title></svg><div class="osc-tip" id="ce-rd-tip" '
        'hidden></div></div><details class="tview"><summary>Voir le tableau</summary><table class="t"><thead><tr><th>'
        "Énergie absorbée</th><th>Machine</th><th>Énergie restituée</th><th>Rendement</th></tr></thead><tbody>"
        f"{rd_rows}</tbody></table></details></div>"
        "<h3>8.6 Rendement global d'une chaîne de puissance</h3><p>Le rendement global d'une chaîne de puissance est le "
        "produit des rendements de chaque bloc :</p>"
        '<div class="formule"><span class="f-main"><i>η</i><sub>global</sub> = <i>η</i><sub>1</sub> × <i>η</i><sub>2</sub> '
        "× <i>η</i><sub>3</sub> × … × <i>η</i><sub>n</sub></span></div>"
        '<div class="remarque"><p><b>⚠</b> Le rendement global d\'une chaîne d\'énergie est donc nécessairement inférieur '
        "au rendement du plus faible de ses étages. D'où la nécessité de soigner la conception de chaque étage dans un "
        "souci d'efficacité énergétique globale.</p></div>"
        '<div class="simu" id="ce-gl"><h3>Simulateur : la chaîne de la trottinette</h3><div class="simu-grid">'
        '<label><span>Puissance absorbée <i>P</i><sub>a</sub> : <output id="ce-gl-p-o"></output></span><input type="range" '
        f'id="ce-gl-p" min="100" max="1000" step="10" value="500"></label>{etages}</div>'
        '<svg class="osc sk" id="ce-gl-svg" viewBox="0 0 640 214" role="img" aria-label="Bande d\'énergie de la '
        'trottinette : à chaque étage, une partie de la puissance part en pertes"></svg>'
        '<div class="simu-out simu-out4"><div><span>Rendement global</span><b id="ce-gl-e"></b></div><div><span>'
        'Puissance utile</span><b id="ce-gl-u"></b></div><div><span>Pertes totales</span><b id="ce-gl-x"></b></div>'
        '<div><span>Plus faible étage</span><b id="ce-gl-m"></b></div></div><p class="simu-verdict ok" id="ce-gl-v" '
        'aria-live="polite"></p></div>'
        "<h3>8.7 Autonomie énergétique et capacité d'une batterie</h3><p>L'autonomie énergétique est un enjeu majeur dans "
        "l'étude des systèmes. Le système étudié est souvent muni d'une batterie qu'il faut dimensionner : il faut donc "
        "savoir estimer sa capacité.</p><p>Pour le stockage de l'électricité, on quantifie l'énergie non pas en J ni en "
        "Wh, mais en <b>ampère-heure (Ah)</b> : c'est la capacité d'une batterie ou d'une pile à débiter un courant "
        "pendant une heure. Par exemple, une batterie de téléphone d'une capacité d'environ 2 Ah peut débiter 2 A pendant "
        "1 heure, 1 A pendant 2 heures ou 4 A pendant 30 minutes.</p>"
        '<div class="formule"><span class="f-main"><i>C</i> = <i>I</i> × <i>t</i></span><span class="f-units"><i>C</i> '
        "capacité en ampère-heure (Ah)<br><i>I</i> courant en ampère (A)<br><i>t</i> temps en heures (h)</span></div>"
        '<div class="simu" id="ce-au"><h3>Calculateur d\'autonomie</h3><div class="ce-presets">'
        '<button type="button" class="btn ghost" data-c="2" data-i="2" data-u="3.7">Téléphone : 2 Ah à 2 A</button>'
        '<button type="button" class="btn ghost" data-c="2" data-i="4" data-u="3.7">Téléphone : 2 Ah à 4 A</button>'
        '<button type="button" class="btn ghost" data-c="7.8" data-i="10" data-u="36">Trottinette : 7,8 Ah à 10 A</button>'
        '</div><div class="simu-grid"><label><span>Capacité <i>C</i> : <output id="ce-au-c-o"></output></span>'
        '<input type="range" id="ce-au-c" min="0.5" max="20" step="0.1" value="2"></label>'
        '<label><span>Courant débité <i>I</i> : <output id="ce-au-i-o"></output></span><input type="range" id="ce-au-i" '
        'min="0.1" max="20" step="0.1" value="2"></label><label><span>Tension de la batterie <i>U</i> : <output '
        'id="ce-au-u-o"></output></span><input type="range" id="ce-au-u" min="1.2" max="48" step="0.1" value="3.7"></label>'
        '</div><div class="simu-out"><div><span>Autonomie t = C / I</span><b id="ce-au-t"></b></div><div><span>Soit</span>'
        '<b id="ce-au-m"></b></div><div><span>Énergie stockée E = U × C</span><b id="ce-au-e"></b></div></div></div>')
    s9 = course_section(9, "c2-syn", "Synthèse : range chaque composant dans sa fonction",
        "<p>Pour chaque composant, choisis la fonction de la chaîne d'énergie qu'il réalise.</p>"
        + jeu_html(JEU_SYNTHESE, FONCTIONS_E, "jeu-syn"))
    s10 = quiz_section(10, "c2-quiz", QUIZ_2, "q2_")
    return f"""<div class="cours" id="cours-2">
{course_head("Cours 2", "Niveau 2", "Chaîne d'énergie des produits",
             "Suivre l'énergie d'un produit mécatronique, de la source jusqu'à l'action : alimenter et stocker, "
             "distribuer, convertir, transmettre, agir ; puis calculer puissances, énergies et rendements. Environ "
             "1\u00a0h\u00a030, avec des figures animées, des fiches de composants, des simulateurs, deux jeux et un quiz.")}
{fiche}
{course_nav([("c2-meca", "Mécatronique"), ("c2-diag", "Diagrammes"), ("c2-alim", "Alimenter"), ("c2-dist", "Distribuer"),
             ("c2-conv", "Convertir"), ("c2-trans", "Transmettre"), ("c2-agir", "Agir"), ("c2-puis", "Puissances"),
             ("c2-syn", "Synthèse"), ("c2-quiz", "Quiz")])}
{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}{s9}{s10}
<div class="cours-foot no-print"><a class="btn" href="formulaire.html#formulaire">Le formulaire</a>
<a class="btn ghost" href="formulaire.html#exercices">Exercices de calcul</a>
<a class="btn ghost" href="?ex=cours-chaine-information">Cours 3 : chaîne d'information</a>
<a class="btn ghost" href="?ex=chaines-information-energie">Exercice 1.1</a>
<button type="button" class="btn ghost cours-print">Imprimer le cours</button>
<a class="btn ghost" href="?">{HOUSE} Retour à l'accueil</a></div>
</div>"""


COURS_2_JS = r"""
  function initCoursEnergie(home) {
    var NS = "http://www.w3.org/2000/svg";
    var calme = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    function q(s, r) { return (r || home).querySelector(s); }
    function qa(s, r) { return Array.prototype.slice.call((r || home).querySelectorAll(s)); }
    function mk(tag, attrs, parent) {
      var e = document.createElementNS(NS, tag);
      Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
      if (parent) parent.appendChild(e);
      return e;
    }
    function tx(parent, x, y, s, cls, anchor) {
      var t = mk("text", { x: x, y: y, "class": cls || "", "text-anchor": anchor || "start" }, parent);
      t.textContent = s;
      return t;
    }
    // nombre « lisible » : au plus 3 chiffres significatifs, écriture française
    function sig(x, n) {
      if (!isFinite(x)) return "–";
      if (x === 0) return "0";
      var d = Math.min(6, Math.max(0, (n || 3) - 1 - Math.floor(Math.log10(Math.abs(x)))));
      return x.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: d }).replace(/^-/, "−");
    }
    function setOut(id, s) { var e = q("#" + id); if (e) e.textContent = s; }
    var animers = [];

    // ---------- flux animés : des points circulent le long des chemins actifs ----------
    function Flux(svg) { this.svg = svg; this.layer = svg.querySelector(".ce-ptc"); this.on = {}; this.clock = 0; }
    Flux.prototype.set = function (ids) {
      var self = this;
      Object.keys(this.on).forEach(function (id) {
        if (ids.indexOf(id) >= 0) return;
        self.on[id].dots.forEach(function (d) { d.remove(); });
        self.on[id].el.classList.remove("on");
        delete self.on[id];
      });
      ids.forEach(function (id) {
        if (self.on[id]) return;
        var el = self.svg.querySelector("#" + id);
        if (!el) return;
        var len = el.getTotalLength(), n = Math.max(1, Math.min(9, Math.round(len / 55))), dots = [];
        for (var k = 0; k < n; k++) dots.push(mk("circle", { r: 5, "class": "ce-dot " + (el.getAttribute("data-k") || "") }, self.layer));
        self.on[id] = { el: el, len: len, dots: dots };
        el.classList.add("on");
      });
      this.draw();
    };
    Flux.prototype.draw = function () {
      var self = this;
      Object.keys(this.on).forEach(function (id) {
        var f = self.on[id], n = f.dots.length;
        f.dots.forEach(function (d, k) {
          var u = ((self.clock * 70 / f.len) + k / n) % 1, p = f.el.getPointAtLength(u * f.len);
          d.setAttribute("cx", p.x.toFixed(1)); d.setAttribute("cy", p.y.toFixed(1));
        });
      });
    };
    Flux.prototype.tick = function (dt) { if (calme) return; this.clock += dt; this.draw(); };

    // ---------- figure 1 : les flux de la trottinette ----------
    (function () {
      var svg = q("#ce-f1"); if (!svg) return;
      var fx = new Flux(svg), out = q("#ce-f1-txt"), btns = qa(".ce-f1-b");
      animers.push(function (dt) { fx.tick(dt); });
      btns.forEach(function (b) {
        b.addEventListener("click", function () {
          var on = b.getAttribute("aria-pressed") !== "true";
          btns.forEach(function (x) { x.setAttribute("aria-pressed", x === b && on ? "true" : "false"); });
          fx.set(on ? [b.getAttribute("data-f")] : []);
          svg.classList.toggle("focus", on);
          out.innerHTML = on ? b.getAttribute("data-t") : "Clique sur un flux pour savoir ce qui circule.";
        });
      });
    })();

    // ---------- figure 2 : la chaîne de puissance en blocs ----------
    (function () {
      var svg = q("#ce-f2"); if (!svg) return;
      var fx = new Flux(svg), out = q("#ce-f2-txt"), go = q("#ce-f2-go");
      animers.push(function (dt) { fx.tick(dt); });
      go.addEventListener("click", function () {
        var on = go.getAttribute("aria-pressed") !== "true";
        go.setAttribute("aria-pressed", on ? "true" : "false");
        go.textContent = on ? "❚❚ Arrêter le flux d'énergie" : "▶ Faire circuler l'énergie";
        fx.set(on ? ["c2-p0", "c2-p1", "c2-p2", "c2-p3", "c2-p4"] : []);
      });
      qa(".ce-blk", svg).forEach(function (g) {
        function pick() {
          qa(".ce-blk", svg).forEach(function (x) { x.classList.toggle("sel", x === g); });
          out.innerHTML = g.getAttribute("data-t");
        }
        g.addEventListener("click", pick);
        g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
      });
    })();

    // ---------- fiches des composants ----------
    qa(".cata").forEach(function (c) {
      var its = qa(".cata-it", c);
      its.forEach(function (b) {
        var ph = c.querySelector('.fiche-c[data-fiche="' + b.getAttribute("data-fiche") + '"] .fc-ph img');
        var src = b.querySelector("img");
        if (ph && src) { ph.src = src.src; ph.width = src.width; ph.height = src.height; }
      });
      function open(k) {
        its.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-fiche") === k ? "true" : "false"); });
        qa(".fiche-c", c).forEach(function (f) { f.hidden = f.getAttribute("data-fiche") !== k; });
      }
      its.forEach(function (b) { b.addEventListener("click", function () { open(b.getAttribute("data-fiche")); }); });
      if (its.length) open(its[0].getAttribute("data-fiche"));
    });

    // ---------- oscilloscope ----------
    (function () {
      var svg = q("#ce-osc"); if (!svg) return;
      var L = 58, R = 624, T = 18, B = 246;
      var grid = q(".osc-grid", svg), curves = q(".osc-curves", svg), ann = q(".osc-ann", svg), xline = q(".osc-x", svg);
      var hit = q(".osc-hit", svg), clip = q("#osc-clip-r"), tip = q("#ce-osc-tip"), leg = q("#ce-osc-leg");
      var vent = q("#ce-vent"), ventBox = q(".osc-vent"), out = q("#ce-osc-out");
      var COL = ["#1F5FA8", "#B26A00", "#1baf7a"], UM = 230 * Math.SQRT2, W50 = 2 * Math.PI * 50 / 1000;
      var cur = "mono", D = null, sweep = 1, tCur = null;
      function src() {
        var v = +vent.value, f = 2 * v, a = 4 * v;
        return {
          mono: { tmax: 40, tstep: 5, ymin: -400, ymax: 400, ystep: 100,
                  series: [{ n: "u", f: function (t) { return UM * Math.sin(W50 * t); } }],
                  tiles: [["Tension efficace U", "230 V"], ["Tension maximale", "325 V"], ["Fréquence f", "50 Hz"], ["Période T", "20 ms"]] },
          tri: { tmax: 40, tstep: 5, ymin: -400, ymax: 400, ystep: 100,
                 series: [0, 1, 2].map(function (k) { return { n: "V" + (k + 1), f: function (t) { return UM * Math.sin(W50 * t - k * 2 * Math.PI / 3); } }; }),
                 tiles: [["V, entre phase et neutre", "230 V"], ["U, entre deux phases", "400 V"], ["Fréquence f", "50 Hz"], ["Décalage entre phases", "T/3 ≈ 6,7 ms"]] },
          bat: { tmax: 40, tstep: 5, ymin: 0, ymax: 50, ystep: 10,
                 series: [{ n: "U", f: function () { return 36; } }],
                 tiles: [["Tension U", "36 V"], ["Nature", "continue"], ["Capacité Q", "7,8 Ah"], ["Exemple", "trottinette"]] },
          eol: { tmax: 200, tstep: 25, ymin: -80, ymax: 80, ystep: 20, f: f, a: a,
                 series: [{ n: "u", f: function (t) { return a * Math.sin(2 * Math.PI * f * t / 1000); } }],
                 tiles: [["Vent", v + " m/s"], ["Tension maximale", a + " V"], ["Fréquence f", f + " Hz"], ["Période T", sig(1000 / f, 3) + " ms"]] }
        }[cur];
      }
      function X(t) { return L + t / D.tmax * (R - L); }
      function Y(u) { return B - (u - D.ymin) / (D.ymax - D.ymin) * (B - T); }
      function bracket(t1, t2, y, label) {
        mk("path", { d: "M" + X(t1) + " " + (y + 5) + "V" + (y - 5) + "M" + X(t1) + " " + y + "H" + X(t2) + "M" + X(t2) + " " + (y + 5) + "V" + (y - 5), "class": "ann-l" }, ann);
        tx(ann, (X(t1) + X(t2)) / 2, y - 7, label, "ann-t", "middle");
      }
      function draw() {
        D = src();
        grid.textContent = ""; curves.textContent = ""; ann.textContent = "";
        var t, u;
        for (t = 0; t <= D.tmax + 1e-9; t += D.tstep) {
          mk("line", { x1: X(t), x2: X(t), y1: T, y2: B, "class": "g" }, grid);
          tx(grid, X(t), B + 16, fr(t, 0), "tick", "middle");
        }
        for (u = D.ymin; u <= D.ymax + 1e-9; u += D.ystep) {
          mk("line", { x1: L, x2: R, y1: Y(u), y2: Y(u), "class": u === 0 ? "g0" : "g" }, grid);
          tx(grid, L - 6, Y(u) + 4, fr(u, 0), "tick", "end");
        }
        tx(grid, R, B + 34, "temps t (ms)", "axl", "end");
        tx(grid, L + 4, 12, "tension (V)", "axl", "start");
        D.series.forEach(function (s, i) {
          var d = "";
          for (var k = 0; k <= 480; k++) { var tt = D.tmax * k / 480; d += (k ? "L" : "M") + X(tt).toFixed(1) + " " + Y(s.f(tt)).toFixed(1); }
          mk("path", { d: d, "class": "crv", stroke: COL[i], "clip-path": "url(#osc-clip)" }, curves);
        });
        if (cur === "mono") {
          mk("line", { x1: L, x2: R, y1: Y(UM), y2: Y(UM), "class": "ann-l" }, ann);
          tx(ann, R - 4, Y(UM) - 6, "Umax = U × √2 ≈ 325 V", "ann-t", "end");
          bracket(15, 35, Y(-UM) + 16, "T = 20 ms");
        } else if (cur === "tri") {
          [5, 5 + 20 / 3, 5 + 40 / 3].forEach(function (tp, k) {
            mk("line", { x1: X(tp) - 9, x2: X(tp) + 1, y1: Y(UM) - 10, y2: Y(UM) - 10, "class": "key", stroke: COL[k] }, ann);
            tx(ann, X(tp) + 4, Y(UM) - 6, "V" + (k + 1), "ann-t", "start");
          });
          bracket(15, 15 + 20 / 3, Y(-UM) + 16, "T/3");
        } else if (cur === "bat") {
          tx(ann, R - 4, Y(36) - 8, "U = 36 V, constante", "ann-t", "end");
        } else {
          mk("line", { x1: L, x2: R, y1: Y(D.a), y2: Y(D.a), "class": "ann-l" }, ann);
          tx(ann, R - 4, Y(D.a) - 6, "Umax ≈ " + D.a + " V", "ann-t", "end");
          var t0 = 750 / D.f;
          if (t0 + 1000 / D.f <= D.tmax) bracket(t0, t0 + 1000 / D.f, Y(-D.a) + 16, "T ≈ " + sig(1000 / D.f, 3) + " ms");
        }
        leg.textContent = "";
        if (D.series.length > 1) D.series.forEach(function (s, i) {
          var sp = document.createElement("span"), k = document.createElement("i");
          k.style.borderColor = COL[i]; sp.appendChild(k); sp.appendChild(document.createTextNode(s.n)); leg.appendChild(sp);
        });
        out.textContent = "";
        D.tiles.forEach(function (tl) {
          var dv = document.createElement("div"), s = document.createElement("span"), b = document.createElement("b");
          s.textContent = tl[0]; b.textContent = tl[1]; dv.appendChild(s); dv.appendChild(b); out.appendChild(dv);
        });
        ventBox.hidden = cur !== "eol";
        q("#ce-vent-o").textContent = vent.value + " m/s";
        if (tCur !== null) hover(tCur);
      }
      function replay() { sweep = calme ? 1 : 0; clip.setAttribute("width", calme ? R - L : 0); }
      animers.push(function (dt) {
        if (sweep >= 1) return;
        sweep = Math.min(1, sweep + dt / 1.4);
        clip.setAttribute("width", (sweep * (R - L)).toFixed(1));
      });
      function hover(t) {
        tCur = Math.max(0, Math.min(D.tmax, t));
        var x = X(tCur);
        xline.setAttribute("x1", x); xline.setAttribute("x2", x); xline.style.display = "block";
        tip.textContent = "";
        var h = document.createElement("b"); h.textContent = "t = " + sig(tCur, 3) + " ms"; tip.appendChild(h);
        D.series.forEach(function (s, i) {
          var r = document.createElement("span"), k = document.createElement("i"), v = document.createElement("strong");
          k.style.borderColor = COL[i]; v.textContent = fr(s.f(tCur), 0) + " V";
          r.appendChild(k); r.appendChild(v); r.appendChild(document.createTextNode(" " + s.n)); tip.appendChild(r);
        });
        tip.hidden = false;
        var box = svg.getBoundingClientRect(), wrap = svg.parentNode.getBoundingClientRect();
        var px = box.left - wrap.left + x / 640 * box.width;
        tip.style.left = Math.min(px + 12, wrap.width - tip.offsetWidth - 4) + "px";
        tip.style.top = (box.top - wrap.top + 8) + "px";
      }
      function leave() { tCur = null; tip.hidden = true; xline.style.display = "none"; }
      hit.addEventListener("pointermove", function (e) {
        var box = svg.getBoundingClientRect(), x = (e.clientX - box.left) / box.width * 640;
        hover((x - L) / (R - L) * D.tmax);
      });
      hit.addEventListener("pointerleave", leave);
      svg.addEventListener("keydown", function (e) {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        e.preventDefault();
        hover((tCur === null ? 0 : tCur) + (e.key === "ArrowRight" ? 1 : -1) * D.tstep / 5);
      });
      svg.addEventListener("blur", leave);
      qa('input[name="ce-src"]').forEach(function (r) {
        r.addEventListener("change", function () { cur = r.value; leave(); draw(); replay(); });
      });
      vent.addEventListener("input", function () { draw(); });
      q("#ce-osc-replay").addEventListener("click", replay);
      draw(); replay();
    })();

    // ---------- hacheur et moteur à courant continu ----------
    (function () {
      var svg = q("#ce-pwm"); if (!svg) return;
      var A = q("#ce-alpha"), INV = q("#ce-inv"), g = q(".pwm-g", svg), rotor = q("#ce-rotor"), leg = q("#ce-pwm-leg");
      var U = 36, NMAX = 3000, L = 58, R = 548, T = 14, B = 196, YMIN = -45, YMAX = 45, NP = 3, ang = 0, n = 0, sens = 1;
      function X(t) { return L + t / NP * (R - L); }
      function Y(u) { return B - (u - YMIN) / (YMAX - YMIN) * (B - T); }
      function draw() {
        var a = +A.value / 100, s = INV.checked ? -1 : 1, um = s * a * U;
        n = a * NMAX; sens = s;
        g.textContent = "";
        for (var k = 0; k <= NP; k++) {
          mk("line", { x1: X(k), x2: X(k), y1: T, y2: B, "class": "g" }, g);
          tx(g, X(k), B + 16, k ? k + "T" : "0", "tick", "middle");
        }
        [-40, -20, 0, 20, 40].forEach(function (u) {
          mk("line", { x1: L, x2: R, y1: Y(u), y2: Y(u), "class": u === 0 ? "g0" : "g" }, g);
          tx(g, L - 6, Y(u) + 4, fr(u, 0), "tick", "end");
        });
        tx(g, L + 4, 10, "tension (V)", "axl"); tx(g, R, B + 32, "temps", "axl", "end");
        var d;
        if (a <= 0 || a >= 1) d = "M" + X(0) + " " + Y(a >= 1 ? s * U : 0) + "H" + X(NP);
        else {
          d = "M" + X(0) + " " + Y(s * U);
          for (k = 0; k < NP; k++) d += "H" + X(k + a) + "V" + Y(0) + "H" + X(k + 1) + (k < NP - 1 ? "V" + Y(s * U) : "");
        }
        mk("path", { d: d, "class": "crv", stroke: "#1F5FA8" }, g);
        mk("line", { x1: L, x2: R, y1: Y(um), y2: Y(um), "class": "crv", stroke: "#B26A00" }, g);
        tx(g, R + 8, Y(um) - 3, "Umoy =", "ann-t", "start");
        tx(g, R + 8, Y(um) + 13, fr(um, 1) + " V", "ann-t", "start");
        q("#ce-alpha-o").textContent = fr(a * 100, 0) + " %";
        setOut("ce-h-a", fr(a * 100, 0) + " % = " + fr(a, 2));
        setOut("ce-h-u", fr(Math.abs(um), 1) + " V");
        setOut("ce-h-n", fr(n, 0) + " tr/min");
        setOut("ce-h-s", a === 0 ? "arrêt" : (s > 0 ? "sens 1 (horaire)" : "sens 2 (inverse)"));
      }
      leg.innerHTML = '<span><i style="border-color:#1F5FA8"></i>tension hachée u(t)</span><span><i style="border-color:#B26A00"></i>tension moyenne U<sub>moy</sub></span>';
      animers.push(function (dt) {
        if (calme) return;
        ang = (ang + sens * n / NMAX * 540 * dt) % 360;
        rotor.setAttribute("transform", "rotate(" + ang.toFixed(1) + " 60 60)");
      });
      A.addEventListener("input", draw); INV.addEventListener("change", draw);
      draw();
    })();

    // ---------- transmettre : engrenage, pignon-crémaillère, vis-écrou ----------
    (function () {
      var box = q("#ce-tr"); if (!box) return;
      var mode = "eng";
      qa(".ce-tab", box).forEach(function (b) {
        b.addEventListener("click", function () {
          mode = b.getAttribute("data-m");
          qa(".ce-tab", box).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          qa(".ce-pane", box).forEach(function (p) { p.hidden = p.getAttribute("data-m") !== mode; });
        });
      });
      // roue dentée : dents trapézoïdales autour du cercle primitif de rayon r, centrées sur l'angle 0
      function gear(Z, r) {
        var m = 2 * r / Z, ra = r + m, rf = r - 1.25 * m, s = 2 * Math.PI / Z, p = "";
        for (var k = 0; k < Z; k++) {
          var c = k * s;
          [[rf, c - s / 2], [rf, c - 0.27 * s], [ra, c - 0.13 * s], [ra, c + 0.13 * s], [rf, c + 0.27 * s]].forEach(function (pt, j) {
            p += (k === 0 && j === 0 ? "M" : "L") + (pt[0] * Math.cos(pt[1])).toFixed(2) + " " + (pt[0] * Math.sin(pt[1])).toFixed(2);
          });
        }
        return p + "Z";
      }
      function gearG(g, Z, r, col, lab) {
        g.textContent = "";
        mk("path", { d: gear(Z, r), "class": "gear", fill: col }, g);
        mk("circle", { r: Math.max(6, r * 0.18), "class": "hub" }, g);
        mk("line", { x1: 0, y1: 0, x2: r * 0.75, y2: 0, "class": "mark" }, g);
        var t = tx(g, 0, r + 26, lab, "glab", "middle"); t.setAttribute("data-norot", "1");
      }
      // engrenage
      var ZE = q("#ce-ze"), ZS = q("#ce-zs"), NE = q("#ce-ne"), CE = q("#ce-ce"), g1 = q("#ce-g1"), g2 = q("#ce-g2");
      var th = 0, ze, zs, ne, r1, r2, cx1, cx2, cy = 140, M = 4.2;
      function eng() {
        ze = +ZE.value; zs = +ZS.value; ne = +NE.value;
        r1 = M * ze / 2; r2 = M * zs / 2;
        var w = 2 * r1 + 2 * r2 + 4 * M;
        cx1 = (640 - w) / 2 + r1 + 2 * M; cx2 = cx1 + r1 + r2;
        g1.innerHTML = ""; g2.innerHTML = "";
        var a = mk("g", {}, g1), b = mk("g", {}, g2);
        gearG(a, ze, r1, "#9DB6D6", "menante"); gearG(b, zs, r2, "#DDBB8A", "menée");
        g1.__rot = a; g2.__rot = b;
        var r = ze / zs, ns = r * ne, ce = +CE.value;
        q("#ce-ze-o").textContent = ze; q("#ce-zs-o").textContent = zs;
        q("#ce-ne-o").textContent = fr(ne, 0) + " tr/min"; q("#ce-ce-o").textContent = ce + " N·m";
        setOut("ce-e-r", sig(r, 3));
        setOut("ce-e-n", fr(ns, 0) + " tr/min");
        setOut("ce-e-c", sig(ce / r, 3) + " N·m");
        setOut("ce-e-t", r < 1 ? "réduction : la vitesse baisse, le couple augmente" : (r > 1 ? "multiplication : la vitesse augmente, le couple baisse" : "même vitesse, même couple"));
        place();
      }
      function place() {
        var phi = 180 - 180 / zs;   // un creux de la roue menée face à une dent de la roue menante
        g1.setAttribute("transform", "translate(" + cx1 + "," + cy + ")");
        g2.setAttribute("transform", "translate(" + cx2 + "," + cy + ")");
        g1.__rot.firstChild.setAttribute("transform", "rotate(" + th.toFixed(2) + ")");
        g1.__rot.querySelector(".mark").setAttribute("transform", "rotate(" + th.toFixed(2) + ")");
        var t2 = phi - th * ze / zs;
        g2.__rot.firstChild.setAttribute("transform", "rotate(" + t2.toFixed(2) + ")");
        g2.__rot.querySelector(".mark").setAttribute("transform", "rotate(" + t2.toFixed(2) + ")");
      }
      [ZE, ZS, NE, CE].forEach(function (el) { el.addEventListener("input", eng); });
      eng();
      // pignon-crémaillère
      var RR = q("#ce-r"), NR = q("#ce-nr"), pin = q("#ce-pin"), rack = q("#ce-rack"), thc = 0, ZP = 20, YP = 186, rp, pitch;
      function cre() {
        var R = +RR.value, N = +NR.value, w = 2 * Math.PI * N / 60, v = w * R / 1000;
        rp = 1.5 * R; pitch = 2 * Math.PI * rp / ZP;
        pin.innerHTML = ""; var a = mk("g", {}, pin);
        gearG(a, ZP, rp, "#9DB6D6", ""); pin.__rot = a;
        rack.innerHTML = "";
        var m = 2 * rp / ZP, y0 = YP + 1.25 * m, d = "M0 " + (y0 + 22) + "V" + y0;
        for (var x = 0; x < 1400; x += pitch) d += "H" + (x + pitch * 0.23) + "L" + (x + pitch * 0.37) + " " + (y0 - 2.25 * m) + "H" + (x + pitch * 0.63) + "L" + (x + pitch * 0.77) + " " + y0 + "H" + (x + pitch);
        d += "V" + (y0 + 22) + "Z";
        rack.__p = mk("path", { d: d, "class": "gear", fill: "#DDBB8A" }, rack);
        rack.__y0 = y0;
        q("#ce-r-o").textContent = R + " mm"; q("#ce-nr-o").textContent = N + " tr/min";
        setOut("ce-c-w", sig(w, 3) + " rad/s");
        setOut("ce-c-v", sig(v, 3) + " m/s");
        setOut("ce-c-d", sig(v * 60, 3) + " m");
        placeC();
      }
      function placeC() {
        pin.setAttribute("transform", "translate(320," + (YP - rp) + ")");
        pin.__rot.firstChild.setAttribute("transform", "rotate(" + (thc + 90).toFixed(2) + ")");
        pin.__rot.querySelector(".mark").setAttribute("transform", "rotate(" + (thc + 90).toFixed(2) + ")");
        var off = ((-thc * Math.PI / 180 * rp) % pitch + pitch) % pitch;
        rack.__p.setAttribute("transform", "translate(" + (320 + off - Math.ceil(360 / pitch) * pitch) + ",0)");
      }
      [RR, NR].forEach(function (el) { el.addEventListener("input", cre); });
      cre();
      // vis-écrou
      var PP = q("#ce-p"), NV = q("#ce-nv"), screw = q("#ce-screw"), nut = q("#ce-nut"), xn = 0, thv = 0;
      function vis() {
        var p = +PP.value, N = +NV.value, v = p * N;
        q("#ce-p-o").textContent = fr(p, p % 1 ? 1 : 0) + " mm"; q("#ce-nv-o").textContent = N + " tr/min";
        setOut("ce-v-v", fr(v, 0) + " mm/min");
        setOut("ce-v-s", sig(v / 60, 3) + " mm/s");
        setOut("ce-v-t", fr(p, p % 1 ? 1 : 0) + " mm");
        screw.innerHTML = "";
        mk("rect", { x: 30, y: 70, width: 580, height: 30, "class": "screw" }, screw);
        var th = mk("g", { "class": "threads", "clip-path": "url(#ce-screw-clip)" }, screw), P = p * 6;
        for (var x = 30 - P; x < 610 + P; x += P) mk("line", { x1: x, y1: 100, x2: x + P * 0.6, y2: 70 }, th);
        screw.__th = th; screw.__P = P;
        nut.innerHTML = "";
        mk("rect", { x: -34, y: 52, width: 68, height: 66, rx: 4, "class": "nut" }, nut);
        tx(nut, 0, 140, "écrou : translation", "glab", "middle");
        tx(screw, 610, 56, "vis : rotation", "glab", "end");
      }
      [PP, NV].forEach(function (el) { el.addEventListener("input", vis); });
      vis();
      animers.push(function (dt) {
        if (calme) return;
        if (mode === "eng") { th = (th + ne / 3000 * 150 * dt) % 360000; place(); }
        else if (mode === "cre") { thc = (thc + (+NR.value) / 300 * 120 * dt) % 360000; placeC(); }
        else {
          var N = +NV.value, p = +PP.value;
          thv = (thv + N / 1500 * 2 * dt) % 1;   // nombre de tours affichés (ralenti)
          screw.__th.setAttribute("transform", "translate(" + (-(thv * screw.__P) % screw.__P) + ",0)");
          xn = (xn + N / 1500 * p / 10 * 60 * dt) % 520;
          nut.setAttribute("transform", "translate(" + (60 + xn) + ",0)");
        }
      });
    })();

    // ---------- 8.1 ordres de grandeur (échelle logarithmique) ----------
    (function () {
      var svg = q("#ce-pu-svg"); if (!svg) return;
      var DATA = [["Télévision", 100], ["Vélo électrique", 250], ["Radiateur électrique", 2e3], ["Voiture citadine", 75e3],
                  ["Camion semi-remorque", 350e3], ["Éolienne", 2e6], ["Train", 10e6], ["Avion", 80e6], ["Centrale nucléaire", 1e9]];
      var L = 180, R = 620, T = 16, ROW = 32, out = q("#ce-pu-txt"), tip = q("#ce-pu-tip"), sel = 5;
      function X(p) { return L + (Math.log10(p) - 1) / 9 * (R - L); }
      function unit(p) {
        var u = [["GW", 1e9], ["MW", 1e6], ["kW", 1e3], ["W", 1]];
        for (var i = 0; i < u.length; i++) if (p >= u[i][1]) return sig(p / u[i][1], 3) + " " + u[i][0];
        return sig(p, 3) + " W";
      }
      var B = T + DATA.length * ROW;
      for (var e = 1; e <= 10; e++) {
        mk("line", { x1: X(Math.pow(10, e)), x2: X(Math.pow(10, e)), y1: T - 6, y2: B, "class": "g" }, svg);
        tx(svg, X(Math.pow(10, e)), B + 16, unit(Math.pow(10, e)), "tick", "middle");
      }
      tx(svg, R, B + 34, "puissance (échelle logarithmique)", "axl", "end");
      var dots = DATA.map(function (d, i) {
        var y = T + i * ROW + ROW / 2;
        tx(svg, L - 10, y + 4, d[0], "rowl", "end");
        var g = mk("g", { "class": "pu-pt", tabindex: "0", role: "button", "aria-label": d[0] + " : " + unit(d[1]) }, svg);
        mk("line", { x1: X(10), x2: X(d[1]), y1: y, y2: y, "class": "stem" }, g);
        mk("circle", { cx: X(d[1]), cy: y, r: 13, "class": "hitc" }, g);
        mk("circle", { cx: X(d[1]), cy: y, r: 6, "class": "dot" }, g);
        tx(g, X(d[1]) + 12, y + 4, unit(d[1]), "vlab", "start");
        function pick() { sel = i; show(); }
        g.addEventListener("click", pick);
        g.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); pick(); } });
        g.addEventListener("pointerenter", function () {
          tip.textContent = d[0] + " : " + unit(d[1]); tip.hidden = false;
          var bx = svg.getBoundingClientRect(), wr = svg.parentNode.getBoundingClientRect();
          tip.style.left = Math.min(bx.left - wr.left + X(d[1]) / 640 * bx.width + 10, wr.width - tip.offsetWidth - 4) + "px";
          tip.style.top = (bx.top - wr.top + (y - 30) / 352 * bx.height) + "px";
        });
        g.addEventListener("pointerleave", function () { tip.hidden = true; });
        return g;
      });
      function show() {
        dots.forEach(function (g, i) { g.classList.toggle("sel", i === sel); });
        var d = DATA[sel], tv = d[1] / 100, rad = d[1] / 2000;
        out.textContent = d[0] + " : " + unit(d[1]) + ", soit la puissance de " + fr(tv, tv < 10 ? 1 : 0) + " téléviseur" + (tv > 1 ? "s" : "") +
          (d[1] >= 2000 ? " ou de " + fr(rad, rad < 10 ? 1 : 0) + " radiateur" + (rad > 1 ? "s" : "") + " de 2 kW." : ".");
      }
      show();
    })();

    // ---------- 8.2 calculateur d'énergie ----------
    (function () {
      var P = q("#ce-en-p"), Tm = q("#ce-en-t"); if (!P) return;
      function calc() {
        var p = parseFloat(P.value), t = parseFloat(Tm.value), wh = p * t;
        var ok = isFinite(wh) && p >= 0 && t >= 0;
        setOut("ce-en-wh", ok ? sig(wh, 4) + " Wh" : "–");
        setOut("ce-en-kwh", ok ? sig(wh / 1000, 4) + " kWh" : "–");
        setOut("ce-en-j", ok ? (wh * 3600 >= 1e6 ? sig(wh * 3600 / 1e6, 4) + " MJ" : sig(wh * 3600, 4) + " J") : "–");
      }
      [P, Tm].forEach(function (el) { el.addEventListener("input", calc); });
      qa("#ce-en .ce-presets button").forEach(function (b) {
        b.addEventListener("click", function () { P.value = b.getAttribute("data-p"); Tm.value = b.getAttribute("data-t"); calc(); });
      });
      calc();
    })();

    // ---------- 8.3 grandeurs d'effort et de flux ----------
    (function () {
      var box = q("#ce-ef"); if (!box) return;
      var CFG = JSON.parse(box.getAttribute("data-cfg")), A = q("#ce-ef-a"), Bv = q("#ce-ef-b"), cur = null;
      function calc() {
        var c = CFG[cur], a = parseFloat(A.value), b = parseFloat(Bv.value), p = a * b;
        setOut("ce-ef-p", isFinite(p) ? sig(p, 4) + " W" : "–");
        setOut("ce-ef-k", isFinite(p) ? (Math.abs(p) >= 1000 ? sig(p / 1000, 4) + " kW" : sig(p, 4) + " W") : "–");
        q("#ce-ef-w").textContent = cur === "rot" && isFinite(b) ? "ω = " + sig(b, 3) + " rad/s correspond à N = 30 ω / π ≈ " + fr(b * 30 / Math.PI, 0) + " tr/min." : "";
      }
      function pick(k) {
        cur = k; var c = CFG[k];
        qa(".ef-table tbody tr").forEach(function (tr) { tr.classList.toggle("sel", tr.getAttribute("data-ef") === k); });
        q("#ce-ef-t").textContent = "Calcul : " + c.n.toLowerCase();
        q("#ce-ef-la").textContent = c.a[0] + " (" + c.a[1] + ")"; q("#ce-ef-lb").textContent = c.b[0] + " (" + c.b[1] + ")";
        A.value = c.a[2]; Bv.value = c.b[2];
        q("#ce-ef-f").innerHTML = c.p;
        calc();
      }
      qa(".ef-table tbody tr").forEach(function (tr) {
        tr.addEventListener("click", function () { pick(tr.getAttribute("data-ef")); });
        tr.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(tr.getAttribute("data-ef")); } });
      });
      [A, Bv].forEach(function (el) { el.addEventListener("input", calc); });
      pick("trans");
    })();

    // ---------- bandes d'énergie : largeur proportionnelle à la puissance, pertes vers le haut ----------
    function bande(svg, Pa, etages, opts) {
      svg.textContent = "";
      var n = etages.length, x0 = 16, x1 = 624, yc = opts.yc || 150, Hmax = opts.hmax || 56, BH = 58, yl = opts.yl || 34;
      var bw = (x1 - x0) / (2 * n + 1), pad = Math.min(10, bw * 0.15), P = [Pa];
      etages.forEach(function (et) { P.push(P[P.length - 1] * et[1]); });
      var h = function (p) { return Math.max(1.5, p / Pa * Hmax); };
      // 1. bandes d'énergie utile (une par intervalle), 2. pertes, 3. blocs et textes par-dessus
      P.forEach(function (p, i) {
        var x = x0 + bw * 2 * i;
        mk("rect", { x: x, y: yc - h(p) / 2, width: bw, height: h(p), "class": "bd-u" }, svg);
        tx(svg, x + bw / 2, yc + Hmax / 2 + 20, sig(p, 3) + " W", "vlab", "middle");
      });
      etages.forEach(function (et, i) {
        var x = x0 + bw * (2 * i + 1), Lp = P[i] - P[i + 1], hl = h(Lp);
        mk("path", { d: "M" + (x + bw / 2 - hl / 2) + " " + (yc - BH / 2) + "V" + yl + "H" + (x + bw / 2 + hl / 2) + "V" + (yc - BH / 2) + "Z", "class": "bd-l" }, svg);
        tx(svg, x + bw / 2, yl - 8, "pertes " + sig(Lp, 3) + " W", "ann-t", "middle");
        mk("rect", { x: x - pad, y: yc - BH / 2, width: bw + 2 * pad, height: BH, rx: 3, "class": "bd-blk" }, svg);
        var mots = et[0].split(" "), l1 = et[0], l2 = "";
        if (et[0].length > 13 && mots.length > 1) { l1 = mots[0]; l2 = mots.slice(1).join(" "); }
        tx(svg, x + bw / 2, yc + (l2 ? -3 : 5), l1, "blk-n", "middle");
        if (l2) tx(svg, x + bw / 2, yc + 13, l2, "blk-n", "middle");
        tx(svg, x + bw / 2, yc + Hmax / 2 + 20, "η = " + fr(et[1], 2), "vlab eta", "middle");
      });
      return P[n];
    }

    // ---------- 8.5 le chargeur de téléphone ----------
    (function () {
      var svg = q("#ce-ch-svg"); if (!svg) return;
      var Pin = q("#ce-ch-p"), Lo = q("#ce-ch-l");
      function calc() {
        var p = +Pin.value, l = +Lo.value / 100, u = bande(svg, p, [["Transformateur 230 V → 5 V", 1 - l]], { yc: 128, hmax: 60, yl: 34 });
        q("#ce-ch-p-o").textContent = p + " W"; q("#ce-ch-l-o").textContent = Lo.value + " %";
        setOut("ce-ch-u", sig(u, 3) + " W"); setOut("ce-ch-x", sig(p - u, 3) + " W");
        setOut("ce-ch-e", fr(1 - l, 2) + " = " + fr((1 - l) * 100, 0) + " %");
      }
      [Pin, Lo].forEach(function (el) { el.addEventListener("input", calc); });
      calc();
    })();

    // ---------- rendements de quelques machines (barres horizontales) ----------
    (function () {
      var svg = q("#ce-rd-svg"); if (!svg) return;
      var D = [["Moteur à explosion", "thermique → mécanique", 40], ["Turbine à vapeur", "thermique → mécanique", 45],
               ["Chaudière", "thermique → thermique", 80], ["Alternateur", "mécanique → électrique", 95],
               ["Dynamo", "mécanique → électrique", 90], ["Pile", "chimique → électrique", 50],
               ["Accumulateur", "chimique → électrique", 70], ["Moteur électrique", "électrique → mécanique", 90],
               ["Radiateur", "électrique → thermique", 100], ["Lampe à filament", "électrique → lumineuse", 3],
               ["Cuve d'électrolyse", "électrique → chimique", 70]];
      D.sort(function (a, b) { return b[2] - a[2]; });
      var L = 220, R = 590, T = 10, ROW = 33, BH = 18, tip = q("#ce-rd-tip");
      function X(v) { return L + v / 100 * (R - L); }
      var B = T + D.length * ROW;
      [0, 25, 50, 75, 100].forEach(function (v) {
        mk("line", { x1: X(v), x2: X(v), y1: T, y2: B, "class": v ? "g" : "g0" }, svg);
        tx(svg, X(v), B + 16, v + " %", "tick", "middle");
      });
      tx(svg, R, B + 34, "rendement", "axl", "end");
      D.forEach(function (d, i) {
        var y = T + i * ROW + (ROW - BH) / 2, w = Math.max(0.5, X(d[2]) - L), r = Math.min(4, w / 2);
        tx(svg, L - 10, y + 8, d[0], "rowl", "end");
        tx(svg, L - 10, y + 21, d[1], "rows", "end");
        var g = mk("g", { "class": "rd-b", tabindex: "0", "aria-label": d[0] + ", " + d[1] + " : " + d[2] + " %" }, svg);
        mk("rect", { x: L - 2, y: T + i * ROW, width: R - L + 60, height: ROW, "class": "hitr" }, g);
        mk("path", { d: "M" + L + " " + y + "H" + (L + w - r) + "A" + r + " " + r + " 0 0 1 " + (L + w) + " " + (y + r) + "V" + (y + BH - r) + "A" + r + " " + r + " 0 0 1 " + (L + w - r) + " " + (y + BH) + "H" + L + "Z", "class": "bar" }, g);
        tx(g, L + w + 6, y + 13, d[2] + " %", "vlab", "start");
        function on() {
          tip.textContent = d[0] + " — " + d[1] + " : " + d[2] + " %"; tip.hidden = false;
          var bx = svg.getBoundingClientRect(), wr = svg.parentNode.getBoundingClientRect();
          tip.style.left = Math.min(bx.left - wr.left + (L + w) / 640 * bx.width + 40, wr.width - tip.offsetWidth - 4) + "px";
          tip.style.top = (bx.top - wr.top + y / 420 * bx.height - 4) + "px";
        }
        g.addEventListener("pointerenter", on); g.addEventListener("focus", on);
        g.addEventListener("pointerleave", function () { tip.hidden = true; }); g.addEventListener("blur", function () { tip.hidden = true; });
      });
    })();

    // ---------- 8.6 rendement global de la chaîne de la trottinette ----------
    (function () {
      var svg = q("#ce-gl-svg"); if (!svg) return;
      var Pa = q("#ce-gl-p"), E = qa('#ce-gl input[id^="ce-eta"]'), NOMS = ["Alimenter", "Distribuer", "Convertir", "Transmettre"];
      function calc() {
        var p = +Pa.value, et = E.map(function (e, i) { return [NOMS[i], +e.value]; });
        var u = bande(svg, p, et, { yc: 150, hmax: 60, yl: 34 });
        var g = et.reduce(function (a, e) { return a * e[1]; }, 1), mn = et.reduce(function (a, e) { return e[1] < a[1] ? e : a; });
        q("#ce-gl-p-o").textContent = p + " W";
        E.forEach(function (e, i) { q("#ce-eta" + i + "-o").textContent = fr(+e.value, 2); });
        setOut("ce-gl-e", fr(g, 3) + " ≈ " + fr(g * 100, 1) + " %");
        setOut("ce-gl-u", sig(u, 3) + " W"); setOut("ce-gl-x", sig(p - u, 3) + " W");
        setOut("ce-gl-m", mn[0] + " (" + fr(mn[1], 2) + ")");
        q("#ce-gl-v").textContent = "η global = " + fr(g, 3) + (g <= mn[1] + 1e-12 ? " ≤ " : " > ") + fr(mn[1], 2) +
          " : le rendement global ne dépasse jamais celui du plus faible étage.";
      }
      [Pa].concat(E).forEach(function (el) { el.addEventListener("input", calc); });
      calc();
    })();

    // ---------- 8.7 autonomie d'une batterie ----------
    (function () {
      var C = q("#ce-au-c"), I = q("#ce-au-i"), U = q("#ce-au-u"); if (!C) return;
      function calc() {
        var c = +C.value, i = +I.value, u = +U.value, t = c / i;
        q("#ce-au-c-o").textContent = fr(c, 1) + " Ah"; q("#ce-au-i-o").textContent = fr(i, 1) + " A";
        q("#ce-au-u-o").textContent = fr(u, 1) + " V";
        setOut("ce-au-t", sig(t, 3) + " h");
        var h = Math.floor(t + 1e-9), m = Math.round((t - h) * 60);
        if (m === 60) { h++; m = 0; }
        setOut("ce-au-m", h ? h + " h " + (m < 10 ? "0" : "") + m + " min" : m + " min");
        setOut("ce-au-e", sig(u * c, 3) + " Wh");
      }
      [C, I, U].forEach(function (el) { el.addEventListener("input", calc); });
      qa("#ce-au .ce-presets button").forEach(function (b) {
        b.addEventListener("click", function () { C.value = b.getAttribute("data-c"); I.value = b.getAttribute("data-i"); U.value = b.getAttribute("data-u"); calc(); });
      });
      calc();
    })();

    // ---------- jeux, quiz, impression ----------
    qa(".jeu").forEach(initJeu);
    initQuiz(home);
    q(".cours-print").addEventListener("click", function () { window.print(); });

    // une seule boucle d'animation pour toute la page
    var last = performance.now();
    function loop(now) {
      var dt = Math.max(0, Math.min(0.1, (now - last) / 1000)); last = now;   // la 1re image peut dater d'avant l'initialisation
      animers.forEach(function (f) { f(dt); });
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
    window.__cours2__ = { animers: animers.length };
  }
"""

COURS_2_CSS = """
/* ---------- cours 2 : chaîne d'énergie ---------- */
body.page-cours-chaine-energie .home-inner{max-width:1180px}
.c2-fiche{display:grid; grid-template-columns:minmax(0,1.1fr) minmax(0,1.4fr) minmax(0,.8fr); gap:12px; margin:0 0 14px}
.c2-fiche>div{background:var(--papier); border:1.5px solid var(--encre); padding:6px 14px 10px}
.c2-fiche h3{margin:4px 0 6px; font:700 1rem var(--f-titre)}
.c2-fiche ul{margin:0; padding-left:1.1rem; font-size:.9rem} .c2-fiche li{margin:.2rem 0}
.c2-fiche .t{font-size:.84rem; margin:0}
@media (max-width:900px){ .c2-fiche{grid-template-columns:1fr} }
/* figures animées */
.ce-fig{margin:8px 0 14px}
.ce-fbtns{display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; margin:0 0 8px}
.ce-fb{border:1.5px solid var(--encre); background:#fff; padding:5px 11px; font:600 .9rem var(--f-titre); cursor:pointer; border-bottom-width:4px}
.ce-fb.k-info{border-bottom-color:var(--bleu)} .ce-fb.k-ener{border-bottom-color:var(--orange)}
.ce-fb[aria-pressed="true"]{background:var(--encre); color:var(--jaune)}
.ce-svg{display:block; width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin)}
.ce-svg text{font-family:var(--f-texte)}
.ce-ftxt{background:var(--jaune-pale); border-left:5px solid var(--jaune); padding:8px 12px; margin:8px 0 0; min-height:2.6em}
.bx-sys{fill:#FFFBEA; stroke:#E7C96A; stroke-width:1.5}
.bx-cap{font-size:15px; fill:var(--encre-2)}
.bx-u{fill:#FBEFF4; stroke:#B0306A; stroke-width:1.5}
.bx-i{fill:var(--bleu-pale); stroke:var(--bleu); stroke-width:2}
.bx-e{fill:var(--orange-pale); stroke:var(--orange); stroke-width:2}
.bx-a{fill:var(--vert-pale); stroke:var(--vert); stroke-width:2}
.bx-mo{fill:#F4F5F2; stroke:var(--trait); stroke-width:1.5}
.bx-t{font-size:15px; font-weight:700; fill:var(--encre)}
.f1-fl,.f2-fl{fill:none; stroke-width:2.5; transition:stroke-width .2s, opacity .2s}
.f1-fl.k-info{stroke:#7FA3CF; marker-end:url(#f1-ai)} .f1-fl.k-ener{stroke:#D3A35E; marker-end:url(#f1-ae)}
.f1-fl.on{stroke-width:4.5} .f1-fl.k-info.on{stroke:var(--bleu)} .f1-fl.k-ener.on{stroke:var(--orange)}
#ce-f1.focus .f1-fl:not(.on){opacity:.35}
.f1-mo{fill:none; stroke:var(--vert); stroke-width:3; marker-end:url(#f1-am)}
.fl-l{font-size:13px; font-weight:600; paint-order:stroke; stroke:#fff; stroke-width:4px; stroke-linejoin:round}
.fl-l.i{fill:var(--bleu)} .fl-l.e{fill:var(--orange)}
.f2-fl{stroke:#D3A35E; marker-end:url(#f2-ae)} .f2-fl.on{stroke:var(--orange); stroke-width:4}
.f2-cmd{stroke:var(--bleu); stroke-width:2; fill:none; marker-end:url(#f1-ai)}
.ce-blk{cursor:pointer}
.ce-blk rect{fill:#F1F8E9; stroke:var(--vert); stroke-width:2; transition:fill .2s}
.ce-blk:hover rect,.ce-blk:focus rect{fill:var(--jaune-pale)}
.ce-blk.sel rect{fill:var(--jaune-pale); stroke:var(--encre); stroke-width:3}
.ce-blk:focus{outline:none}
.blk-t{font-size:15px; font-weight:700; fill:var(--encre)}
.blk-c{font-size:13.5px; font-weight:600; fill:var(--vert)}
.pw-l{font-size:12.5px; fill:var(--encre-2)} .pw-l.i{fill:var(--bleu); font-weight:600}
.ce-dot{stroke:#fff; stroke-width:1.5} .ce-dot.k-info{fill:var(--bleu)} .ce-dot.k-ener{fill:#E98A00}
/* fiches des composants */
.cata{margin:10px 0 14px}
.cata-list{display:grid; grid-template-columns:repeat(auto-fill,minmax(132px,1fr)); gap:8px; margin:0 0 10px}
.cata-it{display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px; border:1.5px solid var(--trait); background:#fff; cursor:pointer; font:600 .85rem/1.2 var(--f-titre); text-align:center}
.cata-it img{width:100%; height:72px; object-fit:contain}
.cata-it:hover{border-color:var(--encre); background:var(--jaune-pale)}
.cata-it[aria-pressed="true"]{border:2.5px solid var(--encre); background:var(--jaune-pale); box-shadow:inset 0 -4px 0 var(--jaune)}
.fiche-c{border:2px solid var(--encre); border-left:8px solid var(--jaune); background:#fff; padding:8px 14px 12px}
.fiche-c h4{margin:2px 0 8px; font:700 1.2rem var(--f-titre)}
.fc-grid{display:grid; grid-template-columns:minmax(0,220px) minmax(0,1fr) minmax(0,240px); gap:12px 18px; align-items:start}
.fc-grid figure{margin:0}
.fc-ph img,.fc-sy img{display:block; width:100%; height:auto; max-height:200px; object-fit:contain}
.fc-sy{border:1px solid var(--trait-fin); padding:6px}
.fc-sy figcaption{font:700 .78rem var(--f-titre); color:var(--encre-2); text-transform:uppercase; letter-spacing:.04em; margin-top:4px}
.fc-nosy span{display:block; padding:24px 6px; text-align:center; color:var(--encre-2); font-style:italic}
.fiche-c dl{margin:0}
.fiche-c dt{font:700 .8rem var(--f-titre); color:var(--encre-2); text-transform:uppercase; letter-spacing:.04em; margin-top:6px}
.fiche-c dt:first-child{margin-top:0}
.fiche-c dd{margin:2px 0 0}
@media (max-width:900px){ .fc-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)} .fiche-c dl{grid-column:1/-1; grid-row:1} }
@media (max-width:520px){ .fc-grid{grid-template-columns:1fr} }
/* graphiques et simulateurs */
.osc-wrap{position:relative}
.osc{display:block; width:100%; max-width:780px; height:auto; background:#fff; border:1px solid var(--trait-fin); font-family:var(--f-texte)}
.osc:focus-visible{outline:3px solid var(--bleu); outline-offset:2px}
.osc .g{stroke:#E3E6E2; stroke-width:1} .osc .g0{stroke:#A5ADAA; stroke-width:1}
.osc .tick{font-size:11.5px; fill:var(--encre-2)} .osc .axl{font-size:12px; font-weight:600; fill:var(--encre-2)}
.osc .crv{fill:none; stroke-width:2; stroke-linejoin:round; stroke-linecap:round}
.osc .ann-l{stroke:#8A939B; stroke-width:1; fill:none}
.osc .ann-t{font-size:12.5px; font-weight:600; fill:var(--encre); paint-order:stroke; stroke:#fff; stroke-width:4px; stroke-linejoin:round}
.osc .key{stroke-width:3}
.osc .osc-x{stroke:var(--encre); stroke-width:1; display:none}
.osc .osc-hit{fill:transparent; cursor:crosshair}
.osc-tip{position:absolute; z-index:3; background:var(--encre); color:#fff; padding:5px 9px; font-size:.85rem; line-height:1.35; pointer-events:none; border-radius:2px; max-width:260px}
.osc-tip b{display:block; color:#C9D1D8; font-weight:600}
.osc-tip span{display:block} .osc-tip strong{font-weight:700}
.osc-tip i,.osc-leg i{display:inline-block; width:16px; height:0; border-top:3px solid; margin-right:6px; vertical-align:middle}
.osc-leg{display:flex; flex-wrap:wrap; gap:4px 16px; margin:6px 0 0; font-size:.88rem; color:var(--encre-2)}
.osc-leg:empty{display:none}
.osc-src{display:flex; flex-wrap:wrap; gap:6px 18px; margin:0 0 8px; font-weight:600}
.osc-src label{cursor:pointer}
.osc-vent{display:flex; flex-wrap:wrap; align-items:center; gap:4px 10px; margin:0 0 8px; font-weight:600}
.osc-vent[hidden]{display:none}
.osc-vent input{flex:1 1 200px; accent-color:var(--bleu)}
.simu .chk{flex-direction:row!important; align-items:center; gap:8px!important; align-self:end}
.hach-row{display:grid; grid-template-columns:minmax(0,780px) 120px; gap:16px; align-items:center; margin-top:10px}
.hach-mot{width:120px; height:140px}
.hach-mot circle{fill:#fff; stroke:var(--encre); stroke-width:3}
.hach-mot #ce-rotor line{stroke:var(--orange); stroke-width:5; stroke-linecap:round}
.hach-mot #ce-rotor circle{fill:var(--orange); stroke:none}
.hach-mot .axe{fill:var(--encre)}
.hach-mot text{font:700 14px var(--f-titre); fill:var(--encre)}
@media (max-width:560px){ .hach-row{grid-template-columns:1fr} .hach-mot{margin:0 auto} }
.ce-tabs{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 10px}
.ce-tab{border:1.5px solid var(--encre); background:var(--papier); padding:5px 12px; font:600 .95rem var(--f-titre); cursor:pointer}
.ce-tab[aria-pressed="true"]{background:var(--encre); color:var(--jaune)}
.mec{display:block; width:100%; max-width:780px; height:auto; background:#fff; border:1px solid var(--trait-fin); margin-top:10px}
.mec .gear{stroke:var(--encre); stroke-width:1.5; stroke-linejoin:round}
.mec .hub{fill:#fff; stroke:var(--encre); stroke-width:1.5}
.mec .mark{stroke:var(--encre); stroke-width:3; stroke-linecap:round}
.mec .glab{font:600 13px var(--f-texte); fill:var(--encre-2)}
.mec .screw{fill:#E3E6E2; stroke:var(--encre); stroke-width:1.5}
.mec .threads line{stroke:#8A939B; stroke-width:2}
.mec .nut{fill:#DDBB8A; stroke:var(--encre); stroke-width:1.5}
.osc .rowl{font-size:12.5px; font-weight:600; fill:var(--encre)} .osc .rows{font-size:11px; fill:var(--encre-2)}
.osc .vlab{font-size:12px; font-weight:600; fill:var(--encre)}
.pu-pt{cursor:pointer} .pu-pt:focus{outline:none}
.pu-pt .stem{stroke:#C9D3DF; stroke-width:2}
.pu-pt .dot{fill:var(--bleu); stroke:#fff; stroke-width:2}
.pu-pt .hitc{fill:transparent}
.pu-pt:hover .dot,.pu-pt:focus .dot{r:8}
.pu-pt.sel .dot{fill:var(--orange); r:8} .pu-pt.sel .stem{stroke:#E5C08A}
.rd-b .bar{fill:var(--bleu)} .rd-b .hitr{fill:transparent}
.rd-b:hover .bar,.rd-b:focus .bar{fill:#3B7BC4} .rd-b:focus{outline:none}
.sk .bd-u{fill:#E9B261} .sk .bd-l{fill:#C3C9CE} .sk .bd-blk{fill:#fff; stroke:var(--encre); stroke-width:1.5}
.sk .eta{fill:var(--encre-2)}
.sk .blk-n{font-size:12.5px; font-weight:700; fill:var(--encre)}
.ce-presets{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 10px}
.ce-presets .btn{padding:4px 10px; font-size:.88rem}
.simu-grid input[type=number]{padding:5px 8px; border:1.5px solid var(--encre-2); background:#fff; font:inherit; max-width:220px}
.ef-table tbody tr{cursor:pointer}
.ef-table tbody tr:hover,.ef-table tbody tr.sel{background:var(--jaune-pale)}
.tview{margin-top:8px; background:#fff; border:1px dashed var(--bleu); padding:6px 10px}
.tview summary{cursor:pointer; font-weight:600}
.tview ul.cols{columns:2; column-gap:28px; margin:.4rem 0}
.agir{display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:12px}
.agir-c{margin:0; border:1.5px solid var(--encre); background:#fff; padding:8px}
.agir-c img{display:block; width:100%; height:130px; object-fit:cover}
.agir-c figcaption{margin-top:6px} .agir-c b{display:block; font-family:var(--f-titre)} .agir-c span{font-size:.9rem; color:var(--encre-2)}
@media print{
  .fiche-c[hidden]{display:block!important; break-inside:avoid; margin-bottom:6px}
  .cata-list,.ce-fbtns,.ce-presets,.ce-tabs,.cours-defi,.osc-tip{display:none!important}
  .tview{border:0} .tview>*{display:block!important}
  .ce-pane[hidden]{display:block!important}
}
"""

# ============================================================ COURS — assemblage


# le cours 3 vit dans son propre module ; il reçoit les éléments communs des cours
AIDES_COURS = types.SimpleNamespace(course_head=course_head, course_section=course_section, course_nav=course_nav,
                                    quiz_section=quiz_section, jeu_html=jeu_html, HOUSE=HOUSE)
COURS_RENDER = {"cours-chaine-fonctionnelle": render_cours_portail, "cours-chaine-energie": render_cours_energie,
                "cours-chaine-information": lambda: cours_information.render(AIDES_COURS)}
COURS_JS = (COURS_COMMUN_JS + cours_portail_js() + COURS_2_JS + cours_information.ci_js() +
            '\n  var INIT = { "cours-chaine-fonctionnelle": initCoursPortail, "cours-chaine-energie": initCoursEnergie, '
            '"cours-chaine-information": initCoursInformation };\n')
COURS_CSS = COURS_COMMUN_CSS + PORTAIL_CSS + COURS_2_CSS + cours_information.CI_CSS


# ============================================================ AIGUILLAGE
ROUTER_JS = r"""<script>/* Aiguillage : accueil, cours ou exercice selon ?ex=… — s'exécute avant les moteurs du gabarit */
(function () {
  "use strict";
  var EXOS = window.__EXOS__, ex = new URLSearchParams(location.search).get("ex") || "";
  function $(s) { return document.querySelector(s); }
  function tpl(id) { return document.getElementById(id).innerHTML; }__COURS_JS__
  var home = $("#home .home-inner");
  window.__PARTS__ = []; window.__QCFG__ = {}; window.__SKCFG__ = {}; window.__CONSEIL_MIN__ = 0;
  if (Object.prototype.hasOwnProperty.call(EXOS, ex)) {
    var E = EXOS[ex];
    window.__PARTS__ = E.parts; window.__QCFG__ = E.qcfg; window.__SKCFG__ = E.skcfg;
    window.__CONSEIL_MIN__ = E.minutes;
    document.title = E.title + " — __TITRE__ — exercice interactif";
    document.body.classList.add("exo-" + ex);
    $(".rail").innerHTML = tpl("tpl-rail-" + ex) + '<div class="grp" aria-hidden="true"></div>' +
      '<a class="tab tab-home" href="?" title="Retour à l\'accueil" aria-label="Retour à l\'accueil">__HOUSE__</a>';
    $(".dp-tabs").innerHTML = tpl("tpl-tabs-" + ex);
    $(".dp-body").innerHTML = tpl("tpl-docs-" + ex);
    $("#parts").innerHTML = tpl("tpl-parts-" + ex);
    $(".consignes").innerHTML = tpl("tpl-consignes-" + ex);
    home.innerHTML = tpl("tpl-home-" + ex) + tpl("tpl-modes");
    $(".cartouche h1").textContent = E.title;
    $(".cartouche .title p").textContent = E.cartouche;
    Array.prototype.forEach.call(document.querySelectorAll(".print-conseil"), function (el) { el.textContent = E.duree; });
  } else {
    document.body.classList.add("hub");
    var page = document.getElementById("tpl-" + ex) && /^cours-/.test(ex) ? "tpl-" + ex : "tpl-hub";
    home.innerHTML = tpl(page);
    if (page !== "tpl-hub") {
      document.body.classList.add("cours-page", "page-" + ex);
      if (typeof INIT[ex] === "function") INIT[ex](home);
      document.title = home.querySelector("h1").textContent + " — cours — __TITRE__";
    } else document.title = "__TITRE__ — cours et exercices interactifs";
  }
})();
</script>"""


CONTENT_CSS = """<style>
/* ---------- compléments de contenu (hors gabarit) : écriture des calculs, documents ---------- */
.eq{margin:.35rem 0 .55rem; overflow-x:auto; line-height:2.1}
.frac{display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 .12em; line-height:1.25}
.frac>span{padding:0 .25em; white-space:nowrap}
.frac>span:first-child{border-bottom:1px solid currentColor}
.doc-text ol,.doc-text ul{padding-left:1.2rem}
.doc-text li{margin:.2rem 0}
.dp-svg{display:block; width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin); margin:10px 0; font-family:var(--f-texte)}
.doc-text tr.dt-i td:first-child{border-left:5px solid var(--bleu)}
.doc-text tr.dt-e td:first-child{border-left:5px solid var(--orange)}
.calc{display:inline-block; font:600 .9rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; background:#fff; border:1px solid var(--trait); padding:2px 8px; margin:2px 0}
.cours-split{display:flex; gap:18px; align-items:flex-start; flex-wrap:wrap}
.cours-split>div{flex:1 1 300px}
.cours-split>.fig{flex:0 1 auto; margin:0 auto}
.part-body .fig{margin:14px auto}

/* ---------- questions à plusieurs cases (mécanisme « fast-q » du gabarit) ---------- */
.grp{margin:14px 0 6px; padding:10px 0 12px 14px; border-left:3px solid var(--trait-fin)}
.grp-fields{display:flex; flex-direction:column; gap:6px; margin:8px 0 4px; max-width:820px}
.grp-l{display:grid; grid-template-columns:minmax(150px,.9fr) minmax(0,1.3fr); gap:4px 14px; align-items:center; padding:2px 0; border-bottom:1px dashed var(--trait-fin)}
.grp-lab{font-size:.95rem}
.grp .sol{display:flex; align-items:center; gap:8px}
/* étiquettes à glisser (ou toucher puis toucher la case) ; le champ lu par le moteur est masqué */
.bank{display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:8px 0 10px; padding:8px 10px; background:var(--bleu-pale); border:1px solid var(--trait-fin); max-width:820px}
.bank-t{font:700 .78rem var(--f-titre); text-transform:uppercase; letter-spacing:.04em; color:var(--encre-2); margin-right:4px}
.etq{font:600 .9rem var(--f-texte); color:var(--encre); background:#fff; border:1.5px solid var(--bleu); border-radius:3px; padding:5px 10px; cursor:grab; touch-action:manipulation; user-select:none}
.etq:hover{background:#EAF1FA}
.etq:focus-visible,.dz:focus-visible{outline:3px solid var(--jaune); outline-offset:1px}
.etq[aria-pressed="true"]{background:var(--bleu); color:#fff}
.etq.is-drag{opacity:.45}
.etq:disabled{cursor:default; opacity:.5; background:#fff; color:var(--encre)}
.dz{flex:1 1 auto; min-width:0; min-height:40px; text-align:left; font:600 .95rem var(--f-texte); color:var(--encre); background:#fff; border:1.5px dashed var(--encre-2); border-radius:3px; padding:7px 10px; cursor:pointer}
.dz .dz-v{display:block}
.dz:not(.filled) .dz-v{font-weight:400; font-style:italic; color:#7A848C}
.dz.filled{border-style:solid; border-color:var(--bleu); cursor:grab}
.grp.picking .dz:not(:disabled),.dz.over{background:var(--jaune-pale); border-color:var(--orange)}
.dz:disabled{cursor:default; background:#F2F3F1}
.grp .sol.is-ok .dz{border:2px solid var(--vert); background:var(--vert-pale)}
.grp .sol.is-ko .dz{border:2px solid var(--rouge); background:var(--rouge-pale)}
.grp .sol .mark{flex:0 0 4.6em; font-size:.82rem; font-weight:700}
.grp .sol.is-ok .mark{color:var(--vert)} .grp .sol.is-ko .mark{color:var(--rouge)}
.grp .fast-foot .q-status{font-weight:700}
.grp-sol{max-width:780px; margin:4px 0 8px}
.grp-sol td:last-child{font-weight:600}
.q-why .why-t{font:700 .95rem var(--f-titre); margin:.6rem 0 .2rem}
.q-why .compo{max-width:640px}
@media (max-width:620px){ .grp-l{grid-template-columns:minmax(0,1fr)} }

/* ---------- accueil, cours et retour (d'après le dépôt RDM) ---------- */
a.btn{display:inline-flex; align-items:center; gap:8px; text-decoration:none}
a.btn svg,.c-top svg{width:18px; height:18px; flex:0 0 auto}
.tab-home{display:flex; align-items:center; justify-content:center; padding:8px 0 8px 4px; background:var(--encre); color:var(--jaune); text-decoration:none}
.tab-home svg{width:22px; height:22px; display:block}
.tab-home:hover{background:#2E3B47}
.c-top{margin:0 0 12px}
.c-top a{display:inline-flex; align-items:center; gap:6px; font:600 .95rem var(--f-titre); color:var(--encre); text-decoration:none; border:1.5px solid var(--encre); background:var(--papier); padding:5px 12px 5px 10px}
.c-top a:hover{background:var(--jaune-pale)}
#home{padding:20px 20px 32px}
.home-top{display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:14px; align-items:stretch; margin:0 0 14px}
.home-top-single{grid-template-columns:1fr}
.home-top-l{display:flex; flex-direction:column; gap:10px; min-width:0}
.home-top .home-head{padding:14px 20px; flex:1}
.home-top .home-head h1{margin:6px 0 6px; font-size:clamp(1.4rem,2.4vw,1.85rem)}
.home-top .home-sub{font-size:.95rem}
.home-top .home-hero{margin:0; padding:8px; display:flex; flex-direction:column; justify-content:center; min-width:0}
.home-top .home-hero img{width:auto!important; max-width:100%; max-height:160px; margin:0 auto}
body.hub .home-top .home-hero img{max-height:210px}
.home-top .home-hero figcaption{font-size:.78rem; line-height:1.3; margin-top:4px}
.home-top .home-facts{grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin:0}
.home-top .home-facts div{padding:6px 10px}
.home-top .home-facts b{font-size:1.02rem}
.home-top .home-facts span{font-size:.76rem; line-height:1.3; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
@media (max-width:980px){ .home-top .home-facts{grid-template-columns:repeat(2,minmax(0,1fr))} }
@media (max-width:820px){ .home-top{grid-template-columns:1fr} }
#home .home-choose{margin:18px 0 8px; font-size:1.25rem}
#home .mode-card{padding:12px 18px 14px}
#home .mode-card .mc-lead{margin:2px 0 4px; font-size:.92rem}
#home .mode-card ul{margin:0 0 10px; font-size:.9rem; line-height:1.45}
#home .mode-card li{margin:.15rem 0}
#home .mode-card .btn{padding:9px 16px}
#home .home-note{margin:10px 0 0}
.home-back{margin:12px 0 0}
.ex-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:16px}
.ex-grid .mode-card p{margin:4px 0 8px; font-size:.95rem}
.ex-grid .mode-card .ex-meta{margin:0 0 12px; font-size:.85rem}
.ex-grid .mode-card h3{font-size:1.2rem}
.ex-grid .mc-head{flex-direction:column; align-items:flex-start; gap:6px}
.ex-grid .mode-card .btn{margin-top:auto; align-self:flex-start}
.ex-grid .en-edition{border-style:dashed; border-color:var(--trait)}
.ex-grid .en-edition h3,.ex-grid .en-edition p{color:var(--encre-2)}
.ex-grid .etat{font-weight:700; color:var(--orange)}
.cours-grid{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.pastille{display:inline-block; font:700 .72rem var(--f-titre); letter-spacing:.03em; background:var(--vert); color:#fff; padding:2px 8px; margin-left:6px; vertical-align:middle}
.pastille.n2{background:var(--bleu)}
.mc-tag .pastille{margin-left:8px; font-size:.68rem; padding:1px 6px}

__COURS_CSS__
@media print{
  .c-top,.home-back{display:none!important}
  /* correctif repris du dépôt RDM : dans le gabarit, « .sketch .q-expl[hidden] » l'emporte sur
     « body:not(.corrections-open) .q-expl » et imprimerait la correction des tracés avant la remise de la copie */
  body:not(.corrections-open) .sketch .q-expl[hidden]{display:none!important}
  .eq{overflow:visible; line-height:1.7}
  .grp-l{break-inside:avoid}
  .bank{background:none; padding:4px 0; border:0} .etq{border-width:1px; padding:1px 6px; font-size:8.5pt}
  .dz{min-height:0; padding:3px 8px} .dz:not(.filled) .dz-v{visibility:hidden}
}
</style>"""


# ============================================================ PAGE « FORMULAIRE »
def build_formulaire():
    """formulaire.html : la page d'origine, augmentée de liens vers l'accueil (remplacements vérifiés)."""
    f = FORMULAIRE_SRC.read_text(encoding="utf-8")
    lien = '<a class="linkbtn" href="index.html">Accueil : chaîne fonctionnelle</a>'
    f = sub_once(f, r'<header class="home-head">\n      <h1 id="menu-title">',
                 f'<header class="home-head">\n      <p class="crumb">{lien}</p>\n      <h1 id="menu-title">')
    f = sub_once(f, r'<p class="crumb no-print"><button type="button" class="linkbtn" data-go="menu">Retour au menu</button></p>',
                 '<p class="crumb no-print"><button type="button" class="linkbtn" data-go="menu">Retour au menu</button>'
                 f' · {lien}</p>')
    f = sub_once(f, r'<p class="crumb"><button type="button" class="linkbtn" data-go="menu">Retour au menu</button></p>',
                 '<p class="crumb"><button type="button" class="linkbtn" data-go="menu">Retour au menu</button>'
                 f' · {lien}</p>')
    # pas de pastilles « Vu dans » (Cours, TD, A1…) : elles renvoient à des séances qui ne sont pas celles du site
    f = sub_once(f, r'    if \(L\.vu && L\.vu\.length\) \{\n.*?\n.*?\n      h \+= "</ul>";\n    \}\n', "",
                 flags=re.S)
    FORMULAIRE.write_text(f, encoding="utf-8")
    return f


# ============================================================ ASSEMBLAGE
DECOR_JS = """  var DECOR = {
    // aucun tracé dans les exercices actuels : une entrée par fond de tracé (voir le dépôt RDM)
  };
"""
DR_NAMES_JS = """  var DR_NAMES = {
    // aucun tracé dans les exercices actuels
  };
"""
DATA_RE = re.compile(r"data:image/(?:png|jpeg);base64,[A-Za-z0-9+/=]+")


ETIQUETTES_JS = r"""<script>/* Étiquettes : glisser une étiquette sur une case, ou la toucher puis toucher la case.
   La case garde le champ (masqué) que lit le moteur du gabarit ; on y écrit l'étiquette et on signale « input ». */
(function () {
  "use strict";
  var parts = document.getElementById("parts");
  if (!parts || !parts.querySelector(".fast-q .bank")) return;
  var sel = null, drag = null;
  function grp(el) { return el.closest(".fast-q"); }
  function inp(dz) { return dz.parentNode.querySelector("input"); }
  function locked(el) { return !!el.closest(".fast-q").querySelector(".btn-fast:disabled") || document.body.classList.contains("graded"); }
  function choisir(b) {
    if (sel) { sel.setAttribute("aria-pressed", "false"); grp(sel).classList.remove("picking"); }
    sel = b && b !== sel ? b : null;
    if (sel) { sel.setAttribute("aria-pressed", "true"); grp(sel).classList.add("picking"); }
  }
  function poser(dz, v) {
    var i = inp(dz);
    if (i.disabled) return;
    i.value = v;
    dz.classList.toggle("filled", !!v);
    dz.querySelector(".dz-v").textContent = v || "case vide";
    dz.draggable = !!v;
    i.dispatchEvent(new Event("input", { bubbles: true }));
  }
  parts.addEventListener("click", function (e) {
    var b = e.target.closest(".etq"), dz = e.target.closest(".dz");
    if (b && !b.disabled) { choisir(b); return; }
    if (!dz || dz.disabled) return;
    if (sel && grp(sel) === grp(dz)) { poser(dz, sel.textContent); choisir(null); dz.focus(); }
    else if (inp(dz).value) poser(dz, "");
    else { choisir(null); grp(dz).querySelector(".q-msg").textContent = "Choisis d'abord une étiquette dans la liste, puis touche la case."; }
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && sel) choisir(null); });
  parts.addEventListener("dragstart", function (e) {
    var b = e.target.closest && e.target.closest(".etq, .dz");
    if (!b || b.disabled || locked(b)) { e.preventDefault(); return; }
    var v = b.classList.contains("dz") ? inp(b).value : b.textContent;
    if (!v) { e.preventDefault(); return; }
    drag = { v: v, from: b.classList.contains("dz") ? b : null, g: grp(b), el: b };
    choisir(null);
    b.classList.add("is-drag");
    e.dataTransfer.effectAllowed = "copyMove";
    e.dataTransfer.setData("text/plain", v);
  });
  parts.addEventListener("dragend", function () {
    if (drag) drag.el.classList.remove("is-drag");
    Array.prototype.forEach.call(parts.querySelectorAll(".dz.over"), function (d) { d.classList.remove("over"); });
    drag = null;
  });
  function cible(e) {
    if (!drag) return null;
    var t = e.target.closest && e.target.closest(".dz, .bank");
    return t && grp(t) === drag.g && !(t.classList.contains("dz") && t.disabled) ? t : null;
  }
  parts.addEventListener("dragover", function (e) {
    var t = cible(e);
    if (!t) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = drag.from ? "move" : "copy";
    if (t.classList.contains("dz")) t.classList.add("over");
  });
  parts.addEventListener("dragleave", function (e) {
    var t = e.target.closest && e.target.closest(".dz");
    if (t && !t.contains(e.relatedTarget)) t.classList.remove("over");
  });
  parts.addEventListener("drop", function (e) {
    var t = cible(e);
    if (!t) return;
    e.preventDefault();
    t.classList.remove("over");
    if (t.classList.contains("bank")) { if (drag.from) poser(drag.from, ""); return; }
    if (t === drag.from) return;
    var ancien = inp(t).value;
    poser(t, drag.v);
    if (drag.from) poser(drag.from, ancien);  /* glisser d'une case à l'autre : les deux étiquettes s'échangent */
  });
  /* une case validée (entraînement) ou corrigée (examen) est verrouillée par le moteur : ses commandes aussi */
  new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      var i = m.target, dz = i.tagName === "INPUT" && i.parentNode.querySelector(".dz");
      if (!dz || !i.disabled || dz.disabled) return;  /* ne réagir qu'aux champs : sinon la boucle s'entretient */
      dz.disabled = true; dz.draggable = false;
      var g = grp(i);
      if (!g.querySelector(".sol input:not(:disabled)")) {
        Array.prototype.forEach.call(g.querySelectorAll(".etq"), function (b) { b.disabled = true; b.draggable = false; });
        if (sel && grp(sel) === g) choisir(null);
      }
    });
  }).observe(parts, { subtree: true, attributes: true, attributeFilter: ["disabled"] });
})();
</script>"""


def build():
    g = GABARIT.read_text(encoding="utf-8")

    # le commentaire d'en-tête du gabarit cite « <style> » : on part de la vraie balise
    s0 = g.index("<style>:root{")
    style = g[s0:g.index("</style>", s0) + len("</style>")]
    grading = re.search(r"<script>/\*GRADING-START\*/.*?</script>", g, re.S).group(0)
    app_start = g.index("<script>(function () {")
    app = g[app_start:g.rindex("</script>") + len("</script>")]

    # entrées du moteur réservées au sujet ; la durée conseillée dépend de l'exercice ouvert
    app = sub_once(app, r"var CONSEIL_MIN = \d+;", "var CONSEIL_MIN = window.__CONSEIL_MIN__ || 0;")
    app = sub_once(app, r"  var DECOR = \{\n.*?\n  \};\n", DECOR_JS, re.S)
    app = sub_once(app, r"  var DR_NAMES = \{\n.*?\n  \};\n", DR_NAMES_JS, re.S)
    app = sub_once(app, r"Quatre pages, une par document", "Une page par document réponse")
    app = sub_once(app, r'btn\.textContent = "Diagramme validé";', 'btn.textContent = "Réponses validées";')

    templates, exos_cfg = [], {}
    for e in EXO_DEFS:
        prepare_exo(e)
    for e in EXO_DEFS:
        CUR["total"] = e["minutes"]
        parts_html = "".join(render_part(p) for p in e["P"])
        rail, tabs, secs = render_docs(e)
        k = e["key"]
        templates += [f'<template id="tpl-rail-{k}">{rail}</template>',
                      f'<template id="tpl-tabs-{k}">{tabs}</template>',
                      f'<template id="tpl-docs-{k}">{secs}</template>',
                      f'<template id="tpl-home-{k}">{render_exo_home(e)}</template>',
                      f'<template id="tpl-consignes-{k}">{e["consignes"]}</template>',
                      f'<template id="tpl-parts-{k}">{parts_html}\n</template>']
        exos_cfg[k] = e["cfg"]
    templates.append(f'<template id="tpl-modes">{MODES_HTML}</template>')
    templates.append(f'<template id="tpl-hub">{render_hub()}</template>')
    for c in COURS:
        templates.append(f'<template id="tpl-{c["key"]}">{COURS_RENDER[c["key"]]()}</template>')

    config = f"<script>window.__EXOS__ = {json.dumps(exos_cfg, ensure_ascii=False)};</script>"
    router = (ROUTER_JS.replace("__COURS_JS__", COURS_JS).replace("__TITRE__", TITRE)
              .replace("__HOUSE__", HOUSE.replace("'", "\\'")))

    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITRE} — cours et exercices interactifs</title>
<meta name="description" content="Chaîne fonctionnelle, cours et exercices interactifs de deux niveaux : chaîne d'information, chaîne d'énergie, composants et symboles, puissances et rendements ; formulaire de la chaîne de puissance.">
{style}
{CONTENT_CSS.replace("__COURS_CSS__", COURS_CSS + rav4.RAV4_CSS)}
</head>
<body class="no-mode">

<nav class="rail" aria-label="Dossiers de présentation et dossier technique"></nav>

<aside id="docpanel" aria-label="Documents du sujet" aria-hidden="true">
  <div class="dp-head">
    <h3 id="dp-title">Documents</h3>
    <button type="button" id="dp-out" aria-label="Réduire">−</button><span id="dp-zoom" class="small">100 %</span>
    <button type="button" id="dp-in" aria-label="Agrandir">+</button>
    <button type="button" id="dp-fit">Ajuster</button>
    <button type="button" id="dp-close">Fermer</button>
  </div>
  <div class="dp-tabs" role="tablist" aria-label="Choisir un document"></div>
  <div class="dp-body"></div>
</aside>

<section id="home" aria-labelledby="home-title"><div class="home-inner"></div></section>

<main class="page">
  <section class="print-only print-summary">
    <p>Élève : <span class="print-nom"></span> | Copie imprimée le <span class="print-date"></span></p>
    <p>Mode : <span class="print-mode"></span> | Temps de rédaction : <strong class="print-time"></strong> (durée conseillée : <span class="print-conseil"></span>)</p>
    <p class="print-note-line">Note finale pondérée : <strong class="final-note"></strong></p>
    <p class="print-nograde">Copie non corrigée : les corrections et la note n'apparaissent qu'après la remise de la copie en mode examen.</p>
  </section>

  <nav class="c-top" aria-label="Navigation"><a href="?">{HOUSE} Accueil</a></nav>

  <header class="cartouche">
    <div class="title">
      <h1>{TITRE}</h1>
      <p></p></div>
    <div class="nom"><label for="nom-eleve">Nom et prénom</label><input id="nom-eleve" type="text" autocomplete="name"></div>
  </header>

  <div class="consignes"></div>

  <div id="parts"></div>

  <section class="recap" id="recap" aria-labelledby="t-recap">
    <header class="recap-head"><h2 id="t-recap">Récapitulatif et note finale</h2>
      <p class="small">Les cases non validées comptent comme fausses. Chaque partie est ramenée sur 20, puis pondérée par sa durée conseillée.</p></header>
    <div id="exam-submit-wrap">
      <p class="es-lead">Ta copie n'est pas encore corrigée : aucune réponse n'est verrouillée, tu peux encore revenir sur les questions.</p>
      <button type="button" class="btn btn-exam" id="exam-submit">J'ai fini, je fais corriger ma copie</button>
      <p class="es-warn" id="exam-warn" role="alert"></p>
    </div>
    <div id="recap-graded">
      <div class="recap-wrap">
        <table class="t recap-table">
          <thead><tr><th>Partie</th><th>Durée</th><th>Poids</th><th>Points</th><th>Note /20</th><th>Contribution</th></tr></thead>
          <tbody id="recap-body"></tbody>
          <tfoot><tr><th colspan="4">Note globale pondérée</th><th class="final-note"></th><th></th></tr></tfoot>
        </table>
      </div>
      <p class="final-detail small"></p>
    </div>
    <div class="recap-foot" id="recap-foot"><button type="button" class="btn btn-print">Imprimer ma copie</button>
      <span class="small no-print">L'impression reprend tes réponses, les corrections et ce récapitulatif.</span>
      <a class="btn ghost no-print" href="?">{HOUSE} Retour à l'accueil</a></div>
  </section>
</main>

<footer class="banner" aria-label="Suivi de la composition">
  <div class="score-block"><div class="lab">Note provisoire</div><div class="score" id="score-val">–<small>/20</small></div></div>
  <div class="exam-block"><div class="lab">Mode examen</div><div class="exam-state">Note masquée</div></div>
  <div class="timer-block"><div class="lab">Temps</div><div class="timer" id="timer-val">0:00:00</div></div>
  <div class="count" id="score-count" aria-live="polite"></div>
  <div class="spacer"></div>
  <button type="button" class="btn-docs" id="btn-docs">Documents</button>
</footer>

{chr(10).join(templates)}

{config}
{router}
{grading}
{app}
{ETIQUETTES_JS}
{rav4.RAV4_JS}
</body>
</html>
"""
    SORTIE.write_text(page, encoding="utf-8")
    imgs = sum(len(m) for m in DATA_RE.findall(page))
    print(f"{SORTIE.name} : {len(page.encode('utf-8')) / 1024:.0f} Kio, dont images {imgs / 1024:.0f} Kio (base64)")
    for e in EXO_DEFS:
        print(f"  ?ex={e['key']} : {len(e['P'])} parties, {e['n_q']} questions, {e['n_cases']} cases, "
              f"{e['points']} points, {hm(e['minutes'])}")
    for c in COURS:
        print(f"  ?ex={c['key']} : {c['tag']} — {c['title']}")
    f = build_formulaire()
    print(f"{FORMULAIRE.name} : {len(f.encode('utf-8')) / 1024:.0f} Kio")


if __name__ == "__main__":
    build()
