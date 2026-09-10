# -*- coding: utf-8 -*-
"""Baut die Portalseite der Website.

Reine Vorfuehrung: kein Server, keine Datenbank, keine Speicherung. Firma und
Zahlen stammen aus der Beispieldatei des Berichtsgenerators, nichts ist
dazuerfunden.

Aufbau nach dem Entwurf: nach der Anmeldung zuerst ein Satz des Beraters,
danach die Kennzahlen nach Status gruppiert, erst dann die Zahlen im Detail.
Die Werte liest tools/bericht/matrix.py aus der Eingabevorlage, damit Portal
und Bericht nicht auseinanderlaufen.
"""
import json
import os
import sys

_HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HIER)
sys.path.insert(0, os.path.join(_HIER, 'bericht'))
from matrix import Matrix                                    # noqa: E402

QUELLE = os.environ.get('VALTIX_DEMO', '/tmp/demo.xlsx')
BERICHT = 'portal-vorschau-bericht.html'
M = Matrix(QUELLE)

KURZ = {'Januar': 'Jan', 'Februar': 'Feb', 'März': 'Mär', 'April': 'Apr',
        'Mai': 'Mai', 'Juni': 'Jun', 'Juli': 'Jul', 'August': 'Aug',
        'September': 'Sep', 'Oktober': 'Okt', 'November': 'Nov',
        'Dezember': 'Dez'}

# Wann der jeweilige Bericht eingestellt wurde. Erfundene, aber plausible
# Daten fuer die Vorfuehrung.
EINGESTELLT = ['06.02.2026', '05.03.2026', '07.04.2026', '06.05.2026',
               '05.06.2026', '07.07.2026', '06.08.2026']

# Was der Berater zum jeweiligen Monat schreibt. Jede Zahl darin stammt aus
# der Beispieldatei; wer hier etwas aendert, prueft sie gegen die Reihen.
KOMMENTARE = [
    'Der Start ins Jahr endet mit einem Verlust von 4.855 €. Vor Abschreibungen '
    'und Zinsen steht ein Plus von 4.671 €, das reicht aber nicht, um beides zu decken.',
    'Erstmals ein positives Ergebnis, wenn auch knapp. Der Kontostand sinkt trotzdem '
    'weiter, um 7.100 € gegenüber Januar.',
    'Ein deutlicher Sprung auf 12.038 € Ergebnis bei gestiegener Auslastung. Der '
    'Kontostand sinkt trotzdem, weil Ihre Kunden unverändert erst nach 44 Tagen zahlen.',
    'Etwas schwächer als im März: der Umsatz geht leicht zurück, das Ergebnis auf '
    '9.927 €. Ihre Kunden zahlen jetzt nach 46 statt nach 44 Tagen.',
    'Der Umsatz wächst, das Ergebnis nicht: die festen Kosten liegen rund 7.800 € '
    'über dem April. Wir sollten über die Personalkosten sprechen.',
    'Ein gutes Ergebnis von 18.519 €. Die Deckungsbeitragsquote ist erstmals unter '
    '62 % gefallen, das liegt am höheren Materialanteil.',
    'Der Umsatz liegt erstmals über Ihrem Monatsziel, das Ergebnis hat sich gegenüber '
    'Juni fast verdoppelt. Zwei Dinge sollten wir besprechen: der Kontostand sinkt seit '
    'Januar, und Ihre Kunden zahlen im Schnitt nach 48 Tagen, acht Tage über Ihrem '
    'eigenen Ziel.',
]

# Klarname und Erklaerung je Kennzahl. Der Fachbegriff steht in der Erklaerung,
# damit ihn findet, wer ihn kennt, ohne dass er die Zeile anfuehrt.
KENNZAHLEN = [
    ('umsatz', 'Umsatz', 'Was Sie im Monat in Rechnung gestellt haben'),
    ('ebt_marge', 'Gewinnmarge vor Steuern',
     'Gewinn vor Steuern, gemessen am Umsatz. Fachbegriff EBT-Marge'),
    ('db_quote', 'Was nach Material und Fremdleistung bleibt',
     'Anteil an der Gesamtleistung. Fachbegriff Deckungsbeitragsquote'),
    ('liquide', 'Kontostand', 'Bank und Kasse am Monatsende'),
    ('ek_quote', 'Eigenkapitalquote', 'Anteil des Eigenkapitals an der Bilanzsumme'),
    ('dso', 'Ihre Kunden zahlen nach',
     'Durchschnitt in Tagen. Fachbegriff Debitorenlaufzeit'),
    ('auslastung', 'Auslastung', 'Geleistete Stunden gemessen an Ihrer Kapazität'),
    ('aktive_kunden', 'Aktive Kunden', 'Objekte und Mandate mit Umsatz im Monat'),
    ('neukunden', 'Neukunden', 'Neue Kunden oder Aufträge im Monat'),
]

# Klarnamen der Detailzeilen. Was hier fehlt, behaelt die Beschriftung aus der
# Eingabevorlage, damit umbenannte Zeilen ihren Namen behalten.
DETAIL_NAMEN = {
    'umsatz': ('Umsatz', ''),
    'gesamtleistung': ('Gesamtleistung', ''),
    'variabel': ('Mengenabhängige Kosten', 'variable Kosten'),
    'db': ('Was danach bleibt', 'Deckungsbeitrag'),
    'db_quote': ('Anteil an der Gesamtleistung', 'Deckungsbeitragsquote'),
    'fix': ('Feste Kosten', 'Fixkosten'),
    'ebitda': ('Ergebnis vor Abschreibungen und Zinsen', 'EBITDA'),
    'afa': ('Abschreibungen', ''),
    'ebit': ('Ergebnis vor Zinsen', 'EBIT'),
    'zins': ('Zinsen', ''),
    'ebt': ('Gewinn vor Steuern', 'EBT'),
    'ebt_marge': ('Gewinnmarge vor Steuern', 'EBT-Marge'),
}


def daten():
    """Alles, was die Seite zum Zeichnen braucht, als eine Struktur."""
    monate = [{'lang': m, 'kurz': KURZ[m], 'eingestellt': EINGESTELLT[i]}
              for i, m in enumerate(M.monate)]

    kennzahlen = []
    for schluessel, klar, erklaerung in KENNZAHLEN:
        zl = M.zeile(schluessel)
        if zl is None or zl.ziel is None:
            continue
        kennzahlen.append({
            'klar': klar, 'erklaerung': erklaerung, 'art': zl.art,
            'ziel': zl.ziel, 'richtung': zl.richtung, 'reihe': zl.werte,
        })

    detail = []
    for kennung, _, zeilen in M.bloecke:
        if kennung != 'ergebnis':
            continue
        hat_kinder = {z.gruppe for z in zeilen if z.gruppe}
        for z in zeilen:
            klar, fach = DETAIL_NAMEN.get(z.schluessel, (z.titel, ''))
            kinder = [k for k in zeilen if k.gruppe == z.schluessel]
            detail.append({
                'schluessel': z.schluessel, 'klar': klar, 'fach': fach,
                'art': z.art, 'reihe': z.werte, 'minus': z.vorzeichen < 0,
                'stark': z.ebene == 0, 'kind': bool(z.gruppe),
                'gruppe': z.gruppe or '',
                'klappbar': z.schluessel in hat_kinder,
                'anzahl': len(kinder),
            })

    return {
        'firma': M.firma, 'branche': M.branche, 'jahr': M.jahr,
        'monate': monate, 'aktiv': M.aktiv, 'kommentare': KOMMENTARE,
        'kennzahlen': kennzahlen, 'detail': detail,
        'umsatz': M.zeile('umsatz').werte,
        'bericht': BERICHT,
    }



