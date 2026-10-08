// Vignettes de l'accueil, capturées dans les pages elles-mêmes (Playwright + Chromium) :
//   - src/images/originaux/vign-*.png      : une figure par cours, le formulaire, les exercices de calcul ;
//   - src/images/originaux/ex1-rav4-schema.png : motorisation du RAV4 (montage d'illustration de l'accueil).
// Les figures étant dessinées en SVG, on les photographie une fois ; outils/preparer-images.sh les réduit ensuite.
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node outils/vignettes.js && bash outils/preparer-images.sh && python3 src/generer.py
const path = require("node:path");
const { chromium } = require("playwright");
const racine = path.join(__dirname, "..");
const ORIG = path.join(racine, "src/images/originaux");
const PAGE = "file://" + path.join(racine, "index.html");
const FORM = "file://" + path.join(racine, "formulaire.html");
const FIGE = ".rv-flow.on,.rv-run .rv-spin,.rv-eng-on .rv-cyl,.ci-fl.on .ci-fl-a,*{animation:none!important;transition:none!important}";

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  async function shot(url, sel, nom, avant) {
    await p.goto(url);
    if (avant) await avant();
    await p.addStyleTag({ content: FIGE });
    await p.waitForTimeout(300);
    await p.locator(sel).first().screenshot({ path: path.join(ORIG, nom + ".png") });
  }
  // exercice 1.1, RAV4 : situation « Accélération »
  await shot(PAGE + "?ex=chaines-information-energie", "#rv-tech", "ex1-rav4-schema",
    async () => { await p.click("[data-mode=training]"); await p.click("#rv-demo [data-m=accel]"); });
  // cours 1 : le portail animé, chaînes d'information et d'énergie
  await shot(PAGE + "?ex=cours-chaine-fonctionnelle", "#chain", "vign-cours-1");
  // cours 2 : la trottinette, tous les flux
  await shot(PAGE + "?ex=cours-chaine-energie", "#ce-f1", "vign-cours-2");
  // cours 3 : la machine à café, étape « commandes »
  await shot(PAGE + "?ex=cours-chaine-information", "#ci-cafe-svg", "vign-cours-3",
    async () => { for (let i = 0; i < 4; i++) await p.click("#ci-cafe-next"); });
  // formulaire : la carte mentale ; exercices de calcul : la première question d'une série générée
  await shot(FORM + "#formulaire", "#mm", "vign-formulaire");
  await shot(FORM + "#exercices", "#q1", "vign-calculs", async () => { await p.click("#btn-start"); });
  await b.close();
})();
