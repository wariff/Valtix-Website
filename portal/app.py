#!/usr/bin/env python3
"""Mandantenportal von Valtix Financial Management.

Start:  VALTIX_SECRET=<zufall> uvicorn app:app --host 127.0.0.1 --port 8000

Zwei Rollen. Ein Administrator sieht alle Mandanten, legt Zugaenge an und laedt
Berichte hoch. Ein Mandant sieht ausschliesslich die Berichte des eigenen
Unternehmens. Registrierung von aussen gibt es nicht: Zugaenge werden angelegt,
die Person setzt ihr Passwort ueber einen einmaligen Einladungslink selbst.
"""
import os, secrets, sys, time
from html import escape

from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(os.path.dirname(HIER), 'tools', 'bericht'))
import datenbank as db                                   # noqa: E402
import perioden as pd                                    # noqa: E402
import speicher as sp                                    # noqa: E402
import benachrichtigung as bn                            # noqa: E402
import aufgaben as af                                    # noqa: E402
import mapping as mp                                     # noqa: E402
import uebernahme as ue                                  # noqa: E402

GEHEIM = os.environ.get('VALTIX_SECRET')
if not GEHEIM:
    GEHEIM = secrets.token_urlsafe(48)
    print('WARNUNG: VALTIX_SECRET war nicht gesetzt, es wurde ein flüchtiger '
          'Schlüssel erzeugt. Beim Neustart sind alle Sitzungen ungültig.')
SITZUNG_MAX = 8 * 3600
signierer = URLSafeTimedSerializer(GEHEIM, salt='valtix-sitzung')

app = FastAPI(title='Valtix Mandantenportal', docs_url=None, redoc_url=None)
db.anlegen()

_versuche = {}          # einfache Bremse gegen Durchprobieren von Passwoertern


def _bremse(schluessel, grenze=5, fenster=300):
    jetzt = time.time()
    liste = [t for t in _versuche.get(schluessel, []) if jetzt - t < fenster]
    _versuche[schluessel] = liste
    return len(liste) >= grenze


def _fehlversuch(schluessel):
    _versuche.setdefault(schluessel, []).append(time.time())


def angemeldet(request):
    keks = request.cookies.get('valtix_sitzung')
    if not keks:
        return None
    try:
        daten = signierer.loads(keks, max_age=SITZUNG_MAX)
    except (BadSignature, SignatureExpired):
        return None
    return db.benutzer(daten.get('id'))


def csrf_token(bid):
    return URLSafeTimedSerializer(GEHEIM, salt='valtix-csrf').dumps(bid)


def csrf_ok(bid, token):
    try:
        return URLSafeTimedSerializer(GEHEIM, salt='valtix-csrf').loads(
            token, max_age=SITZUNG_MAX) == bid
    except Exception:
        return False


# ---------------------------------------------------------------- Darstellung
CSS = '''
:root{--ink:#232941;--ink-soft:#565D73;--gold-deep:#7A6238;--cream:#F5EBD0;
      --bg:#FBF8F2;--hairline:rgba(35,41,65,.12);--r:16px;
      --font:"Inter Tight",system-ui,-apple-system,"Segoe UI",sans-serif}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--ink);
     font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--gold-deep)}
.leiste{border-bottom:1px solid var(--hairline);background:rgba(255,255,255,.7)}
.leiste .innen{max-width:1000px;margin:0 auto;padding:14px 24px;display:flex;
               align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.marke{font-weight:800;letter-spacing:-.03em;font-size:1.05rem;text-decoration:none;color:var(--ink)}
.marke span{font-weight:500;color:var(--ink-soft);margin-left:8px;font-size:.9rem}
.leiste nav{display:flex;gap:6px;align-items:center;font-size:.9rem;
            flex-wrap:wrap;justify-content:flex-end}
.leiste nav a,.leiste nav button{padding:8px 14px;border-radius:999px;text-decoration:none;
  color:var(--ink-soft);background:none;border:0;font:inherit;cursor:pointer}
.leiste nav a:hover{background:rgba(35,41,65,.06);color:var(--ink)}
main{max-width:1000px;margin:0 auto;padding:32px 24px 72px}
.mitte{max-width:420px;margin:8vh auto;padding:0 24px}
h1{font-size:1.6rem;font-weight:800;letter-spacing:-.03em;margin-bottom:6px}
h2{font-size:1.15rem;font-weight:800;letter-spacing:-.025em;margin:32px 0 10px}
p.lead{color:var(--ink-soft);margin-bottom:22px}
.karte{background:#fff;border:1px solid var(--hairline);border-radius:var(--r);
       padding:24px;box-shadow:0 10px 30px rgba(35,41,65,.08)}
label{display:block;font-size:.84rem;font-weight:600;margin:14px 0 5px}
input,select{width:100%;font:inherit;font-size:.97rem;color:var(--ink);background:#fff;
  border:1px solid rgba(35,41,65,.22);border-radius:12px;padding:11px 14px;min-height:46px}
input:focus,select:focus{outline:none;border-color:var(--ink);box-shadow:0 0 0 3px rgba(35,41,65,.14)}
input[type=file]{padding:9px 12px}
.knopf{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;
  padding:0 22px;border-radius:999px;border:0;font:inherit;font-weight:600;cursor:pointer;
  background:linear-gradient(180deg,#232941,#171B2C);color:#fff;text-decoration:none;
  box-shadow:0 8px 20px rgba(35,41,65,.28);margin-top:18px}
.knopf.schmal{min-height:36px;padding:0 14px;font-size:.86rem;margin:0;box-shadow:none}
.knopf.stumm{background:#fff;color:var(--ink);border:1px solid var(--hairline);box-shadow:none}
.meldung{padding:12px 16px;border-radius:12px;font-size:.9rem;margin-bottom:16px}
.fehler{background:#FDECEC;color:#8B1F1F}
.gut{background:#E9F7EA;color:#155724}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin-top:8px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--hairline)}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--ink-soft)}
td.num,th.num{text-align:right}
.rahmen{overflow-x:auto}
.marke-klein{font-size:.78rem;color:var(--ink-soft);margin-top:6px}
code{background:rgba(35,41,65,.06);padding:2px 6px;border-radius:6px;font-size:.86rem;
     word-break:break-all}
.fuss{max-width:1000px;margin:0 auto;padding:0 24px 40px;font-size:.8rem;color:var(--ink-soft)}
'''


