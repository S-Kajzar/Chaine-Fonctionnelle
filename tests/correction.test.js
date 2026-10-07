// Tests unitaires du moteur de correction appliqué aux cases de l'exercice 1.1.
//   node --test tests/correction.test.js
// Le moteur (Grading) et la configuration (__EXOS__) sont lus dans la page générée :
// on teste exactement ce que l'élève utilisera.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const PAGE = path.join(__dirname, "..", "index.html");
const html = fs.readFileSync(PAGE, "utf8");
const code = html.slice(html.indexOf("/*GRADING-START*/"), html.indexOf("/*GRADING-END*/"));
const mod = { exports: {} };
new Function("module", code + "\nmodule.exports = Grading;")(mod);
const G = mod.exports;
const EXOS = JSON.parse(html.match(/window\.__EXOS__ = (.*?);<\/script>/)[1]);
const EX = EXOS["chaines-information-energie"];
const QCFG = EX.qcfg;
const REP = require("./reponses.js");

function ok(id, ans) {
  const r = G.grade(ans, QCFG[id].grader);
  return r.invalid ? "invalid" : r.score;
}

// Réponses acceptées par l'exercice d'origine (dépôt schema_chaine-energie-information) : toutes doivent
// rester justes après la conversion vers le moteur du gabarit.
const SOURCE = {
  a1_1_1: ["acquérir", "acquisition", "acquerir"],
  a1_1_2: ["traiter", "traitement"],
  a1_1_3: ["communiquer", "communication", "restituer"],
  a1_2_1: ["alimenter", "alimentation"],
  a1_2_2: ["distribuer", "distribution"],
  a1_2_3: ["convertir", "conversion"],
  a1_2_4: ["transmettre", "transmission"],
  a1_2_5: ["agir", "action"],
  a1_3_1: ["consigne", "consignes", "ordre", "ordres", "commande", "commandes", "consigne de l'utilisateur", "ordre de l'utilisateur"],
  a1_3_2: ["compte rendu", "compte-rendu", "comptes rendus", "informations des capteurs", "informations capteurs", "etat du systeme", "retour d'information", "état du système"],
  a1_3_3: ["message", "messages", "signalisation", "information", "informations", "affichage"],
  a1_3_4: ["reseau electrique", "réseau électrique", "energie electrique", "énergie électrique", "alimentation electrique", "electricite", "secteur", "reseau edf", "courant electrique"],
  a1_4_1: ["moteur", "le moteur", "moteur electrique", "moteur électrique", "machinerie", "moteur de la machinerie"],
  a1_4_2: ["poulie et cables", "poulie", "cables", "câbles", "boite de reduction", "boîte de réduction", "reducteur", "réducteur", "natte de cables", "systeme de transmission", "poulie et natte de cables"],
  a1_4_3: ["cabine", "la cabine", "cabine de l'ascenseur"],
  a2_1_1: ["reservoir de combustible", "réservoir de combustible", "reservoir", "réservoir", "reservoir de carburant", "reservoir d'essence", "carburant", "combustible"],
  a2_1_2: ["systeme d'injection", "système d'injection", "injection", "injecteurs", "injecteur", "systeme injection"],
  a2_1_3: ["moteur thermique", "le moteur thermique", "moteur a combustion", "moteur essence"],
  a2_2_1: ["batterie", "la batterie", "batteries", "accumulateur", "batterie de traction"],
  a2_2_2: ["repartiteur de puissance", "répartiteur de puissance", "repartiteur", "répartiteur", "le repartiteur de puissance"],
  a2_2_3: ["moteur electrique", "moteur électrique", "le moteur electrique"],
  a2_3_1: ["generatrice", "génératrice", "la generatrice", "alternateur", "generateur", "génératrice électrique"],
  a2_4_1: ["chaine silencieuse", "chaîne silencieuse", "la chaine silencieuse", "arbre de sortie", "chaine", "chaîne"],
  a2_4_2: ["reducteur", "réducteur", "le reducteur", "reducteur de vitesse"],
  a2_4_3: ["differentiel", "différentiel", "le differentiel"],
  a2_4_4: ["roues motrices", "roues", "les roues motrices", "roue motrice", "les roues"],
  a3_1_1: ["alimenter", "alimentation"],
  a3_1_2: ["traiter", "traitement"],
  a3_1_3: ["distribuer", "distribution"],
  a3_1_4: ["alimenter", "alimentation"],
  a3_1_5: ["transmettre", "transmission", "agir", "action"],
  a3_1_6: ["convertir", "conversion"],
  a3_1_7: ["acquérir", "acquerir", "acquisition"],
  a3_1_8: ["acquérir", "acquerir", "acquisition"],
  a3_1_9: ["communiquer", "communication", "restituer"],
  a3_2_1: ["clavier", "le clavier"],
  a3_2_2: ["sonde de temperature exterieure", "sonde de température extérieure", "sonde exterieure", "sonde extérieure", "sonde de temperature", "capteur de temperature exterieure", "sonde te"],
  a3_2_3: ["sonde de temperature interieure", "sonde de température intérieure", "sonde interieure", "sonde intérieure", "sonde de temperature", "capteur de temperature interieure", "sonde ti"],
  a3_2_4: ["regulateur", "régulateur", "le regulateur"],
  a3_2_5: ["ecran retro-eclaire", "écran rétro-éclairé", "ecran", "écran", "ecran retroeclaire", "afficheur"],
  a3_3_1: ["armoire electrique", "armoire électrique", "reseau edf", "réseau EDF", "reseau electrique", "alimentation electrique", "edf"],
  a3_3_2: ["pilote des moteurs", "pilote des moteurs de la pompe a chaleur", "pilote", "pilote moteurs"],
  a3_3_3: ["pompe a chaleur", "pompe à chaleur", "la pompe a chaleur", "pac"],
  a3_3_4: ["plancher chauffant", "le plancher chauffant"],
  a3_3_5: ["capteur geothermique", "capteur géothermique", "le capteur geothermique", "capteur", "sonde geothermique"],
  a4_1_1: ["antenne receptrice", "antenne réceptrice", "antenne", "recepteur", "récepteur", "antenne de reception"],
  a4_1_2: ["boitier de commande", "boîtier de commande", "boitier", "platine de commande", "carte de commande", "unite de commande"],
  a4_1_3: ["feu clignotant", "clignotant", "feu", "feux clignotants", "gyrophare"],
  a4_2_1: ["telecommande", "télécommande", "la telecommande", "emetteur", "boitier telecommande"],
  a4_2_2: ["cellule optique", "cellules optiques", "cellule photoelectrique", "cellule", "capteur", "capteurs", "cellule photo-electrique"],
  a4_2_3: ["message", "messages", "signalisation", "signal lumineux", "information", "informations"],
  a4_3_1: ["reseau electrique", "réseau électrique", "energie electrique", "énergie électrique", "secteur", "electricite", "électricité", "reseau edf", "courant electrique", "230 v"],
  a4_3_2: ["alimentation electrique", "alimentation électrique", "alimentation", "transformateur", "bloc d'alimentation", "armoire electrique"],
  a4_3_3: ["boitier de commande", "boîtier de commande", "carte de puissance", "relais", "variateur", "platine de commande", "boitier"],
  a4_3_4: ["moteur a bras", "moteur à bras", "moteur", "moteurs", "motoreducteur", "moteur electrique"],
  a4_3_5: ["bras", "bras articule", "bras articulé", "systeme a bras", "mecanisme a bras", "reducteur", "bras de transmission"],
  a4_3_6: ["vantail", "vantaux", "le vantail", "les vantaux", "portail"],
};

