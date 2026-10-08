"""Exercice 1.1, partie 2 : le Toyota RAV4 hybride.

Deux figures « vivantes », reprises de la maquette validée :
  - figure 3 : schéma technique de la motorisation, animé selon la situation de conduite (arrêt, démarrage,
    accélération, croisière, freinage), avec la version 4 roues motrices (AWD-i) en option ;
  - figure 4 : chaîne d'énergie à compléter (repères 1 à 11), dont les blocs s'éclairent au même rythme.
Les fonctions (Alimenter, Convertir…) des composants ne s'affichent qu'une fois la partie corrigée.
Toutes les classes et tous les identifiants portent le préfixe « rv- » : le gabarit a déjà des « .modes », « .card »…
"""

# ------------------------------------------------------------ figure 3 : schéma technique
TECH_SVG = """<svg class="rv-tech" id="rv-tech" viewBox="0 0 960 520" role="img" aria-label="Schéma de la motorisation hybride du RAV4 : réservoir de carburant, système d'injection, moteur thermique, train épicycloïdal, génératrice, batterie, répartiteur de puissance, moteur électrique, arbre de sortie et pignons de renvoi, réducteur, différentiel et roues motrices">
  <defs><pattern id="rv-hach" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#8A949B" stroke-width="2"/></pattern></defs>
  <g id="rv-tracks"></g>
  <path class="rv-pipe" d="M140 120 H170 V225 H200"/><path class="rv-pipe" d="M270 225 H300"/>
  <path class="rv-shaft" d="M430 225 H470"/><path class="rv-shaft" d="M500 135 V195"/><path class="rv-shaft" d="M530 225 H700"/>
  <path class="rv-wire" d="M545 107 C600 107 640 137 700 137"/>
  <path class="rv-wire" d="M775 80 q8 5 0 10 t0 10 t0 10"/><path class="rv-wire" d="M775 165 q8 5 0 10 t0 10 t0 10 t0 10"/>
  <path class="rv-shaft" d="M620 300 V330 H520 V450"/><path class="rv-shaft" d="M200 450 H760"/>
  <g class="rv-awd"><path class="rv-wire" d="M850 137 H948 V542 H585"/><path class="rv-shaft" d="M495 565 V605"/><path class="rv-shaft" d="M200 605 H760"/></g>
  <g id="rv-flows"></g>
  <g class="rv-compo" id="rv-c-res" tabindex="0" data-k="res">
    <rect class="rv-bx" x="30" y="60" width="110" height="130" rx="18"/>
    <rect x="58" y="96" width="54" height="58" rx="5" fill="#1C2530"/>
    <rect x="68" y="106" width="22" height="40" rx="2" fill="#F2B705"/><rect x="72" y="111" width="14" height="10" fill="#1C2530"/>
    <path d="M90 116 h7 v20 a4 4 0 0 0 8 0 v-22 l-5 -6" stroke="#F2B705" stroke-width="3" fill="none" stroke-linecap="round"/>
    <text class="rv-lab" x="85" y="38" text-anchor="middle">Réservoir</text><text class="rv-labs" x="85" y="54" text-anchor="middle">de carburant</text>
  </g>
  <g class="rv-compo" id="rv-c-inj" tabindex="0" data-k="inj">
    <rect class="rv-bx" x="200" y="205" width="70" height="40" rx="10"/>
    <path d="M222 215 h26 l-6 10 h-14 z M235 225 v10" stroke="#46525C" stroke-width="2" fill="#E3E5E0"/>
    <text class="rv-labs" x="235" y="266" text-anchor="middle">Système</text><text class="rv-labs" x="235" y="281" text-anchor="middle">d'injection</text>
  </g>
  <g class="rv-compo" id="rv-c-eng" tabindex="0" data-k="eng">
    <rect class="rv-bx" x="300" y="195" width="130" height="60" rx="8"/>
    <g><circle class="rv-cyl" cx="328" cy="225" r="11"/><circle class="rv-cyl" cx="353" cy="225" r="11"/><circle class="rv-cyl" cx="378" cy="225" r="11"/><circle class="rv-cyl" cx="403" cy="225" r="11"/></g>
    <text class="rv-lab" x="365" y="180" text-anchor="middle">Moteur thermique</text>
  </g>
  <g class="rv-compo" id="rv-c-pl" tabindex="0" data-k="pl">
    <circle class="rv-bx" cx="500" cy="225" r="30"/>
    <g class="rv-spin"><circle cx="500" cy="225" r="30" fill="none"/><circle cx="500" cy="207" r="7" fill="#C9CFD3" stroke="#46525C"/><circle cx="516" cy="234" r="7" fill="#C9CFD3" stroke="#46525C"/><circle cx="484" cy="234" r="7" fill="#C9CFD3" stroke="#46525C"/></g>
    <circle cx="500" cy="225" r="6" fill="#46525C"/>
    <text class="rv-labs" x="470" y="282" text-anchor="end">Train</text><text class="rv-labs" x="470" y="297" text-anchor="end">épicycloïdal</text>
  </g>
  <g class="rv-compo" id="rv-c-mg1" tabindex="0" data-k="mg1">
    <rect class="rv-bx" x="455" y="80" width="90" height="55" rx="8"/>
    <g class="rv-spin"><circle cx="500" cy="107" r="16" fill="none" stroke="#46525C" stroke-width="2"/><path d="M500 91 V123 M484 107 H516" stroke="#46525C" stroke-width="2"/></g>
    <text class="rv-lab" x="440" y="102" text-anchor="end">Génératrice</text>
  </g>
  <g class="rv-compo" id="rv-c-bat" tabindex="0" data-k="bat">
    <rect class="rv-bx" x="700" y="20" width="150" height="60" rx="8"/>
    <rect x="712" y="44" width="126" height="22" rx="3" fill="#F4F5F2" stroke="#46525C"/>
    <rect class="rv-soc" id="rv-soc" x="714" y="46" width="73" height="18" rx="2"/>
    <text class="rv-labs" x="775" y="38" text-anchor="middle">Batterie</text>
    <text id="rv-soc-t" x="775" y="60" text-anchor="middle" font-size="12" font-weight="700" fill="#1C2530">60 %</text>
  </g>
  <g class="rv-compo" id="rv-c-ond" tabindex="0" data-k="ond">
    <rect class="rv-bx" x="700" y="110" width="150" height="55" rx="8"/>
    <path d="M718 146 l8 -14 l8 14 l8 -14 l8 14" stroke="#46525C" stroke-width="2" fill="none"/>
    <text class="rv-labs" x="790" y="133" text-anchor="middle">Répartiteur</text><text class="rv-labs" x="790" y="149" text-anchor="middle">de puissance</text>
  </g>
  <g class="rv-compo" id="rv-c-mg2" tabindex="0" data-k="mg2">
    <rect class="rv-bx" x="700" y="195" width="150" height="60" rx="8"/>
    <g class="rv-spin"><circle cx="726" cy="225" r="16" fill="none" stroke="#46525C" stroke-width="2"/><path d="M726 209 V241 M710 225 H742" stroke="#46525C" stroke-width="2"/></g>
    <text class="rv-labs" x="800" y="221" text-anchor="middle">Moteur</text><text class="rv-labs" x="800" y="237" text-anchor="middle">électrique</text>
  </g>
  <g class="rv-compo" id="rv-c-renv" tabindex="0" data-k="renv">
    <rect class="rv-bx" x="604" y="180" width="32" height="90" rx="4"/>
    <rect x="604" y="180" width="32" height="90" rx="4" fill="url(#rv-hach)" stroke="#1C2530" stroke-width="2"/>
    <rect x="606" y="272" width="28" height="64" rx="4" fill="url(#rv-hach)" stroke="#1C2530" stroke-width="2"/>
    <text class="rv-labs" x="650" y="292">Arbre de sortie et</text><text class="rv-labs" x="650" y="307">pignons de renvoi</text>
  </g>
  <g class="rv-compo" id="rv-c-red" tabindex="0" data-k="red">
    <rect x="500" y="300" width="14" height="60" rx="3" fill="url(#rv-hach)" stroke="#1C2530" stroke-width="2"/>
    <text class="rv-labs" x="490" y="345" text-anchor="end">Réducteur</text>
  </g>
  <g class="rv-compo" id="rv-c-diff" tabindex="0" data-k="diff">
    <circle class="rv-bx" cx="520" cy="450" r="20"/>
    <g class="rv-spin"><path d="M520 434 V466 M504 450 H536" stroke="#46525C" stroke-width="2"/></g>
    <text class="rv-labs" x="520" y="492" text-anchor="middle">Différentiel</text>
  </g>
  <g class="rv-compo" id="rv-c-roues" tabindex="0" data-k="roues">
    <rect class="rv-bx" x="150" y="390" width="50" height="120" rx="10"/><rect class="rv-bx" x="760" y="390" width="50" height="120" rx="10"/>
    <g><line class="rv-tread" x1="160" y1="392" x2="160" y2="508"/><line class="rv-tread" x1="175" y1="392" x2="175" y2="508"/><line class="rv-tread" x1="190" y1="392" x2="190" y2="508"/>
       <line class="rv-tread" x1="770" y1="392" x2="770" y2="508"/><line class="rv-tread" x1="785" y1="392" x2="785" y2="508"/><line class="rv-tread" x1="800" y1="392" x2="800" y2="508"/></g>
    <text class="rv-lab" x="835" y="445">Roues</text><text class="rv-labs" x="835" y="462">motrices</text><text class="rv-labs" x="835" y="477">avant</text>
  </g>
  <g class="rv-awd">
    <g class="rv-compo" id="rv-c-mgr" tabindex="0" data-k="mgr">
      <rect class="rv-bx" x="410" y="520" width="175" height="45" rx="8"/>
      <g class="rv-spin"><circle cx="432" cy="542" r="12" fill="none" stroke="#46525C" stroke-width="2"/><path d="M432 530 V554 M420 542 H444" stroke="#46525C" stroke-width="2"/></g>
      <text class="rv-labs" x="515" y="538" text-anchor="middle">Moteur électrique</text><text class="rv-labs" x="515" y="556" text-anchor="middle">arrière (et réducteur)</text>
    </g>
    <g class="rv-compo" id="rv-c-rar" tabindex="0" data-k="rar">
      <rect class="rv-bx" x="150" y="565" width="50" height="80" rx="10"/><rect class="rv-bx" x="760" y="565" width="50" height="80" rx="10"/>
      <g><line class="rv-tread" x1="165" y1="567" x2="165" y2="643"/><line class="rv-tread" x1="185" y1="567" x2="185" y2="643"/><line class="rv-tread" x1="775" y1="567" x2="775" y2="643"/><line class="rv-tread" x1="795" y1="567" x2="795" y2="643"/></g>
      <text class="rv-labs" x="835" y="610">Roues arrière</text>
    </g>
  </g>
  <g id="rv-badges"></g>
</svg>"""


