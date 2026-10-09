"""Exercice 1.1 : les schémas à compléter des parties 1, 3 et 4 (figures 2, 6 et 8), redessinés en SVG.

Les figures d'origine (src/images/originaux/ex1-*-chaines.png) sont des captures dont les cases, trop petites,
ne peuvent pas recevoir une étiquette. Elles sont redessinées avec la même organisation (cadres, cases, flèches,
repères rouges, pictogrammes de l'utilisateur), et des cases assez grandes pour y poser le nom d'un composant.

Chaque fonction renvoie un dictionnaire :
  svg   : le dessin, sans les cases à remplir ;
  w, h  : le repère du viewBox ;
  cases : repère → (x, y, largeur, hauteur, indication), rectangles des cases à remplir dans le repère du viewBox ;
          le générateur y pose les cases (boutons HTML) que l'on remplit en y glissant une étiquette.
Les identifiants des marqueurs portent un préfixe propre à chaque figure : les quatre parties sont dans la même page.
"""

ENCRE = "#1C2530"
ROUGE = "#B3282D"                      # flux d'information
VERT = "#6E9A4B"                       # énergie et matière d'œuvre
ROSE, ROSE_T = "#F7E1E2", "#E2B5B8"    # cases et cadre de la chaîne d'information
BLEU, BLEU_T = "#C9E7EF", "#86C3D3"    # cases des fonctions
VERT_C, VERT_T = "#EDF3E2", "#C5D8A8"  # cadre de la chaîne d'énergie, source, matière d'œuvre
CASE = 6                               # retrait de la case à remplir dans son bloc


def _rect(x, y, w, h, fond, trait, rx=0, ep=1.5, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fond}" stroke="{trait}" '
            f'stroke-width="{ep}"{extra}/>')


def _texte(x, y, s, taille=13, poids=700, couleur=ENCRE, ancre="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{taille}" font-weight="{poids}" fill="{couleur}" '
            f'text-anchor="{ancre}"{extra}>{s}</text>')


def _defs(pre):
    """Pointes de flèche : rouge (information), verte (énergie), encre (schéma géothermique)."""
    def pointe(nom, c):
        return (f'<marker id="{pre}-{nom}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="3.4" '
                f'markerHeight="3.4" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>')
    return "<defs>" + pointe("r", ROUGE) + pointe("v", VERT) + pointe("n", ENCRE) + "</defs>"


def _fleche(pre, d, nom, ep=4.5):
    c = {"r": ROUGE, "v": VERT, "n": ENCRE}[nom]
    return (f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{ep}" stroke-linejoin="round" '
            f'marker-end="url(#{pre}-{nom})"/>')


def _trait(d, c, ep=4.5):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{ep}" stroke-linejoin="round"/>'


def _usager(cx, cy):
    """Pictogramme de l'utilisateur (deux personnes), comme sur les schémas d'origine."""
    x, y = cx - 24, cy - 24
    return (f'<g transform="translate({x} {y})" aria-hidden="true">'
            '<circle cx="17" cy="11" r="8" fill="#7FA65A"/><path d="M3 38 q0 -17 14 -17 q14 0 14 17 z" fill="#7FA65A"/>'
            '<circle cx="31" cy="17" r="8.5" fill="#4F86B5"/><path d="M16 46 q0 -18 15 -18 q15 0 15 18 z" fill="#4F86B5"/>'
            '</g>')


def _svg(pre, w, h, corps, aria):
    return (f'<svg class="plan-svg" viewBox="0 0 {w} {h}" role="img" aria-label="{aria}">' + _defs(pre) + corps +
            "</svg>")


def _case(x, y, w, h, indication=""):
    return (x + CASE, y + CASE, w - 2 * CASE, h - 2 * CASE, indication)