# Kennzahlen der Kopfzeile. Wenige, grosse Werte, damit die Seite einen
# Anfang hat, bevor die Bewertung kommt.
KOPFZAHLEN = ['umsatz', 'ebt', 'liquide']


def kopfzahlen():
    raus = []
    for schluessel in KOPFZAHLEN:
        zl = M.zeile(schluessel)
        if zl is None:
            continue
        klar = {'umsatz': 'Umsatz', 'ebt': 'Gewinn vor Steuern',
                'liquide': 'Kontostand'}[schluessel]
        raus.append({'klar': klar, 'art': zl.art, 'reihe': zl.werte})
    return raus


CSS = '''
:root{
  --ink:#232941; --ink-soft:#565D73; --muted:#8A8FA3;
  --navy:#232941; --navy-deep:#171B2C;
  --gold:#A6813F; --gold-deep:#7A6238; --cream:#F5EBD0;
  --bg:#FBF8F2;
  --serie-a:#404D97; --serie-b:#B0842A;
  --gruen:#0CA30C; --gruen-text:#0A7A0A;
  --gelb:#FAB219; --gelb-text:#8A6100;
  --rot:#D03B3B; --rot-text:#A32C2C;
  --glass:rgba(255,255,255,.62);
  --glass-strong:rgba(255,255,255,.82);
  --glass-border:rgba(255,255,255,.85);
  --glass-shadow:0 18px 50px rgba(35,41,65,.13);
  --hairline:rgba(35,41,65,.12);
  --r-lg:26px; --r-md:18px; --r-sm:12px; --r-pill:999px;
  --font:"Inter Tight",system-ui,-apple-system,"Segoe UI",sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--ink);
     font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased;
     min-height:100vh}
a{color:var(--gold-deep)}
button,input,select{font-family:inherit}
[hidden]{display:none!important}
:focus-visible{outline:3px solid var(--navy);outline-offset:3px;border-radius:8px}

/* Farbschleier wie auf der Website, damit die Flaechen auf etwas liegen */
.aurora{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none}
.aurora span{position:absolute;border-radius:50%;filter:blur(80px);opacity:.55}
.a1{width:60vw;height:60vw;max-width:780px;max-height:780px;left:-14vw;top:-18vw;
    background:radial-gradient(circle,#F0E2C2 0%,rgba(240,226,194,0) 70%)}
.a2{width:52vw;height:52vw;max-width:680px;max-height:680px;right:-12vw;top:-6vw;
    background:radial-gradient(circle,#D3D9E8 0%,rgba(211,217,232,0) 70%)}
.a3{width:46vw;height:46vw;max-width:600px;max-height:600px;left:26vw;top:52vw;
    background:radial-gradient(circle,#EFE0C6 0%,rgba(239,224,198,0) 70%);opacity:.42}

.glass{background:var(--glass);
  backdrop-filter:blur(22px) saturate(180%);
  -webkit-backdrop-filter:blur(22px) saturate(180%);
  border:1px solid var(--glass-border);
  box-shadow:var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.9)}
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
  .glass{background:rgba(255,255,255,.94)}
}
@media(prefers-reduced-transparency:reduce){
  .glass{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none}
}

h1{font-size:1.6rem;font-weight:800;letter-spacing:-.035em}
h2{font-size:1.06rem;font-weight:700;letter-spacing:-.025em}
.bahn{width:min(1180px,100% - 48px);margin-inline:auto}
@media(max-width:767px){.bahn{width:calc(100% - 28px)}}

/* Hinweisband */
.band{background:linear-gradient(180deg,var(--navy),var(--navy-deep));color:#fff;
  font-size:.84rem;padding:11px 0;
  box-shadow:0 8px 24px rgba(23,27,44,.18)}
.band .bahn{display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
.band b{font-weight:700}
.band span{color:rgba(255,255,255,.72)}
.band a{color:var(--cream)}

/* Anmeldung */
.tuer{padding:7vh 0 70px}
.tuer-karte{width:100%;max-width:452px;margin:0 auto;border-radius:var(--r-lg);
  padding:36px 34px 30px}
.marke{font-weight:800;letter-spacing:-.035em;font-size:1.08rem}
.marke span{font-weight:500;color:var(--ink-soft);margin-left:8px;font-size:.88rem}
.lead{color:var(--ink-soft);margin:8px 0 22px}
label{display:block;font-size:.86rem;font-weight:600;margin-bottom:6px}
input[type=email],input[type=password],input[type=text],select{width:100%;
  min-height:50px;font-size:1rem;color:var(--ink);background:rgba(255,255,255,.82);
  border:1px solid rgba(35,41,65,.16);border-radius:14px;padding:10px 15px;
  transition:border-color .2s ease,box-shadow .2s ease}
input:focus,select:focus{outline:none;border-color:var(--navy);
  box-shadow:0 0 0 3px rgba(35,41,65,.14)}
input:disabled,select:disabled{background:rgba(35,41,65,.04);color:var(--muted)}
.feld{margin-bottom:16px}
.pw-reihe{display:flex;gap:8px;align-items:stretch}
.pw-reihe input{flex:1;min-width:0}
.merken{display:flex;align-items:center;gap:10px;min-height:44px;padding:0 4px;
  border:0;background:none;cursor:pointer;color:var(--ink);font-size:.9rem}
.haken{width:22px;height:22px;border-radius:8px;border:1px solid rgba(35,41,65,.28);
  background:rgba(255,255,255,.9);display:flex;align-items:center;
  justify-content:center;flex:none;transition:background .18s ease,border-color .18s ease}
.merken[aria-checked=true] .haken{background:linear-gradient(180deg,var(--navy),var(--navy-deep));
  border-color:var(--navy);color:#fff;box-shadow:0 4px 10px rgba(35,41,65,.28)}
.merken[aria-checked=false] .haken svg{display:none}
.zeile-merken{display:flex;align-items:center;gap:12px;margin-bottom:20px}
.knopf{display:inline-flex;align-items:center;justify-content:center;gap:8px;
  min-height:50px;padding:0 24px;border-radius:var(--r-pill);border:0;font:inherit;
  font-size:1rem;font-weight:600;letter-spacing:-.01em;cursor:pointer;
  text-decoration:none;color:#fff;
  background:linear-gradient(180deg,var(--navy) 0%,var(--navy-deep) 100%);
  box-shadow:0 8px 20px rgba(35,41,65,.32), inset 0 1px 0 rgba(255,255,255,.35);
  transition:transform .2s ease,box-shadow .2s ease}
.knopf:hover{transform:translateY(-2px);
  box-shadow:0 12px 26px rgba(35,41,65,.4), inset 0 1px 0 rgba(255,255,255,.35)}
.knopf.breit{width:100%}
.knopf.stumm{background:rgba(255,255,255,.66);color:var(--ink);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border:1px solid var(--glass-border);
  box-shadow:0 6px 18px rgba(35,41,65,.10), inset 0 1px 0 rgba(255,255,255,.9)}
.knopf.stumm:hover{box-shadow:0 10px 24px rgba(35,41,65,.14), inset 0 1px 0 rgba(255,255,255,.9)}
.knopf.hell{background:var(--cream);color:var(--navy);
  box-shadow:0 8px 20px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.6)}
.knopf.schmal{min-height:40px;padding:0 17px;font-size:.86rem}
.knopf:disabled{opacity:.5;box-shadow:none;cursor:not-allowed;transform:none}
.meldung{display:flex;gap:10px;align-items:flex-start;
  background:rgba(208,59,59,.09);color:#8B1F1F;border:1px solid rgba(208,59,59,.2);
  border-radius:14px;padding:12px 14px;margin-bottom:16px;font-size:.9rem}
.meldung svg{flex:none;margin-top:2px}
.demo{background:linear-gradient(180deg,rgba(245,235,208,.9),rgba(245,235,208,.6));
  border:1px solid rgba(122,98,56,.24);border-radius:var(--r-md);
  padding:15px 17px;margin-bottom:18px;font-size:.88rem;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.7)}
.demo b{display:block;font-size:.68rem;text-transform:uppercase;
  letter-spacing:.12em;color:var(--gold-deep);margin-bottom:8px}
.demo dl{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;align-items:baseline}
.demo dt{color:var(--ink-soft)}
.demo dd{min-width:0;overflow-wrap:anywhere}
.demo p{margin-top:9px;color:var(--ink-soft);font-size:.8rem}
code{background:rgba(35,41,65,.07);padding:2px 6px;border-radius:6px;font-size:.86rem}

/* Kopf des Portals */
.kopf{position:sticky;top:14px;z-index:60;margin-top:14px}
.kopf-innen{border-radius:var(--r-pill);padding:9px 10px 9px 22px;display:flex;
  align-items:center;gap:14px;flex-wrap:wrap}
.wechsler{display:flex;align-items:center;gap:6px;margin:0 auto;
  background:rgba(35,41,65,.05);border-radius:var(--r-pill);padding:4px}
.pfeil{width:42px;height:42px;border-radius:var(--r-pill);border:0;
  background:rgba(255,255,255,.9);color:var(--ink);cursor:pointer;display:flex;
  align-items:center;justify-content:center;
  box-shadow:0 2px 6px rgba(35,41,65,.16), inset 0 1px 0 rgba(255,255,255,.9);
  transition:transform .18s ease}
.pfeil:hover:not(:disabled){transform:translateY(-1px)}
.pfeil:disabled{color:#C4C7D2;cursor:default;box-shadow:none;background:transparent}
.wechsler-text{min-width:158px;text-align:center;padding:0 4px}
.wechsler-text b{display:block;font-size:.98rem;font-weight:700;letter-spacing:-.025em}
.wechsler-text span{font-size:.75rem;color:var(--ink-soft)}
.nutzer{display:flex;align-items:center;gap:11px}
.nutzer-text{text-align:right}
.nutzer-text b{display:block;font-size:.83rem;font-weight:700;line-height:1.3}
.nutzer-text span{font-size:.75rem;color:var(--ink-soft)}
.signet{width:38px;height:38px;border-radius:13px;flex:none;color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:.75rem;
  font-weight:700;letter-spacing:.02em;
  background:linear-gradient(150deg,var(--gold) 0%,var(--gold-deep) 100%);
  box-shadow:0 6px 16px rgba(122,98,56,.34), inset 0 1px 0 rgba(255,255,255,.35)}

/* Reiter als Segmentschalter */
.reiter{margin-top:18px;display:flex}
.reiter-innen{display:inline-flex;gap:4px;border-radius:var(--r-pill);padding:5px;
  overflow-x:auto;max-width:100%}
.reiter button{border:0;background:none;cursor:pointer;padding:0 20px;min-height:42px;
  border-radius:var(--r-pill);font-size:.92rem;font-weight:600;color:var(--ink-soft);
  white-space:nowrap;transition:color .18s ease,background .18s ease,box-shadow .18s ease}
.reiter button:hover{color:var(--ink)}
.reiter button[aria-selected=true]{color:#fff;
  background:linear-gradient(180deg,var(--navy),var(--navy-deep));
  box-shadow:0 6px 16px rgba(35,41,65,.28), inset 0 1px 0 rgba(255,255,255,.3)}

.flaeche{padding:18px 0 56px;display:flex;flex-direction:column;gap:18px}

/* Kommentar als dunkle Buehne */
.kommentar{position:relative;overflow:hidden;border-radius:var(--r-lg);
  padding:30px 32px;color:#fff;
  background:linear-gradient(155deg,#2B3251 0%,var(--navy) 42%,var(--navy-deep) 100%);
  box-shadow:0 26px 60px rgba(23,27,44,.32), inset 0 1px 0 rgba(255,255,255,.14);
  display:flex;gap:26px;flex-wrap:wrap;align-items:center}
.kommentar::after{content:"";position:absolute;left:-70px;bottom:-160px;width:420px;
  height:420px;border-radius:50%;pointer-events:none;
  background:radial-gradient(circle,rgba(166,129,63,.3) 0%,rgba(166,129,63,0) 68%)}
.kommentar-text{flex:1;min-width:270px;position:relative}
.kommentar .kennung{font-size:.7rem;text-transform:uppercase;letter-spacing:.14em;
  color:var(--cream);font-weight:700;margin-bottom:10px}
.kommentar p{font-size:1.12rem;line-height:1.5;max-width:70ch;text-wrap:pretty;
  color:rgba(255,255,255,.94)}
.kommentar-knoepfe{display:flex;flex-direction:column;gap:9px;position:relative}
.kommentar-knoepfe .knopf{min-height:46px;white-space:nowrap}

/* Kennzahlen der Kopfzeile */
.kacheln{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.kachel{border-radius:var(--r-md);padding:20px 22px;
  transition:transform .28s ease,box-shadow .28s ease}
.kachel:hover{transform:translateY(-4px);
  box-shadow:0 26px 60px rgba(35,41,65,.16), inset 0 1px 0 rgba(255,255,255,.9)}
.kachel .titel{font-size:.78rem;color:var(--ink-soft);letter-spacing:.01em}
.kachel .wert{display:block;font-size:1.72rem;font-weight:800;letter-spacing:-.045em;
  line-height:1.14;margin-top:4px;font-variant-numeric:tabular-nums}
.kachel .delta{display:inline-flex;align-items:center;gap:5px;margin-top:8px;
  font-size:.78rem;font-weight:600;padding:3px 10px;border-radius:var(--r-pill)}
.d-hoch{background:rgba(12,163,12,.11);color:var(--gruen-text)}
.d-runter{background:rgba(208,59,59,.1);color:var(--rot-text)}

/* Zweispaltige Bahn */
.spalten{display:grid;grid-template-columns:minmax(0,1fr) 352px;gap:18px;
  align-items:start}
.saeule-rechts{display:flex;flex-direction:column;gap:18px;position:sticky;top:92px}

/* Statusgruppen */
.gruppe{border-radius:var(--r-md);overflow:hidden}
.gruppe-kopf{width:100%;display:flex;align-items:center;gap:11px;padding:15px 22px;
  min-height:56px;border:0;background:none;cursor:pointer;text-align:left;
  font-size:.96rem;transition:background .18s ease}
.gruppe-kopf:hover{background:rgba(255,255,255,.4)}
.gruppe-kopf .zeichen{width:26px;height:26px;border-radius:var(--r-pill);color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:.84rem;
  font-weight:800;flex:none}
.gruppe-kopf .titel{font-weight:700;letter-spacing:-.025em}
.gruppe-kopf .anzahl{color:var(--ink-soft);font-size:.84rem}
.gruppe-kopf .klapp{margin-left:auto;color:var(--ink-soft);font-size:.82rem;
  display:inline-flex;align-items:center;gap:7px}
.gruppe-kopf .pfeilchen{transition:transform .2s ease}
.gruppe-kopf[aria-expanded=true] .pfeilchen{transform:rotate(180deg)}
.g-rot .zeichen{background:linear-gradient(160deg,#E05C5C,var(--rot));
  box-shadow:0 4px 12px rgba(208,59,59,.4)}
.g-rot .titel{color:var(--rot-text)}
.g-gelb .zeichen{background:linear-gradient(160deg,#FBC44A,var(--gelb));
  box-shadow:0 4px 12px rgba(250,178,25,.4)}
.g-gelb .titel{color:var(--gelb-text)}
.g-gruen .zeichen{background:linear-gradient(160deg,#3EBE3E,var(--gruen));
  box-shadow:0 4px 12px rgba(12,163,12,.35)}
.g-gruen .titel{color:var(--gruen-text)}
.posten-liste{padding:0 10px 10px}
.posten{display:grid;grid-template-columns:minmax(0,1fr) auto auto;
  gap:6px 18px;align-items:center;padding:14px 16px;border-radius:14px;
  background:rgba(255,255,255,.5);margin-bottom:6px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.8)}
.posten:last-child{margin-bottom:0}
.posten .name{font-size:1rem;font-weight:600;letter-spacing:-.015em}
.posten .erklaerung{font-size:.81rem;color:var(--ink-soft);margin-top:1px}
.posten .wert{grid-column:2;text-align:right;font-size:1.28rem;font-weight:800;
  letter-spacing:-.04em;font-variant-numeric:tabular-nums;white-space:nowrap}
.posten .tat{grid-column:3;grid-row:1 / span 2;text-align:right}
.posten .unten{grid-column:1 / span 2;display:flex;gap:10px;align-items:baseline;
  flex-wrap:wrap;font-size:.82rem;color:var(--ink-soft);
  font-variant-numeric:tabular-nums}
.marke-ziel{display:inline-flex;align-items:center;padding:2px 9px;border-radius:var(--r-pill);
  background:rgba(35,41,65,.06);font-weight:600;color:var(--ink-soft)}
.abstand{font-weight:600}
.a-gruen{color:var(--gruen-text)} .a-gelb{color:var(--gelb-text)}
.a-rot{color:var(--rot-text)}

/* Karten rechts */
.karte{border-radius:var(--r-md);padding:20px 22px 22px}
.karte h2{margin-bottom:2px}
.hinweis{font-size:.82rem;color:var(--ink-soft)}
.saeulen{display:flex;align-items:flex-end;gap:8px;height:172px;margin-top:16px}
.saeule{flex:1;display:flex;flex-direction:column;align-items:center;gap:7px;
  cursor:pointer;align-self:stretch;justify-content:flex-end;border:0;
  background:none;padding:0;min-width:0}
.saeule .zahl{font-size:.74rem;font-weight:700;color:var(--ink);
  font-variant-numeric:tabular-nums;white-space:nowrap;height:1.1em}
.saeule .balken{width:100%;border-radius:7px 7px 3px 3px;
  background:linear-gradient(180deg,rgba(64,77,151,.34),rgba(64,77,151,.18));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5);transition:background .2s ease}
.saeule:hover .balken{background:linear-gradient(180deg,rgba(64,77,151,.5),rgba(64,77,151,.28))}
.saeule .monat{font-size:.78rem;color:var(--muted)}
.saeule[aria-current] .balken{background:linear-gradient(180deg,#4E5CAB,var(--serie-a));
  box-shadow:0 8px 18px rgba(64,77,151,.35), inset 0 1px 0 rgba(255,255,255,.3)}
.saeule[aria-current] .monat{color:var(--ink);font-weight:700}
.bericht-karte .zeilen{margin-top:12px;display:flex;flex-direction:column;gap:9px}
.bericht-zeile{display:flex;justify-content:space-between;gap:12px;font-size:.88rem;
  padding-bottom:9px;border-bottom:1px solid rgba(35,41,65,.09)}
.bericht-zeile:last-of-type{border-bottom:0;padding-bottom:0}
.bericht-zeile span{color:var(--ink-soft)}
.bericht-zeile b{font-weight:600;font-variant-numeric:tabular-nums}
.bericht-karte .knopf{margin-top:14px;width:100%}

/* Zahlen im Detail */
.tabellenkarte{border-radius:var(--r-md);overflow:hidden}
.tabellenkopf{padding:20px 24px 16px}
.rahmen{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:.89rem;
  min-width:760px}
th,td{padding:11px 16px;text-align:left;font-weight:400;white-space:nowrap;
  border-bottom:1px solid rgba(35,41,65,.07)}
thead th{font-size:.68rem;text-transform:uppercase;letter-spacing:.09em;
  color:var(--ink-soft);font-weight:700;background:rgba(35,41,65,.045);
  border-bottom:1px solid rgba(35,41,65,.1);position:sticky;top:0;z-index:2}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:hover td,tbody tr:hover th{background:rgba(255,255,255,.55)}
tr.summe td,tr.summe th{font-weight:700;background:rgba(35,41,65,.045);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.7)}
tr.summe:hover td,tr.summe:hover th{background:rgba(35,41,65,.065)}
.pos{min-width:300px;white-space:normal}
.pos .fach{font-size:.77rem;color:var(--muted);margin-left:8px}
.kindzeile .pos{padding-left:38px;color:var(--ink-soft)}
td.minus{color:var(--gold-deep)}
.oeffnen{min-height:28px;padding:0 12px;border-radius:var(--r-pill);
  border:1px solid rgba(35,41,65,.16);background:rgba(255,255,255,.8);
  color:var(--ink-soft);font-size:.75rem;font-weight:600;cursor:pointer;
  margin-right:10px;white-space:nowrap;
  box-shadow:0 2px 5px rgba(35,41,65,.08)}
.oeffnen:hover{color:var(--ink)}
.hoch{color:var(--gruen-text)} .runter{color:var(--rot-text)}
.tabellenfuss{padding:14px 24px 18px;font-size:.8rem;color:var(--ink-soft)}

/* Verwaltung */
.status.gut{color:var(--gruen-text);font-weight:600;font-size:.86rem}
.status.offen{color:var(--gold-deep);font-weight:600;font-size:.86rem}
.formular{max-width:470px;padding:20px 24px 24px}
.formular .knopf{margin-top:18px}

.fuss{padding:0 0 40px;font-size:.78rem;color:var(--ink-soft)}

@media(max-width:1020px){
  .spalten{grid-template-columns:minmax(0,1fr)}
  .saeule-rechts{position:static;flex-direction:row;flex-wrap:wrap}
  .saeule-rechts > *{flex:1 1 300px}
}
@media(max-width:860px){
  .kopf{top:8px;margin-top:10px}
  .kopf-innen{border-radius:var(--r-lg);padding:12px 14px;gap:10px}
  .marke{flex:1}
  .nutzer{order:2;width:100%;gap:10px}
  .nutzer-text{flex:1;text-align:left;min-width:0}
  .nutzer-text b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .wechsler{order:3;width:100%;margin:0}
  .wechsler-text{flex:1;min-width:0}
  .reiter-innen{width:100%}
  .kacheln{grid-template-columns:1fr}
  .kommentar{padding:24px 22px;gap:18px}
  .kommentar p{font-size:1.04rem}
  .kommentar-knoepfe{flex-direction:row;flex-wrap:wrap;width:100%}
  .kommentar-knoepfe .knopf{flex:1}
  .posten{grid-template-columns:minmax(0,1fr) auto;padding:13px 14px}
  .posten .erklaerung{display:none}
  .posten .tat{grid-column:1 / span 2;grid-row:3;text-align:left;margin-top:8px}
  .posten .tat .knopf{width:100%}
  .posten .unten{grid-row:2}
  .gruppe-kopf{flex-wrap:wrap;row-gap:2px;padding:14px 16px}
  .gruppe-kopf .titel{flex:1;min-width:0}
  .gruppe-kopf .anzahl{width:100%;padding-left:37px;order:4}
  .posten-liste{padding:0 8px 8px}
  .saeulen{height:140px;gap:5px}
}
'''

