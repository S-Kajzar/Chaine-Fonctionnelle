"""Cours 3 — Chaîne d'information des produits (Niveau 2), d'après le cours Word « Thème 3 ».

Le cours suit le plan du Word (constitution d'un produit, Acquérir, chaîne d'acquisition, Traiter, Communiquer,
encodage de l'information) ; toutes ses figures sont redessinées en SVG et rendues interactives :
machine à café animée, diagramme de blocs internes cliquable, laboratoire des capteurs (logique, analogique,
numérique), filtre passe-bas et spectre, chaîne d'acquisition en direct, convertisseur analogique-numérique,
système programmable, programme « bouton → LED » exécuté pas à pas (algorigramme, pseudo-code, blocs, Python,
C++/Arduino), restitution et optocoupleur, trame envoyée sur un réseau, octet, hexadécimal et ASCII.

render(h) reçoit les fonctions communes du générateur (en-tête, sections, jeux, quiz) : pas d'import circulaire.
Classes et identifiants propres au cours : préfixe « ci- ».
"""
import html

OBJECTIFS = [
    "Identifier les trois fonctions de la chaîne d'information : acquérir, traiter, communiquer.",
    "Caractériser les signaux (logique, analogique, numérique) et les constituants de l'acquisition.",
    "Décrire la chaîne d'acquisition d'un signal analogique : conditionnement et conversion analogique-numérique.",
    "Décrire un algorithme (algorigramme, pseudo-code) et encoder l'information (binaire, hexadécimal, ASCII).",
]
COMPETENCES = [
    ("CO3.1", "Identifier et caractériser les fonctions et les constituants d'un produit ainsi que ses "
              "entrées/sorties.", 2),
    ("CO3.2", "Identifier et caractériser l'agencement matériel et/ou logiciel d'un produit.", 2),
    ("CO3.3", "Identifier et caractériser le fonctionnement temporel d'un produit ou d'un processus.", 2),
    ("CO4.2", "Décrire le fonctionnement et/ou l'exploitation d'un produit en utilisant l'outil de description le "
              "plus pertinent.", 2),
]
PREREQUIS = ["Notion de chaîne de puissance et d'effecteur.", "Lecture d'un schéma-bloc."]

FONCTIONS_I = [("acq", "Acquérir"), ("tra", "Traiter"), ("com", "Communiquer")]
JEU_FONCTIONS = [("Bouton poussoir", "acq"), ("Capteur de température", "acq"), ("Encodeur rotatif", "acq"),
                 ("Microcontrôleur", "tra"), ("Clavier", "acq"), ("Voyant lumineux", "com"),
                 ("Afficheur LCD", "com"), ("Haut-parleur", "com"), ("Détecteur d'obstacle", "acq"),
                 ("Microprocesseur", "tra"), ("Carte de pilotage des effecteurs", "com"), ("Module Wi-Fi", "com")]
SIGNAUX = [("log", "Logique"), ("ana", "Analogique"), ("num", "Numérique")]
JEU_SIGNAUX = [("Détecteur de présence (tout-ou-rien)", "log"), ("Capteur analogique de température", "ana"),
               ("Codeur (capteur numérique)", "num"), ("Bouton poussoir", "log"), ("Sortie d'un CAN", "num"),
               ("Voyant allumé ou éteint", "log"), ("Son envoyé au haut-parleur", "ana"),
               ("Texte envoyé à l'afficheur LCD", "num")]
LIAISONS = [("fil", "Filaire"), ("sf", "Sans fil")]
JEU_LIAISONS = [("Ethernet", "fil"), ("Wi-Fi", "sf"), ("Bus CAN (automobile)", "fil"), ("Bluetooth", "sf"),
                ("USB", "fil"), ("NFC (paiement sans contact)", "sf")]

QUIZ_3 = [
    ("Dans quel ordre la chaîne d'information traite-t-elle les informations ?",
     ["Traiter, acquérir, communiquer", "Acquérir, traiter, communiquer", "Acquérir, communiquer, traiter"], 1,
     "On acquiert d'abord (consignes, capteurs), on traite (microcontrôleur), puis on communique (commandes, "
     "messages)."),
    ("Un détecteur de porte ouverte / fermée produit un signal…", ["logique", "analogique", "numérique codé"], 0,
     "Deux états seulement, 0 ou 1 : c'est un détecteur, ou capteur tout-ou-rien (TOR)."),
    ("Un capteur dont la tension de sortie suit la température mesurée produit un signal…",
     ["logique", "analogique", "numérique codé"], 1,
     "La tension peut prendre n'importe quelle valeur entre un minimum et un maximum : signal analogique."),
    ("Pourquoi amplifie-t-on le signal d'un capteur analogique avant de le numériser ?",
     ["Pour supprimer les parasites", "Parce qu'il est de trop faible amplitude",
      "Pour le transformer en signal logique"], 1,
     "Un signal de quelques millivolts serait numérisé avec peu de fidélité : on l'amplifie (gain) ; les parasites, "
     "eux, sont supprimés par le filtrage."),
    ("Un filtre passe-bas…", ["laisse passer les hautes fréquences", "laisse passer les fréquences inférieures à fc",
                              "amplifie toutes les fréquences"], 1,
     "Il conserve les composantes de fréquence inférieure à sa fréquence de coupure fc et élimine les parasites de "
     "haute fréquence."),
    ("Un CAN 8 bits de pleine échelle 5 V a un quantum de…", ["5 / 8 = 0,625 V", "5 / 256 ≈ 19,5 mV",
                                                             "5 / 255 ≈ 19,6 mV"], 1,
     "q = Vref / 2ⁿ = 5 / 2⁸ = 5 / 256 ≈ 0,0195 V, soit environ 19,5 mV."),
    ("Dans un algorigramme, le losange représente…", ["une opération", "un test et un aiguillage",
                                                       "une entrée ou une sortie"], 1,
     "Le losange teste une condition ; le résultat (oui / non) aiguille la suite du programme."),
    ("(10110101)₂ vaut en décimal…", ["181", "173", "245"], 0, "128 + 32 + 16 + 4 + 1 = 181."),
    ("(7B)₁₆ s'écrit en binaire…", ["0111 1011", "0111 1101", "1011 0111"], 0,
     "Un chiffre hexadécimal = 4 bits : 7 = 0111 et B = 11 = 1011."),
    ("Quel code ASCII correspond à la lettre « I » ?", ["(49)₁₀", "(73)₁₀", "(105)₁₀"], 1,
     "« I » a pour code 73 en décimal, soit (49)₁₆ ou (01001001)₂ ; (105)₁₀ est le « i » minuscule."),
]


def e(s):
    return html.escape(s, quote=True)


# ------------------------------------------------------------ figures SVG (le JS les anime)
def _box(ident, x, y, w, h, lines, cls="", data=""):
    ty = y + h / 2 - (len(lines) - 1) * 8 + 5
    txt = "".join(f'<text x="{x + w / 2}" y="{ty + i * 16}" text-anchor="middle" class="{"ci-bt" if i == 0 else "ci-bs"}">'
                  f"{l}</text>" for i, l in enumerate(lines))
    return (f'<g class="ci-box {cls}" id="{ident}"{data}><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>'
            f"{txt}</g>")


def _fl(ident, d, kind, label="", lx=0, ly=0, anchor="middle"):
    lab = (f'<text class="ci-fl-l k-{kind}" x="{lx}" y="{ly}" text-anchor="{anchor}">{label}</text>' if label else "")
    return (f'<g class="ci-fl k-{kind}" id="{ident}"><path class="ci-fl-p" d="{d}" marker-end="url(#ci-m-{kind})"/>'
            f'<path class="ci-fl-a" d="{d}"/>{lab}</g>')


MARKERS = "".join(
    f'<marker id="ci-m-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="ci-mk-{k}"/></marker>'
    for k in ("i", "e", "m"))


def figure_cafe():
    """Figures 1 et 2 du Word réunies : la machine à café, chaîne d'information globale ou détaillée."""
    return f"""<div class="ci-cafe" id="ci-cafe">
<div class="ci-ctrl no-print"><button type="button" class="btn" id="ci-cafe-go">▶ Préparer un espresso</button>
<button type="button" class="btn ghost" id="ci-cafe-next">Étape suivante</button>
<label class="ci-sw"><input type="checkbox" id="ci-cafe-det" checked> Détailler la chaîne d'information</label></div>
<svg class="ci-svg" id="ci-cafe-svg" viewBox="0 0 980 430" role="img" aria-labelledby="ci-cafe-t">
<title id="ci-cafe-t">Machine à café : l'utilisateur donne ses consignes à la chaîne d'information (acquérir, traiter,
communiquer), qui commande la chaîne de puissance ; celle-ci, alimentée par le réseau électrique, transforme l'eau et
les grains en café.</title>
<defs>{MARKERS}</defs>
<rect class="ci-frame" x="170" y="14" width="620" height="402" rx="6"/><text class="ci-frame-t" x="186" y="404">Machine à café</text>
{_fl("cf-cons", "M140 175 H205 V82 H262", "i", "consignes", 150, 168, "start")}
{_fl("cf-etat", "M430 300 V236 H228 V118 H262", "i", "états de la machine", 330, 230)}
{_fl("cf-info", "M635 50 V28 H80 V150", "i", "informations restituées", 360, 22)}
{_fl("cf-cmd", "M660 140 V250 H560 V298", "i", "commandes", 652, 200, "end")}
{_fl("cf-pin", "M140 340 H378", "e", "puissance entrante", 258, 332)}
{_fl("cf-pout", "M622 330 H818", "e", "puissance utile", 720, 322)}
{_fl("cf-mo1", "M885 224 V278", "m")}
{_fl("cf-mo2", "M885 334 V366", "m")}
{_box("cb-user", 20, 150, 120, 50, ["Utilisateur"], "ci-u")}
{_box("cb-res", 20, 315, 120, 50, ["Réseau", "électrique"], "ci-u")}
<g class="ci-simple">{_box("cb-ci", 262, 52, 440, 86, ["Chaîne d'information", "de la machine à café"], "ci-i")}</g>
<g class="ci-detail">
{_box("cb-acq", 262, 52, 130, 86, ["Acquérir", "boutons, encodeur", "rotatif, capteurs"], "ci-i")}
{_box("cb-tra", 418, 52, 130, 86, ["Traiter", "microcontrôleur"], "ci-i")}
{_box("cb-com", 574, 52, 128, 86, ["Communiquer", "LED, haut-parleurs,", "carte de pilotage"], "ci-i")}
{_fl("cf-at", "M392 95 H416", "i")}{_fl("cf-tc", "M548 95 H572", "i")}
</g>
{_box("cb-cp", 380, 298, 242, 64, ["Chaîne de puissance", "de la machine à café"], "ci-e")}
{_box("cb-eau", 820, 178, 130, 46, ["Eau, grains", "de café"], "ci-mo")}
{_box("cb-faire", 820, 280, 130, 54, ["Faire", "du café"], "ci-a")}
{_box("cb-cafe", 820, 368, 130, 40, ["Café"], "ci-mo")}
<g class="ci-cup" id="ci-cup" aria-hidden="true"><path d="M712 190 h44 v26 a22 22 0 0 1 -44 0 z" class="ci-cup-b"/>
<path d="M756 196 a10 10 0 0 1 0 18" class="ci-cup-h"/><rect class="ci-cup-l" x="715" y="216" width="38" height="0"/>
<path class="ci-steam" d="M724 184 q-6 -8 0 -16 t0 -16 M740 184 q-6 -8 0 -16 t0 -16"/></g>
</svg>
<p class="ci-step" id="ci-cafe-step" aria-live="polite">Appuie sur « Préparer un espresso » : suis le trajet de
l'information, puis celui de l'énergie.</p></div>"""


IBD_BLOCS = {  # identifiant : (x, y, l, h, lignes, chaîne, fonction, rôle)
    "user": (14, 236, 110, 46, ["Utilisateur"], "ext", "",
             "Il donne ses consignes (pressions, rotation) et reçoit les informations visuelles et sonores."),
    "btn": (236, 120, 140, 42, ["Boutons"], "i", "Acquérir",
            "Interface homme-machine : chaque pression produit un signal logique (appuyé / relâché)."),
    "enc": (236, 182, 140, 42, ["Encodeur rotatif"], "i", "Acquérir",
            "Interface homme-machine : l'angle de rotation (choix de la force du café) est transmis en signal numérique."),
    "cap": (236, 244, 140, 42, ["Capteurs"], "i", "Acquérir",
            "Ils mesurent l'état de la machine : niveau d'eau, température, présence du tiroir à marc… (états de la machine)."),
    "uc": (500, 170, 150, 66, ["Microcontrôleur"], "i", "Traiter",
           "Composant programmable : il exécute le programme, compare consignes et états, et décide des actions."),
    "led": (770, 96, 170, 44, ["LED pour", "pictogrammes lumineux"], "i", "Communiquer",
            "Restitution logique : un pictogramme allumé, éteint ou clignotant informe l'utilisateur."),
    "hp": (770, 160, 170, 44, ["Haut-parleurs"], "i", "Communiquer",
           "Restitution analogique : la sonnerie de fin de préparation."),
    "carte": (770, 224, 170, 50, ["Carte de pilotage", "des effecteurs"], "i", "Communiquer",
              "Elle transmet les commandes (signal numérique) à la chaîne de puissance : moulin, pompe, chauffe-eau."),
    "grains": (236, 330, 140, 40, ["Réservoir à grains"], "m", "", "Matière d'œuvre entrante : les grains de café."),
    "eau": (236, 386, 140, 40, ["Réservoir à eau"], "m", "", "Matière d'œuvre entrante : l'eau."),
    "cp": (470, 420, 180, 62, ["Chaîne de puissance", "de la machine à café"], "e", "",
           "Alimenter, distribuer, convertir, transmettre, agir : elle moud, chauffe, pompe et fait couler le café."),
    "rcafe": (770, 430, 160, 42, ["Réservoir à café"], "m", "", "Matière d'œuvre sortante : le café."),
    "reseau": (14, 470, 110, 46, ["Réseau", "électrique"], "ext", "", "Source d'énergie extérieure : l'électricité."),
}
IBD_LIENS = [  # identifiant, d, nature, libellé, x, y, blocs reliés
    ("press", "M124 252 H190 V141 H234", "i", "pressions", 182, 134, "user btn"),
    ("angle", "M124 268 H200 V203 H234", "i", "angle", 205, 222, "user enc"),
    ("sbtn", "M376 141 H440 V188 H498", "i", "signal logique", 440, 132, "btn uc"),
    ("senc", "M376 203 H498", "i", "signal numérique", 437, 196, "enc uc"),
    ("scap", "M376 265 H440 V218 H498", "i", "signaux des capteurs", 440, 284, "cap uc"),
    ("sled", "M650 186 H700 V118 H768", "i", "signal logique", 712, 110, "uc led"),
    ("shp", "M650 203 H712 V182 H768", "i", "signal analogique", 712, 176, "uc hp"),
    ("scar", "M650 220 H700 V249 H768", "i", "signal numérique", 712, 268, "uc carte"),
    ("vis", "M940 118 H952 V56 H70 V234", "i", "informations visuelles : état et clignotement des pictogrammes", 500, 50, "led user"),
    ("son", "M940 182 H962 V30 H54 V234", "i", "informations sonores : sonnerie de fin de préparation", 500, 24, "hp user"),
    ("cmd", "M855 274 V330 H610 V418", "i", "commandes", 863, 316, "carte cp"),
    ("etats", "M520 420 V312 H210 V265 H234", "i", "états de la machine", 330, 306, "cp cap"),
    ("mgr", "M376 350 H500 V418", "m", "grains", 440, 343, "grains cp"),
    ("meau", "M376 406 H480 V418", "m", "eau", 430, 399, "eau cp"),
    ("elec", "M124 493 H468", "e", "électricité", 300, 486, "reseau cp"),
    ("mcafe", "M650 451 H768", "m", "café", 708, 444, "cp rcafe"),
]


