"""QCM « Énergie et chaîne d'énergie », mis aux normes du gabarit.

Source : la page fournie (src/qcm-energie-source.html, fichier d'origine non modifié) ; ses questions sont lues dans
son tableau QDATA, puis corrigées ici (CORRECTIONS, toutes listées) et rangées en six parties pondérées par leur
durée. Chaque question est une question du gabarit à une seule case (mécanisme « fast-q ») : la case, masquée,
reçoit le repère de la ou des propositions choisies ; le moteur Grading la corrige (« code » pour une réponse
unique, « intset » pour plusieurs réponses). Modes entraînement et examen, note, récapitulatif et impression sont
ceux du gabarit. Les images sont extraites dans src/images/originaux/qcm-*.
"""
import html
import json
import pathlib
import re

SOURCE = pathlib.Path(__file__).resolve().parent / "qcm-energie-source.html"

IMAGES = {  # image de la source → (fichier, texte alternatif, largeur maximale)
    "image1": ("qcm-moteur", "Moteur électrique : puissance absorbée 2000 W, puissance utile 1600 W", 420),
    "image2": ("qcm-treuil", "Treuil : moteur, réducteur, tambour et charge", 300),
    "image3": ("qcm-eolienne", "Chaîne de rendements d'une éolienne : puissance cinétique 832,9 kW, rendement éolienne "
                               "(au plus 60 %), rendement mécanique 87 %, rendement génératrice, puissance électrique 400 kW", 760),
    "image4": ("qcm-oscillo-1", "Oscillogramme d'une tension sinusoïdale, premier signal", 420),
    "image5": ("qcm-oscillo-2", "Oscillogramme d'une tension sinusoïdale, second signal", 420),
    "image6": ("qcm-mcc", "Moteur à courant continu alimenté sous une tension U", 320),
    "image7": ("qcm-pont-h", "Pont en H : alimentation E = 24 V, interrupteurs T1 à T4 et moteur M", 300),
    "image8": ("qcm-enceinte", "Température de l'enceinte en fonction du temps : de 27,5 °C à 47 °C", 620),
    "image11": ("qcm-pv-mono", "Panneau photovoltaïque à cellules noires uniformes aux coins coupés", 260),
    "image12": ("qcm-pv-poly", "Panneau photovoltaïque à cellules bleues d'aspect pailleté", 200),
    "image13": ("qcm-pv-amorphe", "Panneau photovoltaïque brun, sans cellules distinctes", 280),
    "image14": ("qcm-pv-courbes", "Caractéristiques I(U) et P(U) d'un panneau photovoltaïque pour plusieurs irradiances", 560),
    "image15": ("qcm-cascade", "Chute d'eau", 460),
}

# parties : (titre, durée en minutes, identifiant de la première question)
PARTIES = [("Conversions et sources d'énergie", 8, "Q1"), ("Unités, puissance et rendement", 15, "Q10"),
           ("Signaux et moteur à courant continu", 12, "Q20"), ("Énergie thermique", 12, "Q26"),
           ("Photovoltaïque et batteries", 20, "Q33"), ("Fonctions de la chaîne d'énergie et stockage", 13, "Q47")]


def _unites(s):
    # kilo s'écrit k minuscule : « KW » → « kW », « KJ » → « kJ »
    return re.sub(r"(\d|\s)K(W|J)\b", lambda m: m.group(1) + "k" + m.group(2), s or "")