JS = r'''
(function () {
  var D = window.__valtix;
  var stand = { monat: D.aktiv, reiter: 'ueberblick',
                auf: { rot: true, gelb: true, gruen: false },
                offen: {}, gemerkt: true, sichtbar: false };

  function tausend(s) { return s.replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function eur(w) {
    if (w === null || w === undefined) return '–';
    return (w < 0 ? '−' : '') + tausend(Math.abs(w).toFixed(0)) + ' €';
  }
  function proz(w) {
    if (w === null || w === undefined) return '–';
    return w.toFixed(1).replace('.', ',').replace('-', '−') + ' %';
  }
  function tage(w) { return w === null || w === undefined ? '–' : w.toFixed(0) + ' Tage'; }
  function zahl(w) { return w === null || w === undefined ? '–' : w.toFixed(0); }
  function fmt(art, w) {
    return art === 'geld' ? eur(w) : art === 'prozent' ? proz(w)
         : art === 'tage' ? tage(w) : zahl(w);
  }
  function el(tag, klasse, text) {
    var e = document.createElement(tag);
    if (klasse) e.className = klasse;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }
  function svg(pfad, groesse, klasse) {
    var s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('width', groesse); s.setAttribute('height', groesse);
    s.setAttribute('fill', 'none'); s.setAttribute('stroke', 'currentColor');
    s.setAttribute('stroke-width', '2.2'); s.setAttribute('stroke-linecap', 'round');
    s.setAttribute('stroke-linejoin', 'round');
    s.setAttribute('aria-hidden', 'true');
    if (klasse) s.setAttribute('class', klasse);
    var p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', pfad);
    s.appendChild(p);
    return s;
  }

  // Der Abstand zu einem Prozentziel sind Prozentpunkte, nicht Prozent.
  function abstandText(art, w) {
    return art === 'prozent' ? proz(w).replace(' %', ' %-Pkt.') : fmt(art, w);
  }

  function bewerten(k, i) {
    var ist = k.reihe[i];
    if (ist === null || ist === undefined || !k.ziel) return null;
    // Abweichung als Anteil des Ziels, damit die Gelbschwelle in beide
    // Richtungen bei zehn Prozent liegt.
    var erreicht = k.richtung === 'hoeher' ? ist >= k.ziel : ist <= k.ziel;
    var daneben = Math.abs(ist - k.ziel) / Math.abs(k.ziel);
    return { stufe: erreicht ? 'gruen' : (daneben <= 0.1 ? 'gelb' : 'rot'), erreicht: erreicht };
  }

  function kopf() {
    var m = D.monate[stand.monat];
    document.getElementById('monat-name').textContent = m.lang + ' ' + D.jahr;
    document.getElementById('monat-stand').textContent = 'Bericht vom ' + m.eingestellt;
    document.getElementById('pfeil-zurueck').disabled = stand.monat === 0;
    document.getElementById('pfeil-vor').disabled = stand.monat === D.monate.length - 1;
  }

  function kacheln(i, vor) {
    var reihe = el('div', 'kacheln');
    D.kopfzahlen.forEach(function (k) {
      var kachel = el('div', 'kachel glass');
      kachel.appendChild(el('span', 'titel', k.klar));
      kachel.appendChild(el('b', 'wert', fmt(k.art, k.reihe[i])));
      if (vor !== null && k.reihe[vor]) {
        var v = (k.reihe[i] - k.reihe[vor]) / Math.abs(k.reihe[vor]) * 100;
        var d = el('span', 'delta ' + (v >= 0 ? 'd-hoch' : 'd-runter'));
        d.appendChild(svg(v >= 0 ? 'M12 19V5M6 11l6-6 6 6' : 'M12 5v14M6 13l6 6 6-6', 13));
        d.appendChild(document.createTextNode(
          Math.abs(v).toFixed(1).replace('.', ',') + ' % zum Vormonat'));
        kachel.appendChild(d);
      }
      reihe.appendChild(kachel);
    });
    return reihe;
  }

  function gruppe(schluessel, titel, zeichen, liste, i, vor) {
    var box = el('section', 'gruppe glass g-' + schluessel);
    var k = el('button', 'gruppe-kopf');
    k.type = 'button';
    k.setAttribute('aria-expanded', String(stand.auf[schluessel]));
    k.appendChild(el('span', 'zeichen', zeichen));
    k.appendChild(el('span', 'titel', titel));
    k.appendChild(el('span', 'anzahl',
      liste.length === 1 ? '1 Kennzahl' : liste.length + ' Kennzahlen'));
    var klapp = el('span', 'klapp');
    klapp.appendChild(document.createTextNode(stand.auf[schluessel] ? 'zuklappen' : 'anzeigen'));
    klapp.appendChild(svg('M6 9l6 6 6-6', 15, 'pfeilchen'));
    k.appendChild(klapp);
    k.addEventListener('click', function () {
      stand.auf[schluessel] = !stand.auf[schluessel];
      zeichnen();
    });
    box.appendChild(k);
    if (!stand.auf[schluessel]) return box;

    var liste_el = el('div', 'posten-liste');
    liste.forEach(function (p) {
      var kz = p.kz, ist = kz.reihe[i];
      var z = el('div', 'posten');
      var nf = el('div', 'name-feld');
      nf.appendChild(el('div', 'name', kz.klar));
      nf.appendChild(el('div', 'erklaerung', kz.erklaerung));
      z.appendChild(nf);
      z.appendChild(el('div', 'wert', fmt(kz.art, ist)));

      var t = el('div', 'tat');
      if (p.b.erreicht) {
        t.appendChild(el('span', 'abstand a-gruen',
          abstandText(kz.art, Math.abs(ist - kz.ziel)) + ' besser'));
      } else {
        var nach = el('button', 'knopf stumm schmal', 'Dazu nachfragen');
        nach.type = 'button';
        t.appendChild(nach);
      }
      z.appendChild(t);

      var unten = el('div', 'unten');
      unten.appendChild(el('span', 'marke-ziel',
        (kz.richtung === 'hoeher' ? 'Ziel ab ' : 'Ziel bis ') + fmt(kz.art, kz.ziel)));
      if (!p.b.erreicht) {
        unten.appendChild(el('span', 'abstand a-' + p.b.stufe,
          abstandText(kz.art, Math.abs(ist - kz.ziel)) + ' entfernt'));
      }
      unten.appendChild(el('span', null, vor === null ? 'kein Vormonat'
        : 'Vormonat ' + fmt(kz.art, kz.reihe[vor])));
      z.appendChild(unten);
      liste_el.appendChild(z);
    });
    box.appendChild(liste_el);
    return box;
  }

  function verlauf(i) {
    var v = el('section', 'karte glass');
    v.appendChild(el('h2', null, 'Umsatz im Jahresverlauf'));
    v.appendChild(el('p', 'hinweis', 'Wählen Sie einen Monat aus'));
    var reihe = el('div', 'saeulen');
    var hoch = Math.max.apply(null, D.umsatz);
    D.umsatz.forEach(function (w, idx) {
      var s = el('button', 'saeule');
      s.type = 'button';
      if (idx === i) s.setAttribute('aria-current', 'true');
      s.setAttribute('aria-label', D.monate[idx].lang + ', ' + eur(w));
      s.appendChild(el('span', 'zahl', idx === i ? eur(w) : ''));
      var b = el('span', 'balken');
      b.style.height = Math.round(w / hoch * 108) + 'px';
      s.appendChild(b);
      s.appendChild(el('span', 'monat', D.monate[idx].kurz));
      s.addEventListener('click', function () { stand.monat = idx; zeichnen(); });
      reihe.appendChild(s);
    });
    v.appendChild(reihe);
    return v;
  }

  function berichtkarte(i, vor) {
    var b = el('section', 'karte glass bericht-karte');
    b.appendChild(el('h2', null, 'Ihr Bericht'));
    b.appendChild(el('p', 'hinweis', 'Die ausführliche Fassung mit allen Auswertungen.'));
    var zeilen = el('div', 'zeilen');
    [['Berichtsmonat', D.monate[i].lang + ' ' + D.jahr],
     ['Eingestellt am', D.monate[i].eingestellt],
     ['Verglichen mit', vor === null ? 'kein Vormonat' : D.monate[vor].lang],
     ['Grundlage', 'Ihre Eingabevorlage']].forEach(function (r) {
      var z = el('div', 'bericht-zeile');
      z.appendChild(el('span', null, r[0]));
      z.appendChild(el('b', null, r[1]));
      zeilen.appendChild(z);
    });
    b.appendChild(zeilen);
    var a = el('a', 'knopf stumm', 'Vollständigen Bericht öffnen');
    a.href = D.bericht;
    b.appendChild(a);
    return b;
  }

  function ueberblick() {
    var i = stand.monat, vor = i > 0 ? i - 1 : null;
    var raus = document.createDocumentFragment();

    var k = el('section', 'kommentar');
    var kt = el('div', 'kommentar-text');
    kt.appendChild(el('div', 'kennung', 'Das sagt Ihr Berater zum ' + D.monate[i].lang));
    kt.appendChild(el('p', null, D.kommentare[i]));
    k.appendChild(kt);
    var kn = el('div', 'kommentar-knoepfe');
    var frage = el('button', 'knopf hell', 'Rückfrage stellen');
    frage.type = 'button';
    kn.appendChild(frage);
    k.appendChild(kn);
    raus.appendChild(k);

    raus.appendChild(kacheln(i, vor));

    var faecher = { rot: [], gelb: [], gruen: [] };
    D.kennzahlen.forEach(function (kz) {
      var b = bewerten(kz, i);
      if (b) faecher[b.stufe].push({ kz: kz, b: b });
    });

    var spalten = el('div', 'spalten');
    var links = el('div', 'saeule-links');
    links.style.display = 'flex';
    links.style.flexDirection = 'column';
    links.style.gap = '18px';
    [['rot', 'Braucht Aufmerksamkeit', '!'],
     ['gelb', 'Im Blick behalten', '•'],
     ['gruen', 'Läuft nach Plan', '✓']].forEach(function (g) {
      if (faecher[g[0]].length) {
        links.appendChild(gruppe(g[0], g[1], g[2], faecher[g[0]], i, vor));
      }
    });
    spalten.appendChild(links);

    var rechts = el('div', 'saeule-rechts');
    rechts.appendChild(verlauf(i));
    rechts.appendChild(berichtkarte(i, vor));
    spalten.appendChild(rechts);
    raus.appendChild(spalten);
    return raus;
  }

  function detail() {
    var i = stand.monat, vor = i > 0 ? i - 1 : null;
    var karte = el('section', 'tabellenkarte glass');
    var kk = el('div', 'tabellenkopf');
    kk.appendChild(el('h2', null, 'Ergebnisrechnung ' + D.monate[i].lang + ' ' + D.jahr));
    kk.appendChild(el('p', 'hinweis', vor === null
      ? 'Für diesen Monat gibt es keinen Vormonat zum Vergleich.'
      : 'Verglichen wird mit ' + D.monate[vor].lang + '. Blöcke lassen sich öffnen.'));
    karte.appendChild(kk);

    var rahmen = el('div', 'rahmen');
    var t = el('table');
    var kopfZ = el('tr');
    ['Position', D.monate[i].kurz + ' ' + String(D.jahr).slice(-2),
     vor === null ? '–' : D.monate[vor].kurz + ' ' + String(D.jahr).slice(-2),
     'Veränderung'].forEach(function (txt, sp) {
      kopfZ.appendChild(el('th', sp ? 'num' : 'pos', txt));
    });
    var thead = el('thead'); thead.appendChild(kopfZ); t.appendChild(thead);

    var tbody = el('tbody');
    D.detail.forEach(function (z) {
      if (z.kind && !stand.offen[z.gruppe]) return;
      var tr = el('tr', (z.stark ? 'summe ' : '') + (z.kind ? 'kindzeile' : ''));
      var th = el('th', 'pos');
      th.scope = 'row';
      if (z.klappbar) {
        var b = el('button', 'oeffnen',
          stand.offen[z.schluessel] ? 'schließen' : z.anzahl + ' Posten');
        b.type = 'button';
        b.setAttribute('aria-expanded', String(!!stand.offen[z.schluessel]));
        b.addEventListener('click', function () {
          stand.offen[z.schluessel] = !stand.offen[z.schluessel];
          zeichnen();
        });
        th.appendChild(b);
      }
      th.appendChild(document.createTextNode(z.klar));
      if (z.fach) th.appendChild(el('span', 'fach', z.fach));
      tr.appendChild(th);

      var vz = z.minus ? -1 : 1;
      tr.appendChild(el('td', 'num' + (z.minus ? ' minus' : ''),
        fmt(z.art, z.reihe[i] === null ? null : z.reihe[i] * vz)));
      tr.appendChild(el('td', 'num', vor === null ? '–'
        : fmt(z.art, z.reihe[vor] === null ? null : z.reihe[vor] * vz)));

      var dtxt = '', dkl = 'num';
      if (vor !== null && z.reihe[i] !== null && z.reihe[vor] !== null) {
        var diff = z.reihe[i] - z.reihe[vor];
        if (z.art === 'prozent') {
          dtxt = (diff >= 0 ? '+' : '−')
               + Math.abs(diff).toFixed(1).replace('.', ',') + ' %-Pkt.';
        } else if (diff === 0) {
          dtxt = 'unverändert';
        } else if (z.reihe[vor]) {
          var pz = diff / Math.abs(z.reihe[vor]) * 100;
          var kern = Math.abs(pz).toFixed(1).replace('.', ',') + ' %';
          // Kostenzeilen stehen negativ in der Spalte. Ein Vorzeichen davor
          // waere doppeldeutig, deshalb steht dort mehr oder weniger.
          dtxt = z.minus ? kern + (diff >= 0 ? ' mehr' : ' weniger')
                         : (diff >= 0 ? '+' : '−') + kern;
        }
        if (diff !== 0) dkl += (z.minus ? diff < 0 : diff > 0) ? ' hoch' : ' runter';
      }
      tr.appendChild(el('td', dkl, dtxt));
      tbody.appendChild(tr);
    });
    t.appendChild(tbody);
    rahmen.appendChild(t);
    karte.appendChild(rahmen);
    karte.appendChild(el('p', 'tabellenfuss',
      'Alle Beträge netto. Grundlage ist die ausgefüllte Eingabevorlage.'));
    return karte;
  }

  function zeichnen() {
    kopf();
    document.querySelectorAll('.reiter button').forEach(function (b) {
      b.setAttribute('aria-selected', String(b.dataset.reiter === stand.reiter));
    });
    document.querySelectorAll('.verwaltung').forEach(function (v) {
      v.hidden = v.dataset.reiter !== stand.reiter;
    });
    var ziel = document.getElementById('flaeche');
    ziel.innerHTML = '';
    if (stand.reiter === 'ueberblick') ziel.appendChild(ueberblick());
    else if (stand.reiter === 'detail') ziel.appendChild(detail());
  }

  document.getElementById('pfeil-zurueck').addEventListener('click', function () {
    if (stand.monat > 0) { stand.monat--; zeichnen(); }
  });
  document.getElementById('pfeil-vor').addEventListener('click', function () {
    if (stand.monat < D.monate.length - 1) { stand.monat++; zeichnen(); }
  });
  document.querySelectorAll('.reiter button').forEach(function (b) {
    b.addEventListener('click', function () { stand.reiter = b.dataset.reiter; zeichnen(); });
  });

  var pw = document.getElementById('pw');
  var mail = document.getElementById('mail');
  var fehler = document.getElementById('fehler');
  function melden(text) {
    document.getElementById('fehlertext').textContent = text;
    fehler.hidden = false;
  }
  document.getElementById('anmeldung').addEventListener('submit', function (e) {
    e.preventDefault();
    if (!mail.value.trim()) { melden('Bitte tragen Sie Ihre E-Mail-Adresse ein.'); return; }
    if (pw.value !== 'Vorschau2026') {
      melden('Das Passwort stimmt nicht. Prüfen Sie die Groß- und Kleinschreibung.');
      return;
    }
    fehler.hidden = true;
    oeffnen('app');
  });
  document.getElementById('sichtbar').addEventListener('click', function () {
    stand.sichtbar = !stand.sichtbar;
    pw.type = stand.sichtbar ? 'text' : 'password';
    this.textContent = stand.sichtbar ? 'Verbergen' : 'Anzeigen';
  });
  var merken = document.getElementById('merken');
  merken.addEventListener('click', function () {
    stand.gemerkt = !stand.gemerkt;
    merken.setAttribute('aria-checked', String(stand.gemerkt));
  });
  document.querySelectorAll('[data-abmelden]').forEach(function (b) {
    b.addEventListener('click', function () { oeffnen('anmelden'); });
  });

  function oeffnen(was) {
    document.getElementById('bs-anmelden').hidden = was !== 'anmelden';
    document.getElementById('bs-app').hidden = was === 'anmelden';
    window.scrollTo(0, 0);
    if (history.replaceState) {
      history.replaceState(null, '', was === 'anmelden' ? location.pathname
        : '#ansicht-' + stand.reiter);
    }
    if (was !== 'anmelden') zeichnen();
  }

  // Die Verwaltung ist nur ueber die Adresse erreichbar, nicht ueber die
  // Anmeldung. Ihre Reiter erscheinen auch nur dann.
  var start = location.hash.replace('#ansicht-', '');
  if (['mandanten', 'zugaenge', 'protokoll'].indexOf(start) >= 0) {
    stand.reiter = start;
    document.querySelectorAll('.nur-admin').forEach(function (e) { e.hidden = false; });
    oeffnen('app');
  } else if (start === 'detail') {
    stand.reiter = 'detail';
  }
})();
'''