def seite(titel, inhalt, nutzer=None, breit=True):
    nav = ''
    if nutzer:
        links = ['<a href="/">Übersicht</a>']
        if nutzer['rolle'] == 'admin':
            links.append('<a href="/uebersicht">Monatsübersicht</a>')
            links.append('<a href="/verwaltung">Verwaltung</a>')
            links.append('<a href="/protokoll">Protokoll</a>')
        else:
            links.append('<a href="/unterlagen">Unterlagen</a>')
        nav = ('<nav>' + ''.join(links) +
               f'<form method="post" action="/abmelden" style="display:inline">'
               f'<button type="submit">Abmelden</button></form></nav>')
    kopf = (f'<div class="leiste"><div class="innen">'
            f'<a class="marke" href="/">Valtix<span>Mandantenportal</span></a>{nav}'
            f'</div></div>')
    huelle = 'main' if breit else 'div class="mitte"'
    zu = 'main' if breit else 'div'
    return HTMLResponse(f'''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>{escape(titel)} · Valtix Mandantenportal</title>
<style>{CSS}</style></head><body>
{kopf}<{huelle}>{inhalt}</{zu}>
<div class="fuss">Valtix Financial Management · Luca Sparhuber und Sharif Ibrahim GbR, Leipzig</div>
</body></html>''')


def sicherheitskopf(antwort):
    antwort.headers['X-Content-Type-Options'] = 'nosniff'
    antwort.headers['X-Frame-Options'] = 'DENY'
    antwort.headers['Referrer-Policy'] = 'same-origin'
    antwort.headers['Cache-Control'] = 'no-store'
    return antwort


@app.middleware('http')
async def kopfzeilen(request, call_next):
    return sicherheitskopf(await call_next(request))


# ---------------------------------------------------------------- Anmeldung
@app.get('/anmelden', response_class=HTMLResponse)
def anmelden_form(request: Request, fehler: str = ''):
    hinweis = f'<div class="meldung fehler">{escape(fehler)}</div>' if fehler else ''
    return seite('Anmelden', f'''
      <h1>Anmelden</h1>
      <p class="lead">Zugang erhalten Mandanten im Rahmen der monatlichen Betreuung.</p>
      <div class="karte">{hinweis}
        <form method="post" action="/anmelden">
          <label for="e">E-Mail-Adresse</label>
          <input id="e" name="email" type="email" required autocomplete="username">
          <label for="p">Passwort</label>
          <input id="p" name="passwort" type="password" required autocomplete="current-password">
          <button class="knopf" type="submit">Anmelden</button>
        </form>
      </div>''', breit=False)


@app.post('/anmelden')
def anmelden(request: Request, email: str = Form(...), passwort: str = Form(...)):
    ip = request.client.host if request.client else '?'
    if _bremse(ip):
        db.protokollieren('anmeldung_gebremst', email=email, detail=ip)
        return RedirectResponse('/anmelden?fehler=Zu+viele+Versuche.+Bitte+in+f%C3%BCnf+'
                                'Minuten+erneut+versuchen.', status_code=303)
    nutzer = db.pruefen(email, passwort)
    if not nutzer:
        _fehlversuch(ip)
        db.protokollieren('anmeldung_fehlgeschlagen', email=email, detail=ip)
        return RedirectResponse('/anmelden?fehler=E-Mail+oder+Passwort+stimmt+nicht.',
                                status_code=303)
    db.protokollieren('anmeldung', benutzer_id=nutzer['id'], email=nutzer['email'], detail=ip)
    antwort = RedirectResponse('/', status_code=303)
    antwort.set_cookie('valtix_sitzung', signierer.dumps({'id': nutzer['id']}),
                       max_age=SITZUNG_MAX, httponly=True, samesite='lax',
                       secure=os.environ.get('VALTIX_HTTPS', '1') == '1')
    return antwort


@app.post('/abmelden')
def abmelden(request: Request):
    n = angemeldet(request)
    if n:
        db.protokollieren('abmeldung', benutzer_id=n['id'], email=n['email'])
    antwort = RedirectResponse('/anmelden', status_code=303)
    antwort.delete_cookie('valtix_sitzung')
    return antwort


@app.get('/einladung/{token}', response_class=HTMLResponse)
def einladung_form(token: str, fehler: str = ''):
    hinweis = f'<div class="meldung fehler">{escape(fehler)}</div>' if fehler else ''
    return seite('Passwort setzen', f'''
      <h1>Passwort setzen</h1>
      <p class="lead">Wählen Sie ein Passwort mit mindestens zwölf Zeichen.
      Es ist ausschließlich Ihnen bekannt.</p>
      <div class="karte">{hinweis}
        <form method="post" action="/einladung/{escape(token)}">
          <label for="p1">Neues Passwort</label>
          <input id="p1" name="passwort" type="password" required minlength="12"
                 autocomplete="new-password">
          <label for="p2">Wiederholung</label>
          <input id="p2" name="wiederholung" type="password" required minlength="12"
                 autocomplete="new-password">
          <button class="knopf" type="submit">Passwort speichern</button>
        </form>
      </div>''', breit=False)


@app.post('/einladung/{token}')
def einladung(token: str, passwort: str = Form(...), wiederholung: str = Form(...)):
    if passwort != wiederholung:
        return RedirectResponse(f'/einladung/{token}?fehler=Die+Eingaben+stimmen+nicht+überein.',
                                status_code=303)
    try:
        bid = db.passwort_setzen(token, passwort)
    except ValueError as e:
        return RedirectResponse(f'/einladung/{token}?fehler={e}', status_code=303)
    if not bid:
        return RedirectResponse('/anmelden?fehler=Der+Einladungslink+ist+nicht+mehr+gültig.',
                                status_code=303)
    db.protokollieren('passwort_gesetzt', benutzer_id=bid)
    return RedirectResponse('/anmelden', status_code=303)