// Saisies fausses, confusions plausibles et fautes de frappe tolérées : [saisie, score attendu]
const CASES = {
  a1_1_1: [["ACQUÉRIR", 1], ["aquérir", 1], ["traiter", 0], ["convertir", 0]],
  a1_1_3: [["communiqué", 1], ["agir", 0]],
  a1_2_2: [["distribuier", 1], ["convertir", 0]],
  a1_2_4: [["transmetre", 1], ["transformer", 0]],
  a1_2_5: [["agir", 1], ["agire", 0], ["transmettre", 0]],
  a1_3_1: [["les consignes", 1], ["compte rendu", 0]],
  a1_3_2: [["informations des capteurs", 1], ["consigne", 0], ["messages", 0]],
  a1_3_4: [["le secteur 230 V", 1], ["énergie mécanique", 0], ["moteur", 0]],
  a1_4_1: [["le moteur de la machinerie", 1], ["poulie", 0]],
  a1_4_2: [["boîte de réduction", 1], ["moteur actionnant des câbles", 0], ["cabine", 0], ["moteur", 0]],
  a1_4_3: [["la cabine", 1], ["contrepoids", 0]],
  a2_1_3: [["moteur à essence", 1], ["moteur électrique", 0], ["moteur", 0]],
  a2_2_3: [["moteur électrique", 1], ["moteur thermique", 0], ["génératrice", 0]],
  a2_3_1: [["alternateur", 1], ["moteur électrique", 0]],
  a2_4_1: [["arbre de sortie", 1], ["réducteur", 0]],
  a3_1_3: [["distribution", 1], ["convertir", 0]],
  a3_1_5: [["transmettre", 1], ["agir", 1], ["convertir", 0]],
  a3_2_2: [["sonde extérieure", 1], ["sonde TE", 1], ["sonde de température intérieure", 0], ["clavier", 0]],
  a3_2_3: [["sonde intérieure", 1], ["sonde TI", 1], ["sonde extérieure", 0], ["capteur géothermique", 0]],
  a3_3_5: [["capteur géothermique", 1], ["sonde de température", 0], ["capteur de température", 0]],
  a4_1_2: [["carte électronique", 1], ["microcontrôleur", 1], ["télécommande", 0], ["boîtier de télécommande", 0]],
  a4_2_1: [["l'émetteur", 1], ["antenne", 0]],
  a4_3_4: [["motoréducteur", 1], ["bras", 0]],
  a4_3_5: [["bras", 1], ["moteur à bras", 0], ["vantail", 0]],
  a4_3_6: [["les vantaux", 1], ["moteur", 0]],
};