def figure_ibd():
    blocs = "".join(
        _box(f"ib-{k}", x, y, w, h, lines, f"ci-{c}", f' data-k="{k}" tabindex="0" role="button"')
        for k, (x, y, w, h, lines, c, _f, _r) in IBD_BLOCS.items())
    liens = "".join(
        _fl(f"il-{k}", d, kind, lab, lx, ly).replace('class="ci-fl ', f'data-b="{b}" class="ci-fl ')
        for k, d, kind, lab, lx, ly, b in IBD_LIENS)
    return f"""<div class="ci-ibd" id="ci-ibd">
<svg class="ci-svg" id="ci-ibd-svg" viewBox="0 0 980 540" role="img" aria-labelledby="ci-ibd-t">
<title id="ci-ibd-t">Diagramme de blocs internes de la machine à café : boutons, encodeur rotatif et capteurs envoient
leurs signaux au microcontrôleur, qui pilote les LED, les haut-parleurs et la carte de pilotage des effecteurs ;
la chaîne de puissance reçoit l'électricité, l'eau et les grains, et produit le café.</title>
<defs>{MARKERS}</defs>
<path class="ci-ibd-tab" d="M150 8 H372 l-14 22 H150 z"/><text class="ci-ibd-tt" x="160" y="24">ibd  Organisation interne [Machine à café]</text>
<rect class="ci-frame" x="150" y="8" width="820" height="524" rx="2"/>
<text class="ci-frame-t" x="166" y="522">Machine à café</text>
{liens}{blocs}
</svg>
<div class="ci-ibd-info" id="ci-ibd-info" aria-live="polite"><p>Touche un bloc : sa fonction, son rôle et ses
échanges s'affichent ici ; ses flux s'éclairent sur le diagramme.</p></div></div>"""


def figure_capteur():
    """Un capteur transforme une grandeur à mesurer en un signal de sortie (avec l'énergie qu'il reçoit)."""
    return """<svg class="ci-svg ci-capt" viewBox="0 0 720 150" role="img" aria-label="Une grandeur à mesurer entre dans le capteur, alimenté en énergie, qui produit un signal de sortie">
<defs><marker id="ci-m-big" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#B42318"/></marker></defs>
<g class="ci-cbx"><rect x="20" y="70" width="170" height="60" rx="4" class="ci-c-g"/><text x="105" y="96" text-anchor="middle" class="ci-bt">Grandeur</text><text x="105" y="114" text-anchor="middle" class="ci-bt">à mesurer</text></g>
<g class="ci-cbx"><rect x="275" y="70" width="170" height="60" rx="4" class="ci-c-c"/><text x="360" y="105" text-anchor="middle" class="ci-bt">Capteur</text></g>
<g class="ci-cbx"><rect x="530" y="70" width="170" height="60" rx="4" class="ci-c-s"/><text x="615" y="96" text-anchor="middle" class="ci-bt">Signal</text><text x="615" y="114" text-anchor="middle" class="ci-bt">de sortie</text></g>
<g class="ci-cbx"><rect x="275" y="6" width="170" height="36" rx="4" class="ci-c-e"/><text x="360" y="29" text-anchor="middle" class="ci-bt">Énergie</text></g>
<path d="M360 42 V66" class="ci-c-ar" stroke-dasharray="4 3"/>
<path d="M190 100 H268" class="ci-c-ar ci-c-anim" marker-end="url(#ci-m-big)"/><path d="M445 100 H523" class="ci-c-ar ci-c-anim" marker-end="url(#ci-m-big)"/>
</svg>"""


def figure_acquisition():
    etapes = [("acq", "Acquérir", "capteur analogique", "i"), ("amp", "Amplifier", "amplificateur", "c"),
              ("fil", "Filtrer", "filtre", "c"), ("can", "Convertir A → N", "CAN", "n"),
              ("tra", "Traiter", "microcontrôleur", "i")]
    x0, w, gap = 14, 158, 34
    blocs = []
    for i, (k, t, s, c) in enumerate(etapes):
        x = x0 + i * (w + gap)
        blocs.append(f'<g class="ci-aq ci-aq-{c}" id="ci-aq-{k}"><rect x="{x}" y="70" width="{w}" height="58" rx="5"/>'
                     f'<text x="{x + w / 2}" y="95" text-anchor="middle" class="ci-bt">{t}</text>'
                     f'<text x="{x + w / 2}" y="114" text-anchor="middle" class="ci-bs">({s})</text>'
                     f'<g class="ci-aq-sc" transform="translate({x + 4} 136)"><rect width="{w - 8}" height="74" class="ci-sc-bg"/>'
                     f'<path class="ci-sc-c" d=""/></g></g>')
        if i < len(etapes) - 1:
            blocs.append(f'<path class="ci-aq-ar" d="M{x + w + 2} 99 H{x + w + gap - 4}" marker-end="url(#ci-m-i)"/>')
    return f"""<svg class="ci-svg" id="ci-aq-svg" viewBox="0 0 980 220" role="img" aria-labelledby="ci-aq-t">
<title id="ci-aq-t">La chaîne d'acquisition : le signal du capteur est amplifié, filtré (conditionnement), puis
converti en nombres par le CAN (numérisation) avant d'être traité. Sous chaque étape, l'allure du signal.</title>
<defs>{MARKERS}</defs>
<rect x="{x0 + w + gap - 12}" y="8" width="{2 * w + gap + 24}" height="26" class="ci-aq-g"/>
<text x="{x0 + w + gap + w + gap / 2}" y="26" text-anchor="middle" class="ci-aq-gt">Conditionnement</text>
<rect x="{x0 + 3 * (w + gap) - 12}" y="8" width="{w + 24}" height="26" class="ci-aq-g"/>
<text x="{x0 + 3 * (w + gap) + w / 2}" y="26" text-anchor="middle" class="ci-aq-gt">Numérisation</text>
<rect x="{x0 + w + gap - 18}" y="40" width="{3 * w + 2 * gap + 36}" height="176" class="ci-aq-zone"/>
<text x="{x0 + w + gap - 10}" y="58" class="ci-aq-zt">Acquisition</text>
{"".join(blocs)}
</svg>"""


def figure_systeme():
    return f"""<svg class="ci-svg ci-sys" viewBox="0 0 980 300" role="img" aria-labelledby="ci-sys-t">
<title id="ci-sys-t">Structure d'un système programmable : les signaux de la fonction Acquérir entrent par l'interface
d'entrées ; le processeur, cadencé par l'horloge, exécute le programme rangé en mémoire et commande l'interface de
sorties, vers la fonction Communiquer.</title>
<defs>{MARKERS}</defs>
<rect x="160" y="20" width="560" height="266" class="ci-sys-z" rx="6"/>
<g id="ci-sys-pk"></g><text x="176" y="42" class="ci-sys-zt">Composant programmable</text>
<g class="ci-sys-b"><rect x="20" y="118" width="110" height="60" rx="4"/><text x="75" y="144" text-anchor="middle" class="ci-bt">Fonction</text><text x="75" y="162" text-anchor="middle" class="ci-bt">Acquérir</text></g>
<g class="ci-sys-b"><rect x="190" y="98" width="100" height="100" rx="4"/><text x="240" y="144" text-anchor="middle" class="ci-bs">Interface</text><text x="240" y="160" text-anchor="middle" class="ci-bs">d'entrées</text></g>
<g class="ci-sys-b ci-cpu"><rect x="360" y="108" width="160" height="80" rx="4"/><text x="440" y="144" text-anchor="middle" class="ci-bt">Processeur</text><text x="440" y="162" text-anchor="middle" class="ci-bs">(CPU)</text></g>
<g class="ci-sys-b"><rect x="360" y="34" width="160" height="44" rx="4"/><text x="440" y="53" text-anchor="middle" class="ci-bs">Mémoire de programme</text><text x="440" y="69" text-anchor="middle" class="ci-bs">et de données</text></g>
<g class="ci-sys-b ci-clk"><rect x="390" y="228" width="100" height="36" rx="4"/><text x="440" y="251" text-anchor="middle" class="ci-bs">Horloge</text></g>
<g class="ci-sys-b"><rect x="590" y="98" width="100" height="100" rx="4"/><text x="640" y="144" text-anchor="middle" class="ci-bs">Interface</text><text x="640" y="160" text-anchor="middle" class="ci-bs">de sorties</text></g>
<g class="ci-sys-b"><rect x="750" y="118" width="120" height="60" rx="4"/><text x="810" y="144" text-anchor="middle" class="ci-bt">Fonction</text><text x="810" y="162" text-anchor="middle" class="ci-bt">Communiquer</text></g>
<g class="ci-sys-b ci-prog"><rect x="760" y="22" width="200" height="56" rx="4"/><text x="860" y="46" text-anchor="middle" class="ci-bt">Programme</text><text x="860" y="64" text-anchor="middle" class="ci-bs">(écrit et téléversé)</text></g>
<path class="ci-sys-ar" d="M130 148 H186" marker-end="url(#ci-m-i)"/><path class="ci-sys-ar" d="M290 148 H356" marker-end="url(#ci-m-i)"/>
<path class="ci-sys-ar" d="M520 148 H586" marker-end="url(#ci-m-i)"/><path class="ci-sys-ar" d="M690 148 H746" marker-end="url(#ci-m-i)"/>
<path class="ci-sys-ar ci-sys-mem" d="M440 80 V104" marker-start="url(#ci-m-i)" marker-end="url(#ci-m-i)"/>
<path class="ci-sys-ar" d="M440 226 V192" marker-end="url(#ci-m-i)"/>
<path class="ci-sys-pr" d="M760 50 H526" marker-end="url(#ci-m-e)"/>
</svg>"""


# ------------------------------------------------------------ algorithme « bouton → LED »
ALGO_NOEUDS = {  # identifiant : (forme, x, y, l, h, texte)
    "deb": ("term", 150, 20, 120, 34, "DÉBUT"),
    "lire": ("io", 150, 84, 120, 40, "Lire le bouton"),
    "test": ("test", 150, 158, 150, 74, "Bouton appuyé ?"),
    "on": ("io", 290, 262, 130, 40, "Allumer la LED"),
    "off": ("io", 10, 262, 130, 40, "Éteindre la LED"),
}
CODES = {
    "pseudo": ("Pseudo-code", [("deb", "Début"), ("lire", "Tant Que vrai"), ("lire", "    Lire le bouton"),
                               ("test", "    Si bouton appuyé Alors"), ("on", "        Allumer la LED"),
                               ("off", "    Sinon"), ("off", "        Éteindre la LED"), ("test", "    Fin Si"),
                               ("lire", "Fin Tant Que")]),
    "python": ("Python", [("deb", "led = LED(13)"), ("deb", "button = Button(11)"), ("lire", "while True:"),
                          ("test", "    if button.is_pressed:"), ("on", "        led.on()"), ("off", "    else:"),
                          ("off", "        led.off()")]),
    "arduino": ("C++ / Arduino", [("deb", "void setup() {"), ("deb", "  pinMode(13, OUTPUT);"),
                                  ("deb", "  pinMode(11, INPUT);"), ("deb", "}"), ("lire", "void loop() {"),
                                  ("test", "  if (digitalRead(11) == HIGH)"), ("on", "    digitalWrite(13, HIGH);"),
                                  ("off", "  else"), ("off", "    digitalWrite(13, LOW);"), ("lire", "}")]),
}


def figure_algo():
    def node(k, forme, x, y, w, h, t):
        cx, cy = x + w / 2, y + h / 2
        if forme == "term":
            shp = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}"/>'
        elif forme == "io":
            shp = f'<path d="M{x + 14} {y} H{x + w} L{x + w - 14} {y + h} H{x} z"/>'
        else:
            shp = f'<path d="M{cx} {y} L{x + w} {cy} L{cx} {y + h} L{x} {cy} z"/>'
        return (f'<g class="ci-an" id="ci-an-{k}">{shp}<text x="{cx}" y="{cy + 5}" text-anchor="middle">{t}</text></g>')
    nodes = "".join(node(k, *v) for k, v in ALGO_NOEUDS.items())
    fl = ('<path class="ci-aa" d="M210 54 V82"/><path class="ci-aa" d="M210 124 V156"/>'
          '<path class="ci-aa" d="M300 195 H355 V260"/><text class="ci-al" x="312" y="188">Oui</text>'
          '<path class="ci-aa" d="M150 195 H75 V260"/><text class="ci-al" x="104" y="188">Non</text>'
          '<path class="ci-aa" d="M355 302 V330 H440 V104 H272"/><path class="ci-aa nj" d="M75 302 V330 H355"/>')
    codes = "".join(
        f'<div class="ci-code" id="ci-code-{k}" role="tabpanel" aria-labelledby="ci-tab-{k}"{"" if k == "pseudo" else " hidden"}>'
        f'<pre>' + "".join(f'<span class="ci-cl" data-n="{n}">{e(l)}</span>' for n, l in lines) + "</pre></div>"
        for k, (_t, lines) in CODES.items())
    blocs = ('<div class="ci-code" id="ci-code-blocs" role="tabpanel" aria-labelledby="ci-tab-blocs" hidden>'
             '<div class="ci-blk ci-blk-loop" data-n="lire"><span>répéter indéfiniment</span>'
             '<div class="ci-blk ci-blk-if" data-n="test"><span>si <i>bouton 11 appuyé ?</i> alors</span>'
             '<div class="ci-blk ci-blk-act" data-n="on">allumer la LED 13</div><span>sinon</span>'
             '<div class="ci-blk ci-blk-act" data-n="off">éteindre la LED 13</div></div></div></div>')
    tabs = "".join(f'<button type="button" role="tab" id="ci-tab-{k}" aria-selected="{"true" if k == "pseudo" else "false"}" '
                   f'data-t="{k}">{t}</button>' for k, t in
                   [("pseudo", "Pseudo-code"), ("blocs", "Blocs"), ("python", "Python"), ("arduino", "C++ / Arduino")])
    return f"""<div class="ci-prog" id="ci-prog">
<div class="ci-prog-l"><svg class="ci-svg ci-algo" id="ci-algo" viewBox="0 0 460 350" role="img" aria-labelledby="ci-algo-t">
<title id="ci-algo-t">Algorigramme : début, lire le bouton, tester s'il est appuyé ; si oui allumer la LED, sinon
l'éteindre ; puis recommencer la lecture, indéfiniment.</title>
<defs><marker id="ci-m-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#1C2530"/></marker></defs>
{fl}{nodes}<circle class="ci-tok" id="ci-tok" r="7" cx="210" cy="37"/></svg></div>
<div class="ci-prog-r">
<div class="ci-carte" aria-label="La carte et son montage">
<button type="button" class="ci-bp" id="ci-bp" aria-pressed="false">Bouton<br><small>broche 11</small></button>
<div class="ci-led" id="ci-led" aria-hidden="true"></div><span class="ci-led-l" id="ci-led-l">LED (broche 13) : éteinte</span></div>
<p class="small no-print">Maintiens le bouton appuyé (souris, doigt ou barre d'espace) : le programme tourne en boucle
et suit l'algorigramme.</p>
<div class="ci-ctrl no-print"><button type="button" class="btn ghost" id="ci-pas">Pas à pas</button>
<label class="ci-sw">Vitesse <input type="range" id="ci-vit" min="1" max="5" step="1" value="2"></label></div>
<div class="ci-tabs" role="tablist" aria-label="Langage">{tabs}</div>{codes}{blocs}</div></div>"""


