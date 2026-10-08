#!/usr/bin/env bash
# Prépare les images intégrées dans la page (ImageMagick 6 requis).
#   - src/images/originaux/ex1-*.png  : figures de l'exercice 1.1 (dépôt « schema_chaine-energie-information »)
#   - src/images/originaux/ce-*.png   : figures et tableaux du cours « Chaîne d'énergie des produits » (Word)
#   - src/images/*.png                : versions quantifiées (PNG 8 bits) intégrées en data URI
#   - src/images/ce-ph-*.png          : photos des composants, découpées dans les tableaux du cours
#   - src/images/ce-sy-*.png          : symboles des composants, découpés dans les mêmes tableaux
#   - src/images/ex1-rav4.jpg         : photo du RAV4 (plaque floutée dans l'original), réduite pour la page
#   - src/images/accueil.png          : montage d'illustration de la page d'accueil
#   - src/images/carte-*.png|jpg      : images des cartes de l'accueil, tirées des exercices (480 × 270)
#   outils/captures.js photographie dans les pages la motorisation du RAV4 (montage) et la carte mentale du
#   formulaire, et rend le dessin carte-capteur.svg : NODE_PATH=$(npm root -g) node outils/captures.js
# Usage : bash outils/preparer-images.sh   (depuis la racine du dépôt)
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=src/images/originaux
OUT=src/images

# 1. Figures reprises telles quelles
for f in "$SRC"/ex1-*.png "$SRC"/ce-fig-*.png; do
  b=$(basename "$f")
  [ "$b" = ex1-rav4-schema.png ] && continue  # sert seulement au montage d'accueil
  convert "$f" -background white -alpha remove -alpha off -strip -colors 256 "PNG8:$OUT/$b"
done

# QCM « énergie et chaîne d'énergie » : images extraites de la page fournie (src/qcm-energie-source.html)
for f in "$SRC"/qcm-*.png; do
  convert "$f" -background white -alpha remove -alpha off -strip -colors 256 "PNG8:$OUT/$(basename "$f")"
done
for f in "$SRC"/qcm-*.jpg; do
  convert "$f" -resize '640x640>' -quality 78 -strip "$OUT/$(basename "$f")"
done

# Photo du RAV4
convert "$SRC/ex1-rav4.jpg" -resize 900x -quality 78 -strip "$OUT/ex1-rav4.jpg"

# 2. Exercice 1.1, ascenseur : le schéma d'origine reprenait les légendes du portail
#    (« Vantail en position initiale / finale ») ; elles sont remplacées par la matière d'œuvre de l'ascenseur.
convert "$SRC/ex1-ascenseur-chaines.png" \
  -fill '#EAF1DD' -stroke none -draw 'rectangle 700,256 838,296' -draw 'rectangle 700,418 838,458' \
  -font DejaVu-Sans-Bold -pointsize 11 -fill '#6E9150' -gravity NorthWest \
  -annotate +722+260 "Usager à l'étage" -annotate +738+276 'de départ' \
  -annotate +722+422 "Usager à l'étage" -annotate +740+438 "d'arrivée" \
  -strip -colors 256 "PNG8:$OUT/ex1-ascenseur-chaines.png"

