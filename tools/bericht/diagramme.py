#!/usr/bin/env python3
"""Diagramme als Inline-SVG im Valtix-Design.

Farbwahl, geprüft mit dem Validator der dataviz-Vorlage gegen den Seitengrund
#FBF8F2: Das Markennavy #232941 liegt mit OKLCH L=0,287 unterhalb des zulässigen
Helligkeitsbandes und beide Markenfarben unterschreiten die Chroma-Grenze. Für
Flächen und Linien mit Datenbedeutung werden deshalb zwei aufgehellte Nachbarn
derselben Farbtöne verwendet: #404D97 (H 273°, wie Navy) und #B0842A (H 80°, wie
Gold). Dieses Paar besteht alle sechs Prüfungen. Navy bleibt Textfarbe.
"""
from html import escape

SERIE_A   = '#404D97'   # geprüft, Farbton des Markennavys
SERIE_B   = '#B0842A'   # geprüft, Farbton des Markengolds
INK       = '#232941'
INK_SOFT  = '#565D73'
MUTED     = '#7C melodrama'  # ersetzt unten
MUTED     = '#8A8FA3'
RASTER    = 'rgba(35,41,65,.12)'
FLAECHE   = '#FBF8F2'
STATUS    = {'gruen': '#0CA30C', 'gelb': '#FAB219', 'rot': '#D03B3B', 'grau': '#8A8FA3'}


def eur(x, nk=0):
    s = f'{x:,.{nk}f}'.replace(',', '#').replace('.', ',').replace('#', '.')
    return s + '\u00a0€'

def zahl(x, nk=2, einheit=''):
    s = f'{x:,.{nk}f}'.replace(',', '#').replace('.', ',').replace('#', '.')
    return (s + '\u00a0' + einheit).strip() if einheit else s

def proz(x, nk=1):
    return zahl(x, nk) + '\u00a0%'

def _t(x, y, text, **kw):
    attrs = ' '.join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<text x="{x:.1f}" y="{y:.1f}" {attrs}>{escape(str(text))}</text>'


def ergebnisbruecke(schritte, breite=860, hoehe=340):
    """Wasserfall. schritte: Liste aus (Bezeichnung, Wert, Art).
    Art: 'start', 'ab' (Abzug), 'zwischen', 'ende'."""
    pad_l, pad_r, pad_o, pad_u = 8, 8, 34, 62
    innen_b = breite - pad_l - pad_r
    innen_h = hoehe - pad_o - pad_u
    n = len(schritte)
    schritt_b = innen_b / n
    balken_b = min(78, schritt_b * 0.62)

    lauf, punkte = 0.0, []
    for name, wert, art in schritte:
        if art in ('start', 'zwischen', 'ende'):
            unten, oben = 0.0, wert
            lauf = wert
        elif art == 'auf':
            unten, oben = lauf, lauf + abs(wert)
            lauf = oben
        else:
            oben, unten = lauf, lauf - abs(wert)
            lauf = unten
        punkte.append((name, wert, art, unten, oben))

    hoch = max(o for *_, o in punkte)
    skala = lambda v: pad_o + innen_h * (1 - v / hoch) if hoch else pad_o + innen_h

    teile = [f'<line x1="{pad_l}" y1="{pad_o+innen_h:.1f}" x2="{breite-pad_r}" '
             f'y2="{pad_o+innen_h:.1f}" stroke="{RASTER}" stroke-width="1"/>']
    vor_x = vor_y = None
    for i, (name, wert, art, unten, oben) in enumerate(punkte):
        x = pad_l + schritt_b * i + (schritt_b - balken_b) / 2
        y, h = skala(oben), max(2, skala(unten) - skala(oben))
        farbe = SERIE_B if art in ('ab', 'auf') else SERIE_A
        if vor_x is not None:
            teile.append(f'<line x1="{vor_x:.1f}" y1="{vor_y:.1f}" x2="{x:.1f}" y2="{vor_y:.1f}" '
                         f'stroke="{RASTER}" stroke-width="1" stroke-dasharray="3 3"/>')
        teile.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{balken_b:.1f}" height="{h:.1f}" rx="4" '
            f'fill="{farbe}"><title>{escape(name)}: {eur(wert, 2)}</title></rect>')
        vz = '−' if art == 'ab' else ('+' if art == 'auf' else '')
        teile.append(_t(x + balken_b/2, y - 9, vz + eur(abs(wert)),
                        text_anchor='middle', font_size='12.5', font_weight='600', fill=INK))
        worte, zeile, zeilen = name.split(), '', []
        for w in worte:
            if len(zeile + ' ' + w) > 16 and zeile:
                zeilen.append(zeile); zeile = w
            else:
                zeile = (zeile + ' ' + w).strip()
        zeilen.append(zeile)
        for j, z in enumerate(zeilen[:2]):
            teile.append(_t(x + balken_b/2, pad_o + innen_h + 20 + j*14, z,
                            text_anchor='middle', font_size='11.5', fill=INK_SOFT))
        vor_x, vor_y = x + balken_b, skala(lauf)

    return (f'<svg viewBox="0 0 {breite} {hoehe}" role="img" '
            f'aria-label="Ergebnisbrücke vom Umsatz zum Ergebnis vor Steuern">'
            + ''.join(teile) + '</svg>')