SYMBOLES = [
    ("term", "DÉBUT", "Début de l'algorigramme"), ("term", "FIN", "Fin de l'algorigramme"),
    ("io", "", "Acquisition des entrées ou mise à jour des sorties"),
    ("op", "", "Traitement des données (assignation de valeurs, opérations…)"),
    ("sp", "", "Appel à un sous-programme"), ("test", "Condition", "Test d'une condition et aiguillage suivant le résultat"),
    ("com", "Commentaire", "Commentaire"),
]


def table_symboles():
    def sym(forme, t):
        if forme == "term":
            s = '<rect x="20" y="8" width="100" height="30" rx="15"/>'
        elif forme == "io":
            s = '<path d="M34 8 H120 L106 38 H20 z"/>'
        elif forme == "op":
            s = '<rect x="20" y="8" width="100" height="30"/>'
        elif forme == "sp":
            s = '<rect x="20" y="8" width="100" height="30"/><path d="M32 8 V38 M108 8 V38"/>'
        elif forme == "test":
            s = '<path d="M70 2 L130 23 L70 44 L10 23 z"/>'
        else:
            s = '<path d="M40 8 H22 V38 H40" fill="none"/><path d="M4 23 H18" stroke-dasharray="3 3"/>'
        tx = f'<text x="{78 if forme == "com" else 70}" y="27" text-anchor="middle">{t}</text>' if t else ""
        return f'<svg viewBox="0 0 140 46" class="ci-sym" aria-hidden="true">{s}{tx}</svg>'
    rows = "".join(f"<tr><td>{sym(f, t)}</td><td>{d}</td></tr>" for f, t, d in SYMBOLES)
    return (f'<table class="t ci-symt"><thead><tr><th>Symbole</th><th>Description</th></tr></thead><tbody>{rows}'
            "</tbody></table>")


def figure_opto():
    return """<div class="ci-opto" id="ci-opto">
<svg class="ci-svg" id="ci-opto-svg" viewBox="0 0 900 250" role="img" aria-labelledby="ci-opto-t">
<title id="ci-opto-t">Isolation galvanique par optocoupleur : le signal d'entrée allume une LED, la lumière traverse
l'isolant et rend passant un phototransistor ; le signal de sortie reproduit l'entrée sans aucune liaison
électrique.</title>
<text x="20" y="24" class="ci-bt">Signal d'entrée (5 V)</text><text x="640" y="24" class="ci-bt">Signal de sortie (24 V)</text>
<rect x="20" y="40" width="240" height="90" class="ci-sc-bg"/><path id="ci-op-in" class="ci-op-sig" d=""/>
<rect x="640" y="40" width="240" height="90" class="ci-sc-bg"/><path id="ci-op-out" class="ci-op-sig o" d=""/>
<rect x="330" y="30" width="240" height="200" rx="8" class="ci-op-box"/><text x="450" y="222" text-anchor="middle" class="ci-bs">optocoupleur</text>
<line x1="450" y1="44" x2="450" y2="206" class="ci-op-iso"/><text x="456" y="60" class="ci-bs">isolant</text>
<g id="ci-op-led"><path d="M370 100 L410 100 L390 130 z" class="ci-op-d"/><line x1="370" y1="130" x2="410" y2="130" class="ci-op-w"/>
<path d="M260 85 H390 V100 M390 130 V180 H260" class="ci-op-w"/></g>
<g id="ci-op-ph"><circle cx="400" cy="115" r="0" class="ci-op-glow"/></g>
<g id="ci-op-rays"><path d="M418 104 l26 0 M418 118 l26 0 M418 132 l26 0" class="ci-op-ray"/></g>
<g><line x1="500" y1="92" x2="500" y2="140" class="ci-op-w ci-op-th"/><path d="M500 104 L530 86 V70 H640 M500 128 L530 146 V180 H640" class="ci-op-w" id="ci-op-tr"/>
<path d="M466 104 l22 10 M466 120 l22 10" class="ci-op-rin"/></g>
</svg>
<div class="ci-ctrl no-print"><button type="button" class="btn" id="ci-op-btn" aria-pressed="false">Envoyer une impulsion</button>
<label class="ci-sw"><input type="checkbox" id="ci-op-auto" checked> Signal carré automatique</label></div></div>"""


def figure_reseau():
    return """<div class="ci-net" id="ci-net">
<div class="ci-ctrl no-print" role="radiogroup" aria-label="Liaison">
<label class="ci-sw"><input type="radio" name="ci-net" value="wifi" checked> Wi-Fi</label>
<label class="ci-sw"><input type="radio" name="ci-net" value="bt"> Bluetooth</label>
<label class="ci-sw"><input type="radio" name="ci-net" value="eth"> Ethernet</label>
<label class="ci-sw"><input type="radio" name="ci-net" value="can"> Bus CAN</label>
<label class="ci-sw">Message <input type="text" id="ci-net-msg" value="Café prêt" maxlength="12" autocomplete="off"></label>
<button type="button" class="btn" id="ci-net-go">Envoyer la trame</button></div>
<svg class="ci-svg" id="ci-net-svg" viewBox="0 0 900 210" role="img" aria-labelledby="ci-net-t">
<title id="ci-net-t">Un produit communicant envoie une trame de bits vers un smartphone ou un réseau, par une liaison
filaire ou sans fil, en suivant un protocole.</title>
<g class="ci-net-b"><rect x="20" y="50" width="150" height="110" rx="8"/><text x="95" y="96" text-anchor="middle" class="ci-bt">Machine</text><text x="95" y="114" text-anchor="middle" class="ci-bt">à café</text></g>
<g class="ci-net-b"><rect x="730" y="40" width="150" height="130" rx="8"/><text x="805" y="96" text-anchor="middle" class="ci-bt" id="ci-net-dst">Smartphone</text><text x="805" y="148" text-anchor="middle" class="ci-bs" id="ci-net-rx">—</text></g>
<g id="ci-net-wire"><path d="M170 105 H730" class="ci-net-w"/></g>
<g id="ci-net-wave"><path d="M190 105 m0 -30 a30 30 0 0 1 0 60 M190 105 m14 -46 a46 46 0 0 1 0 92 M710 105 m0 -30 a30 30 0 0 0 0 60 M710 105 m-14 -46 a46 46 0 0 0 0 92" class="ci-net-wv"/></g>
<g id="ci-net-bits"></g>
<text x="450" y="196" text-anchor="middle" class="ci-bs" id="ci-net-proto"></text>
</svg></div>"""


def figure_octet():
    bits = "".join(f'<button type="button" class="ci-bit" data-w="{2 ** (7 - i)}" aria-pressed="false" '
                   f'aria-label="bit de poids {2 ** (7 - i)}">0</button>' for i in range(8))
    poids = "".join(f"<span>{2 ** (7 - i)}</span>" for i in range(8))
    return f"""<div class="simu ci-oct" id="ci-oct"><h3>L'octet : touche les bits</h3>
<div class="ci-oct-row"><div class="ci-oct-w">{poids}</div><div class="ci-oct-b">{bits}</div>
<div class="ci-oct-n"><span class="ci-nib" id="ci-nib-h">0</span><span class="ci-nib" id="ci-nib-l">0</span></div></div>
<div class="simu-out"><div><span>Binaire</span><b id="ci-oct-bin">(00000000)₂</b></div><div><span>Décimal</span><b id="ci-oct-dec">(0)₁₀</b></div>
<div><span>Hexadécimal</span><b id="ci-oct-hex">(00)₁₆</b></div></div>
<p class="ci-oct-calc" id="ci-oct-calc" aria-live="polite"></p>
<div class="ci-ctrl no-print"><label class="ci-sw">Valeur décimale <input type="number" id="ci-oct-in" min="0" max="255" value="0"></label>
<button type="button" class="btn ghost" data-v="181">181</button><button type="button" class="btn ghost" data-v="161">161</button>
<button type="button" class="btn ghost" data-v="123">(7B)₁₆</button><button type="button" class="btn ghost" data-v="163">(A3)₁₆</button>
<button type="button" class="btn ghost" data-v="255">255</button><button type="button" class="btn ghost" id="ci-oct-plus">+1</button></div></div>"""


ASCII_CTRL = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL", "BS", "HT", "LF", "VT", "FF", "CR", "SO", "SI",
              "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB", "CAN", "EM", "SUB", "ESC", "FS", "GS", "RS", "US"]


def table_ascii():
    def car(n):
        if n < 32:
            return f"<i>{ASCII_CTRL[n]}</i>"
        if n == 32:
            return "<i>SP</i>"
        if n == 127:
            return "<i>DEL</i>"
        return e(chr(n))
    cols = []
    for c in range(4):
        rows = "".join(f'<tr data-c="{n}"><td>{n}</td><td>{n:02X}</td><td>{n:08b}</td><td>{car(n)}</td></tr>'
                       for n in range(c * 32, c * 32 + 32))
        cols.append(f'<table class="t ci-asc"><thead><tr><th>Déc.</th><th>Hex.</th><th>Binaire</th><th>Car.</th></tr>'
                    f"</thead><tbody>{rows}</tbody></table>")
    return f'<div class="ci-asc-grid" id="ci-asc-grid">{"".join(cols)}</div>'


