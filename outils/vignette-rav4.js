// Vignette de la motorisation du RAV4 (figure SVG, situation « Accélération ») pour le montage de l'accueil.
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node outils/vignette-rav4.js && bash outils/preparer-images.sh
const path = require("node:path");
const { chromium } = require("playwright");
(async () => {
  const racine = path.join(__dirname, "..");
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: 1 });
  await p.goto("file://" + path.join(racine, "index.html") + "?ex=chaines-information-energie");
  await p.click("[data-mode=training]");
  await p.click("#rv-demo [data-m=accel]");
  await p.addStyleTag({ content: "*{animation:none!important;transition:none!important}" });
  await p.locator("#rv-tech").screenshot({ path: path.join(racine, "src/images/originaux/ex1-rav4-schema.png") });
  await b.close();
})();
