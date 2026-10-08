// Images photographiées dans les pages (Playwright + Chromium), pour l'accueil :
//   - src/images/originaux/ex1-rav4-schema.png : motorisation du RAV4 (figure SVG), montage d'illustration ;
//   - src/images/originaux/carte-formulaire.png : la carte mentale du formulaire, toute dépliée, vue de loin ;
//   - src/images/originaux/carte-capteur.png : rendu du dessin carte-capteur.svg (cours 3).
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node outils/captures.js && bash outils/preparer-images.sh && python3 src/generer.py
const path = require("node:path");
const { chromium } = require("playwright");
(async () => {
  const racine = path.join(__dirname, "..");
  const ORIG = path.join(racine, "src/images/originaux");
  const FIGE = "*{animation:none!important;transition:none!important}";
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1 });
  await p.goto("file://" + path.join(racine, "index.html") + "?ex=chaines-information-energie");
  await p.click("[data-mode=training]");
  await p.click("#rv-demo [data-m=accel]");
  await p.addStyleTag({ content: FIGE });
  await p.locator("#rv-tech").screenshot({ path: path.join(ORIG, "ex1-rav4-schema.png") });
  await p.goto("file://" + path.join(racine, "formulaire.html") + "#formulaire");
  await p.click("#mm-open");
  await p.waitForTimeout(800);
  await p.addStyleTag({ content: FIGE });
  await p.locator("#mm").screenshot({ path: path.join(ORIG, "carte-formulaire.png") });
  await p.setViewportSize({ width: 960, height: 540 });
  await p.goto("file://" + path.join(ORIG, "carte-capteur.svg"));
  await p.screenshot({ path: path.join(ORIG, "carte-capteur.png") });
  await b.close();
})();