# ------------------------------------------------------------ le cours
def render(h):
    obj = "".join(f"<li>{o}</li>" for o in OBJECTIFS)
    comp = "".join(f"<tr><td><b>{c}</b></td><td>{t}</td><td>{n}</td></tr>" for c, t, n in COMPETENCES)
    pre = "".join(f"<li>{p}</li>" for p in PREREQUIS)
    fiche = (f'<div class="c2-fiche"><div><h3>Objectifs</h3><ul>{obj}</ul></div><div><h3>Compétences travaillées</h3>'
             f'<table class="t"><thead><tr><th>Code</th><th>Compétence</th><th>Taxo.</th></tr></thead><tbody>{comp}'
             f"</tbody></table></div><div><h3>Prérequis</h3><ul>{pre}</ul></div></div>")
    cs = h.course_section
    s1 = cs(1, "c3-prod", "Constitution d'un produit",
        "<p>Un produit, autonome ou automatisé, est conçu et fabriqué par l'homme pour fonctionner seul, en fonction des "
        "consignes entrées par l'utilisateur et d'un programme informatique.</p>"
        '<div class="exemple"><p><b>Exemple :</b> une machine à café à grains est capable de préparer automatiquement '
        "une boisson, en fonction de la demande du consommateur.</p></div>"
        "<h3>1.1 Principe</h3><p>Un produit est composé de nombreux composants qui assurent l'ensemble des fonctions "
        "nécessaires à son bon fonctionnement. Ces fonctions peuvent être regroupées sous la forme de deux chaînes : la "
        "<b>chaîne d'information</b> et la <b>chaîne de puissance</b>.</p><ul>"
        "<li>La chaîne de puissance précise comment l'énergie est amenée en quantité suffisante et sous la bonne forme "
        "aux <b>effecteurs</b> du produit, les composants qui effectuent l'action pour laquelle il a été conçu.</li>"
        "<li>La chaîne d'information <b>pilote</b> la chaîne d'énergie, généralement pour répondre aux demandes de "
        "l'utilisateur. Elle gère le fonctionnement et les actions du produit, et fait un rapport à l'utilisateur.</li>"
        "</ul><h3>1.2 La chaîne d'information</h3><p>Dans un produit, la chaîne d'information va, dans l'ordre :</p><ul>"
        "<li><b>acquérir</b> des informations venant de l'utilisateur, du produit lui-même ou de l'extérieur (réseau, "
        "autres produits, environnement) ;</li><li><b>traiter</b> les informations ;</li>"
        "<li><b>communiquer</b> des informations pour contrôler la chaîne de puissance, pour informer l'utilisateur ou "
        "pour les transmettre à l'extérieur (réseau, autres produits).</li></ul>"
        "<p>On peut donc découper la chaîne d'information en trois blocs fonctionnels : acquérir, traiter et "
        "communiquer.</p>"
        "<h3>Figures 1 et 2 — La machine à café : sa chaîne d'information commande sa chaîne de puissance</h3>"
        '<p class="cours-defi">À toi : prépare un espresso et suis le trajet de l\'information, étape par étape. Décoche '
        "« Détailler » pour revoir la chaîne d'information d'un seul bloc.</p>" + figure_cafe() +
        '<div class="remarque"><p>Un <b>microcontrôleur</b> est un composant électronique programmable.</p></div>'
        "<h3>1.3 Diagramme de blocs internes</h3><p>Le diagramme SysML de blocs internes (ibd) représente graphiquement "
        "la structure interne d'un produit : ses composants et leurs interactions. Il met en évidence les échanges de "
        "flux d'information, d'énergie et/ou de matière entre les composants. La chaîne d'information est souvent "
        "identifiable à l'intérieur de ce diagramme.</p>"
        "<h3>Figure 3 — Diagramme de blocs internes de la machine à café (chaîne d'information en bleu)</h3>"
        + figure_ibd())
    s2 = cs(2, "c3-acq", "Fonction Acquérir",
        "<p>Pour réaliser la fonction Acquérir, on fait appel à :</p><ul>"
        "<li>des composants réalisant une <b>interface homme-machine</b> (IHM), qui permet à l'utilisateur de transmettre "
        "ses consignes au produit : bouton poussoir, clavier, écran tactile ;</li>"
        "<li>des <b>capteurs</b>, qui détectent ou mesurent des phénomènes physiques (température, luminosité, présence "
        "d'obstacle, remplissage d'un réservoir…) : capteur de température et d'humidité, capteur de distance.</li></ul>"
        "<p>Les composants d'IHM et les capteurs produisent un flux d'information, qu'on appelle un <b>signal de "
        "sortie</b>.</p><h3>Figure 4 — Un capteur transforme une grandeur à mesurer en un signal de sortie</h3>"
        + figure_capteur() +
        '<div class="ci-trois"><div><h3>2.1 Détecteurs</h3><p>Un détecteur identifie l\'état d\'un phénomène de nature '
        "binaire : présence / absence d'un obstacle, porte ouverte / fermée. On l'appelle aussi capteur "
        "<b>tout-ou-rien</b> (TOR). Il produit un <b>signal logique</b>, qui ne prend que deux états : <b>0 logique</b> "
        "(état bas) ou <b>1 logique</b> (état haut).</p></div>"
        "<div><h3>2.2 Capteurs analogiques</h3><p>Un capteur analogique mesure une grandeur physique (température, "
        "distance, vitesse, angle). Il produit un <b>signal analogique</b> : une tension ou un courant qui peut prendre "
        "n'importe quelle valeur entre un minimum et un maximum, directement liée à la grandeur mesurée (proportionnelle, "
        "par exemple).</p></div>"
        "<div><h3>2.3 Capteurs numériques</h3><p>Un capteur numérique, ou <b>codeur</b>, mesure lui aussi une grandeur "
        "physique. Il produit un <b>signal numérique codé</b> : deux états seulement, comme un signal logique, mais qui "
        "transmettent une série de <b>bits</b> regroupés en <b>trames</b>. Pour lire la valeur, il faut connaître le "
        "<b>codage</b> utilisé par le capteur.</p></div></div>"
        '<div class="simu" id="ci-lab"><h3>Laboratoire : trois capteurs mesurent la même température</h3>'
        '<div class="ci-ctrl no-print"><button type="button" class="btn" id="ci-lab-play">⏸ Figer</button>'
        '<label class="ci-sw"><input type="checkbox" id="ci-lab-auto" checked> La température varie seule</label></div>'
        '<div class="simu-grid"><label><span>Température mesurée : <output id="ci-lab-t-o"></output></span>'
        '<input type="range" id="ci-lab-t" min="0" max="60" step="0.1" value="22"></label>'
        '<label><span>Seuil du détecteur : <output id="ci-lab-s-o"></output></span>'
        '<input type="range" id="ci-lab-s" min="5" max="55" step="0.5" value="30"></label></div>'
        '<svg class="ci-svg ci-lab-svg" id="ci-lab-svg" viewBox="0 0 980 540" role="img" aria-labelledby="ci-lab-tt">'
        '<title id="ci-lab-tt">Quatre graphiques défilent : la température mesurée et le seuil, la sortie logique du '
        "détecteur de seuil (0 ou 1), la tension du capteur analogique (10 mV par degré) et la trame du capteur "
        "numérique.</title></svg>"
        '<div class="simu-out simu-out4"><div><span>Détecteur (logique)</span><b id="ci-lab-o1"></b></div>'
        '<div><span>Capteur analogique</span><b id="ci-lab-o2"></b></div><div><span>Capteur numérique (trame)</span>'
        '<b id="ci-lab-o3"></b></div><div><span>Trame décodée</span><b id="ci-lab-o4"></b></div></div>'
        '<p class="small">Codage du capteur numérique de ce laboratoire : la trame de 10 bits donne la température en '
        "dixièmes de degré. Avec ce codage, la trame du cours, 1000101110, vaut 558 : 55,8 °C.</p></div>")
    s3 = cs(3, "c3-chaine", "Chaîne d'acquisition d'un signal analogique",
        "<h3>3.1 Chaîne d'acquisition</h3><p>Les composants qui traitent l'information sont généralement <b>numériques</b> : "
        "ils ne manipulent que des données binaires. Les signaux logiques et numériques leur conviennent ; les signaux "
        "analogiques, non : il faut les convertir de l'analogique vers le numérique. On parle de <b>numérisation</b> du "
        "signal.</p><p>Le signal d'un capteur est rarement numérisé directement, car il a deux défauts :</p><ul>"
        "<li>il est de trop faible amplitude pour être numérisé avec fidélité : on va donc l'<b>amplifier</b> ;</li>"
        "<li>il comporte des imperfections, le bruit ou les parasites : on va donc le <b>filtrer</b>.</li></ul>"
        "<p>L'amplification et le filtrage forment le <b>conditionnement</b> du signal. Conditionnement et numérisation "
        "font partie de la <b>chaîne d'acquisition</b> d'une grandeur physique.</p>"
        "<h3>Figure 5 — La chaîne d'acquisition, en direct</h3>"
        '<p class="cours-defi">À toi : règle le gain, la fréquence de coupure et la résolution du CAN, et regarde le '
        "signal se transformer d'une étape à l'autre.</p>" + figure_acquisition() +
        '<div class="simu ci-aq-set"><div class="simu-grid ci-g3">'
        '<label><span>Gain de l\'amplificateur : <output id="ci-aq-g-o"></output></span><input type="range" id="ci-aq-g" min="1" max="800" step="1" value="200"></label>'
        '<label><span>Fréquence de coupure du filtre : <output id="ci-aq-f-o"></output></span><input type="range" id="ci-aq-f" min="20" max="2000" step="10" value="120"></label>'
        '<label><span>Résolution du CAN : <output id="ci-aq-n-o"></output></span><input type="range" id="ci-aq-n" min="2" max="10" step="1" value="4"></label>'
        '</div><p class="simu-verdict" id="ci-aq-v" aria-live="polite"></p></div>'
        "<h3>3.2 Amplification</h3><p>L'amplification augmente, proportionnellement, les valeurs (tension ou courant) du "
        "signal, par un coefficient multiplicateur : le <b>gain</b>.</p>"
        '<p class="ci-form"><b>Valeur en sortie = Valeur en entrée × Gain</b></p>'
        '<div class="simu" id="ci-amp"><h3>Calcule l\'amplification</h3><div class="simu-grid">'
        '<label><span>Tension du capteur <i>V</i><sub>e</sub> : <output id="ci-amp-v-o"></output></span><input type="range" id="ci-amp-v" min="1" max="50" step="1" value="13"></label>'
        '<label><span>Gain : <output id="ci-amp-g-o"></output></span><input type="range" id="ci-amp-g" min="1" max="500" step="1" value="200"></label></div>'
        '<div class="simu-out"><div><span>Calcul</span><b id="ci-amp-c"></b></div><div><span>Tension de sortie</span><b id="ci-amp-s"></b></div>'
        '<div><span>Pleine échelle du CAN : 5 V</span><b id="ci-amp-p"></b></div></div>'
        '<p class="small">Exemple du cours : un capteur de température produit 13 mV à 23 °C ; avec un gain de 200, '
        "13 × 200 = 2 600 mV = 2,6 V.</p></div>"
        "<h3>3.3 Filtrage</h3><p>Le filtrage élimine les perturbations dues au milieu ambiant (bruit de fond, "
        "parasites…). Le mathématicien Joseph <b>Fourier</b> a montré que tout signal est la somme de signaux "
        "sinusoïdaux : le <b>fondamental</b> et les <b>harmoniques</b>, les composantes du signal. Il suffit donc "
        "d'atténuer les composantes de fréquence indésirable pour retrouver un signal « propre » : c'est le rôle des "
        "filtres.</p><p>On décrit un filtre par son <b>gabarit</b> : à chaque fréquence, il applique un gain "
        "<i>T</i>(<i>f</i>). Si <i>T</i>(<i>f</i>) = 0, la fréquence est éliminée ; si <i>T</i>(<i>f</i>) = 1, elle est "
        "conservée. Le plus courant, le <b>filtre passe-bas</b>, ne laisse passer que les composantes de fréquence "
        "inférieure à sa <b>fréquence de coupure</b> <i>f</i><sub>c</sub> : il supprime les parasites de haute "
        "fréquence.</p>"
        '<div class="simu" id="ci-four"><h3>Le filtre passe-bas, composante par composante</h3>'
        '<div class="simu-grid"><label><span>Fréquence de coupure <i>f</i><sub>c</sub> : <output id="ci-four-f-o"></output></span>'
        '<input type="range" id="ci-four-f" min="25" max="1000" step="5" value="1000"></label>'
        '<label><span>Composantes affichées</span><select id="ci-four-v"><option value="0">Le signal seulement</option>'
        '<option value="1" selected>Le signal et ses composantes</option></select></label></div>'
        '<svg class="ci-svg" id="ci-four-svg" viewBox="0 0 980 420" role="img" aria-labelledby="ci-four-t">'
        '<title id="ci-four-t">En haut, le signal reconstitué à partir des composantes conservées ; en bas, le spectre : '
        "le fondamental à 50 Hz, les harmoniques de rang 3, 5 et 7, et des parasites de haute fréquence ; la ligne rouge "
        "est le gabarit du filtre passe-bas.</title></svg>"
        '<p class="small">Fondamental à 50 Hz (rang 1), harmoniques de rang 3, 5 et 7 (150, 250 et 350 Hz) et bruit de '
        "fond au-delà de 500 Hz. Baisse <i>f</i><sub>c</sub> : le bruit disparaît d'abord, puis les harmoniques, "
        "jusqu'à ne garder que le fondamental.</p></div>"
        "<h3>3.4 Conversion analogique-numérique</h3><p>Le convertisseur analogique-numérique (<b>CAN</b>) transforme "
        "un signal d'entrée analogique en un signal de sortie numérique codé sur plusieurs bits : il produit une "
        "trame, comme le capteur numérique. Ses critères de choix :</p><ul>"
        "<li>la <b>durée de conversion</b>, qui répond à la rapidité d'exécution voulue ;</li>"
        "<li>sa <b>résolution <i>n</i></b> en nombre de bits, qui détermine sa précision ;</li>"
        "<li>sa <b>tension de pleine échelle <i>V</i><sub>ref</sub></b>, l'écart entre la plus grande et la plus petite "
        "tension qu'il peut convertir ; elle doit correspondre à la tension du signal à convertir.</li></ul>"
        "<p>Le plus petit écart de tension que le CAN distingue est le <b>quantum <i>q</i></b> :</p>"
        '<p class="ci-form"><b>q = V<sub>ref</sub> / 2<sup>n</sup></b></p><p>Le CAN produit une valeur numérique '
        "<i>N</i>, entière, comprise entre 0 et 2<sup>n</sup> − 1, liée à la tension d'entrée par :</p>"
        '<p class="ci-form"><b>N = V<sub>entrée</sub> / q</b> <span class="small">(on ne garde que la partie entière)</span></p>'
        '<div class="simu" id="ci-can"><h3>Le CAN : sa caractéristique en escalier</h3><div class="simu-grid ci-g3">'
        '<label><span>Résolution <i>n</i> : <output id="ci-can-n-o"></output></span><input type="range" id="ci-can-n" min="1" max="8" step="1" value="3"></label>'
        '<label><span>Pleine échelle <i>V</i><sub>ref</sub></span><select id="ci-can-r"><option value="8" selected>8 V</option><option value="5">5 V</option><option value="3.3">3,3 V</option></select></label>'
        '<label><span>Tension d\'entrée : <output id="ci-can-v-o"></output></span><input type="range" id="ci-can-v" min="0" max="1" step="0.001" value="0.4"></label></div>'
        '<svg class="ci-svg" id="ci-can-svg" viewBox="0 0 980 400" role="img" aria-labelledby="ci-can-t">'
        "<title id=\"ci-can-t\">Caractéristique de sortie du CAN : la valeur numérique N en fonction de la tension "
        "d'entrée ; un point repère la tension choisie.</title></svg>"
        '<div class="simu-out simu-out4"><div><span>Quantum q = Vref / 2ⁿ</span><b id="ci-can-q"></b></div>'
        '<div><span>N = Ventrée / q</span><b id="ci-can-c"></b></div><div><span>N en décimal</span><b id="ci-can-d"></b></div>'
        '<div><span>N en binaire (trame)</span><b id="ci-can-b"></b></div></div>'
        '<p class="ci-ctrl no-print"><button type="button" class="btn ghost" id="ci-can-scan">Balayer de 0 à Vref</button></p>'
        '<p class="small">Réglages du cours (3 bits, 8 V) : q = 1 V ; la sortie va de 000 à 111, soit de 0 à 7.</p></div>')
    s4 = cs(4, "c3-tra", "Fonction Traiter",
        "<h3>4.1 Traitement numérique</h3><p>Le traitement est réalisé par un composant de traitement numérique, comme "
        "un <b>microcontrôleur</b> ou un <b>microprocesseur</b>. Ce composant est <b>programmable</b> : on peut modifier "
        "facilement le fonctionnement du produit et le faire évoluer.</p>"
        "<h3>Figure 6 — Structure d'un système programmable</h3>" + figure_systeme() +
        "<h3>4.2 Description de l'algorithme</h3><p>Pour programmer un composant de traitement, on décrit d'abord son "
        "<b>algorithme</b> : la suite d'opérations qu'il va effectuer pour réaliser son objectif, en tenant compte des "
        "entrées (venant de la fonction Acquérir) et des sorties (vers la fonction Communiquer). L'algorithme se décrit "
        "graphiquement, avec un <b>algorigramme</b>, ou littéralement, avec du <b>pseudo-code</b>. Les trois structures "
        "de base sont la <b>séquence</b> (Début, Opération 1, Opération 2, Fin), l'<b>alternative</b> (Si… Alors… Sinon… "
        "Fin Si) et la <b>répétition</b> (Tant Que… Faire… Fin Tant Que).</p>"
        "<h3>4.3 Langages de programmation</h3><p>Une fois décrit, l'algorithme est transcrit dans un langage de "
        "programmation : graphique (Scratch, Tinkercad Codeblocks…) ou en lignes de code (Python, C++, Arduino, "
        "JavaScript, PHP…).</p>"
        "<h3>Figure 7 — Un même programme, de l'algorigramme au code</h3>"
        '<p class="cours-defi">À toi : appuie sur le bouton et regarde le programme s\'exécuter, dans l\'algorigramme et '
        "dans chaque langage.</p>" + figure_algo() +
        "<h3>Principaux symboles d'un algorigramme</h3>" + table_symboles())
    s5 = cs(5, "c3-com", "Fonction Communiquer",
        "<p>La fonction Communiquer permet de <b>restituer</b> les informations vers l'utilisateur ou vers la chaîne de "
        "puissance pour la piloter, et de <b>communiquer</b> avec l'extérieur, dans un réseau local ou sur Internet.</p>"
        "<h3>5.1 Restitution</h3><p>Les informations produites par le traitement sont restituées à l'utilisateur ou à "
        "un effecteur, sous forme de signal :</p>"
        '<div class="ci-rest" id="ci-rest"><div class="ci-r ci-r-log"><h4>Logique</h4><div class="ci-voyant" id="ci-voy"></div>'
        '<button type="button" class="btn ghost" id="ci-voy-b" aria-pressed="false">Allumer le voyant</button><p>Un voyant : allumé ou éteint.</p></div>'
        '<div class="ci-r ci-r-ana"><h4>Analogique</h4><svg viewBox="0 0 200 70" class="ci-son" aria-hidden="true"><path id="ci-son-p" d=""/></svg>'
        '<label class="ci-sw">Volume <input type="range" id="ci-son" min="0" max="1" step="0.05" value="0.6"></label><p>Un son, ou une commande '
        "vers la chaîne de puissance : toutes les valeurs.</p></div>"
        '<div class="ci-r ci-r-num"><h4>Numérique</h4><div class="ci-lcd" id="ci-lcd"><span id="ci-lcd-1">ESPRESSO</span><span id="ci-lcd-2">PRET</span></div>'
        '<label class="ci-sw">Texte <input type="text" id="ci-lcd-in" value="ESPRESSO" maxlength="16" autocomplete="off"></label>'
        "<p>Un afficheur LCD : des caractères envoyés en trames.</p></div></div>"
        "<p>Pour transmettre des commandes à la chaîne de puissance, des organes supplémentaires sont parfois "
        "nécessaires :</p><ul><li>l'<b>amplification de puissance</b> augmente la puissance du signal : commander un "
        "moteur qui demande une puissance élevée, augmenter la portée d'un émetteur radio ;</li>"
        "<li>l'<b>isolation galvanique</b> permet une commande <b>sans liaison électrique</b> : on fait communiquer des "
        "composants dont les tensions sont de valeur et de nature différentes.</li></ul>"
        "<h3>Figure 8 — Isolation galvanique : l'optocoupleur</h3>" + figure_opto() +
        "<h3>5.2 Communication</h3><p>La communication avec l'extérieur rend les produits <b>communicants</b> : ils "
        "échangent des données, fournissent un auto-diagnostic ou se commandent à distance. Les informations envoyées "
        "vers l'extérieur sont <b>numériques</b> et transmises sous forme de <b>trames</b>, selon les règles d'un "
        "<b>protocole de communication</b>. La transmission peut être <b>filaire</b> (Ethernet, bus CAN…) ou <b>sans "
        "fil</b> (Wi-Fi, Bluetooth…).</p><h3>Figure 9 — La machine prévient le smartphone : une trame part</h3>"
        + figure_reseau() + "<h3>Filaire ou sans fil ?</h3>" + h.jeu_html(JEU_LIAISONS, LIAISONS, "jeu-liaisons"))
    s6 = cs(6, "c3-enc", "Encodage de l'information",
        "<p>Les produits manipulent l'information sous forme binaire ; les humains, sous diverses formes (nombres "
        "décimaux, alphabet…). Il faut donc savoir convertir les données du langage humain au langage machine, et "
        "inversement.</p><h3>6.1 Base binaire</h3><p>Les produits représentent les nombres en base <b>binaire</b> (deux "
        "chiffres, 0 et 1 : les <b>bits</b>), quand les humains utilisent la base <b>décimale</b> (dix chiffres, de 0 à "
        "9). Les bits sont souvent regroupés par 8 en un <b>octet</b>, qui vaut de (0)<sub>10</sub> = "
        "(00000000)<sub>2</sub> à (255)<sub>10</sub> = (11111111)<sub>2</sub>. Chaque bit a un <b>poids</b> : 128, 64, "
        "32, 16, 8, 4, 2, 1 ; la valeur est la somme des poids des bits à 1.</p>"
        "<h3>6.2 Base hexadécimale</h3><p>La base <b>hexadécimale</b> utilise 16 chiffres, de 0 à 9 puis de A à F (A = 10 "
        "… F = 15). Un chiffre hexadécimal correspond exactement à <b>4 bits</b> : on passe très facilement du binaire à "
        "l'hexadécimal. Un octet vaut de (00)<sub>16</sub> à (FF)<sub>16</sub>.</p>" + figure_octet() +
        '<div class="simu" id="ci-defi"><h3>Défi : convertis</h3><p class="ci-defi-q" id="ci-defi-q"></p>'
        '<div class="ci-ctrl"><input type="text" id="ci-defi-in" autocomplete="off" spellcheck="false" aria-label="Ta réponse">'
        '<button type="button" class="btn" id="ci-defi-ok">Vérifier</button><button type="button" class="btn ghost" id="ci-defi-new">Autre nombre</button>'
        '<span class="ci-defi-s" id="ci-defi-s"></span></div><p class="simu-verdict" id="ci-defi-v" aria-live="polite"></p></div>'
        "<h3>6.3 Encodage ASCII</h3><p>Le texte aussi est codé en binaire : chaque caractère (lettre, ponctuation, "
        "chiffre…) a un code, donné par une table de conversion. La table <b>ASCII</b> représente 128 caractères, chacun "
        "codé sur 7 bits ; en mémoire, un caractère occupe un octet complet, dont le premier bit vaut toujours 0.</p>"
        '<div class="simu" id="ci-asc"><h3>Écris un mot, lis son code</h3><label class="ci-sw">Texte '
        '<input type="text" id="ci-asc-in" value="I2D" maxlength="14" autocomplete="off" spellcheck="false"></label>'
        '<div class="ci-asc-out" id="ci-asc-out" aria-live="polite"></div>'
        '<p class="small">Exemple du cours : « I2D » s\'écrit 01001001 00110010 01000100. Les lettres accentuées ne sont '
        "pas dans la table ASCII.</p></div>"
        '<details class="ci-asc-d"><summary>La table ASCII complète (les caractères de ton texte sont surlignés)</summary>'
        + table_ascii() + "</details>")
    s7 = cs(7, "c3-syn", "Synthèse : range chaque composant",
        "<p>Pour chaque composant, choisis la fonction de la chaîne d'information qu'il réalise.</p>"
        + h.jeu_html(JEU_FONCTIONS, FONCTIONS_I, "jeu-fct-i") +
        "<p>Puis, pour chaque élément, le type de signal.</p>" + h.jeu_html(JEU_SIGNAUX, SIGNAUX, "jeu-sig"))
    s8 = h.quiz_section(8, "c3-quiz", QUIZ_3, "q3_")
    return f"""<div class="cours" id="cours-3">
{h.course_head("Cours 3", "Niveau 2", "Chaîne d'information des produits",
               "Suivre l'information d'un produit, de la consigne de l'utilisateur jusqu'aux commandes et aux messages : "
               "acquérir, traiter, communiquer ; puis numériser un signal et encoder l'information. Environ 3 h, "
               "avec une machine à café animée, des laboratoires, un programme qui s'exécute, trois jeux et un quiz.")}
{fiche}
{h.course_nav([("c3-prod", "Produit"), ("c3-acq", "Acquérir"), ("c3-chaine", "Acquisition"), ("c3-tra", "Traiter"),
               ("c3-com", "Communiquer"), ("c3-enc", "Encodage"), ("c3-syn", "Synthèse"), ("c3-quiz", "Quiz")])}
{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}
<div class="cours-foot no-print"><a class="btn" href="?ex=cours-chaine-energie">Cours 2 : chaîne d'énergie</a>
<a class="btn ghost" href="?ex=chaines-information-energie">Exercice 1.1</a>
<button type="button" class="btn ghost cours-print">Imprimer le cours</button>
<a class="btn ghost" href="?">{h.HOUSE} Retour à l'accueil</a></div>
</div>"""