def figure_tech():
    return f"""<figure class="rv-fig" id="rv-demo" data-grp="__GRP__">
  <div class="rv-modes no-print" role="group" aria-label="Situation de conduite">
    <button type="button" data-m="arret">À l'arrêt</button><button type="button" data-m="ev">Démarrage</button>
    <button type="button" data-m="accel">Accélération</button><button type="button" data-m="croisiere">Croisière</button>
    <button type="button" data-m="frein">Freinage</button>
  </div>
  <div class="rv-tools no-print">
    <button type="button" class="rv-play" id="rv-play">▶ Faire un trajet</button>
    <div class="rv-prog" aria-hidden="true"><i id="rv-prog"></i></div>
    <label><input type="checkbox" id="rv-awd"> Version 4 roues motrices (AWD-i)</label>
    <label title="Disponible une fois la partie corrigée"><input type="checkbox" id="rv-fns" disabled> Montrer les fonctions
      <span class="rv-fns-note">(après correction de la partie)</span></label>
  </div>
  <p class="rv-mode-d" id="rv-mode-d" aria-live="polite"></p>
  {TECH_SVG}
  <div class="rv-legende">
    <span><svg viewBox="0 0 42 12" aria-hidden="true"><line x1="2" y1="6" x2="40" y2="6" class="rv-f-chim" style="stroke-dasharray:2 7"/></svg> énergie chimique (carburant)</span>
    <span><svg viewBox="0 0 42 12" aria-hidden="true"><line x1="2" y1="6" x2="40" y2="6" class="rv-f-elec"/></svg> énergie électrique</span>
    <span><svg viewBox="0 0 42 12" aria-hidden="true"><line x1="2" y1="6" x2="40" y2="6" class="rv-f-meca" style="stroke-dasharray:10 5"/></svg> énergie mécanique</span>
  </div>
  <div class="rv-etat no-print" id="rv-etat"></div>
  <div class="rv-info no-print" id="rv-info" aria-live="polite"><p>Touchez un composant du schéma : son nom et son rôle s'affichent ici.</p></div>
  <figcaption>Figure 3 — Schéma simplifié de la motorisation hybride : choisissez une situation de conduite pour voir
  l'énergie circuler, ou lancez un trajet.</figcaption>
</figure>"""