def initialen(name):
    teile = [t for t in name.split() if t]
    return (teile[0][0] + (teile[1][0] if len(teile) > 1 else '')).upper()


def pfad(d, groesse=18, klasse=''):
    k = f' class="{klasse}"' if klasse else ''
    return (f'<svg width="{groesse}" height="{groesse}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true"{k}><path d="{d}"/></svg>')


PFEIL_LINKS = pfad('M15 5l-7 7 7 7')
PFEIL_RECHTS = pfad('M9 5l7 7-7 7')
HAKEN = pfad('M5 12.5l4.5 4.5L19 7', 14)
WARNUNG = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
           'aria-hidden="true"><path d="M12 7v6M12 17h.01"/>'
           '<circle cx="12" cy="12" r="9"/></svg>')

AURORA = ('<div class="aurora" aria-hidden="true"><span class="a1"></span>'
          '<span class="a2"></span><span class="a3"></span></div>')

BAND = '''<div class="band"><div class="bahn">
  <b>Demonstration</b>
  <span>Diese Ansicht dient der Vorführung. Es wird nichts gespeichert und nichts
    übertragen. Firma und Zahlen sind erfunden.</span>
  <a href="index.html">Zurück zur Website</a>
</div></div>'''

ANMELDEN = f'''<section id="bs-anmelden"><div class="tuer bahn">
  <div class="tuer-karte glass">
    <div class="marke">Valtix<span>Mandantenportal</span></div>
    <h1 style="margin-top:20px">Anmelden</h1>
    <p class="lead">Ihre monatliche Auswertung, jederzeit abrufbar.</p>

    <div class="demo"><b>Demonstrationszugang</b>
      <dl>
        <dt>E-Mail</dt><dd><code>mandant@vorschau.valtix</code></dd>
        <dt>Passwort</dt><dd><code>Vorschau2026</code></dd>
      </dl>
      <p>Damit lässt sich die Ansicht eines Mandanten ansehen. Geprüft wird nur im
        Browser. Es gibt keine Datenbank hinter dieser Seite und keinen Server,
        der etwas entgegennimmt.</p>
    </div>

    <div class="meldung" id="fehler" role="alert" hidden>{WARNUNG}<span id="fehlertext"></span></div>

    <form id="anmeldung" novalidate>
      <div class="feld">
        <label for="mail">E-Mail-Adresse</label>
        <input id="mail" type="email" autocomplete="username" value="mandant@vorschau.valtix">
      </div>
      <div class="feld">
        <label for="pw">Passwort</label>
        <div class="pw-reihe">
          <input id="pw" type="password" autocomplete="current-password" value="Vorschau2026">
          <button class="knopf stumm" id="sichtbar" type="button">Anzeigen</button>
        </div>
      </div>
      <div class="zeile-merken">
        <button class="merken" id="merken" type="button" role="checkbox" aria-checked="true">
          <span class="haken">{HAKEN}</span>Angemeldet bleiben</button>
        <span style="flex-grow:1"></span>
        <a href="#" style="font-size:.88rem;text-decoration:none">Passwort vergessen?</a>
      </div>
      <button class="knopf breit" type="submit">Anmelden</button>
    </form>
    <p class="hinweis" style="margin-top:18px">Noch keinen Zugang? Ihren Zugang richten
      wir im Rahmen der monatlichen Betreuung ein.
      <a href="index.html#kontakt">Schreiben Sie uns</a>.</p>
  </div>
</div></section>'''