# ------------------------------------------------------------ comportement (inséré dans l'aiguillage, comme les cours 1 et 2)
CI_JS = r"""
  function initCoursInformation(home) {
    var NS = "http://www.w3.org/2000/svg";
    var calme = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    function q(s, r) { return (r || home).querySelector(s); }
    function qa(s, r) { return Array.prototype.slice.call((r || home).querySelectorAll(s)); }
    function mk(tag, at, parent) { var e = document.createElementNS(NS, tag); for (var k in at) e.setAttribute(k, at[k]); if (parent) parent.appendChild(e); return e; }
    function tx(parent, x, y, s, cls, anchor) { var t = mk("text", { x: x, y: y, "class": cls || "", "text-anchor": anchor || "start" }, parent); t.textContent = s; return t; }
    function pad(s, n) { s = String(s); while (s.length < n) s = "0" + s; return s; }
    function sub(s, b) { return "(" + s + ")" + { 2: "₂", 10: "₁₀", 16: "₁₆" }[b]; }
    var animers = [];

    // ---------- 1. la machine à café : le trajet de l'information, étape par étape ----------
    (function () {
      var svg = q("#ci-cafe-svg"), det = q("#ci-cafe-det"), stepP = q("#ci-cafe-step"), cup = q("#ci-cup");
      var STEPS = [
        { t: "Acquérir : l'utilisateur appuie sur le bouton « espresso ». Le bouton transmet sa consigne à la chaîne d'information (signal logique).",
          f: ["cf-cons"], b: ["cb-user", "cb-acq"] },
        { t: "Acquérir : les capteurs renvoient les états de la machine : réservoir d'eau rempli, tiroir à marc en place, eau à la bonne température.",
          f: ["cf-etat"], b: ["cb-cp", "cb-acq"] },
        { t: "Traiter : le microcontrôleur compare la consigne aux états de la machine et décide : moudre, chauffer, pomper.",
          f: ["cf-at"], b: ["cb-tra"] },
        { t: "Communiquer : la carte de pilotage envoie les commandes à la chaîne de puissance ; le pictogramme « espresso » clignote pour l'utilisateur.",
          f: ["cf-tc", "cf-cmd", "cf-info"], b: ["cb-com", "cb-cp", "cb-user"] },
        { t: "La chaîne de puissance, alimentée par le réseau électrique, moud les grains, chauffe et pompe l'eau : le café coule (matière d'œuvre : eau et grains → café).",
          f: ["cf-pin", "cf-pout", "cf-mo1", "cf-mo2"], b: ["cb-res", "cb-cp", "cb-faire", "cb-eau", "cb-cafe"], cup: 1 },
        { t: "Fin : les capteurs signalent la fin de la préparation ; la machine sonne et le pictogramme reste allumé : informations restituées à l'utilisateur.",
          f: ["cf-etat", "cf-at", "cf-tc", "cf-info"], b: ["cb-acq", "cb-tra", "cb-com", "cb-user"], cup: 2 }
      ];
      var cur = -1, timer = null, lvl = 0;
      function show(i) {
        cur = i;
        qa(".ci-fl.on, .ci-box.on", svg).forEach(function (e) { e.classList.remove("on"); });
        if (i < 0) { stepP.textContent = "Appuie sur « Préparer un espresso » : suis le trajet de l'information, puis celui de l'énergie."; return; }
        var S = STEPS[i], simple = !det.checked;
        S.f.forEach(function (k) { if (!(simple && (k === "cf-at" || k === "cf-tc"))) q("#" + k, svg).classList.add("on"); });
        S.b.forEach(function (k) { q("#" + (simple && /^cb-(acq|tra|com)$/.test(k) ? "cb-ci" : k), svg).classList.add("on"); });
        cup.classList.toggle("fill", !!S.cup); cup.classList.toggle("done", S.cup === 2);
        if (!S.cup) lvl = 0;
        stepP.innerHTML = "<b>Étape " + (i + 1) + " sur " + STEPS.length + ".</b> " + S.t;
      }
      function stop() { if (timer) { clearInterval(timer); timer = null; } q("#ci-cafe-go").textContent = "▶ Préparer un espresso"; }
      q("#ci-cafe-go").addEventListener("click", function () {
        if (timer) { stop(); return; }
        show(0); q("#ci-cafe-go").textContent = "■ Arrêter";
        timer = setInterval(function () { if (cur >= STEPS.length - 1) { stop(); return; } show(cur + 1); }, 3400);
      });
      q("#ci-cafe-next").addEventListener("click", function () { stop(); show(cur >= STEPS.length - 1 ? 0 : cur + 1); });
      det.addEventListener("change", function () { svg.classList.toggle("simple", !det.checked); show(cur); });
      var liq = q(".ci-cup-l", svg);
      animers.push(function (dt) {
        if (cup.classList.contains("fill")) lvl = Math.min(1, lvl + dt / 2.6);
        liq.setAttribute("y", 216 + 22 - 26 * lvl); liq.setAttribute("height", 26 * lvl);
      });
    })();

    // ---------- 2. le diagramme de blocs internes : un bloc touché, ses échanges ----------
    (function () {
      var svg = q("#ci-ibd-svg"), out = q("#ci-ibd-info");
      var CH = { i: "Chaîne d'information", e: "Chaîne de puissance", m: "Matière d'œuvre", ext: "Extérieur du produit" };
      var DATA = __IBD__;
      qa(".ci-box[data-k]", svg).forEach(function (b) {
        function pick() {
          var k = b.getAttribute("data-k"), d = DATA[k], ex = [];
          qa(".ci-box.sel", svg).forEach(function (x) { x.classList.remove("sel"); });
          b.classList.add("sel"); svg.classList.add("focus");
          qa(".ci-fl", svg).forEach(function (l) {
            var on = (" " + l.getAttribute("data-b") + " ").indexOf(" " + k + " ") >= 0;
            l.classList.toggle("on", on);
            if (on) { var t = l.querySelector("text"); ex.push(t ? t.textContent : "liaison " + l.getAttribute("data-b").replace(" ", " → ")); }
          });
          out.innerHTML = "<h4>" + d.n + (d.f ? ' <span class="ci-tag ci-tag-' + d.c + '">' + d.f + "</span>" : "") + "</h4><p><b>" + CH[d.c] +
            ".</b> " + d.r + "</p>" + (ex.length ? "<p class=\"small\">Échanges : " + ex.join(" ; ") + ".</p>" : "");
        }
        b.addEventListener("click", pick);
        b.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
      });
    })();

    // ---------- 3. le laboratoire des capteurs ----------
    (function () {
      var svg = q("#ci-lab-svg"), tIn = q("#ci-lab-t"), sIn = q("#ci-lab-s"), auto = q("#ci-lab-auto"), play = q("#ci-lab-play");
      var X0 = 120, W = 840, P = [{ y: 14, h: 100, t: "Température", u: "°C", max: 60 }, { y: 146, h: 70, t: "Détecteur", u: "logique", max: 1 },
        { y: 250, h: 100, t: "Capteur", u: "analogique (mV)", max: 600 }, { y: 384, h: 100, t: "Capteur", u: "numérique (trame)", max: 1 }];
      var paths = [];
      P.forEach(function (p, i) {
        mk("rect", { x: X0, y: p.y, width: W, height: p.h, "class": "ci-sc-bg" }, svg);
        tx(svg, X0 - 12, p.y + p.h / 2 - 4, p.t, "ci-lab-l", "end"); tx(svg, X0 - 12, p.y + p.h / 2 + 13, p.u, "ci-lab-u", "end");
        if (i === 0 || i === 2) [0, 0.5, 1].forEach(function (f) {
          mk("line", { x1: X0, x2: X0 + W, y1: p.y + p.h * (1 - f), y2: p.y + p.h * (1 - f), "class": "ci-sc-g" }, svg);
          tx(svg, X0 + 4, p.y + p.h * (1 - f) + (f === 1 ? 12 : -3), String(p.max * f), "ci-sc-t");
        });
        if (i === 1) { tx(svg, X0 + 4, p.y + 12, "1", "ci-sc-t"); tx(svg, X0 + 4, p.y + p.h - 3, "0", "ci-sc-t"); }
        paths.push(mk("path", { "class": "ci-lab-c c" + i, d: "" }, svg));
      });
      var seuil = mk("line", { x1: X0, x2: X0 + W, "class": "ci-lab-seuil" }, svg);
      var seuilT = tx(svg, X0 + W - 6, 0, "seuil", "ci-lab-st", "end");
      var bitsG = mk("g", {}, svg);
      tx(svg, X0 + W / 2, 532, "temps →  (les 12 dernières secondes)", "ci-sc-t", "middle");
      var N = 240, hist = [], run = true, tt = -12, acc = 0;
      function T() { return Math.max(0, Math.min(60, 30 + 17 * Math.sin(tt * 2 * Math.PI / 9) + 4 * Math.sin(tt * 2 * Math.PI / 2.7 + 1))); }
      function draw() {
        var s = +sIn.value, T0 = hist[N - 1], code = Math.round(T0 * 10), bits = pad(code.toString(2), 10);
        q("#ci-lab-t-o").textContent = fr(T0, 1) + " °C"; q("#ci-lab-s-o").textContent = fr(s, 1) + " °C";
        var d = [[], [], []];
        hist.forEach(function (v, k) {
          var x = (X0 + k * W / (N - 1)).toFixed(1);
          d[0].push(x + " " + (P[0].y + P[0].h * (1 - v / 60)).toFixed(1));
          d[1].push(x + " " + (P[1].y + (v > s ? 6 : P[1].h - 6)));
          d[2].push(x + " " + (P[2].y + P[2].h * (1 - v * 10 / 600)).toFixed(1));
        });
        paths[0].setAttribute("d", "M" + d[0].join(" L"));
        paths[1].setAttribute("d", "M" + d[1].join(" L"));
        paths[2].setAttribute("d", "M" + d[2].join(" L"));
        var ys = P[0].y + P[0].h * (1 - s / 60); seuil.setAttribute("y1", ys); seuil.setAttribute("y2", ys); seuilT.setAttribute("y", ys - 4);
        // trame du capteur numérique : 10 bits sur toute la largeur
        while (bitsG.firstChild) bitsG.removeChild(bitsG.firstChild);
        var p3 = P[3], bw = W / 10, dd = [];
        for (var b = 0; b < 10; b++) {
          var y = p3.y + (bits[b] === "1" ? 18 : p3.h - 10), x = X0 + b * bw;
          dd.push((b ? "L" : "M") + x + " " + y + " H" + (x + bw));
          tx(bitsG, x + bw / 2, p3.y + 14, bits[b], "ci-lab-bit", "middle");
          if (b) mk("line", { x1: x, x2: x, y1: p3.y, y2: p3.y + p3.h, "class": "ci-sc-g" }, bitsG);
        }
        paths[3].setAttribute("d", dd.join(" "));
        q("#ci-lab-o1").textContent = T0 > s ? "1 (au-dessus du seuil)" : "0 (sous le seuil)";
        q("#ci-lab-o2").textContent = fr(T0 * 10, 0) + " mV";
        q("#ci-lab-o3").textContent = bits;
        q("#ci-lab-o4").textContent = code + " → " + fr(code / 10, 1) + " °C";
      }
      for (var i = 0; i < N; i++) { tt += 0.05; hist.push(T()); }  // 12 s d'historique dès l'ouverture
      play.addEventListener("click", function () { run = !run; play.textContent = run ? "⏸ Figer" : "▶ Reprendre"; });
      tIn.addEventListener("input", function () { auto.checked = false; if (!run) { hist[N - 1] = +tIn.value; draw(); } });
      sIn.addEventListener("input", draw);
      animers.push(function (dt) {
        if (!run) return;
        acc += dt; if (auto.checked) tt += dt;
        if (acc < 0.05) return;
        acc = 0;
        var v = auto.checked ? T() : +tIn.value;
        if (auto.checked) tIn.value = v.toFixed(1);
        hist.shift(); hist.push(v); draw();
      });
      draw();
    })();

    // ---------- 4. la chaîne d'acquisition en direct ----------
    var COMPO = [[50, 1, 0], [150, 0.18, 0.6], [250, 0.08, 1.9], [900, 0.16, 0.3], [1350, 0.12, 2.2], [1800, 0.14, 4.1], [2600, 0.1, 1.2], [3300, 0.09, 5.3]];
    (function () {
      var g = q("#ci-aq-g"), f = q("#ci-aq-f"), n = q("#ci-aq-n"), scopes = qa(".ci-aq-sc"), ph = 0, VREF = 5;
      var SW = 150, SH = 74, NS_ = 300, TW = 0.04;
      function cap(t, fc) { // tension du capteur en volts : 6 mV + 4 mV × composantes
        var s = 0;
        COMPO.forEach(function (c) { if (fc === undefined || c[0] <= fc) s += c[1] * Math.sin(2 * Math.PI * c[0] * t + c[2]); });
        return 0.006 + 0.004 * s;
      }
      function draw() {
        var G = +g.value, fc = +f.value, nb = +n.value, Q = VREF / Math.pow(2, nb), max = Math.pow(2, nb) - 1;
        q("#ci-aq-g-o").textContent = G; q("#ci-aq-f-o").textContent = fc + " Hz"; q("#ci-aq-n-o").textContent = nb + " bits (" + (max + 1) + " niveaux)";
        var series = [[], [], [], [], []], sat = false, top = 0;
        for (var k = 0; k < NS_; k++) {
          var t = ph + k * TW / NS_, u = cap(t), a = G * u, fl = G * cap(t, fc);
          if (a > VREF || a < 0) sat = true;
          a = Math.max(0, Math.min(VREF, a)); fl = Math.max(0, Math.min(VREF, fl)); top = Math.max(top, fl);
          var N = Math.min(max, Math.floor(fl / Q));
          series[0].push(u); series[1].push(a); series[2].push(fl); series[3].push(N * Q); series[4].push(N);
        }
        var ranges = [[0, 0.016], [0, VREF], [0, VREF], [0, VREF], [0, max]];
        scopes.forEach(function (sc, i) {
          var d = [], r = ranges[i];
          series[i].forEach(function (v, k) {
            var x = (k * (SW - 8) / (NS_ - 1)).toFixed(1), y = (SH - 4 - (SH - 8) * (v - r[0]) / (r[1] - r[0] || 1)).toFixed(1);
            if (i === 4 && k % 15) return;
            d.push((d.length ? "L" : "M") + x + " " + y);
          });
          sc.querySelector(".ci-sc-c").setAttribute("d", i === 4 ? d.join(" ").replace(/L/g, "M").replace(/M([\d.]+) ([\d.]+)/g, "M$1 $2 h0.1") : d.join(" "));
          sc.classList.toggle("dots", i === 4);
        });
        var v = [];
        if (sat) v.push("Gain trop fort : le signal dépasse la pleine échelle du CAN (5 V), il est écrêté.");
        else if (top < 1) v.push("Gain trop faible : le signal n'occupe qu'une petite partie des 5 V du CAN, la numérisation est grossière.");
        if (fc < 50) v.push("Fréquence de coupure trop basse : le fondamental (50 Hz) lui-même est supprimé.");
        else if (fc > 800) v.push("Le filtre laisse passer les parasites de haute fréquence.");
        if (nb <= 3) v.push("Résolution faible : l'escalier du CAN est grossier.");
        var el = q("#ci-aq-v");
        el.textContent = v.length ? v.join(" ") : "Bon réglage : le signal est amplifié sans écrêtage, débarrassé de ses parasites et finement numérisé.";
        el.className = "simu-verdict " + (v.length ? "ko" : "ok");
      }
      [g, f, n].forEach(function (i) { i.addEventListener("input", draw); });
      animers.push(function (dt) { if (calme) return; ph += dt * 0.004; draw(); });
      draw();
    })();

    // ---------- 5. l'amplification ----------
    (function () {
      var v = q("#ci-amp-v"), g = q("#ci-amp-g");
      function draw() {
        var ve = +v.value, G = +g.value, vs = ve * G;
        q("#ci-amp-v-o").textContent = ve + " mV"; q("#ci-amp-g-o").textContent = G;
        q("#ci-amp-c").textContent = ve + " × " + G + " = " + fr(vs, 0) + " mV";
        q("#ci-amp-s").textContent = fr(vs / 1000, 2) + " V";
        q("#ci-amp-p").textContent = vs > 5000 ? "dépassée : écrêtage" : "respectée (" + fr(vs / 50, 0) + " %)";
      }
      [v, g].forEach(function (i) { i.addEventListener("input", draw); });
      draw();
    })();

    // ---------- 6. le filtre passe-bas et le spectre ----------
    (function () {
      var svg = q("#ci-four-svg"), fIn = q("#ci-four-f"), vIn = q("#ci-four-v"), ph = 0;
      var SP = [[50, 1, 0, "fondamental (rang 1)"], [150, 0.33, 0.4, "rang 3"], [250, 0.2, 1.1, "rang 5"], [350, 0.14, 2.3, "rang 7"],
        [560, 0.1, 0.7, ""], [640, 0.08, 2.9, ""], [730, 0.11, 1.6, ""], [820, 0.07, 4.2, ""], [910, 0.09, 3.3, ""]];
      var X0 = 70, W = 880, TY = 20, TH = 170, FY = 250, FH = 130;
      mk("rect", { x: X0, y: TY, width: W, height: TH, "class": "ci-sc-bg" }, svg);
      mk("line", { x1: X0, x2: X0 + W, y1: TY + TH / 2, y2: TY + TH / 2, "class": "ci-sc-g" }, svg);
      tx(svg, X0 - 8, TY + 14, "signal", "ci-sc-t", "end"); tx(svg, X0 + W, TY + TH + 16, "temps (40 ms)", "ci-sc-t", "end");
      var comps = mk("g", { "class": "ci-four-comps" }, svg), sum = mk("path", { "class": "ci-four-sum" }, svg);
      var cp = SP.map(function () { return mk("path", { "class": "ci-four-c" }, comps); });
      mk("line", { x1: X0, x2: X0 + W, y1: FY + FH, y2: FY + FH, "class": "ci-sc-ax" }, svg);
      tx(svg, X0 + W, FY + FH + 30, "fréquence (Hz)", "ci-sc-t", "end"); tx(svg, X0 - 8, FY + 10, "amplitude", "ci-sc-t", "end");
      [0, 200, 400, 600, 800, 1000].forEach(function (fq) { tx(svg, X0 + fq / 1000 * W, FY + FH + 16, String(fq), "ci-sc-t", "middle"); });
      var bars = SP.map(function (c) {
        var x = X0 + c[0] / 1000 * W, h = c[1] * (FH - 20);
        var r = mk("rect", { x: x - 6, y: FY + FH - h, width: 12, height: h, "class": "ci-four-bar" + (c[0] > 500 ? " bruit" : "") }, svg);
        if (c[3]) tx(svg, x + 9, FY + FH - h + 4, c[3], "ci-four-bl");
        return r;
      });
      tx(svg, X0 + 0.73 * W, FY + 52, "bruit de fond", "ci-four-bl", "middle");
      var gab = mk("path", { "class": "ci-four-gab" }, svg), gabT = tx(svg, 0, FY + 6, "", "ci-four-gt");
      function draw() {
        var fc = +fIn.value, all = vIn.value === "1", ds = [];
        q("#ci-four-f-o").textContent = fc + " Hz";
        var xc = X0 + Math.min(fc, 1000) / 1000 * W;
        gab.setAttribute("d", "M" + X0 + " " + (FY + 14) + " H" + xc + " V" + (FY + FH) + " H" + (X0 + W));
        gabT.setAttribute("x", Math.max(X0 + 60, xc - 6)); gabT.setAttribute("text-anchor", "end");
        gabT.textContent = "gabarit : T(f) = 1 jusqu'à fc = " + fc + " Hz, puis 0";
        SP.forEach(function (c, i) {
          var kept = c[0] <= fc, d = [];
          bars[i].classList.toggle("off", !kept);
          for (var k = 0; k <= 200; k++) {
            var t = ph + k / 200 * 0.04, y = TY + TH / 2 - 52 * c[1] * Math.sin(2 * Math.PI * c[0] * t + c[2]);
            d.push((k ? "L" : "M") + (X0 + k / 200 * W).toFixed(1) + " " + y.toFixed(1));
          }
          cp[i].setAttribute("d", d.join(" ")); cp[i].classList.toggle("off", !kept); cp[i].style.display = all ? "" : "none";
        });
        for (var k = 0; k <= 400; k++) {
          var t = ph + k / 400 * 0.04, s = 0;
          SP.forEach(function (c) { if (c[0] <= fc) s += c[1] * Math.sin(2 * Math.PI * c[0] * t + c[2]); });
          ds.push((k ? "L" : "M") + (X0 + k / 400 * W).toFixed(1) + " " + (TY + TH / 2 - 52 * s).toFixed(1));
        }
        sum.setAttribute("d", ds.join(" "));
      }
      [fIn, vIn].forEach(function (i) { i.addEventListener("input", draw); });
      animers.push(function (dt) { if (calme) return; ph += dt * 0.006; draw(); });
      draw();
    })();

    // ---------- 7. le CAN : caractéristique en escalier ----------
    (function () {
      var svg = q("#ci-can-svg"), nIn = q("#ci-can-n"), rIn = q("#ci-can-r"), vIn = q("#ci-can-v"), scan = null;
      var X0 = 110, W = 820, Y0 = 40, H = 300, g = mk("g", {}, svg);
      function draw() {
        while (g.firstChild) g.removeChild(g.firstChild);
        var n = +nIn.value, R = +rIn.value, L = Math.pow(2, n), Q = R / L, ve = +vIn.value * R, N = Math.min(L - 1, Math.floor(ve / Q + 1e-9));
        function X(v) { return X0 + v / R * W; } function Y(k) { return Y0 + H - k / (L - 1 || 1) * H; }
        mk("rect", { x: X0, y: Y0, width: W, height: H, "class": "ci-sc-bg" }, g);
        var stepY = L <= 16 ? 1 : L / 8;
        for (var k = 0; k < L; k += stepY) {
          mk("line", { x1: X0, x2: X0 + W, y1: Y(k), y2: Y(k), "class": "ci-sc-g" }, g);
          tx(g, X0 - 8, Y(k) + 4, L <= 16 ? pad(k.toString(2), n) : String(k), "ci-sc-t", "end");
        }
        var stepX = L <= 16 ? 1 : L / 8;
        for (var j = 0; j <= L; j += stepX) tx(g, X(j * Q), Y0 + H + 18, fr(j * Q, Q * stepX < 0.1 ? 3 : Q * stepX < 1 ? 2 : 0), "ci-sc-t", "middle");
        tx(g, X0 + W, Y0 + H + 36, "tension d'entrée (V)", "ci-sc-t", "end");
        tx(g, X0, Y0 - 16, L <= 16 ? "sortie numérique (binaire)" : "sortie numérique N", "ci-sc-t", "start");
        var d = "M" + X(0) + " " + Y(0);
        for (k = 0; k < L; k++) d += " H" + X(Math.min(R, (k + 1) * Q)) + (k < L - 1 ? " V" + Y(k + 1) : "");
        mk("path", { d: d, "class": "ci-can-st" }, g);
        mk("path", { d: "M" + X(N * Q) + " " + Y(N) + " H" + X(Math.min(R, (N + 1) * Q)), "class": "ci-can-hl" }, g);
        mk("line", { x1: X(ve), x2: X(ve), y1: Y0 + H, y2: Y(N), "class": "ci-can-v" }, g);
        mk("line", { x1: X0, x2: X(ve), y1: Y(N), y2: Y(N), "class": "ci-can-v" }, g);
        mk("circle", { cx: X(ve), cy: Y(N), r: 7, "class": "ci-can-pt" }, g);
        q("#ci-can-n-o").textContent = n + " bit" + (n > 1 ? "s" : "") + " (" + L + " valeurs)";
        q("#ci-can-v-o").textContent = fr(ve, 2) + " V";
        q("#ci-can-q").textContent = fr(R, R % 1 ? 1 : 0) + " / " + L + " = " + (Q >= 0.1 ? fr(Q, 3) + " V" : fr(Q * 1000, 1) + " mV");
        q("#ci-can-c").textContent = fr(ve, 2) + " / " + fr(Q, 3) + " = " + fr(ve / Q, 2);
        q("#ci-can-d").textContent = N + (ve / Q >= L ? " (valeur maximale)" : "");
        q("#ci-can-b").textContent = pad(N.toString(2), n);
      }
      [nIn, rIn, vIn].forEach(function (i) { i.addEventListener("input", draw); });
      q("#ci-can-scan").addEventListener("click", function () { scan = scan === null ? 0 : null; vIn.value = 0; draw(); });
      animers.push(function (dt) {
        if (scan === null) return;
        scan += dt / 5; vIn.value = Math.min(1, scan); draw();
        if (scan >= 1) scan = null;
      });
      draw();
    })();

    // ---------- 8. le système programmable : des données circulent ----------
    (function () {
      var pk = q("#ci-sys-pk"), clk = q(".ci-clk"), t = 0, dots = [];
      [[130, 356], [520, 746]].forEach(function (seg, i) {
        for (var k = 0; k < 3; k++) dots.push({ a: seg[0], b: seg[1], o: k / 3 + i * 0.17, el: mk("circle", { r: 5, cy: 148, "class": "ci-pk" }, pk) });
      });
      animers.push(function (dt) {
        if (calme) return;
        t += dt;
        dots.forEach(function (d) { var f = (t * 0.45 + d.o) % 1; d.el.setAttribute("cx", d.a + (d.b - d.a) * f); });
        clk.classList.toggle("tic", Math.floor(t * 4) % 2 === 0);
      });
    })();

    // ---------- 9. le programme « bouton → LED », exécuté pas à pas ----------
    (function () {
      var svg = q("#ci-algo"), tok = q("#ci-tok"), led = q("#ci-led"), ledL = q("#ci-led-l"), bp = q("#ci-bp"), vit = q("#ci-vit");
      var POS = { deb: [134, 37], lire: [138, 104], test: [138, 195], on: [280, 282], off: [152, 282] };  // jeton à côté de l'étape active
      var pressed = false, node = "deb", acc = 0, manuel = false;
      function suivant(n) { return n === "deb" ? "lire" : n === "lire" ? "test" : n === "test" ? (pressed ? "on" : "off") : "lire"; }
      function show() {
        qa(".ci-an", svg).forEach(function (a) { a.classList.toggle("on", a.id === "ci-an-" + node); });
        tok.style.transform = "translate(" + (POS[node][0] - 210) + "px," + (POS[node][1] - 37) + "px)";
        qa(".ci-cl, .ci-blk[data-n]").forEach(function (l) { l.classList.toggle("on", l.getAttribute("data-n") === node); });
        if (node === "on") { led.classList.add("on"); ledL.textContent = "LED (broche 13) : allumée"; }
        if (node === "off") { led.classList.remove("on"); ledL.textContent = "LED (broche 13) : éteinte"; }
      }
      function press(v) { pressed = v; bp.classList.toggle("down", v); bp.setAttribute("aria-pressed", v ? "true" : "false"); }
      bp.addEventListener("pointerdown", function (e) { e.preventDefault(); press(true); });
      ["pointerup", "pointerleave", "pointercancel"].forEach(function (ev) { bp.addEventListener(ev, function () { press(false); }); });
      bp.addEventListener("keydown", function (e) { if (e.key === " " || e.key === "Enter") { e.preventDefault(); press(true); } });
      bp.addEventListener("keyup", function (e) { if (e.key === " " || e.key === "Enter") press(false); });
      q("#ci-pas").addEventListener("click", function () {
        manuel = true; q("#ci-pas").textContent = "Pas suivant"; node = suivant(node); show();
      });
      vit.addEventListener("input", function () { manuel = false; q("#ci-pas").textContent = "Pas à pas"; });
      qa(".ci-tabs [role=tab]").forEach(function (b) {
        b.addEventListener("click", function () {
          qa(".ci-tabs [role=tab]").forEach(function (x) { x.setAttribute("aria-selected", x === b ? "true" : "false"); });
          qa(".ci-code").forEach(function (c) { c.hidden = c.id !== "ci-code-" + b.getAttribute("data-t"); });
        });
      });
      animers.push(function (dt) {
        if (manuel) return;
        acc += dt;
        if (acc < 1.4 / +vit.value) return;
        acc = 0; node = suivant(node); show();
      });
      show();
    })();

    // ---------- 10. la restitution : logique, analogique, numérique ----------
    (function () {
      var vb = q("#ci-voy-b"), voy = q("#ci-voy"), son = q("#ci-son"), sp = q("#ci-son-p"), lcd = q("#ci-lcd-in"), t = 0;
      vb.addEventListener("click", function () {
        var on = !voy.classList.contains("on"); voy.classList.toggle("on", on);
        vb.setAttribute("aria-pressed", on ? "true" : "false"); vb.textContent = on ? "Éteindre le voyant" : "Allumer le voyant";
      });
      function majLcd() {
        var s = (lcd.value || "").toUpperCase().slice(0, 16), h = [];
        q("#ci-lcd-1").textContent = s || " ";
        for (var i = 0; i < Math.min(5, s.length); i++) { var c = s.charCodeAt(i); h.push(c < 128 ? pad(c.toString(16).toUpperCase(), 2) : "??"); }
        q("#ci-lcd-2").textContent = h.join(" ") + (s.length > 5 ? " …" : "");
      }
      lcd.addEventListener("input", majLcd); majLcd();
      animers.push(function (dt) {
        t += calme ? 0 : dt;
        var a = +son.value * 28, d = [];
        for (var k = 0; k <= 100; k++) d.push((k ? "L" : "M") + k * 2 + " " + (35 - a * Math.sin(k / 100 * 6 * Math.PI - t * 8)).toFixed(1));
        sp.setAttribute("d", d.join(" "));
      });
    })();

    // ---------- 11. l'optocoupleur ----------
    (function () {
      var box = q("#ci-opto"), btn = q("#ci-op-btn"), auto = q("#ci-op-auto"), pin = q("#ci-op-in"), pout = q("#ci-op-out");
      var N = 120, hist = [], t = 0, pulse = 0, acc = 0;
      for (var i = 0; i < N; i++) hist.push(0);
      btn.addEventListener("click", function () { auto.checked = false; pulse = 0.7; });
      function path(x0, lo, hi) {
        var d = [];
        hist.forEach(function (v, k) { d.push((k ? "L" : "M") + (x0 + k * 240 / (N - 1)).toFixed(1) + " " + (v ? hi : lo)); });
        return d.join(" ");
      }
      animers.push(function (dt) {
        t += dt; pulse = Math.max(0, pulse - dt); acc += dt;
        var on = auto.checked ? (Math.floor(t / 0.8) % 2 === 0) : pulse > 0;
        box.classList.toggle("on", on);
        btn.setAttribute("aria-pressed", on ? "true" : "false");
        if (acc < 0.04) return;
        acc = 0; hist.shift(); hist.push(on ? 1 : 0);
        pin.setAttribute("d", path(20, 118, 76)); pout.setAttribute("d", path(640, 118, 52));
      });
    })();

    // ---------- 12. une trame part sur le réseau ----------
    (function () {
      var svg = q("#ci-net-svg"), bitsG = q("#ci-net-bits"), msg = q("#ci-net-msg"), rx = q("#ci-net-rx"), envoi = null;
      var P = { wifi: ["Smartphone", "Wi-Fi : liaison sans fil (ondes radio), réseau local et Internet", 1],
        bt: ["Smartphone", "Bluetooth : liaison sans fil de courte portée", 1],
        eth: ["Box Internet", "Ethernet : liaison filaire (câble réseau)", 0],
        can: ["Calculateur", "Bus CAN : liaison filaire, réseau des véhicules et des machines", 0] };
      function maj() {
        var k = q("input[name=ci-net]:checked").value, p = P[k];
        q("#ci-net-dst").textContent = p[0]; q("#ci-net-proto").textContent = p[1];
        svg.classList.toggle("sansfil", !!p[2]);
      }
      qa("input[name=ci-net]").forEach(function (r) { r.addEventListener("change", maj); });
      q("#ci-net-go").addEventListener("click", function () {
        var s = msg.value || "OK", bits = [];
        for (var i = 0; i < s.length; i++) { var c = s.charCodeAt(i); bits.push(pad((c < 128 ? c : 63).toString(2), 8)); }
        while (bitsG.firstChild) bitsG.removeChild(bitsG.firstChild);
        envoi = { s: s.replace(/[^\x00-\x7F]/g, "?"), b: bits.join(""), t: 0, els: [] };
        rx.textContent = "réception…";
      });
      animers.push(function (dt) {
        if (!envoi) return;
        envoi.t += dt;
        var rate = 26, n = envoi.b.length, sent = Math.min(n, Math.floor(envoi.t * rate)), dur = 1.4;
        while (envoi.els.length < sent) {
          var i = envoi.els.length;
          envoi.els.push({ t0: i / rate, el: tx(bitsG, 180, 110, envoi.b[i], "ci-net-bit" + (Math.floor(i / 8) % 2 ? " alt" : ""), "middle") });
        }
        var all = true;
        envoi.els.forEach(function (o) {
          var f = (envoi.t - o.t0) / dur;
          if (f >= 1) { o.el.style.display = "none"; return; }
          all = false; o.el.setAttribute("x", 190 + f * 520);
        });
        if (all && sent === n) { rx.textContent = "« " + envoi.s + " » (" + n + " bits)"; envoi = null; }
      });
      maj();
    })();

    // ---------- 13. l'octet ----------
    (function () {
      var bits = qa(".ci-bit"), inp = q("#ci-oct-in"), v = 0;
      function set(n) {
        v = ((n % 256) + 256) % 256;
        var b = pad(v.toString(2), 8), hx = pad(v.toString(16).toUpperCase(), 2), parts = [];
        bits.forEach(function (el, i) { el.textContent = b[i]; el.setAttribute("aria-pressed", b[i] === "1" ? "true" : "false"); if (b[i] === "1") parts.push(el.getAttribute("data-w")); });
        q("#ci-oct-bin").textContent = sub(b, 2); q("#ci-oct-dec").textContent = sub(v, 10); q("#ci-oct-hex").textContent = sub(hx, 16);
        q("#ci-nib-h").textContent = hx[0]; q("#ci-nib-l").textContent = hx[1];
        q("#ci-oct-calc").innerHTML = (parts.length ? parts.join(" + ") + " = " + v : "Tous les bits à 0 : 0") +
          " &nbsp;·&nbsp; " + b.slice(0, 4) + " = " + hx[0] + " et " + b.slice(4) + " = " + hx[1] + " → (" + hx + ")₁₆";
        if (+inp.value !== v) inp.value = v;
      }
      bits.forEach(function (el) { el.addEventListener("click", function () { set(v ^ +el.getAttribute("data-w")); }); });
      inp.addEventListener("input", function () { var n = parseInt(inp.value, 10); if (!isNaN(n) && n >= 0 && n <= 255) set(n); });
      qa("#ci-oct [data-v]").forEach(function (b) { b.addEventListener("click", function () { set(+b.getAttribute("data-v")); }); });
      q("#ci-oct-plus").addEventListener("click", function () { set(v + 1); });
      set(181);
    })();

    // ---------- 14. défi de conversion ----------
    (function () {
      var qEl = q("#ci-defi-q"), inp = q("#ci-defi-in"), vEl = q("#ci-defi-v"), sEl = q("#ci-defi-s"), cur = null, ok = 0, tot = 0;
      var TYPES = [
        function (n) { return { q: "Écris en décimal : " + sub(pad(n.toString(2), 8), 2), r: String(n), b: 10 }; },
        function (n) { return { q: "Écris en binaire, sur 8 bits : " + sub(n, 10), r: pad(n.toString(2), 8), b: 2 }; },
        function (n) { return { q: "Écris en hexadécimal : " + sub(pad(n.toString(2), 8), 2), r: pad(n.toString(16).toUpperCase(), 2), b: 16 }; },
        function (n) { return { q: "Écris en décimal : " + sub(pad(n.toString(16).toUpperCase(), 2), 16), r: String(n), b: 10 }; }
      ];
      function nouveau() {
        var n = 1 + Math.floor(Math.random() * 255);
        cur = TYPES[Math.floor(Math.random() * TYPES.length)](n); cur.n = n;
        qEl.textContent = cur.q; inp.value = ""; vEl.textContent = ""; vEl.className = "simu-verdict";
      }
      function norm(s, b) {
        s = s.replace(/[\s()₀-₉_]/g, "").toUpperCase();
        if (b === 2) { s = s.replace(/^0+(?=.)/, ""); return pad(s, 8); }
        if (b === 16) return pad(s.replace(/^0+(?=.)/, ""), 2);
        return s.replace(/^0+(?=.)/, "");
      }
      q("#ci-defi-ok").addEventListener("click", function () {
        if (!inp.value.trim()) { vEl.textContent = "Écris ta réponse d'abord."; return; }
        tot++;
        var juste = norm(inp.value, cur.b) === cur.r;
        if (juste) ok++;
        vEl.textContent = juste ? "✔ Juste !" : "✘ La réponse était " + cur.r + " (" + sub(cur.n, 10) + " = " + sub(pad(cur.n.toString(2), 8), 2) + " = " + sub(pad(cur.n.toString(16).toUpperCase(), 2), 16) + ").";
        vEl.className = "simu-verdict " + (juste ? "ok" : "ko");
        sEl.textContent = "Score : " + ok + " / " + tot;
      });
      inp.addEventListener("keydown", function (e) { if (e.key === "Enter") q("#ci-defi-ok").click(); });
      q("#ci-defi-new").addEventListener("click", nouveau);
      nouveau();
    })();

    // ---------- 15. l'ASCII ----------
    (function () {
      var inp = q("#ci-asc-in"), out = q("#ci-asc-out"), rows = qa("#ci-asc-grid tr[data-c]");
      function maj() {
        var s = inp.value, h = [], codes = {};
        for (var i = 0; i < s.length; i++) {
          var c = s.charCodeAt(i), ok = c < 128;
          if (ok) codes[c] = 1;
          var ch = s[i] === " " ? "espace" : s[i].replace(/&/g, "&amp;").replace(/</g, "&lt;");
          h.push('<div class="ci-ac' + (ok ? "" : " ko") + '"><b>' + ch + "</b><span>" + (ok ? c + " · " + pad(c.toString(16).toUpperCase(), 2) : "hors ASCII") + "</span><code>" + (ok ? pad(c.toString(2), 8) : "—") + "</code></div>");
        }
        out.innerHTML = h.join("") || '<p class="small">Écris un mot.</p>';
        rows.forEach(function (r) { r.classList.toggle("hl", !!codes[+r.getAttribute("data-c")]); });
      }
      inp.addEventListener("input", maj); maj();
    })();

    // à l'impression, la table ASCII repliée est dépliée le temps d'imprimer
    var ascD = q(".ci-asc-d"), ascOuvert = false;
    window.addEventListener("beforeprint", function () { ascOuvert = ascD.open; ascD.open = true; });
    window.addEventListener("afterprint", function () { ascD.open = ascOuvert; });

    qa(".jeu", home).forEach(initJeu);
    initQuiz(home);
    q(".cours-print").addEventListener("click", function () { window.print(); });
    var last = null;
    function loop(ts) {
      var dt = last === null ? 0 : Math.max(0, Math.min(0.1, (ts - last) / 1000)); last = ts;
      animers.forEach(function (f) { f(dt); });
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }
"""


