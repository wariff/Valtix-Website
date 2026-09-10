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


CSS = '''
:root{
  --ink:#232941; --ink-soft:#565D73; --muted:#8A8FA3;
  --gold-deep:#7A6238; --cream:#F5EBD0; --bg:#FBF8F2; --flaeche:#F7F4EC;
  --serie-a:#404D97; --serie-b:#B0842A;
  --gruen:#0CA30C; --gruen-text:#0A7A0A;
  --gelb:#FAB219; --gelb-text:#8A6100;
  --rot:#D03B3B; --rot-text:#A32C2C;
  --linie:rgba(35,41,65,.11); --linie-stark:rgba(35,41,65,.18);
  --r:14px; --schatten:0 8px 24px rgba(35,41,65,.07);
  --font:"Inter Tight",system-ui,-apple-system,"Segoe UI",sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--ink);
     font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--gold-deep)}
button,input{font-family:inherit}
[hidden]{display:none!important}
h1{font-size:1.5rem;font-weight:800;letter-spacing:-.03em}
h2{font-size:1.02rem;font-weight:700;letter-spacing:-.02em}

.band{background:var(--ink);color:#fff;font-size:.84rem;padding:11px 22px}
.band-innen{max-width:1220px;margin:0 auto;display:flex;gap:14px;
            align-items:baseline;flex-wrap:wrap}
.band b{font-weight:700}
.band span{color:rgba(255,255,255,.72)}
.band a{color:var(--cream)}

/* Anmeldung */
.tuer{padding:6vh 22px 60px}
.tuer-karte{width:100%;max-width:430px;margin:0 auto;background:#fff;
  border:1px solid var(--linie);border-radius:18px;padding:30px;
  box-shadow:var(--schatten)}
.marke{font-weight:800;letter-spacing:-.03em;font-size:1.06rem}
.marke span{font-weight:500;color:var(--ink-soft);margin-left:8px;font-size:.9rem}
.lead{color:var(--ink-soft);margin:6px 0 20px}
label{display:block;font-size:.86rem;font-weight:600;margin-bottom:6px}
input[type=email],input[type=password],input[type=text],select{width:100%;
  min-height:50px;font-size:1rem;color:var(--ink);background:#fff;
  border:1px solid var(--linie-stark);border-radius:12px;padding:10px 14px}
input:focus,select:focus{outline:none;border-color:var(--ink);
  box-shadow:0 0 0 3px rgba(35,41,65,.13)}
input:disabled,select:disabled{background:var(--flaeche);color:var(--muted)}
.feld{margin-bottom:16px}
.pw-reihe{display:flex;gap:8px;align-items:stretch}
.pw-reihe input{flex:1;min-width:0}
.merken{display:flex;align-items:center;gap:9px;min-height:44px;padding:0 4px;
  border:0;background:none;cursor:pointer;color:var(--ink);font-size:.9rem}
.haken{width:22px;height:22px;border-radius:7px;border:1px solid rgba(35,41,65,.28);
  background:#fff;display:flex;align-items:center;justify-content:center;flex:none}
.merken[aria-checked=true] .haken{background:var(--ink);border-color:var(--ink);color:#fff}
.merken[aria-checked=false] .haken svg{display:none}
.zeile-merken{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.knopf{display:inline-flex;align-items:center;justify-content:center;gap:8px;
  min-height:50px;padding:0 22px;border-radius:999px;border:0;font:inherit;
  font-size:1rem;font-weight:600;cursor:pointer;text-decoration:none;
  background:linear-gradient(180deg,#232941,#171B2C);color:#fff;
  box-shadow:0 6px 16px rgba(35,41,65,.24)}
.knopf.breit{width:100%}
.knopf.stumm{background:#fff;color:var(--ink);border:1px solid var(--linie);
  box-shadow:none}
.knopf.schmal{min-height:40px;padding:0 16px;font-size:.86rem;box-shadow:none}
.knopf:disabled{opacity:.5;box-shadow:none;cursor:not-allowed}
.meldung{display:flex;gap:10px;align-items:flex-start;background:#FDECEC;
  color:#8B1F1F;border-radius:11px;padding:12px 14px;margin-bottom:16px;
  font-size:.9rem}
.meldung svg{flex:none;margin-top:2px}
.demo{background:var(--cream);border:1px solid rgba(122,98,56,.26);
  border-radius:12px;padding:13px 15px;margin-bottom:16px;font-size:.88rem}
.demo b{display:block;font-size:.68rem;text-transform:uppercase;
  letter-spacing:.11em;color:var(--gold-deep);margin-bottom:7px}
.demo dl{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;align-items:baseline}
.demo dt{color:var(--ink-soft)}
.demo dd{min-width:0;overflow-wrap:anywhere}
.demo p{margin-top:8px;color:var(--ink-soft);font-size:.8rem}
code{background:rgba(35,41,65,.08);padding:1px 5px;border-radius:5px;font-size:.86rem}

/* Portalkopf */
.kopf{background:#fff;border-bottom:1px solid var(--linie)}
.kopf-innen{max-width:1220px;margin:0 auto;padding:12px 22px;display:flex;
  align-items:center;gap:14px;flex-wrap:wrap}
.wechsler{display:flex;align-items:center;gap:8px;background:var(--flaeche);
  border:1px solid var(--linie);border-radius:999px;padding:4px;margin:0 auto}
.pfeil{width:44px;height:44px;border-radius:999px;border:0;background:#fff;
  color:var(--ink);cursor:pointer;display:flex;align-items:center;
  justify-content:center;box-shadow:0 1px 3px rgba(35,41,65,.14)}
.pfeil:disabled{color:#C9CBD4;cursor:default;box-shadow:none;background:transparent}
.wechsler-text{min-width:150px;text-align:center}
.wechsler-text b{display:block;font-size:.96rem;font-weight:700;letter-spacing:-.02em}
.wechsler-text span{font-size:.76rem;color:var(--ink-soft)}
.nutzer{display:flex;align-items:center;gap:10px}
.nutzer-text{text-align:right}
.nutzer-text b{display:block;font-size:.82rem;font-weight:700;line-height:1.3}
.nutzer-text span{font-size:.76rem;color:var(--ink-soft)}
.signet{width:36px;height:36px;border-radius:11px;background:var(--gold-deep);
  color:#fff;display:flex;align-items:center;justify-content:center;
  font-size:.74rem;font-weight:700;flex:none}
.reiter{background:#fff;border-bottom:1px solid var(--linie);overflow-x:auto}
.reiter-innen{max-width:1220px;margin:0 auto;padding:0 22px;display:flex;gap:22px}
.reiter button{border:0;background:none;cursor:pointer;padding:12px 2px;
  min-height:48px;font-size:.94rem;font-weight:500;color:var(--ink-soft);
  border-bottom:3px solid transparent;white-space:nowrap}
.reiter button[aria-selected=true]{color:var(--ink);font-weight:700;
  border-bottom-color:var(--ink)}
.flaeche{max-width:1220px;margin:0 auto;padding:20px 22px 48px;
  display:flex;flex-direction:column;gap:16px}

/* Kommentar */
.kommentar{display:flex;gap:18px;flex-wrap:wrap;background:#fff;
  border:1px solid var(--linie);border-left:4px solid var(--gold-deep);
  border-radius:var(--r);padding:20px 24px;box-shadow:var(--schatten)}
.kommentar-text{flex:1;min-width:260px}
.kommentar .kennung{font-size:.7rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--gold-deep);font-weight:700;margin-bottom:8px}
.kommentar p{font-size:1.06rem;line-height:1.5;max-width:74ch;text-wrap:pretty}
.kommentar-knoepfe{display:flex;flex-direction:column;gap:8px;align-self:center}
.kommentar-knoepfe .knopf{min-height:44px;white-space:nowrap}

/* Statusgruppen */
.gruppe{background:#fff;border:1px solid var(--linie);border-radius:var(--r);
  box-shadow:var(--schatten);overflow:hidden}
.gruppe-kopf{width:100%;display:flex;align-items:center;gap:10px;padding:13px 20px;
  min-height:52px;border:0;border-bottom:1px solid var(--linie);cursor:pointer;
  text-align:left;font-size:.95rem}
.gruppe-kopf .zeichen{width:22px;height:22px;border-radius:999px;color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:.8rem;
  font-weight:800;flex:none}
.gruppe-kopf .titel{font-weight:700;letter-spacing:-.02em}
.gruppe-kopf .anzahl{color:var(--ink-soft);font-size:.84rem}
.gruppe-kopf .klapp{margin-left:auto;color:var(--ink-soft);font-size:.84rem}
.g-rot .gruppe-kopf{background:rgba(208,59,59,.07)}
.g-rot .zeichen{background:var(--rot)} .g-rot .titel{color:var(--rot-text)}
.g-gelb .gruppe-kopf{background:rgba(250,178,25,.12)}
.g-gelb .zeichen{background:var(--gelb)} .g-gelb .titel{color:var(--gelb-text)}
.g-gruen .gruppe-kopf{background:rgba(12,163,12,.08)}
.g-gruen .zeichen{background:var(--gruen)} .g-gruen .titel{color:var(--gruen-text)}
.posten{display:grid;grid-template-columns:minmax(0,1fr) 168px 150px 170px;
  gap:16px;align-items:center;padding:14px 20px;
  border-bottom:1px solid rgba(35,41,65,.08)}
.posten:last-child{border-bottom:0}
.posten .name{font-size:.98rem;font-weight:600;letter-spacing:-.01em}
.posten .erklaerung{font-size:.82rem;color:var(--ink-soft);margin-top:2px}
.posten .wert{text-align:right}
.posten .wert b{display:block;font-size:1.2rem;font-weight:800;
  letter-spacing:-.035em;font-variant-numeric:tabular-nums}
.posten .wert span{font-size:.78rem;color:var(--ink-soft);
  font-variant-numeric:tabular-nums}
.posten .ziel{text-align:right;font-size:.85rem;color:var(--ink-soft);
  font-variant-numeric:tabular-nums}
.posten .tat{text-align:right}
.posten .abstand{font-size:.84rem;font-variant-numeric:tabular-nums}
.a-gruen{color:var(--gruen-text)} .a-gelb{color:var(--gelb-text)}
.a-rot{color:var(--rot-text)}

/* Karte, Verlauf */
.karte{background:#fff;border:1px solid var(--linie);border-radius:var(--r);
  padding:18px 22px 20px;box-shadow:var(--schatten)}
.karte.flach{padding:18px 0 0}
.karte.flach .karten-kopf{padding:0 20px}
.karten-kopf{display:flex;justify-content:space-between;align-items:baseline;
  gap:14px;flex-wrap:wrap;margin-bottom:10px}
.hinweis{font-size:.82rem;color:var(--ink-soft)}
.saeulen{display:flex;align-items:flex-end;gap:12px;height:190px;padding-top:18px}
.saeule{flex:1;display:flex;flex-direction:column;align-items:center;gap:8px;
  cursor:pointer;align-self:stretch;justify-content:flex-end;border:0;
  background:none;padding:0;min-width:0}
.saeule .zahl{font-size:.8rem;font-weight:600;color:var(--ink);
  font-variant-numeric:tabular-nums;white-space:nowrap}
.saeule .balken{width:100%;background:rgba(64,77,151,.28);border-radius:6px 6px 0 0}
.saeule .monat{font-size:.8rem;color:var(--muted)}
.saeule[aria-current] .balken{background:var(--serie-a)}
.saeule[aria-current] .monat{color:var(--ink);font-weight:700}

/* Detailraster */
.rahmen{overflow-x:auto;-webkit-overflow-scrolling:touch;
  border-top:1px solid var(--linie)}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:.88rem;
  min-width:720px}
th,td{padding:9px 12px;text-align:left;font-weight:400;
  border-bottom:1px solid rgba(35,41,65,.08);white-space:nowrap}
thead th{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--ink-soft);font-weight:700;background:var(--flaeche)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr.summe td,tr.summe th{font-weight:700;background:rgba(35,41,65,.028)}
.pos{min-width:280px;white-space:normal}
.pos .fach{font-size:.78rem;color:var(--muted);margin-left:7px}
.kindzeile .pos{padding-left:32px;color:var(--ink-soft)}
td.minus{color:var(--gold-deep)}
.oeffnen{min-height:30px;padding:0 11px;border-radius:999px;
  border:1px solid var(--linie-stark);background:#fff;color:var(--ink-soft);
  font-size:.76rem;font-weight:600;cursor:pointer;margin-right:9px;
  white-space:nowrap}
.hoch{color:var(--gruen-text)} .runter{color:var(--rot-text)}

/* Verwaltung */
.status.gut{color:var(--gruen-text);font-weight:600;font-size:.86rem}
.status.offen{color:var(--gold-deep);font-weight:600;font-size:.86rem}
.formular{max-width:460px;padding:0 20px 20px}
.formular .knopf{margin-top:16px}

.fuss{max-width:1220px;margin:0 auto;padding:14px 22px 34px;font-size:.78rem;
      color:var(--ink-soft)}

@media(max-width:860px){
  .kopf-innen{padding:10px 14px;gap:10px}
  .marke{flex:1}
  .nutzer{order:2;width:100%;gap:10px}
  .nutzer-text{flex:1;text-align:left;min-width:0}
  .nutzer-text b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .wechsler{order:3;width:100%;margin:0}
  .wechsler-text{flex:1}
  .gruppe-kopf{flex-wrap:wrap;row-gap:2px}
  .gruppe-kopf .titel{flex:1;min-width:0}
  .gruppe-kopf .anzahl{width:100%;padding-left:32px;order:4}
  .reiter-innen,.flaeche{padding-left:14px;padding-right:14px}
  .kommentar{padding:16px 18px;flex-direction:column;gap:14px}
  .kommentar p{font-size:1rem}
  .kommentar-knoepfe{flex-direction:row;flex-wrap:wrap;align-self:stretch}
  .kommentar-knoepfe .knopf{flex:1}
  .posten{grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:14px 16px}
  .posten .name-feld{grid-column:1}
  .posten .wert{grid-column:2;grid-row:1}
  .posten .wert span{display:none}
  .posten .ziel{grid-column:1;text-align:left;grid-row:2}
  .posten .tat{grid-column:2;grid-row:2}
  .posten .erklaerung{display:none}
  .gruppe-kopf{padding:13px 16px}
  .karte{padding:16px 16px 18px}
  .karte.flach .karten-kopf{padding:0 16px}
  .saeulen{height:150px;gap:6px}
  .saeule .zahl{font-size:.72rem}
}
'''


