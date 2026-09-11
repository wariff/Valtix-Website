#!/usr/bin/env python3
"""Liest hochgeladene Dateien aus.

Reihenfolge nach der Spezifikation: strukturierte Formate zuerst, dann PDF mit
Textebene, OCR nur als Notloesung. Diese Datei macht die ersten beiden Wege.
Wo OCR noetig waere, wird das gemeldet statt geraten.

Nichts davon wird automatisch produktiv. Das Ergebnis ist Rohmaterial fuer die
Pruefansicht in M4.
"""
import csv
import io
import json
import os
import re
import warnings

import openpyxl

warnings.filterwarnings('ignore')

# DATEV-Exporte beginnen mit dieser Kennung in der ersten Zeile.
DATEV_KENNUNG = re.compile(r'^"?EXTF"?;')
# Wieviel Text eine PDF-Seite mindestens haben muss, damit wir sie fuer
# digital erzeugt halten. Darunter ist es ein Scan und braucht OCR.
ZEICHEN_JE_SEITE = 60


class NichtLesbar(Exception):
    pass


def _zahl(wert):
    """Deutsche Schreibweise in eine Zahl. Gibt None, wenn es keine ist."""
    if wert is None:
        return None
    if isinstance(wert, (int, float)):
        return float(wert)
    t = str(wert).strip()
    if not t:
        return None
    t = t.replace(' ', ' ').replace('€', '').replace('EUR', '').strip()
    negativ = t.startswith('-') or t.endswith('-') or (t.startswith('(') and t.endswith(')'))
    t = t.strip('()-').strip()
    if not re.fullmatch(r'[\d.,\s]+', t):
        return None
    t = t.replace(' ', '')
    # Deutsche Schreibweise: Punkt trennt Tausender, Komma die Dezimalstellen.
    # Ohne Komma ist der Punkt nur dann ein Tausendertrenner, wenn danach
    # genau drei Ziffern stehen. Sonst waere aus 1234.56 sonst 123456 geworden,
    # bei Betraegen ein Faktor hundert.
    if ',' in t:
        t = t.replace('.', '').replace(',', '.')
    else:
        stuecke = t.split('.')
        if len(stuecke) > 1 and all(len(x) == 3 for x in stuecke[1:]):
            t = ''.join(stuecke)
        elif len(stuecke) > 2:
            t = ''.join(stuecke)
    try:
        z = float(t)
    except ValueError:
        return None
    return -z if negativ else z


def _text(wert):
    return '' if wert is None else str(wert).strip()


# ------------------------------------------------------------------- Formate
def aus_xlsx(daten):
    wb = openpyxl.load_workbook(io.BytesIO(daten), data_only=True, read_only=True)
    tabellen = []
    for ws in wb.worksheets:
        zeilen = []
        for r in ws.iter_rows(values_only=True):
            if r is None:
                continue
            werte = [_text(z) for z in r]
            if any(werte):
                zeilen.append(werte)
        if zeilen:
            tabellen.append({'blatt': ws.title, 'zeilen': zeilen[:2000]})
    wb.close()
    if not tabellen:
        raise NichtLesbar('Die Arbeitsmappe enthält keine Zeilen.')
    return {'weg': 'xlsx', 'tabellen': tabellen, 'seiten': len(tabellen),
            'konfidenz': 1.0}


def _entschluesseln(daten):
    """DATEV und viele Exporte kommen als Windows-1252, nicht als UTF-8."""
    for kodierung in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        try:
            return daten.decode(kodierung), kodierung
        except UnicodeDecodeError:
            continue
    raise NichtLesbar('Die Zeichenkodierung der Datei ist unbekannt.')


def aus_csv(daten):
    text, kodierung = _entschluesseln(daten)
    probe = text[:4000]
    try:
        dialekt = csv.Sniffer().sniff(probe, delimiters=';,\t|')
        trenner = dialekt.delimiter
    except csv.Error:
        # Im deutschen Raum ist das Semikolon der Normalfall.
        trenner = ';' if probe.count(';') >= probe.count(',') else ','
    zeilen = [z for z in csv.reader(io.StringIO(text), delimiter=trenner) if any(z)]
    if not zeilen:
        raise NichtLesbar('Die Datei enthält keine Zeilen.')
    return {'weg': 'csv', 'tabellen': [{'blatt': 'Datei', 'zeilen': zeilen[:5000]}],
            'seiten': 1, 'konfidenz': 1.0,
            'hinweis': f'Trennzeichen „{trenner}", Kodierung {kodierung}'}


