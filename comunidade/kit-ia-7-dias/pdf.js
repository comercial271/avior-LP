// Converte kit.html em Kit-IA-no-Negocio.pdf (A4) e gera prévias PNG das páginas.
// Uso: node pdf.js [--previa]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'kit.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(__dirname, 'Kit-IA-no-Negocio.pdf'),
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
  });
  if (process.argv.includes('--previa')) {
    const secoes = await page.$$('section.pagina');
    for (let i = 0; i < secoes.length; i++) {
      await secoes[i].screenshot({ path: path.join(process.argv[3] || __dirname, `previa_${String(i + 1).padStart(2, '0')}.png`) });
    }
  }
  await browser.close();
  console.log('Kit-IA-no-Negocio.pdf gerado.');
})();