def _corriger(qs):
    """Corrections apportées à la source (détaillées dans NOTE-DE-LIVRAISON.md)."""
    by = {q["id"]: q for q in qs}
    # Q46 : doublon exact de Q45 dans la source
    qs = [q for q in qs if q["id"] != "Q46"]
    # Q15 : l'explication accepte « la chaleur », la liste des réponses justes l'oubliait
    by["Q15"]["correct"] = ["4", "7"]
    by["Q15"]["explain"] = ("La calorie est une unité d'énergie (quantité de chaleur) : 1 cal ≈ 4,18 J. La réponse "
                            "« la chaleur » est également acceptée, la chaleur étant une forme d'énergie.")
    # Q32B : deux formulations acceptées, sans renvoi à une note extérieure
    by["Q32B"]["explain"] = ("Régime permanent : la température passe de 27,5 °C à 47 °C, soit ΔT = 19,5 K, et toute la "
                             "puissance (Φ = 20 W) traverse le mur. Avec la formule donnée ΔT = R·Φ/S : R = ΔT·S/Φ = "
                             "19,5 × 0,1 / 20 ≈ 0,098 K·m²·W⁻¹ (résistance surfacique). Avec la définition R = ΔT/Φ "
                             "(sans la surface, comme en question suivante), R = 19,5 / 20 = 0,975 K·W⁻¹ : les deux "
                             "réponses a et b sont acceptées.")
    # Q32C : la formule était donnée en image ; elle est écrite dans l'énoncé
    by["Q32C"]["img"] = None
    # Q42C : la « puissance crête » se définit à 1000 W·m⁻² ; on demande la puissance maximale à 600 W·m⁻²
    by["Q42C"]["q"] = ("Courbes I(U) (traits continus) et P(U) (traits pointillés). L'irradiance est de 600 W·m⁻². "
                       "Quelle est la puissance maximale fournie par le panneau (sommet de la courbe P à 600 W·m⁻²) ?")
    by["Q42C"]["explain"] = ("La puissance maximale est le sommet de la courbe P(U) (pointillés) à 600 W·m⁻² : il se lit "
                             "aux alentours de 2,3 W. La « puissance crête » d'un panneau, elle, se mesure à 1000 W·m⁻².")
    # Q52 : sans renvoi à une note extérieure
    by["Q52"]["explain"] = ("Le panneau est la source d'énergie électrique du système : il ALIMENTE. On peut aussi y voir "
                            "un convertisseur de lumière en électricité, mais dans la chaîne d'énergie il tient la place "
                            "de la source.")
    # Q59 : un bouton poussoir relève d'ordinaire de la fonction Acquérir (chaîne d'information) ; la question
    # précise le cas où il coupe lui-même le courant de puissance
    by["Q59"]["q"] = ("Dans une commande directe, sans chaîne d'information, un bouton poussoir coupe ou laisse passer "
                      "le courant d'une lampe. Quelle fonction de la chaîne d'énergie réalise-t-il alors ?")
    by["Q59"]["explain"] = ("Il laisse passer ou coupe l'énergie vers la lampe : il DISTRIBUE. Attention : dans un système "
                            "automatisé, le bouton poussoir envoie une consigne à la chaîne d'information ; il réalise "
                            "alors la fonction ACQUÉRIR.")
    by["Q60"]["explain"] = ("Énergie potentielle : E = m·g·h. 1000 L d'eau = 1000 kg, donc E = 1000 × 9,81 × 50 = "
                            "490 500 J ≈ 490 kJ.")
    for q in qs:
        q["q"] = _unites(q["q"])
        q["explain"] = _unites(q["explain"])
        q["opts"] = [[k, _unites(t)] for k, t in q["opts"]]
    return qs


def questions():
    src = SOURCE.read_text(encoding="utf-8")
    qs = json.loads(re.search(r"const QDATA = (\[.*?\]);\n", src).group(1))
    return _corriger(qs)


def _grader(q):
    if q["multi"]:
        assert all(k.isdigit() for k in q["correct"]), q["id"]
        return {"type": "intset", "value": sorted(int(k) for k in q["correct"])}
    return {"type": "code", "equals": [k.lower() for k in q["correct"]]}


def _attendu(q):
    sep = " ; " if q["multi"] else " ou "
    return sep.join(f"{k}) {t}" for k, t in q["opts"] if k in q["correct"])


def parties():
    """Les six parties, au format des parties d'exercice du générateur (blocs « grp » marqués « qcm »)."""
    qs, out, cur = questions(), [], None
    starts = {p[2]: p for p in PARTIES}
    for q in qs:
        if q["id"] in starts:
            t, mn, _ = starts[q["id"]]
            cur = {"title": t, "minutes": mn, "intro": [], "blocks": []}
            out.append(cur)
        hint = ("Plusieurs réponses : sélectionne toutes les bonnes." if q["multi"]
                else "Une seule réponse." + (" " + q["round_note"] + "." if q.get("round_note") else ""))
        cur["blocks"].append({"kind": "grp", "qcm": True, "stem": q["q"], "hint": hint, "src": q["id"],
                              "fields": [("Réponse", _grader(q), _attendu(q))], "why": q["explain"],
                              "opts": q["opts"], "multi": q["multi"], "img": q.get("img")})
    assert [p["title"] for p in out] == [p[0] for p in PARTIES]
    return out