def figure_chaine():
    return """<figure class="rv-fig rv-fig-ch">
  <svg class="rv-chaine" id="rv-chaine" viewBox="0 0 760 540" role="img" aria-label="Chaîne d'énergie du RAV4 à compléter, cases repérées de 1 à 11 ; le bloc Transmettre — train épicycloïdal est donné">
    <defs><marker id="rv-fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#1C2530"/></marker></defs>
    <g id="rv-c-tracks"></g><g id="rv-c-flows"></g><g id="rv-c-blocks"></g>
    <text class="rv-mo" x="657" y="350" text-anchor="middle">Matière d'œuvre entrante :</text><text class="rv-mo" x="657" y="364" text-anchor="middle">roues immobiles</text>
    <path class="rv-arw" d="M657 372 V398" marker-end="url(#rv-fl)"/><path class="rv-arw" d="M657 470 V496" marker-end="url(#rv-fl)"/>
    <text class="rv-mo" x="657" y="512" text-anchor="middle">Matière d'œuvre sortante :</text><text class="rv-mo" x="657" y="526" text-anchor="middle">roues entraînées</text>
  </svg>
  <figcaption>Figure 4 — Chaîne d'énergie à compléter : les 11 cases à remplir sont repérées en rouge. La case
  <em>Transmettre — train épicycloïdal</em> est donnée. Les blocs en jeu dans la situation choisie sur la figure 3
  s'éclairent.</figcaption>
</figure>"""