# 3. Cours « Chaîne d'énergie » : photos et symboles découpés dans les tableaux du Word.
#    decoupe <tableau> <géométrie> <nom> <fond> : fond = 1 → le fond de la cellule (beige ou orange)
#    est remplacé par du blanc, par remplissage depuis les coins ; fond = 2 → la photo a son propre fond,
#    seule la bordure de cellule restée autour est rognée.
decoupe() {
  local tab=$1 geo=$2 nom=$3 fond=$4 tmp
  shift 4                                  # points supplémentaires « x,y » : zones de fond enclavées
  tmp=$(mktemp --suffix=.png)
  convert "$SRC/$tab" -crop "$geo" +repage "$tmp"
  if [ "$fond" = 1 ]; then
    local c pt
    c=$(convert "$tmp" -format '%[pixel:p{1,1}]' info:)
    convert "$tmp" -bordercolor "$c" -border 1 -fuzz 7% -fill white \
      -draw 'color 0,0 floodfill' -shave 1x1 "$tmp"
    for pt in "$@"; do
      convert "$tmp" -fuzz 7% -fill white -draw "color ${pt/,/ } floodfill" "$tmp"
    done
  elif [ "$fond" = 2 ]; then
    convert "$tmp" -bordercolor "$(convert "$tmp" -format '%[pixel:p{0,0}]' info:)" -border 1 \
      -fuzz 12% -trim +repage "$tmp"
  fi
  convert "$tmp" -strip -colors 256 "PNG8:$OUT/$nom.png"
  rm -f "$tmp"
}
# Alimenter / stocker
decoupe ce-tab-alimenter.png     158x168+180+66   ce-ph-monophase      0
decoupe ce-tab-alimenter.png     150x128+182+250  ce-ph-triphase       0
decoupe ce-tab-alimenter.png     158x125+180+402  ce-ph-batterie       1
decoupe ce-tab-renouvelables.png 158x138+180+28   ce-ph-renouvelables  2
decoupe ce-tab-chargeur.png      158x143+180+30   ce-ph-chargeur       1
decoupe ce-tab-onduleur.png      158x178+180+30   ce-ph-onduleur       1
decoupe ce-tab-alimenter.png     120x70+700+105   ce-sy-monophase      1
decoupe ce-tab-alimenter.png     125x100+697+250  ce-sy-triphase       1
decoupe ce-tab-alimenter.png     110x125+700+405  ce-sy-batterie       1
decoupe ce-tab-renouvelables.png 280x138+720+28   ce-sy-renouvelables  1 199,96
decoupe ce-tab-chargeur.png      360x143+678+30   ce-sy-chargeur       1
decoupe ce-tab-onduleur.png      360x178+678+30   ce-sy-onduleur       1
# Distribuer
decoupe ce-tab-distribuer.png    270x212+160+70   ce-ph-disjoncteur    1
decoupe ce-tab-distribuer.png    270x213+160+292  ce-ph-fusibles       1
decoupe ce-tab-distribuer.png    272x210+158+515  ce-ph-interrupteur   1
decoupe ce-tab-distribuer.png    272x235+158+740  ce-ph-relais         1
decoupe ce-tab-distribuer.png    272x305+158+985  ce-ph-modulateur     1
decoupe ce-tab-distribuer.png    212x210+803+72   ce-sy-disjoncteur    1
decoupe ce-tab-distribuer.png    212x85+803+333   ce-sy-fusible        1
decoupe ce-tab-distribuer.png    212x85+803+568   ce-sy-interrupteur   1
decoupe ce-tab-distribuer.png    215x235+800+740  ce-sy-relais         1
decoupe ce-tab-distribuer.png    215x300+800+990  ce-sy-modulateur     1
# Convertir
decoupe ce-tab-convertir.png     160x160+182+95   ce-ph-moteur-cc         1
decoupe ce-tab-convertir.png     160x150+182+340  ce-ph-moteur-asynchrone 1
decoupe ce-tab-convertir.png     160x175+182+588  ce-ph-moteur-brushless  1
decoupe ce-tab-convertir.png     160x160+182+843  ce-ph-resistance        1
decoupe ce-tab-convertir.png     160x142+182+1090 ce-ph-eclairage         1
decoupe ce-tab-convertir.png     100x100+715+125  ce-sy-moteur-cc         1
decoupe ce-tab-convertir.png     100x100+715+368  ce-sy-moteur-asynchrone 1
decoupe ce-tab-convertir.png     100x110+715+610  ce-sy-moteur-brushless  1
decoupe ce-tab-convertir.png     80x150+725+840   ce-sy-resistance        1
decoupe ce-tab-convertir.png     120x90+705+1110  ce-sy-eclairage         1
# Transmettre
decoupe ce-tab-transmettre.png   258x130+170+68   ce-ph-accouplement   1
decoupe ce-tab-transmettre.png   258x157+170+238  ce-ph-engrenage      1
decoupe ce-tab-transmettre.png   258x180+170+405  ce-ph-train          1
decoupe ce-tab-transmettre.png   258x200+170+595  ce-ph-poulies        1
decoupe ce-tab-transmettre.png   258x170+170+805  ce-ph-cremaillere    1
decoupe ce-tab-transmettre.png   258x165+170+985  ce-ph-vis-ecrou      1
decoupe ce-tab-transmettre.png   258x170+170+1165 ce-ph-roue-vis       1
decoupe ce-tab-transmettre.png   239x130+776+68   ce-sy-accouplement   1
decoupe ce-tab-transmettre.png   243x157+772+238  ce-sy-engrenage      1
decoupe ce-tab-transmettre.png   243x180+772+405  ce-sy-train          1
decoupe ce-tab-transmettre.png   243x195+772+600  ce-sy-poulies        1
decoupe ce-tab-transmettre.png   243x125+772+838  ce-sy-cremaillere    1
decoupe ce-tab-transmettre.png   243x165+772+985  ce-sy-vis-ecrou      1
decoupe ce-tab-transmettre.png   243x170+772+1165 ce-sy-roue-vis       1
decoupe ce-tab-transmettre-2.png 263x140+192+30   ce-ph-echangeur      1
decoupe ce-tab-transmettre-2.png 263x86+192+176   ce-ph-reflecteur     1
decoupe ce-tab-transmettre-2.png 140x100+840+48   ce-sy-echangeur      1
# Agir
decoupe ce-tab-agir.png          143x95+250+60    ce-ph-roues          0
decoupe ce-tab-agir.png          144x95+563+60    ce-ph-scene          0
decoupe ce-tab-agir.png          145x95+875+60    ce-ph-four           0