JS = r'''
(function () {
  var D = window.__valtix;
  var stand = { monat: D.aktiv, reiter: 'ueberblick', auf: { rot: true, gelb: true, gruen: false },
                offen: {}, gemerkt: true, sichtbar: false };

  // ---------------------------------------------------------------- Formate
  function tausend(s) { return s.replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function eur(w) {
    if (w === null || w === undefined) return '–';
    return (w < 0 ? '−' : '') + tausend(Math.abs(w).toFixed(0)) + ' €';
  }
  function proz(w) {
    if (w === null || w === undefined) return '–';
    return w.toFixed(1).replace('.', ',').replace('-', '−') + ' %';
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

  // -------------------------------------------------------------- Bewertung
  function bewerten(k, i) {
    var ist = k.reihe[i];
    if (ist === null || ist === undefined || !k.ziel) return null;
    // Abweichung als Anteil des Ziels, damit die Gelbschwelle in beide
    // Richtungen bei zehn Prozent liegt.
    var erreicht = k.richtung === 'hoeher' ? ist >= k.ziel : ist <= k.ziel;
    var daneben = Math.abs(ist - k.ziel) / Math.abs(k.ziel);
    return { stufe: erreicht ? 'gruen' : (daneben <= 0.1 ? 'gelb' : 'rot'), erreicht: erreicht };
  }

  // ------------------------------------------------------------------- Kopf
  function kopf() {
    var m = D.monate[stand.monat];
    document.getElementById('monat-name').textContent = m.lang + ' ' + D.jahr;
    document.getElementById('monat-stand').textContent = 'Bericht vom ' + m.eingestellt;
    document.getElementById('pfeil-zurueck').disabled = stand.monat === 0;
    document.getElementById('pfeil-vor').disabled = stand.monat === D.monate.length - 1;
  }

  // -------------------------------------------------------------- Überblick
  function ueberblick() {
    var i = stand.monat, vor = i > 0 ? i - 1 : null;
    var wurzel = document.createDocumentFragment();

    var k = el('section', 'kommentar');
    var kt = el('div', 'kommentar-text');
    kt.appendChild(el('div', 'kennung', 'Das sagt Ihr Berater zum ' + D.monate[i].lang));
    kt.appendChild(el('p', null, D.kommentare[i]));
    k.appendChild(kt);
    var kn = el('div', 'kommentar-knoepfe');
    var frage = el('button', 'knopf', 'Rückfrage stellen');
    frage.type = 'button';
    var pdf = el('a', 'knopf stumm', 'Vollständigen Bericht öffnen');
    pdf.href = D.bericht;
    kn.appendChild(frage); kn.appendChild(pdf);
    k.appendChild(kn);
    wurzel.appendChild(k);

    var faecher = { rot: [], gelb: [], gruen: [] };
    D.kennzahlen.forEach(function (kz) {
      var b = bewerten(kz, i);
      if (b) faecher[b.stufe].push({ kz: kz, b: b });
    });

    [['rot', 'Braucht Aufmerksamkeit', '!'],
     ['gelb', 'Im Blick behalten', '•'],
     ['gruen', 'Läuft nach Plan', '✓']].forEach(function (g) {
      var liste = faecher[g[0]];
      if (!liste.length) return;
      var box = el('section', 'gruppe g-' + g[0]);
      var kopfKnopf = el('button', 'gruppe-kopf');
      kopfKnopf.type = 'button';
      kopfKnopf.setAttribute('aria-expanded', String(stand.auf[g[0]]));
      kopfKnopf.appendChild(el('span', 'zeichen', g[2]));
      kopfKnopf.appendChild(el('span', 'titel', g[1]));
      kopfKnopf.appendChild(el('span', 'anzahl',
        liste.length === 1 ? '1 Kennzahl' : liste.length + ' Kennzahlen'));
      kopfKnopf.appendChild(el('span', 'klapp', stand.auf[g[0]] ? 'zuklappen' : 'anzeigen'));
      kopfKnopf.addEventListener('click', function () {
        stand.auf[g[0]] = !stand.auf[g[0]];
        zeichnen();
      });
      box.appendChild(kopfKnopf);

      if (stand.auf[g[0]]) {
        liste.forEach(function (p) {
          var kz = p.kz, ist = kz.reihe[i];
          var z = el('div', 'posten');
          var nf = el('div', 'name-feld');
          nf.appendChild(el('div', 'name', kz.klar));
          nf.appendChild(el('div', 'erklaerung', kz.erklaerung));
          z.appendChild(nf);

          var w = el('div', 'wert');
          w.appendChild(el('b', null, fmt(kz.art, ist)));
          w.appendChild(el('span', null, vor === null ? 'kein Vormonat'
            : 'Vormonat ' + fmt(kz.art, kz.reihe[vor])));
          z.appendChild(w);

          z.appendChild(el('div', 'ziel',
            (kz.richtung === 'hoeher' ? 'Ziel ab ' : 'Ziel bis ') + fmt(kz.art, kz.ziel)));

          var t = el('div', 'tat');
          if (p.b.erreicht) {
            t.appendChild(el('span', 'abstand a-gruen',
              fmt(kz.art, Math.abs(ist - kz.ziel)) + ' besser'));
          } else {
            var nach = el('button', 'knopf stumm schmal', 'Dazu nachfragen');
            nach.type = 'button';
            t.appendChild(nach);
          }
          z.appendChild(t);
          box.appendChild(z);
        });
      }
      wurzel.appendChild(box);
    });

    // Verlauf
    var v = el('section', 'karte');
    var vk = el('div', 'karten-kopf');
    vk.appendChild(el('h2', null, 'Umsatz im Jahresverlauf'));
    vk.appendChild(el('p', 'hinweis', 'Wählen Sie einen Monat aus'));
    v.appendChild(vk);
    var reihe = el('div', 'saeulen');
    var hoch = Math.max.apply(null, D.umsatz);
    D.umsatz.forEach(function (w, idx) {
      var s = el('button', 'saeule');
      s.type = 'button';
      if (idx === i) s.setAttribute('aria-current', 'true');
      s.setAttribute('aria-label', D.monate[idx].lang + ', ' + eur(w));
      s.appendChild(el('span', 'zahl', idx === i ? eur(w) : ''));
      var b = el('span', 'balken');
      b.style.height = Math.round(w / hoch * 122) + 'px';
      s.appendChild(b);
      s.appendChild(el('span', 'monat', D.monate[idx].kurz));
      s.addEventListener('click', function () { stand.monat = idx; zeichnen(); });
      reihe.appendChild(s);
    });
    v.appendChild(reihe);
    wurzel.appendChild(v);
    return wurzel;
  }

  // ------------------------------------------------------------ Zahlen im Detail
  function detail() {
    var i = stand.monat, vor = i > 0 ? i - 1 : null;
    var karte = el('section', 'karte flach');
    var kk = el('div', 'karten-kopf');
    var kkl = el('div');
    kkl.appendChild(el('h2', null, 'Ergebnisrechnung ' + D.monate[i].lang + ' ' + D.jahr));
    kkl.appendChild(el('p', 'hinweis', vor === null
      ? 'Für diesen Monat gibt es keinen Vormonat zum Vergleich.'
      : 'Verglichen wird mit ' + D.monate[vor].lang + '. Blöcke lassen sich öffnen.'));
    kk.appendChild(kkl);
    karte.appendChild(kk);

    var rahmen = el('div', 'rahmen');
    var t = el('table');
    var kopfZ = el('tr');
    ['Position', D.monate[i].kurz + ' ' + String(D.jahr).slice(-2),
     vor === null ? '–' : D.monate[vor].kurz + ' ' + String(D.jahr).slice(-2),
     'Veränderung'].forEach(function (txt, sp) {
      var th = el('th', sp ? 'num' : 'pos', txt);
      kopfZ.appendChild(th);
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
      var td1 = el('td', 'num' + (z.minus ? ' minus' : ''),
        fmt(z.art, z.reihe[i] === null ? null : z.reihe[i] * vz));
      tr.appendChild(td1);
      tr.appendChild(el('td', 'num', vor === null ? '–'
        : fmt(z.art, z.reihe[vor] === null ? null : z.reihe[vor] * vz)));

      var dtxt = '', dkl = 'num';
      if (vor !== null && z.reihe[i] !== null && z.reihe[vor] !== null) {
        var diff = z.reihe[i] - z.reihe[vor];
        if (z.art === 'prozent') {
          dtxt = (diff >= 0 ? '+' : '−')
               + Math.abs(diff).toFixed(1).replace('.', ',') + ' %-Pkt.';
        } else if (z.reihe[vor]) {
          var p = diff / Math.abs(z.reihe[vor]) * 100;
          var kern = Math.abs(p).toFixed(1).replace('.', ',') + ' %';
          // Kostenzeilen stehen negativ in der Spalte. Ein Vorzeichen davor
          // waere doppeldeutig, deshalb steht dort mehr oder weniger.
          dtxt = z.minus ? kern + (diff >= 0 ? ' mehr' : ' weniger')
                         : (diff >= 0 ? '+' : '−') + kern;
        }
        var gut = z.minus ? diff <= 0 : diff >= 0;
        dkl += gut ? ' hoch' : ' runter';
      }
      tr.appendChild(el('td', dkl, dtxt));
      tbody.appendChild(tr);
    });
    t.appendChild(tbody);
    rahmen.appendChild(t);
    karte.appendChild(rahmen);
    var f = el('p', 'hinweis');
    f.style.padding = '13px 20px';
    f.textContent = 'Alle Beträge netto. Grundlage ist die ausgefüllte Eingabevorlage.';
    karte.appendChild(f);
    return karte;
  }

  // ------------------------------------------------------------------ Zeichnen
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

  // ------------------------------------------------------------------ Bedienung
  document.getElementById('pfeil-zurueck').addEventListener('click', function () {
    if (stand.monat > 0) { stand.monat--; zeichnen(); }
  });
  document.getElementById('pfeil-vor').addEventListener('click', function () {
    if (stand.monat < D.monate.length - 1) { stand.monat++; zeichnen(); }
  });
  document.querySelectorAll('.reiter button').forEach(function (b) {
    b.addEventListener('click', function () { stand.reiter = b.dataset.reiter; zeichnen(); });
  });

  // Anmeldung
  var pw = document.getElementById('pw');
  var mail = document.getElementById('mail');
  var fehler = document.getElementById('fehler');
  function anmelden() {
    if (!mail.value.trim()) { melden('Bitte tragen Sie Ihre E-Mail-Adresse ein.'); return; }
    if (pw.value !== 'Vorschau2026') {
      melden('Das Passwort stimmt nicht. Prüfen Sie die Groß- und Kleinschreibung.');
      return;
    }
    fehler.hidden = true;
    oeffnen('app');
  }
  function melden(text) {
    document.getElementById('fehlertext').textContent = text;
    fehler.hidden = false;
  }
  document.getElementById('anmeldung').addEventListener('submit', function (e) {
    e.preventDefault();
    anmelden();
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


PFEIL_LINKS = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
               'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>')
PFEIL_RECHTS = PFEIL_LINKS.replace('M15 5l-7 7 7 7', 'M9 5l7 7-7 7')
HAKEN = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
         'stroke="currentColor" stroke-width="3" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>')
WARNUNG = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
           'aria-hidden="true"><path d="M12 7v6M12 17h.01"/>'
           '<circle cx="12" cy="12" r="9"/></svg>')

BAND = '''<div class="band"><div class="band-innen">
  <b>Demonstration</b>
  <span>Diese Ansicht dient der Vorführung. Es wird nichts gespeichert und nichts
    übertragen. Firma und Zahlen sind erfunden.</span>
  <a href="index.html">Zurück zur Website</a>