# ------------------------------------------------------------ figures 2 et 8 : chaînes d'information et d'énergie
def _chaines(pre, aria, mo, composants):
    """Schéma commun de l'ascenseur et du portail : repères 1 à 12 aux mêmes places que sur les figures d'origine.
    mo : textes (deux lignes chacun) de la matière d'œuvre entrante et sortante de la case 12.
    composants : les blocs 10, 11 et 12 reçoivent aussi le composant qui réalise la fonction (ascenseur, Q1.4)."""
    s, cases = [], {}
    xi = {3: 230, 4: 372, 5: 514}                       # chaîne d'information : blocs de 124
    xe = {8: 230, 9: 372, 10: 514, 11: 656, 12: 798}    # chaîne d'énergie : mêmes colonnes, 4 → 9 à la verticale
    yi, hi = 157, 66                                     # blocs 3 à 5 (centre 190)
    ye, he = 304, 62                                     # blocs 8 à 12 (centre 335)
    hc = 84 if composants else 0                         # partie « composant » sous les fonctions 10, 11, 12
    bas = ye + he + hc                                   # bas des blocs 10 à 12
    cadre_bas = bas + 14
    retour = cadre_bas + 18
    arrivee = bas + 34
    h = arrivee + 38 + 12

    # cadres des deux chaînes
    s.append(_rect(212, 66, 444, 174, ROSE, ROSE_T))
    s.append(_texte(226, 88, "CHAÎNE D'INFORMATION", 14, 700, "#3A3A3A", extra=' letter-spacing=".4"'))
    s.append(_rect(212, 272, 724, cadre_bas - 272, VERT_C, VERT_T))
    s.append(_texte(226, 293, "CHAÎNE D'ÉNERGIE", 14, 700, "#3A3A3A", extra=' letter-spacing=".4"'))

    # flèches (sous les blocs)
    s.append(_fleche(pre, "M100 60 V84", "r"))
    s.append(_fleche(pre, "M180 114 H292 V157", "r"))
    s.append(_fleche(pre, "M180 190 H230", "r"))
    s.append(_fleche(pre, "M354 190 H372", "r"))
    s.append(_fleche(pre, "M496 190 H514", "r"))
    s.append(_fleche(pre, "M638 190 H682", "r"))
    s.append(_fleche(pre, "M832 190 H862", "r"))
    s.append(_fleche(pre, f"M434 {yi + hi} V{ye}", "r"))
    s.append(_fleche(pre, f"M576 {cadre_bas} V{retour} H32 V220", "r"))
    s.append(_fleche(pre, "M196 335 H230", "v"))
    for a, b in ((8, 9), (9, 10), (10, 11), (11, 12)):
        s.append(_fleche(pre, f"M{xe[a] + 124} 335 H{xe[b]}", "v"))
    s.append(_fleche(pre, f"M860 262 V{ye}", "v", 4))
    s.append(_fleche(pre, f"M860 {bas} V{arrivee}", "v", 4))

    # entrées et sorties : repères 1, 2, 6 (cases roses) et 7 (case verte)
    s.append(_usager(100, 34))
    s.append(_usager(892, 190))
    for k, (x, y, w, hh) in {"1": (20, 84, 160, 60), "2": (20, 160, 160, 60), "6": (682, 162, 150, 56)}.items():
        s.append(_rect(x, y, w, hh, ROSE, ROSE_T))
        cases[k] = _case(x, y, w, hh)
    s.append(_rect(50, 305, 146, 60, VERT_C, VERT_T))
    cases["7"] = _case(50, 305, 146, 60)

    # blocs des fonctions
    for k, x in xi.items():
        s.append(_rect(x, yi, 124, hi, BLEU, BLEU_T, 7))
        cases[str(k)] = _case(x, yi, 124, hi, "fonction ?" if composants else "")
    for k, x in xe.items():
        if composants and k >= 10:
            s.append(_rect(x, ye, 124, he + hc, BLEU, BLEU_T, 7))
            s.append(f'<path d="M{x + 1} {ye + he} H{x + 123} V{bas - 7} q0 6 -6 6 H{x + 7} q-6 0 -6 -6 z" '
                     'fill="#E7F4F8"/>')
            s.append(f'<line x1="{x}" y1="{ye + he}" x2="{x + 124}" y2="{ye + he}" stroke="{BLEU_T}" '
                     'stroke-width="1.5" stroke-dasharray="5 4"/>')
            cases[f"{k}c"] = _case(x, ye + he - 2, 124, hc + 2, "composant ?")
        else:
            s.append(_rect(x, ye, 124, he, BLEU, BLEU_T, 7))
        cases[str(k)] = _case(x, ye, 124, he, "fonction ?" if composants else "")

    # matière d'œuvre de la case 12
    for (l1, l2), y in ((mo[0], 224), (mo[1], arrivee)):
        s.append(_rect(785, y, 150, 38, VERT_C, VERT_T))
        s.append(_texte(860, y + 16, l1, 11.5, 700, "#4F7434", "middle"))
        s.append(_texte(860, y + 31, l2, 11.5, 700, "#4F7434", "middle"))
    return {"svg": _svg(pre, 960, h, "".join(s), aria), "w": 960, "h": h, "cases": cases}


def ascenseur():
    return _chaines("pa", "Chaînes d'information et d'énergie de l'ascenseur, cases repérées de 1 à 12 ; les blocs 10, "
                          "11 et 12 reçoivent aussi le composant qui réalise la fonction",
                    (("Usager à l'étage", "de départ"), ("Usager à l'étage", "d'arrivée")), True)