def ci_js():
    data = {k: {"n": " ".join(v[4]).replace("Réservoir à", "Réservoir à"), "c": v[5], "f": v[6], "r": v[7]}
            for k, v in IBD_BLOCS.items()}
    import json
    return CI_JS.replace("__IBD__", json.dumps(data, ensure_ascii=False))


CI_CSS = """
/* ---------- cours 3 : chaîne d'information (préfixe ci-) ---------- */
body.page-cours-chaine-information .home-inner{max-width:1180px}
.ci-svg{display:block; width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin); font-family:var(--f-texte); margin:6px 0}
.ci-svg text{font-family:var(--f-texte)}
.ci-bt{font-size:14.5px; font-weight:700; fill:var(--encre)} .ci-bs{font-size:12.5px; fill:var(--encre-2)}
.ci-ctrl{display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; margin:6px 0}
.ci-sw{display:inline-flex; gap:6px; align-items:center; font-size:.92rem; cursor:pointer}
.ci-sw input[type=text],.ci-sw input[type=number],#ci-defi-in{padding:5px 8px; border:1.5px solid var(--encre-2); font:inherit; min-width:0}
.ci-step{background:var(--jaune-pale); border-left:5px solid var(--jaune); padding:8px 12px; margin:6px 0 0; min-height:3.2em}
.ci-form{font-size:1.1rem; background:#fff; border:1.5px solid var(--encre); display:inline-block; padding:6px 16px; margin:4px 0 10px}
.ci-tag{display:inline-block; font:700 .72rem var(--f-titre); color:#fff; padding:1px 7px; margin-left:6px; vertical-align:middle; letter-spacing:.04em; background:var(--bleu)}
/* boîtes et flux */
.ci-frame{fill:#FFFBEA; stroke:#E7C96A; stroke-width:1.5} .ci-frame-t{font-size:14px; font-weight:700; fill:var(--encre)}
.ci-box rect{stroke-width:2; transition:fill .3s, stroke-width .3s}
.ci-box.ci-u rect,.ci-box.ci-ext rect{fill:#FBEFF4; stroke:#B0306A}
.ci-box.ci-i rect{fill:var(--bleu-pale); stroke:var(--bleu)}
.ci-box.ci-e rect{fill:var(--orange-pale); stroke:var(--orange)}
.ci-box.ci-a rect{fill:var(--vert-pale); stroke:var(--vert)}
.ci-box.ci-mo rect,.ci-box.ci-m rect{fill:#F4F5F2; stroke:var(--trait)}
.ci-box.on rect{fill:var(--jaune-pale); stroke-width:3.5}
.ci-box[data-k]{cursor:pointer} .ci-box[data-k]:hover rect,.ci-box[data-k]:focus rect{fill:var(--jaune-pale)} .ci-box:focus{outline:none}
.ci-box.sel rect{fill:var(--jaune-pale); stroke:var(--encre); stroke-width:3}
.ci-fl-p{fill:none; stroke-width:2}
.ci-fl.k-i .ci-fl-p{stroke:#7FA3CF} .ci-fl.k-e .ci-fl-p{stroke:#D3A35E} .ci-fl.k-m .ci-fl-p{stroke:#B0306A}
.ci-mk-i{fill:var(--bleu)} .ci-mk-e{fill:var(--orange)} .ci-mk-m{fill:#B0306A}
.ci-fl-a{fill:none; stroke-width:5; stroke-linecap:round; stroke-dasharray:3 14; opacity:0}
.ci-fl.k-i .ci-fl-a{stroke:var(--bleu)} .ci-fl.k-e .ci-fl-a{stroke:#E98A00} .ci-fl.k-m .ci-fl-a{stroke:#B0306A}
.ci-fl.on .ci-fl-p{stroke-width:3.5} .ci-fl.k-i.on .ci-fl-p{stroke:var(--bleu)} .ci-fl.k-e.on .ci-fl-p{stroke:var(--orange)}
.ci-fl.on .ci-fl-a{opacity:1; animation:ci-couler .9s linear infinite}
@keyframes ci-couler{to{stroke-dashoffset:-34}}
.ci-fl-l{font-size:12.5px; font-weight:600; paint-order:stroke; stroke:#fff; stroke-width:4px; stroke-linejoin:round}
.ci-fl-l.k-i{fill:var(--bleu)} .ci-fl-l.k-e{fill:var(--orange)} .ci-fl-l.k-m{fill:#B0306A}
#ci-cafe-svg .ci-simple{display:none} #ci-cafe-svg.simple .ci-simple{display:inline} #ci-cafe-svg.simple .ci-detail{display:none}
.ci-cup-b{fill:#fff; stroke:var(--encre); stroke-width:2} .ci-cup-h{fill:none; stroke:var(--encre); stroke-width:2}
.ci-cup-l{fill:#6B3E1F} .ci-steam{fill:none; stroke:#A5ADAA; stroke-width:2; opacity:0}
.ci-cup.done .ci-steam{opacity:1; animation:ci-vapeur 1.6s ease-in-out infinite}
@keyframes ci-vapeur{50%{transform:translateY(-4px); opacity:.4}}
#ci-ibd-svg.focus .ci-fl:not(.on){opacity:.3}
.ci-ibd-tab{fill:#fff; stroke:var(--encre); stroke-width:1.5} .ci-ibd-tt{font-size:12.5px; font-weight:700; fill:var(--encre)}
.ci-ibd-info{border:1.5px solid var(--encre); background:#fff; padding:8px 12px; min-height:4.4em}
.ci-ibd-info h4{margin:0 0 2px; font:700 1.05rem var(--f-titre)} .ci-ibd-info p{margin:2px 0}
/* capteur, laboratoire, oscillogrammes */
.ci-capt{max-width:720px}
.ci-c-g{fill:#F28A2E} .ci-c-c{fill:#F2B705} .ci-c-s{fill:#F7CF4D} .ci-c-e{fill:#EA7A5C}
.ci-c-ar{stroke:#B42318; stroke-width:6; fill:none}
.ci-c-anim{stroke-dasharray:10 8; animation:ci-couler 1.2s linear infinite}
.ci-trois{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:12px 0}
.ci-trois>div{background:#fff; border:1.5px solid var(--encre); padding:2px 12px 6px}
.ci-trois h3{font-size:1.02rem!important}
@media (max-width:900px){ .ci-trois{grid-template-columns:1fr} }
.ci-sc-bg{fill:#FBFCFB; stroke:#D3D8D5} .ci-sc-g{stroke:#E3E6E2; stroke-width:1} .ci-sc-ax{stroke:var(--encre-2); stroke-width:1.5}
.ci-sc-t{font-size:12px; fill:var(--encre-2)}
.ci-lab-l{font-size:14px; font-weight:700; fill:var(--encre)} .ci-lab-u{font-size:12px; fill:var(--encre-2)}
.ci-lab-c{fill:none; stroke-width:2.5; stroke-linejoin:round}
.ci-lab-c.c0{stroke:var(--encre)} .ci-lab-c.c1{stroke:#B42318} .ci-lab-c.c2{stroke:var(--orange)} .ci-lab-c.c3{stroke:var(--bleu)}
.ci-lab-seuil{stroke:#B42318; stroke-width:1.5; stroke-dasharray:6 4} .ci-lab-st{font-size:12px; font-weight:700; fill:#B42318}
.ci-lab-bit{font:700 14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; fill:var(--bleu)}
/* chaîne d'acquisition */
.ci-aq rect:first-child{stroke-width:2} .ci-aq-i rect:first-child{fill:var(--bleu-pale); stroke:var(--bleu)}
.ci-aq-c rect:first-child{fill:#fff; stroke:var(--encre-2)} .ci-aq-n rect:first-child{fill:#fff; stroke:var(--rouge)}
.ci-aq-sc .ci-sc-c{fill:none; stroke:var(--bleu); stroke-width:1.8; stroke-linejoin:round}
.ci-aq-sc.dots .ci-sc-c{stroke-width:5; stroke-linecap:round; stroke:var(--encre)}
.ci-aq-ar{stroke:var(--encre); stroke-width:2; fill:none}
.ci-aq-g{fill:none; stroke:var(--rouge); stroke-width:1.5} .ci-aq-gt{font:700 13px var(--f-titre); fill:var(--encre)}
.ci-aq-zone{fill:none; stroke:var(--encre-2); stroke-dasharray:5 4} .ci-aq-zt{font:700 12px var(--f-titre); fill:var(--orange)}
.ci-g3{grid-template-columns:repeat(3,minmax(0,1fr))}
@media (max-width:760px){ .ci-g3{grid-template-columns:1fr} }
/* filtre et spectre */
.ci-four-c{fill:none; stroke:#7FA3CF; stroke-width:1; opacity:.8} .ci-four-c.off{stroke:#C9CFD3; stroke-dasharray:3 3; opacity:.6}
.ci-four-sum{fill:none; stroke:var(--encre); stroke-width:2.6; stroke-linejoin:round}
.ci-four-bar{fill:#1F5FA8; transition:fill .2s} .ci-four-bar.bruit{fill:#7A848C} .ci-four-bar.off{fill:#E3E6E2}
.ci-four-bl{font-size:12px; fill:var(--encre-2)} .ci-four-gab{fill:none; stroke:#B42318; stroke-width:2.5}
.ci-four-gt{font-size:12.5px; font-weight:700; fill:#B42318}
/* CAN */
.ci-can-st{fill:none; stroke:#B42318; stroke-width:2.5} .ci-can-hl{stroke:var(--jaune); stroke-width:8; stroke-linecap:round}
.ci-can-v{stroke:var(--bleu); stroke-width:1.5; stroke-dasharray:5 4} .ci-can-pt{fill:var(--bleu); stroke:#fff; stroke-width:2}
/* système programmable */
.ci-sys-z{fill:var(--bleu-pale); stroke:var(--bleu); stroke-dasharray:6 4} .ci-sys-zt{font:700 13px var(--f-titre); fill:var(--bleu)}
.ci-sys-b rect{fill:#fff; stroke:var(--encre); stroke-width:1.6}
.ci-sys-b.ci-cpu rect{fill:#EAF1FA; stroke-width:2.5} .ci-sys-b.ci-prog rect{fill:#FFF3E0; stroke:#F2A33A; stroke-width:2.5}
.ci-clk.tic rect{fill:var(--jaune-pale); stroke:var(--orange)}
.ci-sys-ar{stroke:var(--encre); stroke-width:2; fill:none} .ci-sys-pr{stroke:#F2A33A; stroke-width:3; fill:none}
.ci-pk{fill:#B42318}
/* programme */
.ci-prog{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.1fr); gap:16px; align-items:start; margin:8px 0}
@media (max-width:900px){ .ci-prog{grid-template-columns:1fr} }
.ci-algo{max-width:470px}
.ci-an path,.ci-an rect{fill:#fff; stroke:var(--encre); stroke-width:1.8; transition:fill .2s}
.ci-an text{font-size:13.5px; font-weight:600; fill:var(--encre)}
.ci-an.on path,.ci-an.on rect{fill:var(--jaune-pale); stroke:var(--orange); stroke-width:3}
.ci-aa{fill:none; stroke:var(--encre); stroke-width:1.6; marker-end:url(#ci-m-a)} .ci-aa.nj{marker-end:none}
.ci-al{font-size:12.5px; font-style:italic; fill:var(--encre-2)}
.ci-tok{fill:#B42318; transition:transform .35s ease}
.ci-carte{display:flex; align-items:center; gap:16px; background:#1E6B52; padding:12px 16px; border-radius:6px; color:#fff; flex-wrap:wrap}
.ci-bp{width:96px; height:72px; border-radius:50%; border:4px solid #0F3A2C; background:#E0E3E0; font:700 .9rem var(--f-titre); color:var(--encre); cursor:pointer; box-shadow:0 5px 0 #0F3A2C; touch-action:none; user-select:none}
.ci-bp.down{transform:translateY(4px); box-shadow:0 1px 0 #0F3A2C; background:#C9CFD3}
.ci-bp small{font-weight:400}
.ci-led{width:34px; height:34px; border-radius:50%; background:#5A2020; border:3px solid #0F3A2C; transition:background .15s, box-shadow .15s}
.ci-led.on{background:#FF4136; box-shadow:0 0 18px 6px rgba(255,65,54,.7)}
.ci-led-l{font-weight:600}
.ci-tabs{display:flex; flex-wrap:wrap; gap:4px; margin:8px 0 0}
.ci-tabs button{font:600 .88rem var(--f-titre); border:1.5px solid var(--encre); background:#fff; padding:5px 10px; cursor:pointer}
.ci-tabs button[aria-selected="true"]{background:var(--encre); color:var(--jaune)}
.ci-code{border:1.5px solid var(--encre); background:#1C2530; color:#E3E6E2; padding:8px 0}
.ci-code pre{margin:0; font:13.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; overflow-x:auto}
.ci-cl{display:block; padding:0 12px; white-space:pre}
.ci-cl.on{background:#4A3B00; color:#FFE27A; box-shadow:inset 4px 0 0 var(--jaune)}
#ci-code-blocs{background:#fff; color:var(--encre); padding:10px}
.ci-blk{border-radius:6px; padding:6px 10px; margin:4px 0; font:600 .9rem var(--f-texte); color:#fff}
.ci-blk-loop{background:#F2A33A} .ci-blk-if{background:#E8892B; margin-left:10px} .ci-blk-act{background:#1F5FA8; margin-left:14px}
.ci-blk>span{display:block}
.ci-blk.on{outline:4px solid var(--jaune); outline-offset:1px}
.ci-symt{max-width:640px} .ci-symt td:first-child{width:160px}
.ci-sym{width:140px; height:46px} .ci-sym path,.ci-sym rect{fill:var(--bleu-pale); stroke:var(--encre); stroke-width:1.5}
.ci-sym text{font-size:11px; fill:var(--encre)}
/* restitution, optocoupleur, réseau */
.ci-rest{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:10px 0}
@media (max-width:900px){ .ci-rest{grid-template-columns:1fr} }
.ci-r{background:#fff; border:1.5px solid var(--encre); padding:8px 12px; display:flex; flex-direction:column; gap:8px; align-items:flex-start}
.ci-r h4{margin:0; font:700 1rem var(--f-titre)} .ci-r p{margin:0; font-size:.9rem}
.ci-voyant{width:40px; height:40px; border-radius:50%; background:#3B4A3F; border:3px solid #1C2530; transition:all .15s}
.ci-voyant.on{background:#3FD16E; box-shadow:0 0 16px 5px rgba(63,209,110,.7)}
.ci-son{width:200px; height:70px; background:#FBFCFB; border:1px solid var(--trait-fin)} .ci-son path{fill:none; stroke:var(--orange); stroke-width:2.5}
.ci-lcd{background:#9EBF3B; border:6px solid #1C2530; padding:6px 10px; font:700 1.05rem/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; color:#22300A; width:100%; max-width:240px; letter-spacing:.06em}
.ci-lcd span{display:block; white-space:pre; overflow:hidden}
.ci-op-sig{fill:none; stroke:var(--bleu); stroke-width:2.5} .ci-op-sig.o{stroke:var(--orange)}
.ci-op-box{fill:#F4F5F2; stroke:var(--encre); stroke-width:2} .ci-op-iso{stroke:var(--encre-2); stroke-width:2; stroke-dasharray:6 4}
.ci-op-w{fill:none; stroke:var(--encre); stroke-width:2} .ci-op-d{fill:#fff; stroke:var(--encre); stroke-width:2}
.ci-op-ray{stroke:#E8B400; stroke-width:3; opacity:0; stroke-dasharray:6 6}
.ci-op-rin{stroke:#E8B400; stroke-width:2; opacity:.25}
#ci-opto.on .ci-op-d{fill:#FFD84D} #ci-opto.on .ci-op-ray{opacity:1; animation:ci-couler .5s linear infinite} #ci-opto.on .ci-op-rin{opacity:1}
#ci-opto.on .ci-op-th{stroke:var(--orange); stroke-width:4}
.ci-net-b rect{fill:#fff; stroke:var(--encre); stroke-width:2}
.ci-net-w{stroke:var(--encre-2); stroke-width:6; fill:none} .ci-net-wv{fill:none; stroke:var(--bleu); stroke-width:2.5}
#ci-net-svg #ci-net-wave{display:none} #ci-net-svg.sansfil #ci-net-wave{display:inline} #ci-net-svg.sansfil #ci-net-wire{display:none}
.ci-net-bit{font:700 15px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; fill:var(--bleu)} .ci-net-bit.alt{fill:var(--orange)}
/* octet, défi, ASCII */
.ci-oct-row{display:flex; flex-wrap:wrap; gap:8px 18px; align-items:flex-end}
.ci-oct-w,.ci-oct-b{display:grid; grid-template-columns:repeat(8,42px); gap:4px}
.ci-oct-w{grid-column:1} .ci-oct-w span{font:600 .8rem var(--f-titre); text-align:center; color:var(--encre-2)}
.ci-oct-row{display:grid; grid-template-columns:max-content max-content; grid-template-rows:auto auto}
.ci-oct-b{grid-row:2} .ci-oct-n{grid-row:2; display:flex; gap:4px}
.ci-bit{height:48px; font:700 1.4rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; border:2px solid var(--encre); background:#fff; cursor:pointer}
.ci-bit:nth-child(-n+4){border-bottom:5px solid var(--bleu)} .ci-bit:nth-child(n+5){border-bottom:5px solid var(--orange)}
.ci-bit[aria-pressed="true"]{background:var(--encre); color:var(--jaune)}
.ci-nib{display:inline-flex; align-items:center; justify-content:center; width:46px; height:48px; font:700 1.5rem var(--f-titre); color:#fff}
.ci-nib:first-child{background:var(--bleu)} .ci-nib:last-child{background:var(--orange)}
@media (max-width:520px){ .ci-oct-w,.ci-oct-b{grid-template-columns:repeat(8,32px)} .ci-oct-row{grid-template-columns:max-content} .ci-oct-n{grid-row:3} }
.ci-oct-calc{font-weight:600}
.ci-defi-q{font:700 1.15rem var(--f-titre)} #ci-defi-in{width:12em; font-size:1.05rem} .ci-defi-s{font-weight:700}
.ci-asc-out{display:flex; flex-wrap:wrap; gap:6px; margin:8px 0}
.ci-ac{display:flex; flex-direction:column; align-items:center; border:1.5px solid var(--encre); background:#fff; padding:4px 8px; min-width:86px}
.ci-ac b{font:700 1.4rem var(--f-titre)} .ci-ac span{font-size:.8rem; color:var(--encre-2)}
.ci-ac code{font:700 .95rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; color:var(--bleu)}
.ci-ac.ko{border-color:var(--rouge); background:var(--rouge-pale)}
.ci-asc-d summary{cursor:pointer; font-weight:600; margin:8px 0}
.ci-asc-grid{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px}
@media (max-width:900px){ .ci-asc-grid{grid-template-columns:repeat(2,minmax(0,1fr))} }
@media (max-width:520px){ .ci-asc-grid{grid-template-columns:1fr} }
.ci-asc{font-size:.78rem; margin:0} .ci-asc td,.ci-asc th{padding:1px 5px}
.ci-asc tr.hl td{background:var(--jaune); font-weight:700}
@media (prefers-reduced-motion:reduce){ .ci-fl.on .ci-fl-a,.ci-c-anim,#ci-opto.on .ci-op-ray{animation-duration:4s} }
@media print{ .ci-svg{break-inside:avoid} }
"""