</div></div>'''

ANMELDEN = f'''<section id="bs-anmelden"><div class="tuer"><div class="tuer-karte">
  <div class="marke">Valtix<span>Mandantenportal</span></div>
  <h1 style="margin-top:18px">Anmelden</h1>
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
  <p class="hinweis" style="margin-top:16px">Noch keinen Zugang? Ihren Zugang richten wir
    im Rahmen der monatlichen Betreuung ein.
    <a href="index.html#kontakt">Schreiben Sie uns</a>.</p>
</div></div></section>'''


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
        return (f'<section class="karte flach verwaltung" data-reiter="{kennung}" hidden>'
                f'<div class="karten-kopf"><h2>{titel}</h2></div>'
                f'<div class="rahmen"><table><thead><tr>{spalten}</tr></thead>'
                f'<tbody>{zeilen}</tbody></table></div>{zusatz}</section>')

    hochladen = '''<div class="formular">
      <div class="feld"><label for="vm">Mandant</label>
        <select id="vm" disabled><option>Muster Lüftungstechnik GmbH</option></select></div>
      <div class="feld"><label for="vd">Ausgefüllte Eingabevorlage (.xlsx)</label>
        <input id="vd" type="file" accept=".xlsx" disabled></div>
      <button class="knopf" type="button" disabled>Hochladen und Bericht erzeugen</button>
      <p class="hinweis" style="margin-top:10px">In der Vorführung ohne Funktion.
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
    reiter = [('ueberblick', 'Überblick', False), ('detail', 'Zahlen im Detail', False),
              ('mandanten', 'Mandanten', True), ('zugaenge', 'Zugänge', True),
              ('protokoll', 'Protokoll', True)]
    def knopf(k, t, admin):
        gewaehlt = 'true' if k == 'ueberblick' else 'false'
        zusatz = ' class="nur-admin" hidden' if admin else ''
        return (f'<button type="button" data-reiter="{k}" role="tab" '
                f'aria-selected="{gewaehlt}"{zusatz}>{t}</button>')

    knoepfe = ''.join(knopf(*r) for r in reiter)

    app = f'''<section id="bs-app" hidden>
  <div class="kopf"><div class="kopf-innen">
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
  </div></div>
  <div class="reiter"><div class="reiter-innen" role="tablist">{knoepfe}</div></div>
  <div class="flaeche">
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
{BAND}
{ANMELDEN}
{app}
<div class="fuss">Valtix Financial Management · Luca Sparhuber und Sharif Ibrahim GbR,
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
