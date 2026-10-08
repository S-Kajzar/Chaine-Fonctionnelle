// Tests navigateur (Playwright + Chromium) : accueil, cours, parcours entraînement et examen, documents, formulaire.
//   NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const fs = require("node:fs");
const { chromium } = require("playwright");
const REP = require("./reponses.js");

const FILE = path.join(__dirname, "..", "index.html");
const URL = "file://" + FILE;
const FORM = "file://" + path.join(__dirname, "..", "formulaire.html");
const EX = "?ex=chaines-information-energie";
// questions à plusieurs cases : identifiant du groupe → identifiants des cases
const GROUPES = {};
for (const id of Object.keys(REP)) (GROUPES[id.replace(/_\d+$/, "")] ||= []).push(id);
let browser;

test.before(async () => { browser = await chromium.launch(); });
test.after(async () => { await browser.close(); });

async function open(url, viewport) {
  const context = await browser.newContext({ viewport: viewport || { width: 1366, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("dialog", (d) => d.accept());
  await page.goto(url.startsWith("file:") ? url : URL + url);
  return { context, page, errors };
}
const text = (page, sel) => page.locator(sel).first().innerText();
const set = (page, sel, v) => page.locator(sel).evaluate((e, x) => { e.value = x; e.dispatchEvent(new Event("input")); }, v);
// une case se remplit comme le fait l'élève : toucher l'étiquette, puis la case
async function poser(page, id, etiquette) {
  const gid = id.replace(/_\d+$/, "");
  await page.locator(`#${gid} .bank`).getByRole("button", { name: etiquette, exact: true }).click();
  await page.click(`#dz-${id}`);
}
async function remplir(page, gid, valeurs) {
  for (const id of GROUPES[gid]) await poser(page, id, valeurs[id] !== undefined ? valeurs[id] : REP[id]);
}
const valeur = (page, id) => page.locator(`#in-${id}`).inputValue();

test("accueil : cartes illustrées à mots-clés (trois cours, formulaire, exercices, études de cas)", async () => {
  const { context, page, errors } = await open("");
  assert.ok(await page.locator("body.hub").count());
  assert.ok(await page.isVisible("#home"));
  assert.ok(!(await page.isVisible("main.page")));
  assert.ok(!(await page.isVisible(".banner")));
  assert.match(await text(page, "#home h1"), /Chaîne fonctionnelle/);
  const card = (sel) => page.locator(sel).evaluateAll((cs) => cs.map((c) => [
    c.querySelector(".mc-tag").textContent.trim(), c.querySelector("h3").textContent,
    c.querySelector("a") ? c.querySelector("a").getAttribute("href") : null]));
  assert.deepEqual(await card(".cours-grid .mode-card"), [
    ["Cours 1 Niveau 1", "La chaîne fonctionnelle", "?ex=cours-chaine-fonctionnelle"],
    ["Cours 2 Niveau 2", "Chaîne d'énergie des produits", "?ex=cours-chaine-energie"],
    ["Cours 3 Niveau 2", "Chaîne d'information des produits", "?ex=cours-chaine-information"]]);
  // le formulaire est une carte comme les autres ; ses exercices de calcul sont rangés avec les exercices
  assert.deepEqual(await card(".form-grid .mode-card"), [
    ["Formulaire", "Formulaire de la chaîne de puissance", "formulaire.html#formulaire"]]);
  assert.deepEqual(await card(".exo-grid .mode-card"), [
    ["Exercice 1.1 Niveau 1", "Chaînes d'information et d'énergie", "?ex=chaines-information-energie"],
    ["QCM 2.1 Niveau 2", "QCM : énergie et chaîne d'énergie", "?ex=qcm-energie"],
    ["Calculs", "Exercices de calcul", "formulaire.html#exercices"]]);
  assert.deepEqual(await page.locator("#home h2").allInnerTexts(), ["Les cours", "Le formulaire", "Les exercices", "Études de cas"]);
  // chaque carte : une vignette chargée, 3 à 5 mots-clés, aucun paragraphe de texte
  const cartes = await page.locator("#home .carte-v").evaluateAll((cs) => cs.map((c) => ({
    img: !!c.querySelector("img.cv-img") ? c.querySelector("img.cv-img").naturalWidth : -1,
    mots: c.querySelectorAll(".cv-mots li").length, p: c.querySelectorAll("p:not(.etat)").length })));
  assert.equal(cartes.length, 8);
  for (const c of cartes) { assert.ok(c.mots >= 3 && c.mots <= 5, JSON.stringify(c)); assert.equal(c.p, 0); }
  assert.equal(cartes.filter((c) => c.img > 0).length, 8, "toutes les cartes illustrées");
  // toutes les cartes ont la même taille, d'une rubrique à l'autre
  const tailles = await page.locator("#home .carte-v").evaluateAll((cs) => cs.map((c) => [Math.round(c.offsetWidth), c.offsetHeight]));
  for (const [w, h] of tailles) { assert.equal(w, tailles[0][0]); assert.ok(Math.abs(h - tailles[0][1]) <= 1, JSON.stringify(tailles)); }
  assert.deepEqual(await card(".etude-grid .mode-card"), [["Étude 1", "Étude de cas", null]]);
  assert.match(await text(page, ".etude-grid .etat"), /En cours d'édition/);
  assert.equal(await page.locator("#home .btn-mode").count(), 0);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  const src = fs.readFileSync(FILE, "utf8").replace(/data:[^"]+/g, "");
  assert.doesNotMatch(src, /\b(BTS|STI2D|bac(calaur[ée]at)?|session \d|[ée]preuve|acad[ée]mie|sujet z[ée]ro|brevet)\b/i);
  assert.deepEqual(errors, []);
  await context.close();
});

test("adresse inconnue : retour à l'accueil", async () => {
  const { context, page, errors } = await open("?ex=inconnu");
  assert.ok(await page.locator(".cours-grid").count());
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 1 (niveau 1) : animation du portail, scénarios, clavier, plein écran, cartes, jeux, quiz", async () => {
  const { context, page, errors } = await open("?ex=cours-chaine-fonctionnelle");
  assert.match(await text(page, "#home .home-head"), /Cours 1[\s\S]*Niveau 1[\s\S]*La chaîne fonctionnelle/);
  assert.equal(await page.locator(".cours-sec").count(), 4);
  assert.match(await text(page, "#ex-step"), /Étape 1 \/ 13/);
  for (let i = 0; i < 3; i++) await page.click("#btn-next");
  assert.match(await text(page, "#ex-title"), /Traiter : la carte électronique décide/);
  assert.ok(await page.locator("#b-tra.on").count());
  // second scénario, puis pilotage au clavier après un clic sur la scène
  await page.click(".scenarios [data-sc='1']");
  assert.match(await text(page, "#ex-step"), /Étape 1 \/ 8/);
  await page.click("#scene", { position: { x: 300, y: 150 } });
  await page.keyboard.press("ArrowRight");
  assert.match(await text(page, "#ex-step"), /Étape 2 \/ 8/);
  // plein écran : le scénario et l'étape sont conservés, Échap ramène au cours
  await page.click("#cp-fs");
  assert.ok(await page.locator(".cp.cp-full").count());
  assert.deepEqual(await page.evaluate(() => { const s = window.__anim__.state(); return [s.sc, s.idx]; }), [1, 1]);
  await page.keyboard.press("Escape");
  assert.equal(await page.locator(".cp.cp-full").count(), 0);
  await page.click(".carte >> nth=4");
  assert.match(await text(page, ".carte >> nth=4"), /relais/);
  for (const id of ["#jeu-circule", "#jeu-compo"]) {
    const lignes = page.locator(id + " .jeu-l");
    const n = await lignes.count();
    for (let i = 0; i < n; i++) {
      const ok = await lignes.nth(i).getAttribute("data-ok");
      await lignes.nth(i).locator(`button[data-v="${i === 0 ? (ok === "info" ? "ener" : "traiter") : ok}"]`).click();
    }
    assert.equal((await text(page, id + " .jeu-s")).trim(), `${n - 1} / ${n}`);
    assert.ok(await page.locator(id + " .jeu-l >> nth=0 >> .pick-good").count());
  }
  const q = await page.locator(".quiz-q").count();
  for (let i = 0; i < q; i++) {
    const fs_ = page.locator(".quiz-q").nth(i);
    await fs_.locator(`input[value="${await fs_.getAttribute("data-ok")}"]`).check();
  }
  assert.equal((await text(page, "#qz-score")).trim(), `${q} / ${q}`);
  assert.equal((await text(page, "#qz-stars")).trim(), "★★★");
  await page.click(".cours-foot a[href='?ex=chaines-information-energie']");
  await page.waitForURL(/\?ex=chaines-information-energie$/);
  assert.equal(await page.locator("#home .btn-mode").count(), 2);
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 2 (niveau 2) : figures animées, fiches, oscilloscope, hacheur, transmissions, puissances, rendements", async () => {
  const { context, page, errors } = await open("?ex=cours-chaine-energie");
  assert.match(await text(page, "#home .home-head"), /Cours 2[\s\S]*Niveau 2[\s\S]*Chaîne d'énergie des produits/);
  assert.equal(await page.locator(".cours-sec").count(), 10);
  // pas de tableau de compétences : le cours ne vise pas une seule filière
  assert.doesNotMatch(await text(page, ".c2-fiche"), /Compétences|CO\d\.\d/);
  // figure 1 : un flux s'anime ; figure 2 : un bloc explique son rôle
  await page.click(".ce-f1-b[data-f='f1-commandes']");
  assert.match(await text(page, "#ce-f1-txt"), /commande la chaîne de puissance/);
  assert.ok(await page.locator("#ce-f1 .ce-dot").count() > 0);
  await page.click("#ce-f2-go");
  assert.equal(await page.locator("#ce-f2 .f2-fl.on").count(), 5);
  await page.click("#ce-f2 .ce-blk[data-b='dist']");
  assert.match(await text(page, "#ce-f2-txt"), /préactionneurs/);
  // fiches : 25 composants, photo recopiée dans la fiche ouverte
  assert.equal(await page.locator(".fiche-c").count(), 25);
  await page.click(".cata[data-cata='conv'] .cata-it[data-fiche='moteur-asynchrone']");
  assert.match(await text(page, ".cata[data-cata='conv'] .fiche-c:not([hidden])"), /Moteur asynchrone[\s\S]*2 des 3 phases/);
  assert.ok(await page.locator(".cata[data-cata='conv'] .fiche-c:not([hidden]) .fc-ph img").evaluate((i) => i.src.startsWith("data:image/png")));
  // oscilloscope : triphasé, lecture au survol
  await page.check("input[name=ce-src][value=tri]");
  assert.match(await text(page, "#ce-osc-out"), /230 V[\s\S]*400 V[\s\S]*50 Hz/);
  assert.equal(await page.locator("#ce-osc-leg span").count(), 3);
  const box = await page.locator("#ce-osc").boundingBox();
  await page.mouse.move(box.x + box.width * 0.3, box.y + box.height * 0.5);
  assert.match(await text(page, "#ce-osc-tip"), /t = [\d,]+ ms[\s\S]*V1[\s\S]*V2[\s\S]*V3/);
  await page.check("input[name=ce-src][value=eol]");
  await set(page, "#ce-vent", "5");
  assert.match(await text(page, "#ce-osc-out"), /20 V[\s\S]*10 Hz[\s\S]*100 ms/);
  // hacheur : 75 % de 36 V, polarités inversées
  await set(page, "#ce-alpha", "75");
  await page.check("#ce-inv");
  assert.equal(await text(page, "#ce-h-u"), "27,0 V");
  assert.match(await text(page, "#ce-h-n"), /2\s250 tr\/min/);
  assert.match(await text(page, "#ce-h-s"), /inverse/);
  // transmissions
  await set(page, "#ce-ze", "20"); await set(page, "#ce-zs", "60"); await set(page, "#ce-ne", "1500");
  assert.equal(await text(page, "#ce-e-r"), "0,333");
  assert.equal(await text(page, "#ce-e-n"), "500 tr/min");
  assert.equal(await text(page, "#ce-e-c"), "30 N·m");
  await page.click(".ce-tab[data-m=cre]");
  await set(page, "#ce-r", "20"); await set(page, "#ce-nr", "60");
  assert.equal(await text(page, "#ce-c-w"), "6,28 rad/s");
  assert.equal(await text(page, "#ce-c-v"), "0,126 m/s");
  await page.click(".ce-tab[data-m=vis]");
  await set(page, "#ce-p", "4"); await set(page, "#ce-nv", "300");
  assert.match(await text(page, "#ce-v-v"), /1\s200 mm\/min/);
  assert.equal(await text(page, "#ce-v-s"), "20 mm/s");
  // puissances, énergie, effort et flux
  await page.click("#ce-pu-svg .pu-pt >> nth=5");
  assert.match(await text(page, "#ce-pu-txt"), /Éolienne : 2 MW, soit la puissance de 20\s000 téléviseurs/);
  await page.click("#ce-en .ce-presets button >> nth=0");
  assert.deepEqual([await text(page, "#ce-en-wh"), await text(page, "#ce-en-kwh"), await text(page, "#ce-en-j")],
    ["6 000 Wh", "6 kWh", "21,6 MJ"]);
  await page.click(".ef-table tbody tr[data-ef=rot]");
  assert.match(await text(page, "#ce-ef-p"), /1\s000 W/);
  assert.match(await text(page, "#ce-ef-w"), /955 tr\/min/);
  // rendements : chargeur, puis chaîne de la trottinette
  await set(page, "#ce-ch-l", "30");
  assert.equal(await text(page, "#ce-ch-u"), "7 W");
  assert.match(await text(page, "#ce-ch-e"), /70 %/);
  assert.match(await text(page, "#ce-gl-e"), /0,654/);
  await set(page, "#ce-eta2", "0.6");
  assert.match(await text(page, "#ce-gl-e"), /0,462/);
  assert.match(await text(page, "#ce-gl-m"), /Convertir \(0,60\)/);
  assert.equal(await page.locator("#ce-rd-svg .rd-b").count(), 11);
  // autonomie de la batterie de la trottinette
  await page.click("#ce-au .ce-presets button >> nth=2");
  assert.deepEqual([await text(page, "#ce-au-t"), await text(page, "#ce-au-m"), await text(page, "#ce-au-e")],
    ["0,78 h", "47 min", "281 Wh"]);
  for (const id of ["#jeu-conv", "#jeu-syn"]) {
    const lignes = page.locator(id + " .jeu-l");
    const n = await lignes.count();
    for (let i = 0; i < n; i++) {
      const ok = await lignes.nth(i).getAttribute("data-ok");
      await lignes.nth(i).locator(`button[data-v="${ok}"]`).click();
    }
    assert.equal((await text(page, id + " .jeu-s")).trim(), `${n} / ${n}`);
  }
  const q = await page.locator(".quiz-q").count();
  for (let i = 0; i < q; i++) {
    const fs_ = page.locator(".quiz-q").nth(i);
    await fs_.locator(`input[value="${await fs_.getAttribute("data-ok")}"]`).check();
  }
  assert.equal((await text(page, "#qz-score")).trim(), "10 / 10");
  // impression : toutes les fiches sont imprimées
  await page.emulateMedia({ media: "print" });
  assert.equal(await page.locator(".fiche-c:visible").count(), 25);
  await page.emulateMedia({ media: "screen" });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 3 : machine à café, blocs internes, capteurs, acquisition, CAN, programme, communication, encodage", async () => {
  const { context, page, errors } = await open("?ex=cours-chaine-information");
  assert.ok(await page.locator("body.cours-page.page-cours-chaine-information").count());
  assert.match(await text(page, "#home h1"), /Chaîne d'information des produits/);
  assert.equal(await page.locator(".cours-nav a").count(), 8);
  // machine à café : six étapes ; le café coule à l'étape 5
  for (let i = 0; i < 5; i++) await page.click("#ci-cafe-next");
  assert.doesNotMatch(await text(page, ".c2-fiche"), /Compétences|CO\d\.\d/);
  assert.match(await text(page, "#ci-cafe-step"), /Étape 5 sur 6[\s\S]*café coule/);
  assert.ok(await page.locator("#cf-pout.on").count());
  await page.uncheck("#ci-cafe-det");
  await page.click("#ci-cafe-next");
  assert.ok(await page.locator("#cb-ci.on").count(), "chaîne d'information d'un seul bloc");
  // diagramme de blocs internes
  await page.click("#ib-uc rect");
  assert.match(await text(page, "#ci-ibd-info"), /Microcontrôleur[\s\S]*Traiter[\s\S]*Chaîne d'information/);
  assert.equal(await page.locator("#ci-ibd-svg .ci-fl.on").count(), 6);
  // laboratoire : 47,5 °C au-dessus d'un seuil de 30 °C
  await page.click("#ci-lab-play");
  await page.uncheck("#ci-lab-auto");
  await set(page, "#ci-lab-t", "47.5");
  assert.match(await text(page, "#ci-lab-o1"), /^1/);
  assert.equal(await text(page, "#ci-lab-o2"), "475 mV");
  assert.equal(await text(page, "#ci-lab-o3"), "0111011011");
  assert.match(await text(page, "#ci-lab-o4"), /475 → 47,5 °C/);
  // chaîne d'acquisition : gain trop fort, puis bon réglage
  await set(page, "#ci-aq-g", "800");
  assert.match(await text(page, "#ci-aq-v"), /écrêté/);
  await set(page, "#ci-aq-g", "200"); await set(page, "#ci-aq-f", "120"); await set(page, "#ci-aq-n", "8");
  assert.match(await text(page, "#ci-aq-v"), /Bon réglage/);
  // amplification : exemple du cours
  assert.equal(await text(page, "#ci-amp-s"), "2,60 V");
  // CAN 3 bits, 8 V, 3,2 V en entrée
  assert.match(await text(page, "#ci-can-q"), /8 \/ 8 = 1,000 V/);
  assert.equal(await text(page, "#ci-can-d"), "3");
  assert.equal(await text(page, "#ci-can-b"), "011");
  await set(page, "#ci-can-v", "1");
  assert.match(await text(page, "#ci-can-d"), /^7/);
  await set(page, "#ci-can-n", "8"); await page.selectOption("#ci-can-r", "5");
  assert.match(await text(page, "#ci-can-q"), /5 \/ 256 = 19,5 mV/);
  assert.match(await text(page, "#ci-can-d"), /^255/);
  // programme : bouton maintenu, la LED s'allume par le programme ; relâché, elle s'éteint
  await page.locator("#ci-bp").dispatchEvent("pointerdown");
  await page.waitForFunction(() => document.getElementById("ci-led").classList.contains("on"));
  assert.ok(await page.locator("#ci-an-on.on, #ci-an-test.on, #ci-an-lire.on").count());
  await page.locator("#ci-bp").dispatchEvent("pointerup");
  await page.waitForFunction(() => !document.getElementById("ci-led").classList.contains("on"));
  await page.click("#ci-tab-python");
  assert.ok(await page.isVisible("#ci-code-python"));
  assert.ok(!(await page.isVisible("#ci-code-pseudo")));
  await page.click("#ci-pas");
  assert.equal(await page.locator("#ci-code-python .ci-cl.on").count() > 0, true);
  // restitution et trame envoyée
  await page.click("#ci-voy-b");
  assert.ok(await page.locator("#ci-voy.on").count());
  await page.fill("#ci-lcd-in", "I2D");
  assert.equal(await text(page, "#ci-lcd-2"), "49 32 44");
  await page.check("input[name=ci-net][value=eth]");
  assert.match(await page.locator("#ci-net-proto").textContent(), /Ethernet : liaison filaire/);
  await page.fill("#ci-net-msg", "OK");
  await page.click("#ci-net-go");
  await page.waitForFunction(() => /OK/.test(document.getElementById("ci-net-rx").textContent));
  assert.match(await page.locator("#ci-net-rx").textContent(), /« OK » \(16 bits\)/);
  // octet, hexadécimal, ASCII
  assert.equal(await text(page, "#ci-oct-hex"), "(B5)₁₆");
  await page.click("#ci-oct [data-v='123']");
  assert.equal(await text(page, "#ci-oct-bin"), "(01111011)₂");
  await page.click(".ci-bit[data-w='128']");
  assert.equal(await text(page, "#ci-oct-dec"), "(251)₁₀");
  assert.equal(await page.locator("#ci-asc-out .ci-ac").count(), 3);
  assert.match(await text(page, "#ci-asc-out"), /01001001[\s\S]*00110010[\s\S]*01000100/);
  assert.equal(await page.locator("#ci-asc-grid tr.hl").count(), 3);
  await page.fill("#ci-asc-in", "é");
  assert.match(await text(page, "#ci-asc-out"), /hors ASCII/);
  // défi : on lit la question, on répond juste
  const qt = await text(page, "#ci-defi-q");
  const m = qt.match(/\(([0-9A-F]+)\)(₂|₁₀|₁₆)/);
  const n = parseInt(m[1], { "₂": 2, "₁₀": 10, "₁₆": 16 }[m[2]]);
  const rep = /binaire/.test(qt) ? n.toString(2).padStart(8, "0") : /hexadécimal/.test(qt) ? n.toString(16).toUpperCase() : String(n);
  await page.fill("#ci-defi-in", rep);
  await page.click("#ci-defi-ok");
  assert.match(await text(page, "#ci-defi-v"), /Juste/);
  // jeux et quiz
  for (const jeu of ["#jeu-liaisons", "#jeu-fct-i", "#jeu-sig"]) {
    const lignes = page.locator(`${jeu} .jeu-l`);
    for (let i = 0; i < await lignes.count(); i++) {
      const l = lignes.nth(i);
      await l.locator(`button[data-v="${await l.getAttribute("data-ok")}"]`).click();
    }
    const n = await lignes.count();
    assert.equal(await text(page, `${jeu} .jeu-s`), `${n} / ${n}`, jeu);
  }
  const qz = await page.locator(".quiz-q").count();
  for (let i = 0; i < qz; i++) {
    const f = page.locator(".quiz-q").nth(i);
    await f.locator(`input[value="${await f.getAttribute("data-ok")}"]`).check();
  }
  assert.equal((await text(page, "#qz-score")).trim(), "10 / 10");
  await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
  await page.emulateMedia({ media: "print" });
  assert.ok(await page.isVisible("#ci-asc-grid"), "table ASCII imprimée");
  await page.emulateMedia({ media: "screen" });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("exercice 1.1 en entraînement : questions à plusieurs cases, sujet entièrement juste = 20/20", async () => {
  const { context, page, errors } = await open(EX);
  assert.match(await text(page, "#home .home-head"), /Exercice 1\.1[\s\S]*Niveau 1[\s\S]*Chaînes d'information et d'énergie/);
  await page.click("[data-mode=training]");
  assert.match(await text(page, ".cartouche"), /14 questions, 57 cases notées, réparties en 4 parties/);
  assert.match(await text(page, ".consignes"), /Des étiquettes, pas de calcul/);
  // groupe vide, puis groupe incomplet : confirmation demandée
  await page.click("#a1_1 .btn-fast");
  assert.match(await text(page, "#a1_1 .q-msg"), /Complète au moins une case/);
  await poser(page, "a1_1_1", "Acquérir");
  await poser(page, "a1_1_2", "Traiter");
  await page.click("#a1_1 .btn-fast");
  assert.match(await text(page, "#a1_1 .btn-fast"), /Valider quand même \(1 case vide\)/);
  await page.click("#a1_1 .btn-fast");
  assert.match(await text(page, "#a1_1 .q-status"), /2 cases justes sur 3/);
  assert.equal(await text(page, "#a1_1 .btn-fast"), "Réponses validées");
  assert.ok(await page.locator("#in-a1_1_3").isDisabled());
  assert.ok(await page.locator("#dz-a1_1_3").isDisabled());
  assert.equal(await page.locator("#a1_1 .etq:not([disabled])").count(), 0, "étiquettes verrouillées");
  assert.ok(await page.isVisible("#a1_1 .q-expl"));
  assert.match(await text(page, "#a1_1 .grp-sol"), /Repère 5[\s\S]*Communiquer/);
  assert.match(await text(page, "#score-val"), /13,3/);
  // tout le reste juste
  for (const gid of Object.keys(GROUPES)) {
    if (gid === "a1_1") continue;
    await remplir(page, gid, {});
    await page.click(`#${gid} .btn-fast`);
    const n = GROUPES[gid].length;
    assert.match(await text(page, `#${gid} .q-status`), new RegExp(`${n} cases? justes? sur ${n}`), gid);
  }
  // partie 1 : 14/15 → 18,67/20 (15 min) ; parties 2 à 4 : 20/20 → 19,7
  assert.equal((await text(page, "#recap .final-note")).trim(), "19,7/20");
  assert.match(await text(page, "#recap-body"), /Partie 1 — L'ascenseur[\s\S]*14,0 \/ 15[\s\S]*18,7/);
  assert.deepEqual(errors, []);
  await context.close();

  // second passage : tout juste dès le départ
  const b = await open(EX);
  await b.page.click("[data-mode=training]");
  for (const gid of Object.keys(GROUPES)) { await remplir(b.page, gid, {}); await b.page.click(`#${gid} .btn-fast`); }
  assert.equal((await text(b.page, "#recap .final-note")).trim(), "20,0/20");
  assert.equal((await text(b.page, "#score-val")).replace(/\s/g, ""), "20,0/20");
  assert.deepEqual(b.errors, []);
  await b.context.close();
});

test("exercice 1.1 en examen : rien ne filtre avant la remise, y compris à l'impression ; remise en deux temps", async () => {
  const { context, page, errors } = await open(EX);
  await page.click("[data-mode=exam]");
  assert.ok(!(await page.isVisible("#score-val")));
  assert.ok(!(await page.isVisible("#a1_1 .btn-fast")));
  for (const gid of Object.keys(GROUPES)) if (gid !== "a1_1") await remplir(page, gid, { a4_3_6: "Le moteur à bras" });
  assert.match(await text(page, "#score-count"), /54 réponse\(s\) renseignée\(s\) sur 57/);
  await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
  await page.emulateMedia({ media: "print" });
  assert.ok(await page.isVisible(".print-nograde"));
  assert.ok(!(await page.isVisible(".print-note-line")));
  assert.ok(!(await page.isVisible("#a2_1 .q-expl")));
  assert.ok(!(await page.isVisible("#recap-graded")));
  await page.emulateMedia({ media: "screen" });
  await page.click("#exam-submit");
  assert.match(await text(page, "#exam-warn"), /3 réponse\(s\) encore vide\(s\)/);
  await page.click("#exam-submit");
  assert.ok(await page.locator("body.graded").count());
  assert.match(await text(page, "#a1_1 .q-status"), /0 case juste sur 3/);
  assert.match(await text(page, "#a4_3 .q-status"), /5 cases justes sur 6/);
  assert.ok(await page.locator("#in-a4_3_6").evaluate((i) => i.closest(".sol").classList.contains("is-ko")));
  const t1 = await text(page, "#timer-val");
  await page.waitForTimeout(1300);
  assert.equal(await text(page, "#timer-val"), t1, "chronomètre arrêté");
  // P1 : 12/15 → 16 ; P2, P3 : 20 ; P4 : 11/12 → 18,33 → (15×16 + 12×20 + 18×20 + 15×18,33) / 60 = 18,6
  assert.equal((await text(page, "#recap .final-note")).trim(), "18,6/20");
  await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
  await page.emulateMedia({ media: "print" });
  assert.ok(await page.isVisible(".print-note-line"));
  assert.ok(await page.isVisible("#a2_1 .q-expl"));
  assert.deepEqual(errors, []);
  await context.close();
});

test("étiquettes : toucher puis toucher, glisser-déposer, échanger, vider", async () => {
  const { context, page, errors } = await open(EX);
  await page.click("[data-mode=training]");
  assert.match(await text(page, ".consignes"), /glisse[\s\S]*touche/);
  assert.equal(await page.locator("#a1_1 .bank .etq").count(), 8);
  // toucher une case vide sans étiquette choisie : aide
  await page.click("#dz-a1_1_1");
  assert.match(await text(page, "#a1_1 .q-msg"), /Choisis d'abord une étiquette/);
  // toucher une étiquette la sélectionne ; la retoucher ou Échap la désélectionne
  const acq = page.locator("#a1_1 .bank").getByRole("button", { name: "Acquérir", exact: true });
  await acq.click();
  assert.equal(await acq.getAttribute("aria-pressed"), "true");
  assert.ok(await page.locator("#a1_1.picking").count());
  await page.keyboard.press("Escape");
  assert.equal(await acq.getAttribute("aria-pressed"), "false");
  // au clavier : Entrée sur l'étiquette, puis Entrée sur la case
  await acq.focus(); await page.keyboard.press("Enter");
  await page.focus("#dz-a1_1_1"); await page.keyboard.press("Enter");
  assert.equal(await valeur(page, "a1_1_1"), "Acquérir");
  assert.match(await page.locator("#dz-a1_1_1").getAttribute("class"), /filled/);
  // glisser-déposer une étiquette sur une case
  await page.dragAndDrop("#a1_1 .etq >> text=Communiquer", "#dz-a1_1_2");
  assert.equal(await valeur(page, "a1_1_2"), "Communiquer");
  // une étiquette sert plusieurs fois
  await page.dragAndDrop("#a1_1 .etq >> text=Communiquer", "#dz-a1_1_3");
  assert.equal(await valeur(page, "a1_1_3"), "Communiquer");
  // glisser d'une case à l'autre : les deux étiquettes s'échangent
  await page.dragAndDrop("#dz-a1_1_1", "#dz-a1_1_2");
  assert.deepEqual([await valeur(page, "a1_1_1"), await valeur(page, "a1_1_2")], ["Communiquer", "Acquérir"]);
  // ramener une étiquette dans la liste, ou toucher une case remplie : la case se vide
  await page.dragAndDrop("#dz-a1_1_1", "#a1_1 .bank-t");
  assert.equal(await valeur(page, "a1_1_1"), "");
  assert.equal(await text(page, "#dz-a1_1_1"), "case vide");
  await page.click("#dz-a1_1_3");
  assert.equal(await valeur(page, "a1_1_3"), "");
  // pas de dépôt dans une autre question
  await page.dragAndDrop("#a1_1 .etq >> text=Traiter", "#dz-a1_2_1");
  assert.equal(await valeur(page, "a1_2_1"), "");
  // validation : 1 case juste (Acquérir mal placée en repère 4), cases verrouillées
  await poser(page, "a1_1_1", "Acquérir");
  await page.click("#a1_1 .btn-fast"); await page.click("#a1_1 .btn-fast");
  assert.match(await text(page, "#a1_1 .q-status"), /1 case juste sur 3/);
  await page.dragAndDrop("#a1_2 .etq >> text=Agir", "#dz-a1_1_3");
  assert.equal(await valeur(page, "a1_1_3"), "");
  // téléphone : la liste et les cases tiennent dans l'écran
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("partie 2, RAV4 : schéma animé, chaîne synchronisée, fonctions dévoilées après correction", async () => {
  const { context, page, errors } = await open(EX);
  await page.click("[data-mode=training]");
  assert.match(await text(page, "#t-partie-2"), /Toyota RAV4 hybride/);
  assert.ok(await page.locator("#partie-2 img[src^='data:image/jpeg']").count());
  const actifs = () => page.locator("#rv-flows .rv-flow.on").evaluateAll((fs) => fs.length);
  const blocs = () => page.locator("#rv-c-blocks .rv-blk.act").evaluateAll((bs) => bs.map((b) => b.id.slice(5)));
  // démarrage : branche électrique seule, moteur thermique arrêté
  assert.match(await text(page, "#rv-mode-d"), /Démarrage/);
  assert.deepEqual(await blocs(), ["1", "2", "3", "8", "9", "10", "11", "T"]);
  assert.match(await text(page, "#rv-etat"), /Moteur thermique\s*arrêté[\s\S]*se décharge/i);
  // croisière : branche thermique et génératrice, la batterie se recharge (flux inversé)
  await page.click("#rv-demo [data-m=croisiere]");
  assert.ok(await page.locator("#rv-c-eng.rv-eng-on").count());
  assert.deepEqual((await blocs()).sort(), ["1", "10", "11", "2", "4", "5", "6", "7", "8", "9", "T"]);
  assert.match(await text(page, "#rv-etat"), /en marche[\s\S]*se recharge/);
  // freinage : le flux remonte des roues vers la batterie
  await page.click("#rv-demo [data-m=frein]");
  assert.ok(await page.locator("#rv-flows .rv-flow.on.rev").count() >= 5);
  assert.equal(await page.locator("#rv-c-eng.rv-eng-on").count(), 0);
  await page.click("#rv-demo [data-m=arret]");
  assert.equal(await actifs(), 0);
  // version 4 roues motrices
  assert.ok(!(await page.isVisible("#rv-c-mgr")));
  await page.check("#rv-awd");
  await page.click("#rv-demo [data-m=accel]");
  assert.ok(await page.isVisible("#rv-c-mgr"));
  assert.match(await text(page, "#rv-etat"), /Roues arrière\s*motrices/i);
  // un composant touché : son rôle, sans sa fonction avant la correction
  await page.click("#rv-c-mg1 .rv-bx");
  assert.match(await text(page, "#rv-info"), /Génératrice[\s\S]*électricité/);
  assert.equal(await page.locator("#rv-info .rv-fn-tag").count(), 0);
  assert.ok(await page.locator("#rv-fns").isDisabled());
  for (const gid of ["a2_1", "a2_2", "a2_3", "a2_4"]) { await remplir(page, gid, {}); await page.click(`#${gid} .btn-fast`); }
  await page.waitForFunction(() => !document.getElementById("rv-fns").disabled);
  await page.check("#rv-fns");
  await page.click("#rv-c-mg1 .rv-bx");
  assert.match(await text(page, "#rv-info .rv-fn-tag"), /CONVERTIR/);
  // trajet automatique
  await page.click("#rv-play");
  assert.match(await text(page, "#rv-play"), /Arrêter/);
  await page.click("#rv-play");
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("QCM : propositions, correction du gabarit, 20/20 en entraînement, examen avec réponses vides", async () => {
  // bonnes propositions de chaque question, lues dans la configuration du moteur
  const bons = (page) => page.evaluate(() => [...document.querySelectorAll(".qcm")].map((q) => {
    const g = window.__QCFG__[q.querySelector(".sol input").dataset.q].grader;
    return [q.id, (g.equals || g.value.map(String))];
  }));
  const { context, page, errors } = await open("?ex=qcm-energie");
  assert.match(await text(page, "#home .home-head"), /QCM 2\.1[\s\S]*Niveau 2[\s\S]*QCM : énergie et chaîne d'énergie/);
  await page.click("[data-mode=training]");
  assert.match(await text(page, ".cartouche"), /76 questions, réparties en 6 parties/);
  assert.equal(await page.locator(".qcm").count(), 76);
  // les figures partagées sont toutes chargées
  assert.ok(await page.evaluate(() => [...document.querySelectorAll("img[data-qimg]")].every((i) => i.complete && i.naturalWidth > 0)));
  // Valider reste inactif sans choix ; une réponse unique remplace la précédente
  assert.ok(await page.locator("#b1_1 .btn-fast").isDisabled());
  await page.click("#b1_1 .qcm-o[data-k='1']"); await page.click("#b1_1 .qcm-o[data-k='2']");
  assert.equal(await page.locator("#b1_1 .qcm-o[aria-checked=true]").count(), 1);
  // une fausse réponse : propositions marquées, explication
  await page.click("#b1_2 .qcm-o[data-k='1']"); await page.click("#b1_2 .btn-fast");
  assert.equal(await text(page, "#b1_2 .q-status"), "Réponse fausse");
  assert.ok(await page.locator("#b1_2 .qcm-o.ko[data-k='1']").count());
  assert.ok(await page.locator("#b1_2 .qcm-o.ok[data-k='4']").count());
  assert.ok(await page.isVisible("#b1_2 .q-expl"));
  assert.ok(await page.locator("#b1_2 .qcm-o[data-k='3']").isDisabled());
  await context.close();
  // tout juste : 20/20
  const b = await open("?ex=qcm-energie");
  await b.page.click("[data-mode=training]");
  for (const [id, ks] of await bons(b.page)) {
    for (const k of (await b.page.locator(`#${id}`).getAttribute("data-multi")) === "1" ? ks : [ks[0]])
      await b.page.click(`#${id} .qcm-o[data-k='${k}' i]`);
    await b.page.click(`#${id} .btn-fast`);
  }
  assert.equal((await text(b.page, "#recap .final-note")).trim(), "20,0/20");
  assert.equal(await b.page.locator(".qcm .q-status:text-is('Bonne réponse')").count(), 76);
  assert.deepEqual(b.errors.concat(errors), []);
  await b.context.close();
  // examen : partie 1 juste, le reste vide ; remise en deux temps
  const c = await open("?ex=qcm-energie");
  await c.page.click("[data-mode=exam]");
  assert.ok(!(await c.page.isVisible("#b1_1 .btn-fast")));
  for (const [id, ks] of (await bons(c.page)).filter(([id]) => id.startsWith("b1_"))) await c.page.click(`#${id} .qcm-o[data-k='${ks[0]}' i]`);
  assert.match(await text(c.page, "#score-count"), /9 réponse\(s\) renseignée\(s\) sur 76/);
  await c.page.click("#exam-submit"); await c.page.click("#exam-submit");
  assert.ok(await c.page.locator("body.graded").count());
  assert.equal(await text(c.page, "#b2_1 .q-status"), "Pas de réponse");
  // partie 1 : 20/20, pèse 8 min sur 80 → 2,0/20
  assert.equal((await text(c.page, "#recap .final-note")).trim(), "2,0/20");
  assert.deepEqual(c.errors, []);
  await c.context.close();
});

test("documents et téléphone : rail, panneau, Échap ; bouton « Documents » sur petit écran", async () => {
  const { context, page, errors } = await open(EX);
  await page.click("[data-mode=training]");
  assert.deepEqual(await page.locator(".rail .tab[data-doc]").evaluateAll((t) => t.map((x) => x.textContent)), ["DP1", "DT1"]);
  await page.click(".rail .tab[data-doc=DP1]");
  assert.ok(await page.locator("body.panel-open").count());
  assert.match(await text(page, "#dp-title"), /DP1 : Chaîne d'information et chaîne d'énergie/);
  assert.ok(await page.isVisible("#doc-DP1 .dp-svg"));
  await page.click(".dp-tabs [data-doc=DT1]");
  assert.match(await text(page, "#doc-DT1"), /Distribuer[\s\S]*hacheur/);
  await page.keyboard.press("Escape");
  assert.equal(await page.locator("body.panel-open").count(), 0);
  await page.click(".qbar[aria-label='Q2.1'] .doc-chip[data-doc=DT1]");
  assert.ok(await page.locator("body.panel-open").count());
  await page.keyboard.press("Escape");
  await page.setViewportSize({ width: 420, height: 860 });
  assert.ok(await page.isVisible("#btn-docs"));
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("formulaire : page autonome, liens vers l'accueil, vues ouvertes depuis l'accueil", async () => {
  const { context, page, errors } = await open(FORM);
  assert.match(await page.title(), /Chaîne de puissance : formulaire et exercices/);
  assert.equal(await page.locator("a.linkbtn[href='index.html']").count(), 3);
  await page.goto(URL);
  await page.click(".form-grid a[href='formulaire.html#formulaire']");
  await page.waitForFunction(() => document.body.classList.contains("view-map"));
  assert.match(await text(page, "#view-map h1"), /Formulaire de la chaîne de puissance/);
  // fiche d'une formule : grandeurs, unités… mais plus de pastilles « Vu dans »
  await page.click("#mm-open");
  await page.locator(".leaf").first().click();
  assert.match(await text(page, "#pn-body"), /\S/);
  assert.equal(await page.locator("#pn-body .pn-vu").count(), 0);
  assert.doesNotMatch(await text(page, "#pn-body"), /Vu dans/);
  await page.click("#pn-close");
  await page.click("#view-map .crumb a[href='index.html']");
  await page.waitForURL(/index\.html$/);
  await page.click(".exo-grid a[href='formulaire.html#exercices']");
  await page.waitForFunction(() => document.body.classList.contains("view-ex"));
  assert.match(await text(page, "#home h1"), /Exercices : appliquer les formules/);
  assert.deepEqual(errors, []);
  await context.close();
});