def portail():
    return _chaines("pp", "Chaînes d'information et d'énergie du portail, cases repérées de 1 à 12",
                    (("Vantail en", "position initiale"), ("Vantail en", "position finale")), False)


# ------------------------------------------------------------ figure 6 : chauffage géothermique
def geothermie():
    pre, s, cases = "pg", [], {}
    blanc = "#FFFFFF"

    def bloc(k, x, y, w=160, hh=62):
        s.append(_rect(x, y, w, hh, blanc, ENCRE, 0, 1.6))
        cases[str(k)] = _case(x, y, w, hh)

    # chaîne d'information : entrées, blocs 1 à 3, régulateur (4), sorties
    s.append(_texte(20, 36, "Consignes", 12.5))
    s.append(_texte(20, 52, "Commandes", 12.5))
    s.append(_fleche(pre, "M112 43 H190", "n", 4))
    s.append(_texte(20, 118, "Climat", 12.5))
    s.append(_fleche(pre, "M112 113 H190", "n", 4))
    s.append(_fleche(pre, "M350 43 H374 V100 H400", "n", 2.5))
    s.append(_fleche(pre, "M350 113 H400", "n", 2.5))
    s.append(_fleche(pre, "M350 183 H374 V126 H400", "n", 2.5))
    s.append(_fleche(pre, "M560 113 H588 V47 H620", "n", 2.5))
    s.append(_fleche(pre, "M588 113 V150 H620", "n", 2.5))
    s.append(_fleche(pre, "M790 47 H872", "n", 4))
    s.append(_texte(878, 52, "Messages", 12.5))
    s.append(_rect(620, 118, 170, 64, blanc, ENCRE, 0, 1.6))
    s.append(_texte(705, 145, "Conversion numérique", 13, 600, ENCRE, "middle", ' font-style="italic"'))
    s.append(_texte(705, 163, "analogique", 13, 600, ENCRE, "middle", ' font-style="italic"'))
    s.append(_fleche(pre, "M705 182 V236 H320 V272", "n", 2.5))
    s.append(_texte(520, 229, "Consigne marche arrêt", 11.5, 700, ENCRE, "middle"))
    for k, y in ((1, 12), (2, 82), (3, 152)):
        bloc(k, 190, y)
    bloc(4, 400, 82)
    bloc(5, 620, 16, 170)

    # chaîne d'énergie : deux alimentations, pompe à chaleur, plancher, « Chauffer la maison »
    s.append(_fleche(pre, "M200 303 H240", "n", 2.5))
    s.append(_fleche(pre, "M400 303 H424 V330 H450", "n", 2.5))
    s.append(_fleche(pre, "M200 405 H240", "n", 2.5))
    s.append(_fleche(pre, "M400 405 H424 V356 H450", "n", 2.5))
    s.append(_fleche(pre, "M610 343 H650", "n", 2.5))
    s.append(_fleche(pre, "M810 343 H850", "n", 2.5))
    s.append(_rect(40, 374, 160, 62, blanc, ENCRE, 0, 1.6))
    s.append(_texte(120, 400, "Énergie thermique", 13, 600, ENCRE, "middle", ' font-style="italic"'))
    s.append(_texte(120, 418, "du sol", 13, 600, ENCRE, "middle", ' font-style="italic"'))
    s.append(_texte(40, 456, "Chaîne d'énergie", 12, 700))
    for k, x, y in ((6, 40, 272), (7, 240, 272), (10, 240, 374), (8, 450, 312), (9, 650, 312)):
        bloc(k, x, y)
    s.append(_rect(850, 248, 90, 206, "#2B2B2B", "#555", 0, 2))
    s.append(_texte(0, 0, "CHAUFFER LA MAISON", 14, 700, "#FFFFFF", "middle",
                    ' transform="translate(901 351) rotate(-90)" letter-spacing=".6"'))

    # retour : la température intérieure revient à la sonde (repère 3)
    s.append(_trait("M830 343 V474 H22 V183", ENCRE, 2.5))
    s.append(_fleche(pre, "M22 183 H190", "n", 2.5))
    s.append(_texte(430, 467, "Information température intérieur", 11.5, 700, ENCRE, "middle"))
    return {"svg": _svg(pre, 960, 486, "".join(s), "Chaînes d'information et d'énergie du chauffage géothermique, "
                        "cases repérées de 1 à 10 ; les cases « Conversion numérique analogique », « Énergie thermique "
                        "du sol » et « Chauffer la maison » sont données"), "w": 960, "h": 486, "cases": cases}
