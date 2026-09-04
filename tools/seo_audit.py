#!/usr/bin/env python3
"""Lokale SEO-Pruefung gegen die Kriterien aus claude-seo (seo-page, seo-technical,
seo-schema). Laeuft ohne Netz direkt gegen die Dateien im Repository."""
import glob, json, os, re, sys
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

befunde = []
def f(schwere, seite, kategorie, text):
    befunde.append((schwere, seite, kategorie, text))

seiten = sorted(glob.glob('*.html') + glob.glob('ratgeber/*.html'))
titel_gesehen, desc_gesehen = {}, {}

for p in seiten:
    s = open(p).read()
    d = BeautifulSoup(s, 'lxml')
    noindex = 'noindex' in (d.find('meta', attrs={'name':'robots'}) or {}).get('content','')

    # --- Titel ---
    t = d.title.string.strip() if d.title and d.title.string else ''
    if not t: f('HOCH', p, 'Titel', 'fehlt')
    elif len(t) > 65: f('MITTEL', p, 'Titel', f'{len(t)} Zeichen, Google kuerzt ab ~60')
    elif len(t) < 30: f('NIEDRIG', p, 'Titel', f'nur {len(t)} Zeichen')
    titel_gesehen.setdefault(t, []).append(p)

    # --- Description ---
    md = d.find('meta', attrs={'name':'description'})
    dc = (md.get('content','').strip() if md else '')
    if not dc: f('HOCH', p, 'Description', 'fehlt')
    elif len(dc) > 165: f('MITTEL', p, 'Description', f'{len(dc)} Zeichen, wird gekuerzt')
    elif len(dc) < 110: f('NIEDRIG', p, 'Description', f'nur {len(dc)} Zeichen, Platz verschenkt')
    desc_gesehen.setdefault(dc, []).append(p)

    # --- Canonical ---
    if not d.find('link', rel=lambda v: v and 'canonical' in v):
        f('HOCH' if not noindex else 'NIEDRIG', p, 'Canonical', 'fehlt')

    # --- H1 und Gliederung ---
    h1 = d.find_all('h1')
    if len(h1) != 1: f('HOCH', p, 'H1', f'{len(h1)} Stueck, genau eine erwartet')
    stufen = [int(h.name[1]) for h in d.find_all(re.compile('^h[1-6]$'))]
    for a, b in zip(stufen, stufen[1:]):
        if b > a + 1:
            f('MITTEL', p, 'Gliederung', f'Sprung von h{a} auf h{b}'); break

    # --- Open Graph ---
    if not noindex:
        for og in ('og:title','og:description','og:image','og:url'):
            if not d.find('meta', property=og): f('MITTEL', p, 'Open Graph', f'{og} fehlt')

    # --- Bilder ---
    for img in d.find_all('img'):
        src = img.get('src','?')
        if img.get('alt') is None: f('HOCH', p, 'Bild', f'alt fehlt bei {src}')
        if not (img.get('width') and img.get('height')):
            f('NIEDRIG', p, 'Bild', f'width/height fehlen bei {src}, verursacht Layoutsprung')
        if not img.get('loading') and 'logo' not in src:
            f('NIEDRIG', p, 'Bild', f'loading=lazy fehlt bei {src}')

    # --- Strukturierte Daten ---
    ld = d.find_all('script', type='application/ld+json')
    if not ld and not noindex: f('MITTEL', p, 'Schema', 'keine strukturierten Daten')

    # --- lang / viewport ---
    if d.html.get('lang') != 'de': f('HOCH', p, 'Sprache', 'lang-Attribut fehlt oder falsch')
    if not d.find('meta', attrs={'name':'viewport'}): f('HOCH', p, 'Viewport', 'fehlt')

    # --- interne Verlinkung ---
    intern = [a for a in d.find_all('a', href=True)
              if not a['href'].startswith(('http','mailto','tel','#'))]
    if len(intern) < 3 and not noindex:
        f('MITTEL', p, 'Verlinkung', f'nur {len(intern)} interne Links')

    # --- Textmenge ---
    for tag in d(['script','style']): tag.decompose()
    worte = len(d.get_text(' ', strip=True).split())
    grenze = 900 if p.startswith('ratgeber/') else 300
    if worte < grenze and not noindex:
        f('MITTEL', p, 'Umfang', f'{worte} Woerter, unter der Zielmarke {grenze}')

for t, ps in titel_gesehen.items():
    if len(ps) > 1: f('HOCH', ', '.join(ps), 'Titel', 'identischer Titel auf mehreren Seiten')
for dc, ps in desc_gesehen.items():
    if len(ps) > 1 and dc: f('HOCH', ', '.join(ps), 'Description', 'identische Description')

rang = {'HOCH':0,'MITTEL':1,'NIEDRIG':2}
befunde.sort(key=lambda b: (rang[b[0]], b[2], b[1]))
print(f'{len(seiten)} Seiten geprueft, {len(befunde)} Befunde\n')
for sch, seite, kat, txt in befunde:
    print(f'[{sch:7}] {kat:12} {seite}: {txt}')