def verwaltung():
    """Ansichten der Verwaltung. Nicht ueber die Anmeldung erreichbar, nur
    ueber die Adresse, weil die Seite oeffentlich steht."""
    mandanten = ''.join(
        f'<tr><td>{n}</td><td class="num">{b}</td><td>{s}</td></tr>'
        for n, b, s in [('Muster Lüftungstechnik GmbH', 3, 'Juli 2026'),
                        ('Beispiel Bau GmbH', 1, 'Juli 2026'),
                        ('Beispiel Handel e. K.', 2, 'Juli 2026')])
    zugaenge = ''.join(
        f'<tr><td>{a}</td><td>{b}</td><td>{c}</td>'
        f'<td><span class="status {k}">{d}</span></td></tr>'
        for a, b, c, d, k in [
            ('Administrator', 'admin@vorschau.valtix', 'Administrator', 'aktiv', 'gut'),
            ('Ansprechpartner Muster', 'mandant@vorschau.valtix',
             'Muster Lüftungstechnik GmbH', 'aktiv', 'gut'),
            ('Ansprechpartner Beispiel Bau', 'bau@vorschau.valtix',
             'Beispiel Bau GmbH', 'Einladung offen', 'offen')])
    protokoll = ''.join(
        f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in [
            ('06.08.2026 09:14:02', 'anmeldung', 'mandant@vorschau.valtix', ''),
            ('06.08.2026 09:14:11', 'bericht_geoeffnet', 'mandant@vorschau.valtix',
             'Juli 2026'),
            ('06.08.2026 08:52:40', 'bericht_eingestellt', 'admin@vorschau.valtix',
             'Muster Lüftungstechnik GmbH'),
            ('05.08.2026 17:30:19', 'zugang_angelegt', 'admin@vorschau.valtix',
             'bau@vorschau.valtix'),
            ('05.08.2026 17:29:03', 'anmeldung_fehlgeschlagen', '', 'unbekannte Kennung')])

    def block(kennung, titel, kopf, zeilen, zusatz=''):
        spalten = ''.join('<th class="num">' + h + '</th>' if n
                          else '<th>' + h + '</th>' for h, n in kopf)
        return (f'<section class="tabellenkarte glass verwaltung" '
                f'data-reiter="{kennung}" hidden>'
                f'<div class="tabellenkopf"><h2>{titel}</h2></div>'
                f'<div class="rahmen"><table><thead><tr>{spalten}</tr></thead>'
                f'<tbody>{zeilen}</tbody></table></div>{zusatz}</section>')

    hochladen = '''<div class="formular">
      <div class="feld"><label for="vm">Mandant</label>
        <select id="vm" disabled><option>Muster Lüftungstechnik GmbH</option></select></div>
      <div class="feld"><label for="vd">Ausgefüllte Eingabevorlage (.xlsx)</label>
        <input id="vd" type="file" accept=".xlsx" disabled></div>
      <button class="knopf" type="button" disabled>Hochladen und Bericht erzeugen</button>
      <p class="hinweis" style="margin-top:12px">In der Vorführung ohne Funktion.
        Es lässt sich nichts hochladen.</p>
    </div>'''

    return (block('mandanten', 'Mandanten',
                  [('Name', 0), ('Berichte', 1), ('Letzter Bericht', 0)],
                  mandanten, hochladen)
            + block('zugaenge', 'Zugänge',
                    [('Name', 0), ('E-Mail', 0), ('Zugehörigkeit', 0), ('Status', 0)],
                    zugaenge)
            + block('protokoll', 'Letzte Ereignisse',
                    [('Zeitpunkt', 0), ('Ereignis', 0), ('E-Mail', 0), ('Detail', 0)],
                    protokoll))


