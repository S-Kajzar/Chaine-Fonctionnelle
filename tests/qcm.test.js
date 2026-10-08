// QCM « énergie et chaîne d'énergie » : chaque bonne réponse est acceptée, chaque autre proposition refusée.
//   node --test tests/qcm.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const code = html.slice(html.indexOf("/*GRADING-START*/"), html.indexOf("/*GRADING-END*/"));
const mod = { exports: {} };
new Function("module", code + "\nmodule.exports = Grading;")(mod);
const G = mod.exports;
const EX = JSON.parse(html.match(/window\.__EXOS__ = (.*?);<\/script>/)[1])["qcm-energie"];
// questions lues dans la page : identifiant de la case, réponse multiple ou non, repères des propositions
const Q = [...html.matchAll(/<div class="fast-q grp qcm" id="(\w+)" data-multi="(\d)">([\s\S]*?)<div class="fast-foot">/g)]
  .map((m) => ({ id: m[1] + "_1", multi: m[2] === "1", keys: [...m[3].matchAll(/data-k="([^"]+)"/g)].map((x) => x[1]) }));
const juste = (q) => { const g = EX.qcfg[q.id].grader; return (g.equals || g.value.map(String)); };
const ok = (q, v) => G.grade(v, EX.qcfg[q.id].grader).ok;

test("configuration : 6 parties, 76 questions d'un point, 1 h 20", () => {
  assert.equal(Q.length, 76);
  assert.equal(Object.keys(EX.qcfg).length, 76);
  assert.deepEqual(EX.parts.map((p) => p.title), ["Conversions et sources d'énergie", "Unités, puissance et rendement",
    "Signaux et moteur à courant continu", "Énergie thermique", "Photovoltaïque et batteries",
    "Fonctions de la chaîne d'énergie et stockage"]);
  assert.equal(EX.minutes, 80);
  assert.equal(EX.parts.reduce((s, p) => s + p.points, 0), 76);
});

test("réponse unique : chaque bonne proposition acceptée, toutes les autres refusées", () => {
  let n = 0;
  for (const q of Q.filter((x) => !x.multi)) {
    const bons = juste(q);
    for (const k of q.keys) { assert.equal(ok(q, k), bons.includes(k.toLowerCase()), `${q.id} : ${k}`); n++; }
    assert.equal(ok(q, q.keys.join(",")), false, `${q.id} : tout cocher`);
  }
  assert.ok(n > 300, `${n} propositions testées`);
});

test("réponses multiples : il faut toutes les bonnes, et elles seules", () => {
  const multi = Q.filter((x) => x.multi);
  assert.ok(multi.length >= 1);
  for (const q of multi) {
    const bons = juste(q);
    assert.ok(ok(q, bons.join(",")), q.id);
    assert.equal(ok(q, bons.slice(1).join(",")), false, `${q.id} : incomplet`);
    const intrus = q.keys.find((k) => !bons.includes(k));
    assert.equal(ok(q, bons.concat(intrus).join(",")), false, `${q.id} : avec un intrus`);
  }
});

test("corrections de la source", () => {
  const txt = html.replace(/data:[^"]+/g, "");  // sans les images (base64)
  assert.doesNotMatch(txt, /\d\s?K(W|J)\b/, "kilo s'écrit k minuscule");
  assert.doesNotMatch(txt, /note de livraison/i, "plus de renvoi à une note extérieure");
  const cal = Q.find((q) => /La Calorie/.test(html.slice(html.indexOf(`id="${q.id.slice(0, -2)}"`)).slice(0, 400)));
  assert.deepEqual(juste(cal).sort(), ["4", "7"], "Q15 : « la chaleur » acceptée");
  assert.equal((html.match(/Si elle fournit 40 A/g) || []).length, 1, "doublon Q45 / Q46 retiré");
});