def kostenstruktur(posten, gesamt, breite=860, zeile_h=30):
    """Sortierte Balken, ein Farbton. posten: Liste aus (Name, Betrag)."""
    posten = [p for p in posten if p[1] > 0]
    posten.sort(key=lambda p: -p[1])
    label_b, wert_b = 250, 190
    bar_b = breite - label_b - wert_b - 16
    hoehe = zeile_h * len(posten) + 10
    hoch = max(b for _, b in posten) if posten else 1
    teile = []
    for i, (name, betrag) in enumerate(posten):
        y = i * zeile_h + 6
        anteil = betrag / gesamt * 100 if gesamt else 0
        teile.append(_t(0, y + 14, name, font_size='12.5', fill=INK))
        teile.append(
            f'<rect x="{label_b}" y="{y+3.5}" width="{max(3, bar_b*betrag/hoch):.1f}" '
            f'height="14" rx="4" fill="{SERIE_A}">'
            f'<title>{escape(name)}: {eur(betrag,2)} ({proz(anteil)})</title></rect>')
        teile.append(_t(breite, y + 14, f'{eur(betrag)}  ·  {proz(anteil)}',
                        text_anchor='end', font_size='12.5', font_weight='600', fill=INK))
    return (f'<svg viewBox="0 0 {breite} {hoehe}" role="img" '
            f'aria-label="Kostenstruktur nach Kostenart">' + ''.join(teile) + '</svg>')


def verlauf(monate, werte, titel, formatierer, breite=860, hoehe=190, negativ_ok=False):
    """Ein Balken je Monat, eine Datenreihe, nur Eckwerte beschriftet."""
    pad_l, pad_r, pad_o, pad_u = 4, 4, 26, 46
    innen_b, innen_h = breite - pad_l - pad_r, hoehe - pad_o - pad_u
    n = len(werte)
    schritt = innen_b / n
    bar_b = min(64, schritt * 0.58)
    hoch = max(werte); tief = min(min(werte), 0) if negativ_ok else 0
    spanne = (hoch - tief) or 1
    null_y = pad_o + innen_h * (hoch / spanne)
    teile = [f'<line x1="{pad_l}" y1="{null_y:.1f}" x2="{breite-pad_r}" y2="{null_y:.1f}" '
             f'stroke="{RASTER}" stroke-width="1"/>']
    zeig = {0, n - 1, werte.index(hoch), werte.index(min(werte))}
    for i, (mo, w) in enumerate(zip(monate, werte)):
        x = pad_l + schritt * i + (schritt - bar_b) / 2
        h = abs(w) / spanne * innen_h
        y = null_y - h if w >= 0 else null_y
        teile.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_b:.1f}" height="{max(2,h):.1f}" '
                     f'rx="4" fill="{SERIE_A if w>=0 else SERIE_B}">'
                     f'<title>{escape(mo)}: {formatierer(w)}</title></rect>')
        if i in zeig:
            teile.append(_t(x + bar_b/2, (y - 7) if w >= 0 else (y + h + 14), formatierer(w),
                            text_anchor='middle', font_size='11.5', font_weight='600', fill=INK))
        teile.append(_t(x + bar_b/2, hoehe - 6, mo[:3], text_anchor='middle',
                        font_size='11.5', fill=INK_SOFT))
    return (f'<svg viewBox="0 0 {breite} {hoehe}" role="img" '
            f'aria-label="{escape(titel)}">' + ''.join(teile) + '</svg>')