def bauen():
    d = daten()
    d['kopfzahlen'] = kopfzahlen()

    def knopf(k, t, admin):
        gewaehlt = 'true' if k == 'ueberblick' else 'false'
        zusatz = ' class="nur-admin" hidden' if admin else ''
        return (f'<button type="button" data-reiter="{k}" role="tab" '
                f'aria-selected="{gewaehlt}"{zusatz}>{t}</button>')

    reiter = [('ueberblick', 'Überblick', False), ('detail', 'Zahlen im Detail', False),
              ('mandanten', 'Mandanten', True), ('zugaenge', 'Zugänge', True),
              ('protokoll', 'Protokoll', True)]
    knoepfe = ''.join(knopf(*r) for r in reiter)

    app = f'''<section id="bs-app" hidden>
  <header class="kopf bahn"><div class="kopf-innen glass">
    <div class="marke">Valtix<span>Mandantenportal</span></div>
    <div class="wechsler">
      <button class="pfeil" id="pfeil-zurueck" type="button"
        aria-label="Vorheriger Monat">{PFEIL_LINKS}</button>
      <div class="wechsler-text"><b id="monat-name"></b><span id="monat-stand"></span></div>
      <button class="pfeil" id="pfeil-vor" type="button"
        aria-label="Nächster Monat">{PFEIL_RECHTS}</button>
    </div>
    <div class="nutzer">
      <div class="nutzer-text"><b>{d["firma"]}</b><span>Ansprechpartner Muster</span></div>
      <div class="signet">{initialen(d["firma"])}</div>
      <button class="knopf stumm schmal" type="button" data-abmelden>Abmelden</button>
    </div>
  </div></header>
  <div class="reiter bahn"><div class="reiter-innen glass" role="tablist">{knoepfe}</div></div>
  <div class="flaeche bahn">
    <div id="flaeche"></div>
    {verwaltung()}
  </div>
</section>'''

    html = f'''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Mandantenportal · Valtix Financial Management</title>
<link rel="icon" href="favicon.ico" sizes="any">
<style>{CSS}</style></head><body>
{AURORA}
{BAND}
{ANMELDEN}
{app}
<div class="fuss bahn">Valtix Financial Management · Luca Sparhuber und Sharif Ibrahim GbR,
Leipzig · Diese Seite dient allein der Ansicht. Sie verarbeitet keine personenbezogenen
Daten, setzt keine Cookies und sendet nichts an einen Server.</div>
<script>window.__valtix = {json.dumps(d, ensure_ascii=False)};</script>
<script>{JS}</script>
</body></html>'''

    ziel = os.path.join(ROOT, 'portal-vorschau.html')
    open(ziel, 'w', encoding='utf-8').write(html)
    return ziel, len(html), len(d['monate'])


if __name__ == '__main__':
    ziel, groesse, monate = bauen()
    print('geschrieben:', ziel, groesse, 'Zeichen,', monate, 'Monate')
    if M.ohne_zuordnung:
        print('Zielzeilen ohne passende Kennzahl:', M.ohne_zuordnung)