# ---------------------------------------------------------------- Übersicht
@app.get('/', response_class=HTMLResponse)
def start(request: Request, meldung: str = ''):
    n = angemeldet(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    hinweis = f'<div class="meldung gut">{escape(meldung)}</div>' if meldung else ''
    if n['rolle'] == 'admin':
        zeilen = ''.join(
            f'<tr><td>{escape(b["mandant_name"])}</td><td>{escape(b["zeitraum"])}</td>'
            f'<td>{escape(b["erstellt_am"][:10])}</td>'
            f'<td class="num"><a class="knopf schmal stumm" href="/bericht/{b["id"]}">Ansehen</a></td></tr>'
            for b in db.berichte()) or '<tr><td colspan="4">Noch keine Berichte.</td></tr>'
        return seite('Übersicht', f'''{hinweis}
          <h1>Alle Berichte</h1>
          <p class="lead">Angemeldet als {escape(n["name"])}, Administrator.</p>
          <div class="rahmen"><table><thead><tr><th>Mandant</th><th>Zeitraum</th>
          <th>Eingestellt</th><th class="num">&nbsp;</th></tr></thead>
          <tbody>{zeilen}</tbody></table></div>''', n)
    zeilen = ''.join(
        f'<tr><td>{escape(b["zeitraum"])}</td><td>{escape(b["erstellt_am"][:10])}</td>'
        f'<td class="num"><a class="knopf schmal stumm" href="/bericht/{b["id"]}">Ansehen</a></td></tr>'
        for b in db.berichte(n['mandant_id'])) or \
        '<tr><td colspan="3">Ihr erster Bericht erscheint hier, sobald er vorliegt.</td></tr>'
    return seite('Ihre Berichte', f'''{hinweis}{statusblock(n)}
      <h1>Ihre Berichte</h1>
      <p class="lead">Angemeldet als {escape(n["name"])}.</p>
      <div class="rahmen"><table><thead><tr><th>Zeitraum</th><th>Eingestellt</th>
      <th class="num">&nbsp;</th></tr></thead><tbody>{zeilen}</tbody></table></div>''', n)


@app.get('/bericht/{bid}', response_class=HTMLResponse)
def bericht_ansehen(request: Request, bid: int):
    n = angemeldet(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    b = db.bericht(bid)
    if not b or (n['rolle'] != 'admin' and b['mandant_id'] != n['mandant_id']):
        db.protokollieren('zugriff_verweigert', benutzer_id=n['id'], detail=f'bericht {bid}')
        return seite('Nicht gefunden',
                     '<h1>Nicht gefunden</h1><p class="lead">Dieser Bericht existiert nicht '
                     'oder gehört nicht zu Ihrem Zugang.</p>', n)
    db.protokollieren('bericht_geoeffnet', benutzer_id=n['id'], detail=f'bericht {bid}')
    return HTMLResponse(b['html'])


# ---------------------------------------------------------------- Verwaltung
def _nur_admin(request):
    n = angemeldet(request)
    return n if n and n['rolle'] == 'admin' else None


@app.get('/verwaltung', response_class=HTMLResponse)
def verwaltung(request: Request, meldung: str = '', link: str = ''):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    hinweis = f'<div class="meldung gut">{escape(meldung)}</div>' if meldung else ''
    if link:
        hinweis += (f'<div class="meldung gut">Einladungslink, einmalig gültig, bitte an die '
                    f'Person weitergeben:<br><code>{escape(link)}</code></div>')
    mand = db.mandanten()
    auswahl = ''.join(f'<option value="{m["id"]}">{escape(m["name"])}</option>' for m in mand)
    m_zeilen = ''.join(f'<tr><td>{escape(m["name"])}</td><td class="num">{m["anzahl"]}</td></tr>'
                       for m in mand) or '<tr><td colspan="2">Noch keine Mandanten.</td></tr>'
    b_zeilen = ''.join(
        f'<tr><td>{escape(b["name"])}</td><td>{escape(b["email"])}</td>'
        f'<td>{"Administrator" if b["rolle"]=="admin" else escape(b["mandant_name"] or "")}</td>'
        f'<td>{"offen" if b["einladung"] else ("aktiv" if b["aktiv"] else "gesperrt")}</td></tr>'
        for b in db.benutzer_liste())
    t = csrf_token(n['id'])
    return seite('Verwaltung', f'''{hinweis}
      <h1>Verwaltung</h1>
      <h2>Bericht einstellen</h2>
      <div class="karte"><form method="post" action="/hochladen" enctype="multipart/form-data">
        <input type="hidden" name="csrf" value="{t}">
        <label for="m">Mandant</label>
        <select id="m" name="mandant_id" required>{auswahl}</select>
        <label for="d">Ausgefüllte Eingabevorlage (.xlsx)</label>
        <input id="d" name="datei" type="file" accept=".xlsx" required>
        <button class="knopf" type="submit">Hochladen und Bericht erzeugen</button>
      </form></div>

      <h2>Mandanten</h2>
      <div class="rahmen"><table><thead><tr><th>Name</th><th class="num">Berichte</th></tr>
      </thead><tbody>{m_zeilen}</tbody></table></div>
      <div class="karte" style="margin-top:14px"><form method="post" action="/mandant">
        <input type="hidden" name="csrf" value="{t}">
        <label for="mn">Neuer Mandant</label>
        <input id="mn" name="name" required placeholder="Firmenname">
        <button class="knopf" type="submit">Anlegen</button>
      </form></div>

      <h2>Zugänge</h2>
      <div class="rahmen"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Zugehörigkeit</th>
      <th>Status</th></tr></thead><tbody>{b_zeilen}</tbody></table></div>
      <div class="karte" style="margin-top:14px"><form method="post" action="/zugang">
        <input type="hidden" name="csrf" value="{t}">
        <label for="zn">Name</label><input id="zn" name="name" required>
        <label for="ze">E-Mail</label><input id="ze" name="email" type="email" required>
        <label for="zr">Rolle</label>
        <select id="zr" name="rolle"><option value="mandant">Mandant</option>
        <option value="admin">Administrator</option></select>
        <label for="zm">Mandant, nur bei der Rolle Mandant</label>
        <select id="zm" name="mandant_id"><option value="">ohne</option>{auswahl}</select>
        <button class="knopf" type="submit">Zugang anlegen</button>
        <p class="marke-klein">Es wird kein Passwort vergeben. Die Person setzt es
        selbst über einen einmaligen Link.</p>
      </form></div>''', n)


@app.post('/mandant')
def mandant_neu(request: Request, name: str = Form(...), csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    db.mandant_anlegen(name)
    db.protokollieren('mandant_angelegt', benutzer_id=n['id'], detail=name)
    return RedirectResponse('/verwaltung?meldung=Mandant+angelegt.', status_code=303)


@app.post('/zugang')
def zugang_neu(request: Request, name: str = Form(...), email: str = Form(...),
               rolle: str = Form('mandant'), mandant_id: str = Form(''), csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    mid = int(mandant_id) if mandant_id and rolle == 'mandant' else None
    if rolle == 'mandant' and mid is None:
        return RedirectResponse('/verwaltung?meldung=Ein+Mandantenzugang+braucht+eine+Zuordnung.',
                                status_code=303)
    token = db.benutzer_anlegen(email, name, rolle, mid)
    db.protokollieren('zugang_angelegt', benutzer_id=n['id'], detail=f'{email} als {rolle}')
    basis = os.environ.get('VALTIX_BASIS', 'https://portal.valtixfm.de')
    return RedirectResponse(f'/verwaltung?link={basis}/einladung/{token}', status_code=303)


@app.post('/hochladen')
async def hochladen(request: Request, mandant_id: int = Form(...),
                    datei: UploadFile = File(...), csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    import tempfile
    from rendern import bauen
    inhalt = await datei.read()
    if len(inhalt) > 8 * 1024 * 1024:
        return RedirectResponse('/verwaltung?meldung=Datei+zu+groß.', status_code=303)
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        f.write(inhalt)
        pfad = f.name
    try:
        ziel, b = bauen(pfad, pfad.replace('.xlsx', '.html'))
        html = open(ziel).read()
        zeitraum = f"{b.aktuell} {b.stamm['jahr']}"
    except Exception as e:
        db.protokollieren('bericht_fehlgeschlagen', benutzer_id=n['id'], detail=str(e)[:200])
        return RedirectResponse(f'/verwaltung?meldung=Die+Datei+konnte+nicht+gelesen+werden%3A+'
                                f'{escape(str(e)[:120])}', status_code=303)
    finally:
        for p in (pfad, pfad.replace('.xlsx', '.html')):
            if os.path.exists(p):
                os.remove(p)
    bid = db.bericht_speichern(mandant_id, zeitraum, datei.filename, html, n['id'])
    db.protokollieren('bericht_eingestellt', benutzer_id=n['id'], detail=f'bericht {bid}')
    return RedirectResponse(f'/verwaltung?meldung=Bericht+für+{escape(zeitraum)}+eingestellt.',
                            status_code=303)


@app.get('/protokoll', response_class=HTMLResponse)
def protokoll(request: Request):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    zeilen = ''.join(
        f'<tr><td>{escape(p["zeitpunkt"][:19].replace("T"," "))}</td>'
        f'<td>{escape(p["ereignis"])}</td><td>{escape(p["email"] or "")}</td>'
        f'<td>{escape(p["detail"] or "")}</td></tr>' for p in db.protokoll())
    return seite('Protokoll', f'''
      <h1>Protokoll</h1>
      <p class="lead">Die letzten Ereignisse. Anmeldungen, Zugriffe auf Berichte und
      Änderungen an Zugängen werden festgehalten.</p>
      <div class="rahmen"><table><thead><tr><th>Zeitpunkt</th><th>Ereignis</th>
      <th>E-Mail</th><th>Detail</th></tr></thead><tbody>{zeilen}</tbody></table></div>''', n)


# ======================================================================
# M1: Perioden, Unterlagen, Einreichen
# ======================================================================
from datetime import date                                  # noqa: E402

AMPEL_TEXT = {'vollstaendig': ('Vollständig', '#0CA30C'),
              'unvollstaendig': ('Unvollständig', '#FAB219'),
              'fehlt': ('Fehlt', '#D03B3B')}


def aktueller_monat():
    """Der Monat, für den Unterlagen erwartet werden: der Vormonat."""
    h = date.today()
    jahr, monat = (h.year, h.month - 1) if h.month > 1 else (h.year - 1, 12)
    return f'{jahr}-{monat:02d}'


def statusblock(n):
    """F1: der einzige Zusatz auf der bestehenden Startseite."""
    if n['rolle'] != 'mandant' or not n['mandant_id']:
        return ''
    jm = aktueller_monat()
    p = pd.periode(n['mandant_id'], jm)
    zustand = p['status'] if p else 'offen'
    a = pd.ampel(n['mandant_id'], jm)
    text, farbe = AMPEL_TEXT[a]
    fehlend = pd.fehlende_pflichtslots(n['mandant_id'], jm)
    zusatz = ('Alles da.' if not fehlend else
              'Es fehlen noch: ' + escape(', '.join(f['bezeichnung'] for f in fehlend)) + '.')
    return (f'<div class="karte" style="margin-bottom:18px">'
            f'<h2 style="margin-top:0">Unterlagen {escape(pd.monatstext(jm))}</h2>'
            f'<p class="lead" style="margin-bottom:10px">'
            f'<span class="punkt" style="background:{farbe}"></span>'
            f'{escape(pd.STATUS_TEXT[zustand])} · {text}. {zusatz}</p>'
            f'<a class="knopf" href="/unterlagen/{jm}">Unterlagen hochladen</a></div>')


def _mandant_pflicht(request):
    n = angemeldet(request)
    if not n or n['rolle'] != 'mandant' or not n['mandant_id']:
        return None
    return n


def _zurueck(ziel, meldung='', fehler=''):
    from urllib.parse import urlencode
    teile = {}
    if meldung:
        teile['meldung'] = meldung
    if fehler:
        teile['fehler'] = fehler
    return RedirectResponse(ziel + ('?' + urlencode(teile) if teile else ''),
                            status_code=303)


@app.get('/unterlagen', response_class=HTMLResponse)
def unterlagen(request: Request):
    n = _mandant_pflicht(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    heute = date.today()
    monate = []
    for zurueck in range(0, 12):
        jahr, monat = heute.year, heute.month - zurueck
        while monat < 1:
            monat += 12
            jahr -= 1
        monate.append(f'{jahr}-{monat:02d}')
    zeilen = ''
    for jm in monate:
        p = pd.periode(n['mandant_id'], jm)
        a = pd.ampel(n['mandant_id'], jm)
        text, farbe = AMPEL_TEXT[a]
        zeilen += (f'<tr><td>{escape(pd.monatstext(jm))}</td>'
                   f'<td><span class="punkt" style="background:{farbe}"></span>{text}</td>'
                   f'<td>{escape(pd.STATUS_TEXT[p["status"]] if p else "offen")}</td>'
                   f'<td class="num"><a class="knopf schmal stumm" '
                   f'href="/unterlagen/{jm}">Öffnen</a></td></tr>')
    return seite('Unterlagen', f'''
      <h1>Unterlagen</h1>
      <p class="lead">Für jeden Monat sehen Sie, was schon vorliegt. Auch für
      zurückliegende Monate können Sie jederzeit noch etwas nachreichen.</p>
      <div class="rahmen"><table><thead><tr><th>Monat</th><th>Vollständigkeit</th>
      <th>Status</th><th class="num">&nbsp;</th></tr></thead>
      <tbody>{zeilen}</tbody></table></div>''', n)


@app.get('/unterlagen/{jahr_monat}', response_class=HTMLResponse)
def monat(request: Request, jahr_monat: str, meldung: str = '', fehler: str = ''):
    n = _mandant_pflicht(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    if not pd.gueltig(jahr_monat):
        return RedirectResponse('/unterlagen', status_code=303)
    s = pd.stand(n['mandant_id'], jahr_monat)
    p = s['periode']
    offen = pd.darf_hochladen(p) if p else True
    t = csrf_token(n['id'])

    kopf = ''
    if meldung:
        kopf += f'<div class="meldung gut">{escape(meldung)}</div>'
    if fehler:
        kopf += f'<div class="meldung fehler">{escape(fehler)}</div>'

    reihen = ''
    for slot in s['slots']:
        if slot['dateien']:
            d = slot['dateien'][-1]
            zustand = (f'<a href="/datei/{d["id"]}">{escape(d["dateiname"])}</a>'
                       f'<span class="marke-klein"> · Fassung {d["version"]} · '
                       f'{d["groesse"] // 1024} KB</span>')
        elif slot['entfaellt']:
            zustand = (f'entfällt: {escape(slot["entfaellt"]["grund"])}'
                       + (f' <form method="post" action="/unterlagen/{jahr_monat}/'
                          f'entfaellt-aufheben" style="display:inline">'
                          f'<input type="hidden" name="csrf" value="{t}">'
                          f'<input type="hidden" name="slot" value="{slot["schluessel"]}">'
                          f'<button class="knopf schmal stumm" type="submit">'
                          f'zurücknehmen</button></form>' if offen else ''))
        else:
            zustand = '<span class="marke-klein">liegt noch nicht vor</span>'
        pflicht = 'Pflicht' if slot['pflicht'] else 'optional'
        werkzeug = ''
        if offen and not slot['dateien'] and not slot['entfaellt']:
            werkzeug = (f'<form method="post" action="/unterlagen/{jahr_monat}/entfaellt" '
                        f'style="display:flex;gap:6px;align-items:center">'
                        f'<input type="hidden" name="csrf" value="{t}">'
                        f'<input type="hidden" name="slot" value="{slot["schluessel"]}">'
                        f'<input name="grund" placeholder="Grund" '
                        f'style="min-height:34px;font-size:.85rem">'
                        f'<button class="knopf schmal stumm" type="submit">entfällt'
                        f'</button></form>')
        reihen += (f'<tr><td><b>{escape(slot["bezeichnung"])}</b>'
                   f'<span class="marke-klein"> · {pflicht}</span></td>'
                   f'<td>{zustand}</td><td>{werkzeug}</td></tr>')

    hochladen = ''
    if offen:
        auswahl = ''.join(f'<option value="{s2["schluessel"]}">{escape(s2["bezeichnung"])}'
                          f'</option>' for s2 in s['slots'])
        hochladen = f'''
        <h2>Dateien hochladen</h2>
        <div class="karte">
          <form method="post" action="/unterlagen/{jahr_monat}/hochladen"
                enctype="multipart/form-data">
            <input type="hidden" name="csrf" value="{t}">
            <label for="slot">Wozu gehört die Datei?</label>
            <select id="slot" name="slot">{auswahl}
              <option value="">Sonstiges</option></select>
            <label for="dateien">Dateien</label>
            <input id="dateien" name="dateien" type="file" multiple
                   accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.csv,.txt,.zip">
            <button class="knopf" type="submit">Hochladen</button>
            <p class="marke-klein">PDF, Bilder, Excel, CSV, DATEV-Export oder ZIP,
            bis {sp.GROESSTE_DATEI // 1048576} MB je Datei. Auf dem Telefon können
            Sie die Kamera benutzen.</p>
          </form>
        </div>'''

    fehlend = pd.fehlende_pflichtslots(n['mandant_id'], jahr_monat)
    if offen:
        warnung = ('<p class="marke-klein">Alle Pflichtunterlagen liegen vor.</p>'
                   if not fehlend else
                   '<p class="marke-klein">Noch offen: '
                   + escape(', '.join(f['bezeichnung'] for f in fehlend)) + '. '
                   'Sie können trotzdem einreichen, wir fragen dann nach.</p>')
        abschluss = f'''
        <h2>Einreichen</h2>
        <div class="karte">{warnung}
          <form method="post" action="/unterlagen/{jahr_monat}/einreichen">
            <input type="hidden" name="csrf" value="{t}">
            <button class="knopf" type="submit">Unterlagen einreichen</button>
          </form>
        </div>'''
    else:
        abschluss = f'''
        <h2>Eingereicht</h2>
        <div class="karte">
          <p class="marke-klein">Eingereicht am
          {escape((p["eingereicht_am"] or "")[:10])}. Zum Ändern brauchen Sie einen
          Nachtrag, wir werden dann erneut benachrichtigt.</p>
          <form method="post" action="/unterlagen/{jahr_monat}/nachtrag">
            <input type="hidden" name="csrf" value="{t}">
            <button class="knopf stumm" type="submit">Nachtrag</button>
          </form>
        </div>'''

    return seite(pd.monatstext(jahr_monat), f'''{kopf}
      <h1>Unterlagen {escape(pd.monatstext(jahr_monat))}</h1>
      <p class="lead">Status: {escape(pd.STATUS_TEXT[p["status"]] if p else "offen")}.</p>
      <div class="rahmen"><table><thead><tr><th>Unterlage</th><th>Stand</th>
      <th>&nbsp;</th></tr></thead><tbody>{reihen}</tbody></table></div>
      {hochladen}{abschluss}''', n)


@app.post('/unterlagen/{jahr_monat}/hochladen')
async def monat_hochladen(request: Request, jahr_monat: str,
                          slot: str = Form(''), csrf: str = Form(...)):
    n = _mandant_pflicht(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    form = await request.form()
    dateien = [f for f in form.getlist('dateien') if getattr(f, 'filename', '')]
    if not dateien:
        return _zurueck(f'/unterlagen/{jahr_monat}', fehler='Es war keine Datei dabei.')
    gut, schlecht = 0, []
    for f in dateien:
        inhalt = await f.read()
        try:
            pd.dokument_ablegen(n['mandant_id'], jahr_monat, slot or None,
                                f.filename, f.content_type or '', inhalt, n['id'])
            gut += 1
        except (pd.Verweigert, sp.Abgelehnt) as e:
            schlecht.append(f'{f.filename}: {e}')
    meldung = f'{gut} {"Datei" if gut == 1 else "Dateien"} hochgeladen.' if gut else ''
    return _zurueck(f'/unterlagen/{jahr_monat}', meldung=meldung,
                    fehler=' '.join(schlecht)[:400])


@app.post('/unterlagen/{jahr_monat}/entfaellt')
def monat_entfaellt(request: Request, jahr_monat: str, slot: str = Form(...),
                    grund: str = Form(''), csrf: str = Form(...)):
    n = _mandant_pflicht(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        pd.entfaellt_setzen(n['mandant_id'], jahr_monat, slot, grund, n['id'])
        return _zurueck(f'/unterlagen/{jahr_monat}', meldung='Als entfallen vermerkt.')
    except pd.Verweigert as e:
        return _zurueck(f'/unterlagen/{jahr_monat}', fehler=str(e))


@app.post('/unterlagen/{jahr_monat}/entfaellt-aufheben')
def monat_entfaellt_weg(request: Request, jahr_monat: str, slot: str = Form(...),
                        csrf: str = Form(...)):
    n = _mandant_pflicht(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        pd.entfaellt_aufheben(n['mandant_id'], jahr_monat, slot, n['id'])
        return _zurueck(f'/unterlagen/{jahr_monat}', meldung='Vermerk zurückgenommen.')
    except pd.Verweigert as e:
        return _zurueck(f'/unterlagen/{jahr_monat}', fehler=str(e))


@app.post('/unterlagen/{jahr_monat}/einreichen')
def monat_einreichen(request: Request, jahr_monat: str, csrf: str = Form(...)):
    n = _mandant_pflicht(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        anzahl = pd.einreichen(n['mandant_id'], jahr_monat, n['id'])
    except pd.Verweigert as e:
        return _zurueck(f'/unterlagen/{jahr_monat}', fehler=str(e))
    p = pd.periode(n['mandant_id'], jahr_monat)
    name = next((m['name'] for m in db.mandanten() if m['id'] == n['mandant_id']), '')
    bn.eingereicht(name, jahr_monat, anzahl, p['id'])
    bn.bestaetigung(n['email'], name, jahr_monat, anzahl)
    return _zurueck(f'/unterlagen/{jahr_monat}',
                    meldung='Vielen Dank, wir haben Ihre Unterlagen erhalten.')


@app.post('/unterlagen/{jahr_monat}/nachtrag')
def monat_nachtrag(request: Request, jahr_monat: str, csrf: str = Form(...)):
    n = _mandant_pflicht(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        pd.nachtrag_oeffnen(n['mandant_id'], jahr_monat, n['id'])
    except pd.Verweigert as e:
        return _zurueck(f'/unterlagen/{jahr_monat}', fehler=str(e))
    p = pd.periode(n['mandant_id'], jahr_monat)
    name = next((m['name'] for m in db.mandanten() if m['id'] == n['mandant_id']), '')
    bn.nachtrag(name, jahr_monat, p['id'])
    return _zurueck(f'/unterlagen/{jahr_monat}',
                    meldung='Sie können jetzt weitere Unterlagen nachreichen.')


@app.get('/datei/{dokument_id}')
def datei(request: Request, dokument_id: int):
    n = angemeldet(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    d = pd.dokument(dokument_id, None if n['rolle'] == 'admin' else n['mandant_id'])
    if not d:
        db.protokollieren('zugriff_verweigert', benutzer_id=n['id'],
                          detail=f'dokument {dokument_id}')
        return seite('Nicht gefunden', '<h1>Nicht gefunden</h1><p class="lead">'
                     'Diese Datei existiert nicht oder gehört nicht zu Ihrem Zugang.'
                     '</p>', n)
    db.protokollieren('datei_geoeffnet', benutzer_id=n['id'], detail=f'dokument {d["id"]}')
    from urllib.parse import quote
    return Response(sp.lesen(d['speicher_schluessel']), media_type=d['mime'],
                    headers={'Content-Disposition':
                             f"attachment; filename*=UTF-8''{quote(d['dateiname'])}",
                             'Cache-Control': 'no-store'})


# ---------------------------------------------------------------- Admin M1/M2
@app.get('/uebersicht', response_class=HTMLResponse)
def uebersicht(request: Request, jahr: int = 0, filter: str = ''):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    jahr = jahr or date.today().year
    zeilen = ''
    for z in pd.matrix(jahr):
        felder = ''
        for m in z['monate']:
            if filter and m['status'] != filter:
                felder += '<td class="num" style="opacity:.25">·</td>'
                continue
            _, farbe = AMPEL_TEXT[m['ampel']]
            titel = f'{pd.STATUS_TEXT[m["status"]]}, {m["ampel"]}'
            inhalt = (f'<a href="/uebersicht/{m["periode_id"]}" title="{titel}">'
                      f'<span class="punkt" style="background:{farbe}"></span></a>'
                      if m['periode_id'] else
                      f'<span class="punkt" style="background:#D9DBE2" title="ohne '
                      f'Eintrag"></span>')
            felder += f'<td class="num">{inhalt}</td>'
        zeilen += f'<tr><td>{escape(z["mandant"]["name"])}</td>{felder}</tr>'
    kopf = ''.join(f'<th class="num">{pd.MONATE[m - 1][:3]}</th>' for m in range(1, 13))
    filterlinks = ' · '.join(
        f'<a href="/uebersicht?jahr={jahr}&filter={k}">{escape(v)}</a>'
        for k, v in [('', 'alle'), ('offen', 'offen'), ('eingereicht', 'eingereicht'),
                     ('in_pruefung', 'in Bearbeitung')])
    return seite('Monatsübersicht', f'''
      <h1>Monatsübersicht {jahr}</h1>
      <p class="lead">Ein Punkt je Mandant und Monat. Grün vollständig, gelb
      unvollständig, rot fehlt, grau ohne Eintrag. Filter: {filterlinks}</p>
      <p class="marke-klein"><a href="/uebersicht?jahr={jahr - 1}">← {jahr - 1}</a>
      &nbsp;·&nbsp; <a href="/uebersicht?jahr={jahr + 1}">{jahr + 1} →</a></p>
      <div class="rahmen"><table><thead><tr><th>Mandant</th>{kopf}</tr></thead>
      <tbody>{zeilen}</tbody></table></div>''', n)


@app.get('/uebersicht/{periode_id}', response_class=HTMLResponse)
def periode_ansehen(request: Request, periode_id: int, meldung: str = ''):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    p = pd.periode_nach_id(periode_id)
    if not p:
        return seite('Nicht gefunden', '<h1>Nicht gefunden</h1>', n)
    name = next((m['name'] for m in db.mandanten() if m['id'] == p['mandant_id']), '')
    s = pd.stand(p['mandant_id'], p['jahr_monat'])
    t = csrf_token(n['id'])
    reihen = ''
    for slot in s['slots'] + [{'bezeichnung': 'Sonstiges', 'schluessel': '',
                               'dateien': s['ohne_slot'], 'entfaellt': None,
                               'pflicht': 0}]:
        for d in slot['dateien']:
            reihen += (f'<tr><td>{escape(slot["bezeichnung"])}</td>'
                       f'<td><a href="/datei/{d["id"]}">{escape(d["dateiname"])}</a></td>'
                       f'<td>Fassung {d["version"]}</td>'
                       f'<td class="num">{d["groesse"] // 1024} KB</td></tr>')
        if slot['entfaellt']:
            reihen += (f'<tr><td>{escape(slot["bezeichnung"])}</td>'
                       f'<td colspan="3">entfällt: '
                       f'{escape(slot["entfaellt"]["grund"])}</td></tr>')
    auswahl = ''.join(f'<option value="{k}"{" selected" if k == p["status"] else ""}>'
                      f'{escape(v)}</option>' for k, v in pd.STATUS_TEXT.items())

    WEG_TEXT = {'xlsx': 'Excel', 'csv': 'CSV', 'datev': 'DATEV',
                'pdf_text': 'PDF mit Text', 'bild': 'Bild', 'zip': 'Archiv'}
    LESE_TEXT = {'roh': 'gelesen', 'geprueft': 'geprüft', 'verworfen': 'verworfen',
                 'ocr_noetig': 'braucht OCR'}
    leseliste = ''
    for z in af.stand(periode_id):
        if z['aufgabe'] in (None, 'wartet'):
            stand_text = 'wartet'
        elif z['aufgabe'] == 'laeuft':
            stand_text = 'wird gelesen'
        elif z['aufgabe'] == 'fehler':
            stand_text = f'Fehler: {escape((z["fehler"] or "")[:80])}'
        else:
            stand_text = escape(LESE_TEXT.get(z['extraktion'] or '', z['extraktion'] or ''))
        leseliste += (f'<tr><td>{escape(z["dateiname"])}</td>'
                      f'<td>{escape(WEG_TEXT.get(z["weg"] or "", z["weg"] or "–"))}</td>'
                      f'<td>{stand_text}</td>'
                      f'<td>{escape((z["hinweis"] or "")[:90])}</td></tr>')
    leseliste = leseliste or '<tr><td colspan="4">Noch nichts gelesen.</td></tr>'
    return seite(f'{name} {p["jahr_monat"]}', f'''
      {f'<div class="meldung gut">{escape(meldung)}</div>' if meldung else ''}
      <h1>{escape(name)}</h1>
      <p class="lead">{escape(pd.monatstext(p["jahr_monat"]))} ·
      {escape(pd.STATUS_TEXT[p["status"]])}
      {' · Nachtrag offen' if p['nachtrag_offen'] else ''}</p>
      <div class="rahmen"><table><thead><tr><th>Unterlage</th><th>Datei</th>
      <th>Stand</th><th class="num">Größe</th></tr></thead>
      <tbody>{reihen or '<tr><td colspan="4">Noch nichts vorhanden.</td></tr>'}</tbody>
      </table></div>
      <div class="karte" style="margin-top:14px">
        <a class="knopf stumm" href="/uebersicht/{periode_id}/paket">Alle Dateien als ZIP</a>
      </div>
      <h2>Auslesen</h2>
      <p class="marke-klein">Was das Portal aus den Dateien lesen konnte. Nichts
      davon wird produktiv, bevor es geprüft und freigegeben ist.</p>
      <div class="rahmen"><table><thead><tr><th>Datei</th><th>Weg</th>
      <th>Stand</th><th>Hinweis</th></tr></thead><tbody>{leseliste}</tbody></table></div>
      <div class="karte" style="margin-top:14px">
        <a class="knopf" href="/uebersicht/{periode_id}/pruefen">Werte prüfen und freigeben</a>
      </div>
      <h2>Status und Notiz</h2>
      <div class="karte"><form method="post" action="/uebersicht/{periode_id}/pflegen">
        <input type="hidden" name="csrf" value="{t}">
        <label for="st">Status</label>
        <select id="st" name="status">{auswahl}</select>
        <label for="no">Notiz</label>
        <input id="no" name="notiz" value="{escape(p['notiz'] or '')}">
        <button class="knopf" type="submit">Speichern</button>
      </form></div>''', n)


@app.post('/uebersicht/{periode_id}/pflegen')
def periode_pflegen(request: Request, periode_id: int, status: str = Form(...),
                    notiz: str = Form(''), csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        pd.status_setzen(periode_id, status, n['id'])
        pd.notiz_setzen(periode_id, notiz, n['id'])
    except pd.Verweigert as e:
        return _zurueck(f'/uebersicht/{periode_id}', meldung=str(e))
    return _zurueck(f'/uebersicht/{periode_id}', meldung='Gespeichert.')


@app.get('/uebersicht/{periode_id}/paket')
def periode_paket(request: Request, periode_id: int):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    try:
        daten, anzahl = pd.paket(periode_id)
    except pd.Verweigert as e:
        return seite('Nicht möglich', f'<h1>Nicht möglich</h1><p>{escape(str(e))}</p>', n)
    p = pd.periode_nach_id(periode_id)
    db.protokollieren('paket_geladen', benutzer_id=n['id'],
                      detail=f'periode {periode_id}, {anzahl} Dateien')
    return Response(daten, media_type='application/zip',
                    headers={'Content-Disposition':
                             f'attachment; filename="unterlagen-{p["jahr_monat"]}.zip"',
                             'Cache-Control': 'no-store'})


# ======================================================================
# M4: Pruefen, Zuordnen, Freigeben, Ausgeben
# ======================================================================
@app.get('/uebersicht/{periode_id}/pruefen', response_class=HTMLResponse)
def pruefen(request: Request, periode_id: int, meldung: str = '', fehler: str = ''):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    p = pd.periode_nach_id(periode_id)
    if not p:
        return seite('Nicht gefunden', '<h1>Nicht gefunden</h1>', n)
    name = next((m['name'] for m in db.mandanten() if m['id'] == p['mandant_id']), '')
    liste = ue.pruefliste(periode_id)
    t = csrf_token(n['id'])

    kopf = ''
    if meldung:
        kopf += f'<div class="meldung gut">{escape(meldung)}</div>'
    if fehler:
        kopf += f'<div class="meldung fehler">{escape(fehler)}</div>'

    zeilen = ''
    for z in liste['zeilen']:
        if z['wert'] is None and not z['warnungen']:
            continue
        wert = '' if z['wert'] is None else f'{z["wert"]:.2f}'
        herkunft = ', '.join(sorted({pos['datei'] for pos in z['posten']})) or '–'
        konten = ', '.join(f'{pos["quelle"]}' for pos in z['posten'][:6])
        warn = ('<br><span style="color:#A32C2C">'
                + escape(' · '.join(z['warnungen'])) + '</span>') if z['warnungen'] else ''
        haken = '✓' if z['freigegeben'] else ''
        konf = '' if z['konfidenz'] is None else f'{z["konfidenz"] * 100:.0f} %'
        zeilen += (f'<tr><td><b>{escape(z["klartext"])}</b>'
                   f'<span class="marke-klein"> · {z["blatt"]} Zeile {z["zeile"]}</span>'
                   f'{warn}</td>'
                   f'<td><span class="marke-klein">{escape(herkunft)}<br>'
                   f'{escape(konten)}</span></td>'
                   f'<td class="num">{konf}</td>'
                   f'<td class="num">{haken}</td>'
                   f'<td><form method="post" action="/uebersicht/{periode_id}/wert" '
                   f'style="display:flex;gap:6px">'
                   f'<input type="hidden" name="csrf" value="{t}">'
                   f'<input type="hidden" name="feld" value="{z["schluessel"]}">'
                   f'<input name="wert" value="{wert}" inputmode="decimal" '
                   f'style="min-height:34px;max-width:130px;text-align:right">'
                   f'<button class="knopf schmal stumm" type="submit">setzen</button>'
                   f'</form></td></tr>')

    auswahl = ''.join(f'<option value="{k}">{escape(v[2])}</option>'
                      for k, v in mp.ZIELFELDER.items())
    klaer = ''
    for k in liste['klaerliste']:
        klaer += (f'<tr><td>{escape(k["quelle"])}</td>'
                  f'<td>{escape(k["bezeichnung"] or "")}</td>'
                  f'<td class="num">{k["betrag"]:,.2f}</td>'.replace(',', '.')
                  + f'<td><form method="post" action="/uebersicht/{periode_id}/klaerfall" '
                    f'style="display:flex;gap:6px">'
                    f'<input type="hidden" name="csrf" value="{t}">'
                    f'<input type="hidden" name="klaerfall" value="{k["id"]}">'
                    f'<select name="feld">{auswahl}</select>'
                    f'<button class="knopf schmal stumm" type="submit">zuordnen</button>'
                    f'</form></td></tr>')
    klaer = klaer or '<tr><td colspan="4">Nichts offen.</td></tr>'

    return seite(f'Prüfen {p["jahr_monat"]}', f'''{kopf}
      <h1>Werte prüfen</h1>
      <p class="lead">{escape(name)} · {escape(pd.monatstext(p["jahr_monat"]))} ·
      Kontenrahmen {escape(liste["rahmen"])} · {liste["posten_gesamt"]} Posten gelesen</p>
      <p class="marke-klein">Die Kontenbereiche sind eine fachliche Schätzung und an
      echten Daten noch nicht geprüft. Jeder Wert hier ist ein Vorschlag. Erst die
      Freigabe macht ihn gültig, jede Korrektur wird protokolliert und für den
      Folgemonat gemerkt.</p>
      <div class="rahmen"><table><thead><tr><th>Position</th><th>Herkunft</th>
      <th class="num">Konfidenz</th><th class="num">frei</th><th>Wert</th>
      </tr></thead><tbody>{zeilen}</tbody></table></div>

      <h2>Klärliste</h2>
      <p class="marke-klein">Posten, für die es noch keine Zuordnung gibt. Was Sie
      hier zuordnen, gilt ab dem nächsten Monat automatisch.</p>
      <div class="rahmen"><table><thead><tr><th>Konto</th><th>Bezeichnung</th>
      <th class="num">Betrag</th><th>Zuordnen</th></tr></thead>
      <tbody>{klaer}</tbody></table></div>

      <h2>Freigeben und ausgeben</h2>
      <div class="karte">
        <form method="post" action="/uebersicht/{periode_id}/freigeben">
          <input type="hidden" name="csrf" value="{t}">
          <button class="knopf" type="submit">Alle Vorschläge freigeben</button>
        </form>
        <p class="marke-klein" style="margin-top:12px">
          <a href="/uebersicht/{periode_id}/export.xlsx">Als Eingabevorlage (.xlsx)</a>
          &nbsp;·&nbsp;
          <a href="/uebersicht/{periode_id}/export.json">Als JSON</a></p>
      </div>''', n)


@app.post('/uebersicht/{periode_id}/wert')
def wert_setzen(request: Request, periode_id: int, feld: str = Form(...),
                wert: str = Form(''), csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    import leser
    zahl = leser._zahl(wert) if wert.strip() else None
    if wert.strip() and zahl is None:
        return _zurueck(f'/uebersicht/{periode_id}/pruefen',
                        fehler=f'„{wert}" ist keine Zahl.')
    try:
        ue.wert_setzen(periode_id, feld, zahl, n['id'])
    except pd.Verweigert as e:
        return _zurueck(f'/uebersicht/{periode_id}/pruefen', fehler=str(e))
    return _zurueck(f'/uebersicht/{periode_id}/pruefen', meldung='Wert gesetzt.')


@app.post('/uebersicht/{periode_id}/klaerfall')
def klaerfall(request: Request, periode_id: int, klaerfall: int = Form(...),
              feld: str = Form(...), csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        ue.klaerfall_zuordnen(periode_id, klaerfall, feld, n['id'])
    except (pd.Verweigert, ValueError) as e:
        return _zurueck(f'/uebersicht/{periode_id}/pruefen', fehler=str(e))
    return _zurueck(f'/uebersicht/{periode_id}/pruefen',
                    meldung='Zugeordnet und für den Folgemonat gemerkt.')


@app.post('/uebersicht/{periode_id}/freigeben')
def freigeben(request: Request, periode_id: int, csrf: str = Form(...)):
    n = _nur_admin(request)
    if not n or not csrf_ok(n['id'], csrf):
        return RedirectResponse('/anmelden', status_code=303)
    try:
        anzahl = ue.freigeben(periode_id, n['id'])
    except pd.Verweigert as e:
        return _zurueck(f'/uebersicht/{periode_id}/pruefen', fehler=str(e))
    return _zurueck(f'/uebersicht/{periode_id}/pruefen',
                    meldung=f'{anzahl} Werte freigegeben.')


@app.get('/uebersicht/{periode_id}/export.json')
def export_json(request: Request, periode_id: int):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    p = pd.periode_nach_id(periode_id)
    return Response(ue.als_json(periode_id), media_type='application/json',
                    headers={'Content-Disposition':
                             f'attachment; filename="valtix-{p["jahr_monat"]}.json"'})


@app.get('/uebersicht/{periode_id}/export.xlsx')
def export_xlsx(request: Request, periode_id: int):
    n = _nur_admin(request)
    if not n:
        return RedirectResponse('/anmelden', status_code=303)
    p = pd.periode_nach_id(periode_id)
    db.protokollieren('export_xlsx', benutzer_id=n['id'], detail=f'periode {periode_id}')
    return Response(
        ue.als_xlsx(periode_id),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition':
                 f'attachment; filename="valtix-{p["jahr_monat"]}.xlsx"'})