test("configuration : 4 parties, 14 questions, 57 cases, 1 h, barème pondéré par la durée", () => {
  assert.deepEqual(EX.parts.map((p) => p.title), ["L'ascenseur", "Toyota Prius", "Chauffage géothermique", "Portail automatisé"]);
  assert.deepEqual(EX.parts.map((p) => p.minutes), [15, 12, 18, 15]);
  assert.deepEqual(EX.parts.map((p) => p.points), [15, 11, 19, 12]);
  assert.equal(EX.minutes, 60);
  assert.equal(Object.keys(QCFG).length, 57);
  for (const [id, c] of Object.entries(QCFG)) {
    assert.match(id, /^a[1-4]_\d+_\d+$/);
    assert.equal(c.part, id[1]);
    assert.equal(c.pts, 1);
    assert.equal(c.grader.type, "kw");
  }
  assert.deepEqual(Object.keys(REP).sort(), Object.keys(QCFG).sort());
  assert.deepEqual(Object.keys(SOURCE).sort(), Object.keys(QCFG).sort());
  assert.equal(EX.skcfg && Object.keys(EX.skcfg).length, 0);
});

test("réponse de référence : juste pour chacune des 57 cases", () => {
  for (const [id, ans] of Object.entries(REP)) assert.equal(ok(id, ans), 1, `${id} : ${ans}`);
});

test("réponses acceptées par l'exercice d'origine : toutes justes", () => {
  let n = 0;
  for (const [id, list] of Object.entries(SOURCE)) for (const ans of list) { assert.equal(ok(id, ans), 1, `${id} : ${ans}`); n++; }
  assert.ok(n > 250, `${n} formulations testées`);
});

test("confusions, mauvaises fonctions et fautes de frappe", () => {
  for (const [id, cases] of Object.entries(CASES)) for (const [ans, exp] of cases) assert.equal(ok(id, ans), exp, `${id} : ${ans}`);
});

test("une fonction de la chaîne n'est jamais acceptée à la place d'une autre", () => {
  const FONCTIONS = { a1_1_1: "acquérir", a1_1_2: "traiter", a1_1_3: "communiquer", a1_2_1: "alimenter",
                      a1_2_2: "distribuer", a1_2_3: "convertir", a1_2_4: "transmettre", a1_2_5: "agir" };
  for (const [id, juste] of Object.entries(FONCTIONS))
    for (const autre of Object.values(FONCTIONS)) assert.equal(ok(id, autre), autre === juste ? 1 : 0, `${id} : ${autre}`);
});

test("saisie vide refusée sans être notée", () => {
  for (const id of Object.keys(QCFG)) assert.equal(ok(id, "   "), "invalid", id);
});

// Étiquettes proposées dans chaque question (lues dans la page) : la réponse de référence en fait partie, et
// aucune autre étiquette de la liste n'est acceptée, sauf les doubles réponses prévues par la correction.
const ETIQUETTES = {};
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
for (const m of html.matchAll(/<div class="fast-q grp" id="(\w+)">([\s\S]*?)<div class="fast-foot">/g)) {
  const bank = [...m[2].matchAll(/class="etq"[^>]*>([^<]*)</g)].map((x) => unesc(x[1]));
  for (const x of m[2].matchAll(/data-q="(\w+)"/g)) ETIQUETTES[x[1]] = bank;
}
const DOUBLES = { a3_1_5: ["Agir", "Transmettre"] };  // plancher chauffant : Transmettre (Agir accepté)

test("étiquettes : la bonne est proposée, les autres de la liste sont refusées", () => {
  assert.deepEqual(Object.keys(ETIQUETTES).sort(), Object.keys(QCFG).sort());
  for (const [id, bank] of Object.entries(ETIQUETTES)) {
    assert.ok(bank.includes(REP[id]), `${id} : « ${REP[id]} » absente de la liste`);
    assert.equal(new Set(bank).size, bank.length, `${id} : doublon dans la liste`);
    const cases = Object.keys(QCFG).filter((k) => k.replace(/_\d+$/, "") === id.replace(/_\d+$/, "")).length;
    assert.ok(bank.length >= Math.min(cases + 2, 8), `${id} : pas assez d'intrus (${bank.length} étiquettes)`);
    const acceptees = bank.filter((b) => ok(id, b) === 1).sort();
    assert.deepEqual(acceptees, DOUBLES[id] || [REP[id]], id);
  }
});