RAV4_CSS = """
/* ---------- exercice 1.1, partie 2 : RAV4 animé (préfixe rv-) ---------- */
.rv-fig{margin:14px 0; padding:12px 14px; background:#fff; border:1px solid var(--trait-fin); --chim:#B26A00; --elec:#1F5FA8; --meca:#1B7A43}
.rv-fig figcaption{font-size:.88rem; color:var(--encre-2); margin-top:8px}
.rv-modes{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 8px}
.rv-modes button,.rv-play{font:600 .92rem var(--f-texte); border:1.5px solid var(--encre); background:#fff; color:var(--encre); padding:7px 12px; border-radius:2px; cursor:pointer}
.rv-modes button[aria-pressed="true"]{background:var(--encre); color:#fff}
.rv-tools{display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; margin:0 0 6px}
.rv-tools label{font-size:.92rem; display:flex; gap:6px; align-items:center; cursor:pointer}
.rv-tools label:has(input:disabled){color:#7A848C; cursor:not-allowed}
.rv-fns-note{font-size:.82rem; color:var(--encre-2)}
.rv-play{min-width:9.5em}
.rv-prog{flex:1 1 120px; height:6px; background:var(--trait-fin); position:relative; min-width:100px}
.rv-prog i{position:absolute; left:0; top:0; bottom:0; width:0; background:var(--jaune)}
.rv-mode-d{margin:4px 0 8px; min-height:3em; font-size:.95rem}
.rv-tech,.rv-chaine{width:100%; height:auto; display:block; background:#fff; border:1px solid var(--trait-fin); font-family:var(--f-texte)}
.rv-chaine{max-width:760px; margin:0 auto}
.rv-track{fill:none; stroke:#E1E4E1; stroke-linecap:round}
.rv-flow{fill:none; stroke-linecap:round; opacity:0; transition:opacity .35s}
.rv-flow.on{opacity:1; animation:rv-couler 1s linear infinite}
.rv-flow.on.rev{animation-direction:reverse}
@keyframes rv-couler{to{stroke-dashoffset:-32}}
.rv-f-chim{stroke:var(--chim); stroke-width:4; stroke-dasharray:2 14}
.rv-f-elec{stroke:var(--elec); stroke-width:4.5; stroke-dasharray:10 6}
.rv-f-meca{stroke:var(--meca); stroke-width:6; stroke-dasharray:14 18}
.rv-shaft{stroke:var(--encre); stroke-width:5; fill:none}
.rv-wire{stroke:var(--encre); stroke-width:2; fill:none}
.rv-pipe{stroke:var(--encre); stroke-width:2.5; stroke-dasharray:3 4; fill:none}
.rv-compo{cursor:pointer}
.rv-bx{fill:#fff; stroke:var(--encre); stroke-width:2}
.rv-compo:hover .rv-bx,.rv-compo:focus .rv-bx{fill:var(--jaune-pale)}
.rv-compo:focus{outline:none}
.rv-compo.sel .rv-bx{stroke:var(--jaune); stroke-width:4}
.rv-lab{font-size:15px; font-weight:600; fill:var(--encre)}
.rv-labs{font-size:13px; fill:var(--encre-2)}
.rv-badge{opacity:0; transition:opacity .3s}
.rv-fonctions .rv-badge{opacity:1}
.rv-badge text{font:700 11px var(--f-titre); fill:#fff; letter-spacing:.04em}
.rv-spin{transform-box:fill-box; transform-origin:center; pointer-events:none}
.rv-run .rv-spin{animation:rv-tourner 1.2s linear infinite}
.rv-run.rev .rv-spin{animation-direction:reverse}
@keyframes rv-tourner{to{transform:rotate(360deg)}}
.rv-cyl{fill:#D3D8D5}
.rv-eng-on .rv-cyl{animation:rv-explo .5s ease-in-out infinite alternate}
.rv-eng-on .rv-cyl:nth-child(2n){animation-delay:.25s}
@keyframes rv-explo{from{fill:#D3D8D5}to{fill:#E8892B}}
.rv-tread{stroke:#6B747B; stroke-width:2; stroke-dasharray:4 6}
.rv-roll .rv-tread{animation:rv-couler .6s linear infinite}
.rv-awd{display:none}
.rv-avec-awd .rv-awd{display:inline}
.rv-soc{fill:#7FB08F; transition:width .4s linear}
.rv-soc.bas{fill:#E0A13A}
.rv-legende{display:flex; flex-wrap:wrap; gap:6px 18px; font-size:.86rem; margin:6px 0 0}
.rv-legende span{display:inline-flex; align-items:center; gap:6px}
.rv-legende svg{width:42px; height:12px}
.rv-etat{display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:6px 14px; margin:8px 0 2px; font-size:.92rem}
.rv-etat div{border-left:4px solid var(--trait); padding:2px 8px; background:#FAFAF8}
.rv-etat b{display:block; font:700 .75rem var(--f-titre); text-transform:uppercase; letter-spacing:.04em; color:var(--encre-2)}
.rv-etat .on{border-left-color:var(--vert)}
.rv-info{min-height:4.6em; margin-top:8px; padding:8px 12px; border:1.5px solid var(--encre); font-size:.95rem}
.rv-info h4{margin:0 0 2px; font:700 1.05rem var(--f-titre)}
.rv-info p{margin:2px 0}
.rv-fn-tag{display:inline-block; font:700 .72rem var(--f-titre); color:#fff; padding:1px 7px; margin-left:6px; vertical-align:middle; letter-spacing:.04em}
.rv-blk rect{fill:#fff; stroke:var(--encre); stroke-width:1.6; transition:fill .35s, stroke .35s}
.rv-blk.act rect{fill:#EAF4EE; stroke:var(--vert); stroke-width:2.6}
.rv-blk .rv-fn{font:700 13px var(--f-titre); fill:var(--encre); letter-spacing:.03em}
.rv-blk .rv-nm{font-size:12.5px; fill:var(--encre-2)}
.rv-rep circle{fill:var(--rouge)} .rv-rep text{fill:#fff; font:700 13px var(--f-texte)}
.rv-arw{fill:none; stroke:var(--encre); stroke-width:1.8}
.rv-mo{font-size:12px; font-style:italic; fill:var(--encre-2)}
@media (prefers-reduced-motion:reduce){ .rv-flow.on,.rv-run .rv-spin,.rv-eng-on .rv-cyl,.rv-roll .rv-tread{animation-duration:3s} }
@media print{ .rv-fig{break-inside:avoid; border:0; padding:0} .rv-flow,.rv-blk.act rect{animation:none} }
"""