def render_qcm(b, h):
    """Une question : énoncé, image éventuelle, propositions ; la case du gabarit est masquée."""
    gid, label, fid = b["id"], b["label"], b["fids"][0]
    img = ""
    if b["img"]:  # l'image n'est écrite qu'une fois dans la page (images_js) : plusieurs questions la partagent
        name, alt, maxw = IMAGES[b["img"]]
        _src, w, hh = (h.jpg if (h.IMAGES / f"{name}.jpg").exists() else h.png)(name)
        img = (f'<figure class="fig" style="max-width:{maxw}px"><img data-qimg="{name}" alt="{html.escape(alt)}" '
               f'width="{w}" height="{hh}"></figure>')
    role = "group" if b["multi"] else "radiogroup"
    opts = "".join(f'<button type="button" class="qcm-o" data-k="{html.escape(k)}" role="{"checkbox" if b["multi"] else "radio"}" '
                   f'aria-checked="false"><span class="qcm-k">{html.escape(k)}</span><span class="qcm-t">{html.escape(t)}</span></button>'
                   for k, t in b["opts"])
    return f"""
        <div class="fast-q grp qcm" id="{gid}" data-multi="{1 if b['multi'] else 0}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{html.escape(b['stem'])}</strong></p>
          <p class="q-hint">{html.escape(b['hint'])}</p>{img}
          <div class="qcm-opts" role="{role}" aria-label="Propositions de la question {label}">{opts}</div>
          <div class="sol qcm-sol"><input type="hidden" id="in-{fid}" data-q="{fid}"><span class="mark" aria-live="polite"></span></div>
          <div class="fast-foot"><button type="button" class="btn btn-fast" disabled>Valider</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="qcm-rep"><b>Réponse attendue :</b> {html.escape(b['fields'][0][2])}</p>
            <div class="q-why"><p class="why-t">Explication</p><p>{html.escape(b['why'])}</p></div>
          </div>
        </div>"""


CONSIGNES = """<p class="only-training"><strong>Mode entraînement.</strong> Choisis ta réponse puis clique sur « Valider » : une réponse validée est définitive, sa correction et son explication s'affichent aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Réponds à tout le questionnaire sans correction ni note : tes choix restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections et la note.</p>
    <p><strong>Une ou plusieurs réponses.</strong> La plupart des questions n'ont qu'une bonne réponse ; quand il y en a plusieurs, l'énoncé le précise et il faut toutes les sélectionner. Certaines questions s'appuient sur une figure : un schéma, un oscillogramme, une courbe.</p>
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque question vaut un point, chaque partie est notée sur 20, puis pèse au prorata de son temps.</p>"""

QCM_CSS = """
/* ---------- QCM (questions à propositions) ---------- */
.qcm .fig{margin:8px 0}
.qcm-opts{display:flex; flex-direction:column; gap:6px; margin:8px 0 4px; max-width:820px}
.qcm-o{display:flex; align-items:flex-start; gap:10px; width:100%; text-align:left; background:#fff; border:1.5px solid var(--trait); border-radius:3px; padding:8px 12px; font:inherit; font-size:.97rem; color:var(--encre); cursor:pointer}
.qcm-o:hover:not(:disabled){border-color:var(--encre); background:var(--jaune-pale)}
.qcm-o:focus-visible{outline:3px solid var(--jaune); outline-offset:1px}
.qcm-k{flex:0 0 auto; min-width:1.9em; height:1.9em; display:inline-flex; align-items:center; justify-content:center; border:1.5px solid var(--bleu); color:var(--bleu); font:700 .85rem var(--f-titre); border-radius:3px}
.qcm[data-multi="1"] .qcm-k{border-radius:3px} .qcm[data-multi="0"] .qcm-k{border-radius:50%}
.qcm-o[aria-checked="true"]{border-color:var(--bleu); background:var(--bleu-pale); box-shadow:inset 0 0 0 1px var(--bleu)}
.qcm-o[aria-checked="true"] .qcm-k{background:var(--bleu); color:#fff}
.qcm-o:disabled{cursor:default}
.qcm-o.ok{border-color:var(--vert); background:var(--vert-pale)} .qcm-o.ok .qcm-k{border-color:var(--vert); background:var(--vert); color:#fff}
.qcm-o.ko{border-color:var(--rouge); background:var(--rouge-pale)} .qcm-o.ko .qcm-k{border-color:var(--rouge); background:var(--rouge); color:#fff}
.qcm-o .qcm-tag{margin-left:auto; flex:0 0 auto; font:700 .75rem var(--f-titre); padding:1px 7px; color:#fff}
.qcm-o.ok .qcm-tag{background:var(--vert)} .qcm-o.ko .qcm-tag{background:var(--rouge)}
.qcm-sol{min-height:0}
.qcm-sol .mark{flex:0 0 auto}
.qcm-rep{margin:0 0 6px}
@media print{ .qcm-o{padding:2px 8px; font-size:9pt; break-inside:avoid} .qcm{break-inside:avoid} }
"""