def aus_datev(daten):
    """DATEV-Export im EXTF-Format. Zeile 1 ist der Kopf, Zeile 2 die
    Spaltennamen, ab Zeile 3 die Buchungen."""
    text, kodierung = _entschluesseln(daten)
    zeilen = [z for z in csv.reader(io.StringIO(text), delimiter=';') if any(z)]
    if len(zeilen) < 3:
        raise NichtLesbar('Der DATEV-Export enthält keine Buchungen.')
    kopf = zeilen[0]
    # Feldfolge des EXTF-Kopfes: 4 Formatname, 11 Beraternummer,
    # 12 Mandantennummer. Gezaehlt ab eins, im Code also drei kleiner.
    art = kopf[3] if len(kopf) > 3 else ''
    berater = kopf[10] if len(kopf) > 10 else ''
    mandant = kopf[11] if len(kopf) > 11 else ''
    return {'weg': 'datev',
            'tabellen': [{'blatt': 'Buchungen', 'zeilen': zeilen[1:20000]}],
            'seiten': 1, 'konfidenz': 1.0,
            'hinweis': f'DATEV-Format „{art}", Berater {berater}, Mandant {mandant}, '
                       f'Kodierung {kodierung}, {len(zeilen) - 2} Buchungen'}


def aus_pdf(daten):
    """PDF mit Textebene. Fehlt die Ebene, wird das gemeldet, nicht geraten."""
    import pdfplumber
    tabellen, stuecke, seiten = [], [], 0
    with pdfplumber.open(io.BytesIO(daten)) as pdf:
        seiten = len(pdf.pages)
        for nr, seite in enumerate(pdf.pages[:40], start=1):
            t = seite.extract_text() or ''
            stuecke.append(t)
            for tab in (seite.extract_tables() or []):
                zeilen = [[_text(z) for z in r] for r in tab if any(r)]
                if zeilen:
                    tabellen.append({'blatt': f'Seite {nr}', 'zeilen': zeilen})
    text = '\n'.join(stuecke).strip()
    if seiten and len(text) / seiten < ZEICHEN_JE_SEITE:
        return {'weg': 'pdf_text', 'tabellen': [], 'rohtext': text, 'seiten': seiten,
                'konfidenz': 0.0, 'status': 'ocr_noetig',
                'hinweis': 'Die Datei hat keine durchsuchbare Textebene, '
                           'vermutlich ein Scan oder Foto. Sie braucht OCR.'}
    return {'weg': 'pdf_text', 'tabellen': tabellen, 'rohtext': text[:200000],
            'seiten': seiten, 'konfidenz': 0.9 if tabellen else 0.6,
            'hinweis': f'{len(tabellen)} Tabellen erkannt' if tabellen
                       else 'Text erkannt, keine Tabellenstruktur'}


# -------------------------------------------------------------------- Router
def lesen(dateiname, daten):
    """Waehlt den Weg nach Endung und Inhalt, nicht nach dem gemeldeten Typ."""
    endung = os.path.splitext(dateiname or '')[1].lower()
    if endung in ('.xlsx', '.xls'):
        return aus_xlsx(daten)
    if endung in ('.csv', '.txt'):
        kopf = daten[:200].decode('cp1252', errors='replace')
        if DATEV_KENNUNG.match(kopf.lstrip()):
            return aus_datev(daten)
        return aus_csv(daten)
    if endung == '.pdf':
        return aus_pdf(daten)
    if endung in ('.jpg', '.jpeg', '.png'):
        return {'weg': 'bild', 'tabellen': [], 'seiten': 1, 'konfidenz': 0.0,
                'status': 'ocr_noetig',
                'hinweis': 'Ein Bild lässt sich nur mit OCR auslesen.'}
    if endung == '.zip':
        return {'weg': 'zip', 'tabellen': [], 'seiten': 0, 'konfidenz': 0.0,
                'status': 'verworfen',
                'hinweis': 'Archive werden nicht ausgepackt. Bitte einzeln hochladen.'}
    raise NichtLesbar(f'Für „{endung}" gibt es keinen Leseweg.')


def als_json(ergebnis):
    return json.dumps(ergebnis.get('tabellen', []), ensure_ascii=False)