RAV4_JS = r"""<script>/* Exercice 1.1, partie 2 : schéma du RAV4 animé et chaîne d'énergie synchronisée */
(function () {
  "use strict";
  var root = document.getElementById("rv-demo");
  if (!root) return;
  var NS = "http://www.w3.org/2000/svg", tech = document.getElementById("rv-tech");
  function $(s) { return document.querySelector(s); }
  function el(tag, at, parent) { var e = document.createElementNS(NS, tag); for (var k in at) e.setAttribute(k, at[k]); if (parent) parent.appendChild(e); return e; }

  // flux du schéma technique, dans leur sens « moteur » ; « rev » les inverse (freinage, recharge)
  var FLUX = {
    carb: ["chim", "M140 120 H170 V225 H300"], eng: ["meca", "M430 225 H470"], mg1: ["meca", "M500 195 V135"],
    mg1e: ["elec", "M545 107 C600 107 640 137 700 137"], bat: ["elec", "M775 80 V110"], mg2e: ["elec", "M775 165 V195"],
    out: ["meca", "M530 225 H604"], mg2m: ["meca", "M700 225 H636"], renv: ["meca", "M620 270 V330 H520 V430"],
    rg: ["meca", "M500 450 H200"], rd: ["meca", "M540 450 H760"],
    mgre: ["elec", "M850 137 H948 V542 H585"], arr: ["meca", "M495 565 V605"], arrg: ["meca", "M495 605 H200"],
    arrd: ["meca", "M495 605 H760"]
  };
  var AWD = { mgre: 1, arr: 1, arrg: 1, arrd: 1 };
  Object.keys(FLUX).forEach(function (k) {
    var t = FLUX[k][0], d = FLUX[k][1], g = AWD[k] ? " rv-awd" : "";
    el("path", { d: d, "class": "rv-track" + g, "stroke-width": t === "meca" ? 10 : 8 }, $("#rv-tracks"));
    FLUX[k].el = el("path", { d: d, "class": "rv-flow rv-f-" + t + g }, $("#rv-flows"));
  });

  // composants : nom, rôle, fonction, position de l'étiquette de fonction
  var FN = { A: ["Alimenter", "#1B7A43"], D: ["Distribuer", "#B26A00"], C: ["Convertir", "#1F5FA8"], T: ["Transmettre", "#46525C"], G: ["Agir", "#B42318"] };
  var COMPO = {
    res: ["Réservoir de carburant", "Stocke l'essence : l'énergie chimique de la voiture.", "A", [85, 200]],
    inj: ["Système d'injection", "Dose l'essence envoyée dans les cylindres, sur ordre du calculateur.", "D", [235, 300]],
    eng: ["Moteur thermique", "Brûle l'essence : l'énergie chimique devient de l'énergie mécanique de rotation.", "C", [365, 262]],
    pl: ["Train épicycloïdal", "Partage la puissance du moteur thermique entre les roues et la génératrice.", "T", [557, 172]],
    mg1: ["Génératrice", "Transforme l'énergie mécanique du moteur thermique en électricité : elle recharge la batterie ou alimente le moteur électrique. Elle sert aussi de démarreur.", "C", [500, 60]],
    bat: ["Batterie haute tension", "Stocke l'énergie électrique ; elle se recharge en roulant et au freinage.", "A", [775, 2]],
    ond: ["Répartiteur de puissance", "Électronique de puissance (onduleur) : dirige le courant entre la batterie, la génératrice et les moteurs, dans un sens ou dans l'autre.", "D", [900, 168]],
    mg2: ["Moteur électrique", "Transforme l'électricité en rotation pour entraîner les roues ; au freinage, il fonctionne en génératrice et récupère l'énergie.", "C", [900, 262]],
    renv: ["Arbre de sortie et pignons de renvoi", "Reportent la rotation vers le réducteur.", "T", [710, 318]],
    red: ["Réducteur", "Diminue la vitesse de rotation et augmente le couple.", "T", [420, 365]],
    diff: ["Différentiel", "Répartit le couple entre les deux roues et leur permet de tourner à des vitesses différentes en virage.", "T", [520, 500]],
    roues: ["Roues motrices", "Transmettent l'effort au sol : la voiture avance.", "G", [175, 375]],
    mgr: ["Moteur électrique arrière", "Version AWD-i : entraîne les roues arrière, sans arbre de transmission, au démarrage et quand l'adhérence l'exige.", "C", [355, 535]],
    rar: ["Roues arrière", "Version AWD-i : deviennent motrices au démarrage et sur sol glissant.", "G", [175, 555]]
  };
  Object.keys(COMPO).forEach(function (k) {
    var c = COMPO[k], f = FN[c[2]], x = c[3][0], y = c[3][1], w = f[0].length * 7.4 + 12;
    var g = el("g", { "class": "rv-badge" + (k === "mgr" || k === "rar" ? " rv-awd" : ""), "aria-hidden": "true" }, $("#rv-badges"));
    el("rect", { x: x - w / 2, y: y, width: w, height: 17, rx: 3, fill: f[1] }, g);
    el("text", { x: x, y: y + 12.5, "text-anchor": "middle" }, g).textContent = f[0].toUpperCase();
  });
  var fns = $("#rv-fns"), awd = $("#rv-awd");
  function info(k) {
    var c = COMPO[k], f = FN[c[2]];
    Array.prototype.forEach.call(root.querySelectorAll(".rv-compo.sel"), function (e) { e.classList.remove("sel"); });
    $("#rv-c-" + k).classList.add("sel");
    $("#rv-info").innerHTML = "<h4>" + c[0] + (fns.checked ? '<span class="rv-fn-tag" style="background:' + f[1] + '">' + f[0].toUpperCase() + "</span>" : "") +
      "</h4><p>" + c[1] + "</p>";
  }
  Array.prototype.forEach.call(root.querySelectorAll(".rv-compo"), function (g) {
    g.addEventListener("click", function () { info(g.dataset.k); });
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); info(g.dataset.k); } });
  });
  fns.addEventListener("change", function () { tech.classList.toggle("rv-fonctions", fns.checked); var s = root.querySelector(".rv-compo.sel"); if (s) info(s.dataset.k); });
  awd.addEventListener("change", function () {
    tech.classList.toggle("rv-avec-awd", awd.checked);
    tech.setAttribute("viewBox", awd.checked ? "0 0 960 660" : "0 0 960 520");  // pas de vide sans l'essieu arrière
    appliquer(mode);
  });
  // les fonctions ne s'affichent qu'une fois la partie corrigée (questions validées, ou copie remise en examen)
  var GRP = (root.getAttribute("data-grp") || "").split(" ").filter(Boolean);
  function corrigee() {
    if (document.body.classList.contains("graded")) return true;
    return GRP.length > 0 && GRP.every(function (g) { var b = document.querySelector("#" + g + " .btn-fast"); return b && b.disabled; });
  }

  // figure 4 : chaîne d'énergie (repères 1 à 11)
  var BLK = {
    1: [300, 20, "ALIMENTER"], 2: [170, 125, "DISTRIBUER"], 3: [300, 125, "CONVERTIR"], 4: [590, 125, "CONVERTIR"],
    T: [440, 200, "TRANSMETTRE", "Train épicycloïdal"],
    5: [40, 275, "ALIMENTER"], 6: [170, 275, "DISTRIBUER"], 7: [300, 275, "CONVERTIR"],
    8: [100, 400, "TRANSMETTRE"], 9: [230, 400, "TRANSMETTRE"], 10: [360, 400, "TRANSMETTRE"], 11: [600, 400, "AGIR"]
  };
  var W = 114, H = 68;
  Object.keys(BLK).forEach(function (k) {
    var b = BLK[k], g = el("g", { "class": "rv-blk", id: "rv-b-" + k }, $("#rv-c-blocks")), t;
    el("rect", { x: b[0], y: b[1], width: W, height: H, rx: 4 }, g);
    el("text", { "class": "rv-fn", x: b[0] + W / 2, y: b[1] + 18, "text-anchor": "middle" }, g).textContent = b[2];
    if (b[3]) el("text", { "class": "rv-nm", x: b[0] + W / 2, y: b[1] + 42, "text-anchor": "middle" }, g).textContent = b[3];
    else {
      t = el("g", { "class": "rv-rep" }, g); el("circle", { cx: b[0] + 18, cy: b[1] + H - 16, r: 11 }, t);
      el("text", { x: b[0] + 18, y: b[1] + H - 11.5, "text-anchor": "middle" }, t).textContent = k;
    }
  });
  function R(k) { return BLK[k][0] + W; } function L(k) { return BLK[k][0]; } function M(k) { return BLK[k][1] + H / 2; }
  var CF = {
    a12: "M" + R(1) + " " + M(1) + " H432 V10 H150 V" + (M(2) + 10) + " H" + L(2),
    a21: "M" + (L(2) + 70) + " " + BLK[2][1] + " V" + M(1) + " H" + L(1),
    a23: "M" + R(2) + " " + M(2) + " H" + L(3),
    a3T: "M" + R(3) + " " + M(3) + " H426 V" + (M("T") - 12) + " H" + L("T"),
    a56: "M" + R(5) + " " + M(5) + " H" + L(6),
    a67: "M" + R(6) + " " + M(6) + " H" + L(7),
    a7T: "M" + R(7) + " " + M(7) + " H426 V" + (M("T") + 12) + " H" + L("T"),
    aT4: "M" + R("T") + " " + (M("T") - 12) + " H572 V" + M(4) + " H" + L(4),
    a42: "M" + R(4) + " " + M(4) + " H730 V2 H140 V" + (M(2) - 10) + " H" + L(2),
    aT8: "M" + (L("T") + W / 2) + " " + (BLK.T[1] + H) + " V375 H80 V" + M(8) + " H" + L(8),
    a89: "M" + R(8) + " " + M(8) + " H" + L(9),
    a910: "M" + R(9) + " " + M(9) + " H" + L(10),
    a1011: "M" + R(10) + " " + M(10) + " H" + L(11)
  };
  Object.keys(CF).forEach(function (k) {
    el("path", { d: CF[k], "class": "rv-arw", "marker-end": "url(#rv-fl)" }, $("#rv-c-tracks"));
    var t = k === "a56" || k === "a67" ? "chim" : (/^a(12|21|23|42)$/.test(k) ? "elec" : "meca");
    CF[k] = { el: el("path", { d: CF[k], "class": "rv-flow rv-f-" + t }, $("#rv-c-flows")) };
  });

  // situations de conduite
  var MODES = {
    arret: { t: "À l'arrêt", d: "Feu rouge : tout est arrêté, le moteur thermique ne consomme rien.",
      f: [], c: [], b: [], eng: false, soc: 0, roues: "immobiles" },
    ev: { t: "Démarrage", d: "Au démarrage et à basse vitesse, seul le moteur électrique entraîne les roues, avec l'énergie de la batterie. Le moteur thermique reste arrêté.",
      f: ["bat", "mg2e", "mg2m", "renv", "rg", "rd"], awd: ["mgre", "arr", "arrg", "arrd"],
      c: ["a12", "a23", "a3T", "aT8", "a89", "a910", "a1011"], b: [1, 2, 3, "T", 8, 9, 10, 11], eng: false, soc: -1, roues: "entraînées" },
    accel: { t: "Accélération", d: "Pour accélérer fort, tout travaille : le moteur thermique entraîne les roues et la génératrice, le moteur électrique ajoute sa puissance, alimenté par la génératrice et la batterie.",
      f: ["carb", "eng", "mg1", "mg1e", "out", "bat", "mg2e", "mg2m", "renv", "rg", "rd"], awd: ["mgre", "arr", "arrg", "arrd"],
      c: ["a56", "a67", "a7T", "aT4", "a42", "a12", "a23", "a3T", "aT8", "a89", "a910", "a1011"], b: [1, 2, 3, 4, 5, 6, 7, "T", 8, 9, 10, 11], eng: true, soc: -1, roues: "entraînées" },
    croisiere: { t: "Croisière", d: "À vitesse stable, le moteur thermique entraîne les roues ; une partie de sa puissance passe par la génératrice et recharge la batterie.",
      f: ["carb", "eng", "out", "renv", "rg", "rd", "mg1", "mg1e", "bat"], rev: { bat: 1 },
      c: ["a56", "a67", "a7T", "aT4", "a42", "a21", "aT8", "a89", "a910", "a1011"], b: [1, 2, 4, 5, 6, 7, "T", 8, 9, 10, 11], eng: true, soc: 1, roues: "entraînées" },
    frein: { t: "Freinage", d: "Au freinage, les roues entraînent le moteur électrique, qui fonctionne en génératrice : l'énergie du mouvement repart vers la batterie au lieu de chauffer les freins.",
      f: ["rg", "rd", "renv", "mg2m", "mg2e", "bat"], rev: { rg: 1, rd: 1, renv: 1, mg2m: 1, mg2e: 1, bat: 1, mgre: 1, arr: 1, arrg: 1, arrd: 1 }, awd: ["mgre", "arr", "arrg", "arrd"],
      c: ["a1011", "a910", "a89", "aT8", "a3T", "a23", "a21"], crev: { a1011: 1, a910: 1, a89: 1, aT8: 1, a3T: 1, a23: 1 }, b: [1, 2, 3, "T", 8, 9, 10, 11], eng: false, soc: 1, roues: "freinées : l'énergie est récupérée" }
  };
  var mode = "ev", soc = 60;
  function appliquer(m) {
    mode = m; var M_ = MODES[m], a4 = awd.checked, rev = M_.rev || {}, crev = M_.crev || {};
    var actifs = M_.f.concat(a4 && M_.awd ? M_.awd : []);
    Object.keys(FLUX).forEach(function (k) {
      var on = actifs.indexOf(k) >= 0;
      FLUX[k].el.classList.toggle("on", on); FLUX[k].el.classList.toggle("rev", on && !!rev[k]);
    });
    Object.keys(CF).forEach(function (k) {
      var on = M_.c.indexOf(k) >= 0;
      CF[k].el.classList.toggle("on", on); CF[k].el.classList.toggle("rev", on && !!crev[k]);
    });
    Object.keys(BLK).forEach(function (k) { $("#rv-b-" + k).classList.toggle("act", M_.b.indexOf(isNaN(k) ? k : +k) >= 0); });
    function run(k, on, r) { var e = $("#rv-c-" + k); e.classList.toggle("rv-run", on); e.classList.toggle("rev", !!r); }
    $("#rv-c-eng").classList.toggle("rv-eng-on", M_.eng);
    run("pl", M_.eng || actifs.indexOf("out") >= 0);
    run("mg1", actifs.indexOf("mg1") >= 0);
    run("mg2", actifs.indexOf("mg2m") >= 0, rev.mg2m);
    run("diff", actifs.indexOf("rg") >= 0, rev.rg);
    run("mgr", a4 && actifs.indexOf("arr") >= 0, rev.arr);
    ["roues", "rar"].forEach(function (k) { $("#rv-c-" + k).classList.toggle("rv-roll", actifs.indexOf("rg") >= 0); });
    Array.prototype.forEach.call(root.querySelectorAll(".rv-modes button"), function (b) { b.setAttribute("aria-pressed", b.dataset.m === m ? "true" : "false"); });
    $("#rv-mode-d").innerHTML = "<strong>" + M_.t + ".</strong> " + M_.d;
    var arr = a4 && M_.awd && actifs.indexOf("arr") >= 0;
    $("#rv-etat").innerHTML =
      '<div class="' + (M_.eng ? "on" : "") + '"><b>Moteur thermique</b>' + (M_.eng ? "en marche" : "arrêté") + "</div>" +
      '<div class="' + (M_.soc ? "on" : "") + '"><b>Batterie</b>' + (M_.soc < 0 ? "se décharge" : M_.soc > 0 ? "se recharge" : "au repos") + "</div>" +
      '<div class="' + (M_.f.length ? "on" : "") + '"><b>Roues avant</b>' + M_.roues + "</div>" +
      (a4 ? '<div class="' + (arr ? "on" : "") + '"><b>Roues arrière</b>' + (arr ? (m === "frein" ? "récupèrent aussi" : "motrices") : "roues libres") + "</div>" : "");
  }
  Array.prototype.forEach.call(root.querySelectorAll(".rv-modes button"), function (b) {
    b.addEventListener("click", function () { stop(); appliquer(b.dataset.m); });
  });

  // la jauge de batterie vit au rythme de la situation ; on vérifie au passage si la partie est corrigée
  var tic = 0;
  setInterval(function () {
    soc = Math.max(20, Math.min(90, soc + MODES[mode].soc * 0.5));
    $("#rv-soc").setAttribute("width", (122 * soc / 100).toFixed(1));
    $("#rv-soc").classList.toggle("bas", soc < 35);
    $("#rv-soc-t").textContent = Math.round(soc) + " %";
    if (++tic % 4 === 0 && fns.disabled && corrigee()) { fns.disabled = false; root.querySelector(".rv-fns-note").textContent = ""; }
  }, 200);

  // un trajet : les situations s'enchaînent
  var TRAJET = [["arret", 3], ["ev", 6], ["accel", 5], ["croisiere", 8], ["frein", 5], ["arret", 3]];
  var timer = null, total = TRAJET.reduce(function (s, x) { return s + x[1]; }, 0);
  function stop() { if (timer) { clearInterval(timer); timer = null; } $("#rv-play").textContent = "▶ Faire un trajet"; $("#rv-prog").style.width = "0"; }
  $("#rv-play").addEventListener("click", function () {
    if (timer) { stop(); return; }
    var t0 = performance.now(), cur = -1;
    $("#rv-play").textContent = "■ Arrêter le trajet";
    timer = setInterval(function () {
      var s = (performance.now() - t0) / 1000, acc = 0, i;
      if (s >= total) { stop(); appliquer("arret"); return; }
      for (i = 0; i < TRAJET.length; i++) { acc += TRAJET[i][1]; if (s < acc) break; }
      if (cur !== i) { cur = i; appliquer(TRAJET[i][0]); }
      $("#rv-prog").style.width = (100 * s / total).toFixed(1) + "%";
    }, 100);
  });
  appliquer("ev");
})();
</script>"""