# 4. Montage d'accueil : les quatre systèmes de l'exercice 1.1
convert -size 1120x620 xc:white \
  \( "$SRC/ex1-ascenseur.png" -resize x540 \) -gravity northwest -geometry +24+64 -composite \
  \( "$SRC/ex1-portail.png" -crop 699x372+0+0 +repage -resize 500x \) -gravity northwest -geometry +318+64 -composite \
  \( "$SRC/ex1-geothermie.png" -resize x222 \) -gravity northwest -geometry +384+388 -composite \
  \( "$SRC/ex1-rav4.jpg" -resize 262x \) -gravity northwest -geometry +842+64 -composite \
  \( "$SRC/ex1-rav4-schema.png" -resize 262x \) -gravity northwest -geometry +842+248 -composite \
  -fill '#1C2530' -stroke none -draw 'rectangle 298,20 300,600' -draw 'rectangle 826,20 828,600' \
  -fill '#F2B705' -draw 'rectangle 24,14 156,46' -draw 'rectangle 318,14 552,46' -draw 'rectangle 384,342 672,374' \
  -draw 'rectangle 842,14 1030,46' \
  -font DejaVu-Sans-Bold -pointsize 19 -fill '#1C2530' -gravity northwest \
  -annotate +32+19 'Ascenseur' -annotate +326+19 'Portail automatique' -annotate +392+347 'Chauffage géothermique' \
  -annotate +850+19 'Voiture hybride' \
  -strip -colors 256 "PNG8:$OUT/accueil.png"

# 5. Images des cartes de l'accueil, tirées des exercices : toutes au même format 480 × 270.
#    remplir : l'image couvre la carte (recadrée) ; entiere : l'image entière sur fond blanc (figures très allongées).
remplir() { convert "$1" -background white -alpha remove -alpha off -resize 480x270^ -gravity "${4:-center}" \
  -extent 480x270 -strip $3 "$OUT/$2"; }
entiere() { convert "$1" -background "${3:-white}" -alpha remove -alpha off -resize 456x250 -gravity center \
  -extent 480x270 -strip -colors 256 "PNG8:$OUT/$2"; }
tmp=$(mktemp --suffix=.png)
convert "$SRC/ex1-portail.png" -crop 699x372+0+0 +repage "$tmp"  # sans la légende
remplir "$tmp"                    carte-cours-1.png  "-colors 256"
rm -f "$tmp"
tmp=$(mktemp --suffix=.png)
convert "$SRC/qcm-moteur.png" -crop 256x176+166+46 +repage "$tmp"        # le moteur seul, sans texte ni flèches
entiere "$tmp"                    carte-cours-2.png
rm -f "$tmp"
remplir "$SRC/carte-capteur.png"  carte-cours-3.jpg  "-quality 82"           # dessin carte-capteur.svg (outils/captures.js)
tmp=$(mktemp --suffix=.png)
convert "$SRC/carte-formulaire.png" -gravity center -crop 1376x780+0+0 +repage "$tmp"  # la carte mentale dépliée, vue de loin
remplir "$tmp"                    carte-formulaire.png "-colors 256"
rm -f "$tmp"
remplir "$SRC/ex1-rav4.jpg"       carte-ex11.jpg     "-quality 80"
remplir "$SRC/qcm-pv-mono.png"    carte-qcm.jpg      "-quality 80"
remplir "$SRC/carte-calculatrice.jpg" carte-calculs.jpg "-quality 80"   # photo fournie : calculatrice et brouillon
remplir "$SRC/ex1-ascenseur.png"  carte-etude.png    "-colors 256" north

ls -l "$OUT"/*.png | awk '{s += $5} END {print NR " images, " int(s / 1024) " Kio"}'