def break_even_bild(be, einheit, breite=860, hoehe=300):
    """Kosten-Erlös-Diagramm. Zwei Reihen, eine Achse, Legende und Direktbeschriftung."""
    pad_l, pad_r, pad_o, pad_u = 58, 130, 24, 52
    innen_b, innen_h = breite - pad_l - pad_r, hoehe - pad_o - pad_u
    x_max = max(be['kapazitaet'], be['ist']) * 1.05 or 1
    y_max = max(be['kapazitaet_umsatz'], be['ist'] * be['umsatz_je_einheit'],
                be['fix_inkl_afa'] + be['kapazitaet'] * (be['umsatz_je_einheit'] - be['db_je_einheit'])) * 1.05 or 1
    X = lambda m: pad_l + innen_b * m / x_max
    Y = lambda v: pad_o + innen_h * (1 - v / y_max)
    var_je = be['umsatz_je_einheit'] - be['db_je_einheit']
    kosten = lambda m: be['fix_inkl_afa'] + var_je * m
    erloes = lambda m: be['umsatz_je_einheit'] * m

    teile = [f'<line x1="{pad_l}" y1="{Y(0):.1f}" x2="{breite-pad_r}" y2="{Y(0):.1f}" stroke="{RASTER}"/>',
             f'<line x1="{pad_l}" y1="{pad_o}" x2="{pad_l}" y2="{Y(0):.1f}" stroke="{RASTER}"/>']
    teile.append(f'<polyline fill="none" stroke="{SERIE_B}" stroke-width="2" stroke-linecap="round" '
                 f'points="{X(0):.1f},{Y(kosten(0)):.1f} {X(x_max):.1f},{Y(kosten(x_max)):.1f}"/>')
    teile.append(f'<polyline fill="none" stroke="{SERIE_A}" stroke-width="2" stroke-linecap="round" '
                 f'points="{X(0):.1f},{Y(0):.1f} {X(x_max):.1f},{Y(erloes(x_max)):.1f}"/>')
    bx, by = X(be['schwelle']), Y(erloes(be['schwelle']))
    teile.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{Y(0):.1f}" '
                 f'stroke="{INK_SOFT}" stroke-width="1" stroke-dasharray="3 3"/>')
    teile.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="5" fill="{INK}" stroke="{FLAECHE}" stroke-width="2"/>')
    teile.append(_t(bx, by - 12, 'Gewinnschwelle', text_anchor='middle', font_size='11.5',
                    font_weight='600', fill=INK))
    teile.append(_t(bx, hoehe - 26, zahl(be['schwelle'], 0), text_anchor='middle',
                    font_size='11.5', fill=INK_SOFT))
    ix, iy = X(be['ist']), Y(erloes(be['ist']))
    teile.append(f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{ix:.1f}" y2="{Y(0):.1f}" '
                 f'stroke="{SERIE_A}" stroke-width="1" stroke-dasharray="3 3"/>')
    teile.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="5" fill="{SERIE_A}" stroke="{FLAECHE}" stroke-width="2"/>')
    # Beschriftungen versetzen, wenn sie zu nah beieinander liegen
    tief = hoehe - 26 if abs(ix - bx) > 70 else hoehe - 10
    teile.append(_t(ix, tief, f'Ist {zahl(be["ist"], 0)}', text_anchor='middle',
                    font_size='11.5', font_weight='600', fill=INK))
    teile.append(_t(breite - pad_r + 10, Y(erloes(x_max)) + 14, 'Erlös',
                    font_size='12', font_weight='600', fill=INK))
    teile.append(_t(breite - pad_r + 10, Y(kosten(x_max)) + 4, 'Gesamtkosten',
                    font_size='12', font_weight='600', fill=INK))
    for anteil in (0, .5, 1):
        v = y_max * anteil
        teile.append(_t(pad_l - 8, Y(v) + 4, eur(v), text_anchor='end', font_size='11', fill=MUTED))
    return (f'<svg viewBox="0 0 {breite} {hoehe}" role="img" '
            f'aria-label="Kosten-Erlös-Diagramm mit Gewinnschwelle">' + ''.join(teile) + '</svg>')