def images_js(h):
    """Les images du QCM, une seule fois chacune, posées dans les questions à l'ouverture de la page."""
    data = {}
    for name, _alt, _w in IMAGES.values():
        data[name] = (h.jpg if (h.IMAGES / f"{name}.jpg").exists() else h.png)(name)[0]
    return ("<script>(function () { var I = " + json.dumps(data) + ";\n"
            "  Array.prototype.forEach.call(document.querySelectorAll(\"img[data-qimg]\"), function (im) { "
            "im.src = I[im.getAttribute(\"data-qimg\")]; }); })();</script>")


QCM_JS = r"""<script>/* QCM : un clic choisit une proposition (ou plusieurs) ; le repère va dans la case masquée du gabarit */
(function () {
  "use strict";
  var parts = document.getElementById("parts");
  if (!parts || !parts.querySelector(".qcm")) return;
  function inp(q) { return q.querySelector(".sol input"); }
  function choisis(q) { return Array.prototype.filter.call(q.querySelectorAll(".qcm-o"), function (o) { return o.getAttribute("aria-checked") === "true"; }); }
  function maj(q) {
    var i = inp(q), v = choisis(q).map(function (o) { return o.getAttribute("data-k"); }).join(",");
    i.value = v;
    var b = q.querySelector(".btn-fast");
    if (!i.disabled) b.disabled = !v;
    i.dispatchEvent(new Event("input", { bubbles: true }));
  }
  parts.addEventListener("click", function (e) {
    var o = e.target.closest(".qcm-o");
    if (!o || o.disabled) return;
    var q = o.closest(".qcm"), multi = q.getAttribute("data-multi") === "1";
    if (inp(q).disabled) return;
    if (multi) o.setAttribute("aria-checked", o.getAttribute("aria-checked") === "true" ? "false" : "true");
    else Array.prototype.forEach.call(q.querySelectorAll(".qcm-o"), function (x) { x.setAttribute("aria-checked", x === o ? "true" : "false"); });
    maj(q);
  });
  // flèches du clavier dans une question à réponse unique
  parts.addEventListener("keydown", function (e) {
    var o = e.target.closest && e.target.closest(".qcm-o");
    if (!o || (e.key !== "ArrowDown" && e.key !== "ArrowUp")) return;
    var all = Array.prototype.slice.call(o.parentNode.querySelectorAll(".qcm-o")), k = all.indexOf(o) + (e.key === "ArrowDown" ? 1 : -1);
    if (all[k]) { e.preventDefault(); all[k].focus(); }
  });
  // une fois la question corrigée par le moteur (champ verrouillé) : propositions justes et fausses marquées
  function corriger(q) {
    var id = inp(q).getAttribute("data-q"), g = (window.__QCFG__[id] || {}).grader || {}, bons = {};
    (g.equals || []).forEach(function (k) { bons[k] = 1; });
    (g.value || []).forEach(function (k) { bons[String(k)] = 1; });
    Array.prototype.forEach.call(q.querySelectorAll(".qcm-o"), function (o) {
      var k = o.getAttribute("data-k").toLowerCase(), sel = o.getAttribute("aria-checked") === "true", tag;
      o.disabled = true;
      if (bons[k] || (sel && !bons[k])) {
        o.classList.add(bons[k] ? "ok" : "ko");
        tag = document.createElement("span"); tag.className = "qcm-tag";
        tag.textContent = bons[k] ? (sel ? "✔ ta réponse" : "✔ bonne réponse") : "✘ ta réponse";
        o.appendChild(tag);
      }
    });
    var juste = q.querySelector(".sol").classList.contains("is-ok");
    q.querySelector(".q-status").textContent = juste ? "Bonne réponse" : (inp(q).value ? "Réponse fausse" : "Pas de réponse");
  }
  new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      var i = m.target;
      if (i.tagName !== "INPUT" || !i.disabled) return;
      var q = i.closest(".qcm");
      if (q && !q.classList.contains("corrigee")) { q.classList.add("corrigee"); corriger(q); }
    });
  }).observe(parts, { subtree: true, attributes: true, attributeFilter: ["disabled"] });
})();
</script>"""
