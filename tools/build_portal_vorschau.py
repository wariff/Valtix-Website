# -*- coding: utf-8 -*-
"""Baut die statische Portal-Vorschau. Reine Attrappe, keine echten Daten."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = re.search(r"CSS = '''(.*?)'''", open(os.path.join(ROOT, 'portal/app.py')).read(), re.S).group(1)

ZUSATZ = '''
/* nur fuer die Vorschau, im echten Portal nicht vorhanden */
.band{background:var(--ink);color:#fff;font-size:.86rem;line-height:1.5;
      padding:12px 24px}
.band .innen{max-width:1000px;margin:0 auto;display:flex;gap:14px;
             align-items:baseline;flex-wrap:wrap}
.band b{font-weight:700;letter-spacing:-.01em}
.band span{color:rgba(255,255,255,.72)}
.band a{color:var(--cream)}
.zugang{background:var(--cream);border:1px solid rgba(122,98,56,.28);border-radius:12px;
        padding:14px 16px;margin-bottom:18px;font-size:.88rem}
.zugang b{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;
          color:var(--gold-deep);margin-bottom:8px}
.zugang dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:4px 14px;
           align-items:baseline;font-size:.88rem}
.zugang dt{color:var(--ink-soft)}
.zugang dd{min-width:0}
@media(max-width:460px){.zugang dl{grid-template-columns:1fr;gap:2px}
  .zugang dt{margin-top:6px}}
.zugang code{background:rgba(35,41,65,.08);word-break:normal;white-space:nowrap}
.zugang dd code+code{margin-left:2px}
.zugang p{margin-top:8px;color:var(--ink-soft);font-size:.82rem}
.schalterband{background:rgba(35,41,65,.05);border-bottom:1px solid var(--hairline)}
.schalterband .innen{max-width:1000px;margin:0 auto;padding:10px 24px;display:flex;
                     gap:12px;align-items:center;flex-wrap:wrap}
.schalter-titel{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;
                color:var(--ink-soft);font-weight:600}
.schalter{display:flex;gap:6px;flex-wrap:wrap}
.schalter button{font:inherit;font-size:.84rem;padding:7px 14px;border-radius:999px;
  border:1px solid var(--hairline);background:#fff;color:var(--ink-soft);cursor:pointer}
.schalter button[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}
.leiste nav button.text{color:var(--ink-soft)}
.leiste nav button.text:hover{background:rgba(35,41,65,.06);color:var(--ink)}
.mitte{margin:6vh auto}
.fuss{padding-top:8px}
@media(max-width:600px){.band{padding:10px 16px}}
'''

BANNER = '''<div class="band"><div class="innen">
<b>Vorschau</b>
<span>Attrappe zur Ansicht. Es wird nichts gespeichert und nichts übertragen.
Alle Namen und Zahlen sind erfunden.</span>
<a href="index.html">Zurück zur Website</a>
</div></div>'''

ZUGANGSBOX = '''<div class="zugang"><b>Zugangsdaten der Vorschau</b>
<dl>
<dt>Administrator</dt><dd><code>admin@vorschau.valtix</code></dd>
<dt>Mandant</dt><dd><code>mandant@vorschau.valtix</code></dd>
<dt>Passwort, beide</dt><dd><code>Vorschau2026</code></dd>
</dl>
<p>Beide Eingaben werden nur im Browser geprüft. Es gibt keine Datenbank hinter
dieser Seite und keinen Server, der etwas entgegennimmt.</p></div>'''


def leiste(rolle):
    if rolle == 'admin':
        links = ('<a href="#" data-ziel="admin-start">Übersicht</a>'
                 '<a href="#" data-ziel="admin-verwaltung">Verwaltung</a>'
                 '<a href="#" data-ziel="admin-protokoll">Protokoll</a>')
    elif rolle == 'mandant':
        links = '<a href="#" data-ziel="mandant-start">Übersicht</a>'
    else:
        links = ''
    nav = (f'<nav>{links}<button class="text" type="button" data-ziel="anmelden">'
           f'Abmelden</button></nav>') if links else ''
    return ('<div class="leiste"><div class="innen">'
            '<a class="marke" href="#" data-ziel="anmelden">Valtix'
            '<span>Mandantenportal</span></a>' + nav + '</div></div>')


def schalter():
    p = [('anmelden', 'Anmeldung'), ('mandant-start', 'Mandantenansicht'),
         ('admin-start', 'Adminübersicht'), ('admin-verwaltung', 'Verwaltung'),
         ('admin-protokoll', 'Protokoll')]
    k = ''.join(f'<button type="button" data-ziel="{z}" aria-pressed="false">{t}</button>'
                for z, t in p)
    return (f'<div class="schalterband"><div class="innen">'
            f'<span class="schalter-titel">Ansicht</span>'
            f'<div class="schalter" role="group" aria-label="Ansicht wechseln">{k}</div>'
            f'</div></div>')


BERICHT = 'portal-vorschau-bericht.html'

# ---------------------------------------------------------------- Bildschirme
anmelden = f'''
  <h1>Anmelden</h1>
  <p class="lead">Zugang erhalten Mandanten im Rahmen der monatlichen Betreuung.</p>
  {ZUGANGSBOX}
  <div class="karte">
    <div class="meldung fehler" id="fehler" hidden></div>
    <form id="form-anmelden" novalidate>
      <label for="e">E-Mail-Adresse</label>
      <input id="e" name="email" type="email" autocomplete="off" value="mandant@vorschau.valtix">
      <label for="p">Passwort</label>
      <input id="p" name="passwort" type="password" autocomplete="off" value="Vorschau2026">
      <button class="knopf" type="submit">Anmelden</button>
    </form>
  </div>'''

_admin_zeilen = ''.join(
    f'<tr><td>{n}</td><td>{z}</td><td>{d}</td>'
    f'<td class="num"><a class="knopf schmal stumm" href="{BERICHT}">Ansehen</a></td></tr>'
    for n, z, d in [
        ('Muster Lüftungstechnik GmbH', 'Juli 2026', '2026-08-06'),
        ('Muster Lüftungstechnik GmbH', 'Juni 2026', '2026-07-07'),
        ('Beispiel Bau GmbH', 'Juli 2026', '2026-08-05'),
        ('Beispiel Handel e. K.', 'Juli 2026', '2026-08-04'),
        ('Beispiel Handel e. K.', 'Juni 2026', '2026-07-06'),
    ])

admin_start = f'''
  <h1>Alle Berichte</h1>
  <p class="lead">Angemeldet als Administrator.</p>
  <div class="rahmen"><table><thead><tr><th>Mandant</th><th>Zeitraum</th>
  <th>Eingestellt</th><th class="num">&nbsp;</th></tr></thead>
  <tbody>{_admin_zeilen}</tbody></table></div>'''

_mand_zeilen = ''.join(
    f'<tr><td>{m["name"]}</td><td class="num">{m["n"]}</td></tr>'
    for m in [{'name': 'Muster Lüftungstechnik GmbH', 'n': 2},
              {'name': 'Beispiel Bau GmbH', 'n': 1},
              {'name': 'Beispiel Handel e. K.', 'n': 2}])

_zug_zeilen = ''.join(
    f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in [
        ('Administrator', 'admin@vorschau.valtix', 'Administrator', 'aktiv'),
        ('Ansprechpartner Muster', 'mandant@vorschau.valtix',
         'Muster Lüftungstechnik GmbH', 'aktiv'),
        ('Ansprechpartner Beispiel Bau', 'bau@vorschau.valtix',
         'Beispiel Bau GmbH', 'offen'),
    ])

_auswahl = ('<option>Muster Lüftungstechnik GmbH</option>'
            '<option>Beispiel Bau GmbH</option><option>Beispiel Handel e. K.</option>')

admin_verwaltung = f'''
  <h1>Verwaltung</h1>
  <h2>Bericht einstellen</h2>
  <div class="karte"><form onsubmit="return false">
    <label for="m">Mandant</label>
    <select id="m">{_auswahl}</select>
    <label for="d">Ausgefüllte Eingabevorlage (.xlsx)</label>
    <input id="d" type="file" accept=".xlsx" disabled>
    <button class="knopf" type="button" disabled>Hochladen und Bericht erzeugen</button>
    <p class="marke-klein">In der Vorschau ohne Funktion. Es lässt sich nichts hochladen.</p>
  </form></div>

  <h2>Mandanten</h2>
  <div class="rahmen"><table><thead><tr><th>Name</th><th class="num">Berichte</th></tr>
  </thead><tbody>{_mand_zeilen}</tbody></table></div>
  <div class="karte" style="margin-top:14px"><form onsubmit="return false">
    <label for="mn">Neuer Mandant</label>
    <input id="mn" placeholder="Firmenname" disabled>
    <button class="knopf" type="button" disabled>Anlegen</button>
  </form></div>

  <h2>Zugänge</h2>
  <div class="rahmen"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Zugehörigkeit</th>
  <th>Status</th></tr></thead><tbody>{_zug_zeilen}</tbody></table></div>
  <div class="karte" style="margin-top:14px"><form onsubmit="return false">
    <label for="zn">Name</label><input id="zn" disabled>
    <label for="ze">E-Mail</label><input id="ze" type="email" disabled>
    <label for="zr">Rolle</label>
    <select id="zr" disabled><option>Mandant</option><option>Administrator</option></select>
    <label for="zm">Mandant, nur bei der Rolle Mandant</label>
    <select id="zm" disabled><option>ohne</option>{_auswahl}</select>
    <button class="knopf" type="button" disabled>Zugang anlegen</button>
    <p class="marke-klein">Es wird kein Passwort vergeben. Die Person setzt es
    selbst über einen einmaligen Link.</p>
  </form></div>'''

_prot = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in [
    ('2026-08-06 09:14:02', 'anmeldung', 'mandant@vorschau.valtix', ''),
    ('2026-08-06 09:14:11', 'bericht_geoeffnet', 'mandant@vorschau.valtix', 'bericht 5'),
    ('2026-08-06 08:52:40', 'bericht_eingestellt', 'admin@vorschau.valtix',
     'Muster Lüftungstechnik GmbH, Juli 2026'),
    ('2026-08-05 17:30:19', 'zugang_angelegt', 'admin@vorschau.valtix', 'bau@vorschau.valtix'),
    ('2026-08-05 17:29:03', 'anmeldung_fehlgeschlagen', '', 'unbekannte Kennung'),
])

admin_protokoll = f'''
  <h1>Protokoll</h1>
  <p class="lead">Die letzten Ereignisse. Anmeldungen, Zugriffe auf Berichte und
  Änderungen an Zugängen werden festgehalten.</p>
  <div class="rahmen"><table><thead><tr><th>Zeitpunkt</th><th>Ereignis</th>
  <th>E-Mail</th><th>Detail</th></tr></thead><tbody>{_prot}</tbody></table></div>'''

_mb = ''.join(
    f'<tr><td>{z}</td><td>{d}</td>'
    f'<td class="num"><a class="knopf schmal stumm" href="{BERICHT}">Ansehen</a></td></tr>'
    for z, d in [('Juli 2026', '2026-08-06'), ('Juni 2026', '2026-07-07')])

mandant_start = f'''
  <h1>Ihre Berichte</h1>
  <p class="lead">Angemeldet als Muster Lüftungstechnik GmbH.</p>
  <div class="rahmen"><table><thead><tr><th>Zeitraum</th><th>Eingestellt</th>
  <th class="num">&nbsp;</th></tr></thead><tbody>{_mb}</tbody></table></div>'''

BILDSCHIRME = [
    ('anmelden', '', False, anmelden),
    ('mandant-start', 'mandant', True, mandant_start),
    ('admin-start', 'admin', True, admin_start),
    ('admin-verwaltung', 'admin', True, admin_verwaltung),
    ('admin-protokoll', 'admin', True, admin_protokoll),
]

teile = []
for kennung, rolle, breit, inhalt in BILDSCHIRME:
    huelle = ('<main>' if breit else '<div class="mitte">')
    zu = ('</main>' if breit else '</div>')
    teile.append(f'<section class="bildschirm" id="bs-{kennung}" hidden>'
                 f'{leiste(rolle)}{huelle}{inhalt}{zu}</section>')

JS = '''
(function(){
  var zeigen = function(id){
    document.querySelectorAll('.bildschirm').forEach(function(s){ s.hidden = (s.id !== 'bs-' + id); });
    document.querySelectorAll('.schalter button').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.ziel === id));
    });
    window.scrollTo(0,0);
    if (history.replaceState) history.replaceState(null, '', '#ansicht-' + id);
  };
  document.addEventListener('click', function(e){
    var t = e.target.closest('[data-ziel]');
    if (!t) return;
    e.preventDefault();
    zeigen(t.dataset.ziel);
  });
  var f = document.getElementById('form-anmelden');
  f.addEventListener('submit', function(e){
    e.preventDefault();
    var mail = document.getElementById('e').value.trim().toLowerCase();
    var pw = document.getElementById('p').value;
    var box = document.getElementById('fehler');
    if (pw === 'Vorschau2026' && mail === 'admin@vorschau.valtix') { box.hidden = true; zeigen('admin-start'); return; }
    if (pw === 'Vorschau2026' && mail === 'mandant@vorschau.valtix') { box.hidden = true; zeigen('mandant-start'); return; }
    box.textContent = 'E-Mail-Adresse oder Passwort stimmen nicht. In der Vorschau gelten nur die oben genannten Zugangsdaten.';
    box.hidden = false;
  });
  var start = location.hash.replace('#ansicht-','').replace('#','');
  zeigen(document.getElementById('bs-' + start) ? start : 'anmelden');
})();
'''

html = f'''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Vorschau Mandantenportal · Valtix Financial Management</title>
<link rel="icon" href="favicon.ico" sizes="any">
<style>{CSS}{ZUSATZ}</style></head><body>
{BANNER}
{schalter()}
{''.join(teile)}
<div class="fuss">Valtix Financial Management · Luca Sparhuber und Sharif Ibrahim GbR, Leipzig ·
Diese Seite dient allein der Ansicht. Sie verarbeitet keine personenbezogenen Daten,
setzt keine Cookies und sendet nichts an einen Server.</div>
<script>{JS}</script>
</body></html>'''

ziel = os.path.join(ROOT, 'portal-vorschau.html')
open(ziel, 'w').write(html)
print('geschrieben:', ziel, len(html), 'Zeichen')
