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
            links.append('<a href="/verwaltung">Verwaltung</a>')
            links.append('<a href="/protokoll">Protokoll</a>')
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
    return seite('Ihre Berichte', f'''{hinweis}
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
