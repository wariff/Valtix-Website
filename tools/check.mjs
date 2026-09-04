// Prueft alle Seiten in drei Breiten auf Ueberlauf, Konsolenfehler und tote Links.
// Voraussetzung: npm i playwright   (Chromium liegt unter /opt/pw-browsers/chromium)
// Aufruf: node tools/check.mjs
import { chromium } from 'playwright';
import http from 'http'; import fs from 'fs'; import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const mime = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.xml':'application/xml',
  '.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.webp':'image/webp',
  '.ico':'image/x-icon','.txt':'text/plain','.webmanifest':'application/manifest+json'};

const alle = [
  ...fs.readdirSync(ROOT).filter(f => f.endsWith('.html')).map(f => '/' + f),
  ...fs.readdirSync(path.join(ROOT,'ratgeber')).filter(f => f.endsWith('.html')).map(f => '/ratgeber/' + f),
];

const srv = http.createServer((q, r) => {
  let u = decodeURIComponent(q.url.split('?')[0]);
  if (u.endsWith('/')) u += 'index.html';
  const f = path.join(ROOT, u);
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) {
    r.writeHead(404, {'Content-Type':'text/html'});
    return r.end(fs.readFileSync(path.join(ROOT, '404.html')));
  }
  r.writeHead(200, {'Content-Type': mime[path.extname(f)] || 'application/octet-stream'});
  r.end(fs.readFileSync(f));
});
await new Promise(r => srv.listen(8099, r));

const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
let fehler = 0;

for (const [w, h] of [[375,812],[768,1024],[1440,900]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } });
  const p = await ctx.newPage();
  const konsole = [];
  p.on('console', m => { if (m.type() === 'error') konsole.push(m.text()); });
  p.on('pageerror', e => konsole.push(String(e)));
  for (const u of alle) {
    await p.goto('http://localhost:8099' + u, { waitUntil: 'networkidle' });
    const ueber = await p.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (ueber > 0 || konsole.length) {
      console.log('PROBLEM', w, u, 'Ueberlauf', ueber, konsole);
      fehler++; konsole.length = 0;
    }
  }
  await ctx.close();
}

// Linkpruefung
const ctx = await b.newContext(); const p = await ctx.newPage();
const gesehen = new Set();
for (const u of alle) {
  await p.goto('http://localhost:8099' + u, { waitUntil: 'domcontentloaded' });
  const hrefs = await p.$$eval('a[href]', as => as.map(a => a.getAttribute('href')));
  for (const href of hrefs) {
    if (!href || /^(https?:|mailto:|tel:|#)/.test(href)) continue;
    const ziel = href.split('#')[0];
    if (!ziel) continue;
    const abs = new URL(ziel, new URL(u, 'http://localhost:8099')).pathname;
    if (gesehen.has(abs)) continue;
    gesehen.add(abs);
    const f = path.join(ROOT, abs.endsWith('/') ? abs + 'index.html' : abs);
    if (!fs.existsSync(f)) { console.log('TOTER LINK', u, '->', href); fehler++; }
  }
}
await b.close(); srv.close();
console.log(fehler === 0 ? 'ALLES OK' : 'PROBLEME: ' + fehler);
