#!/usr/bin/env python3
"""Ordnet Konten und BWA-Zeilen den Valtix-Positionen zu.

WICHTIG, BITTE PRUEFEN. Die Kontenbereiche unten sind eine fachliche
Schaetzung nach den ueblichen Standardkontenrahmen SKR03 und SKR04. Sie sind
nicht an echten Mandantendaten geprueft. Jede Zuordnung, die daraus entsteht,
geht durch die Pruefansicht und muss freigegeben werden; automatisch wird
nichts produktiv. Wer eine echte anonymisierte Summen- und Saldenliste hat,
korrigiert diese Tabelle einmal und danach lernt das Portal je Mandant dazu.

Die Zielfelder entsprechen den Zeilen der Eingabevorlage, damit der Export
spaltengleich wird und der Berichtsgenerator sie ohne Uebersetzung liest.
"""
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402

# schluessel -> (Blatt der Eingabevorlage, Zeile, Klartext, Vorzeichen)
# Vorzeichen 1 heisst: positiv eintragen, so wie die Vorlage es erwartet.
ZIELFELDER = {
    'hauptleistung':  ('2 GuV', 6,  'Erlöse Hauptleistung', 1),
    'nebenleistung1': ('2 GuV', 7,  'Erlöse Nebenleistung 1', 1),
    'warenverkauf':   ('2 GuV', 9,  'Warenverkauf / weiterberechnetes Material', 1),
    'sonstige_ertrag': ('2 GuV', 11, 'Sonstige betriebliche Erträge', 1),
    'wareneinsatz':   ('2 GuV', 15, 'Wareneinsatz / Materialaufwand', 1),
    'fremdleistung':  ('2 GuV', 16, 'Fremdleistungen / Subunternehmer', 1),
    'sonst_variabel': ('2 GuV', 21, 'Sonstige variable Kosten', 1),
    'personal':       ('2 GuV', 27, 'Personalaufwand', 1),
    'miete':          ('2 GuV', 28, 'Miete & Nebenkosten', 1),
    'energie':        ('2 GuV', 29, 'Energie', 1),
    'fahrzeuge':      ('2 GuV', 30, 'Fahrzeuge / Fuhrpark', 1),
    'wartung':        ('2 GuV', 31, 'Wartung & Instandhaltung', 1),
    'versicherung':   ('2 GuV', 32, 'Versicherungen & Beiträge', 1),
    'it':             ('2 GuV', 33, 'IT, Software & Kommunikation', 1),
    'marketing':      ('2 GuV', 34, 'Marketing & Vertrieb', 1),
    'beratung':       ('2 GuV', 35, 'Beratung', 1),
    'sonst_aufwand':  ('2 GuV', 36, 'Sonstige betriebliche Aufwendungen', 1),
    'afa':            ('2 GuV', 41, 'Abschreibungen', 1),
    'zinsaufwand':    ('2 GuV', 43, 'Zinsaufwand', 1),
    'zinsertrag':     ('2 GuV', 44, 'Zinserträge', 1),
    'liquide':        ('4 Liquidität & Bilanz', 6,  'Liquide Mittel', 1),
    'forderungen':    ('4 Liquidität & Bilanz', 7,  'Offene Forderungen', 1),
    'kurzfr_verb':    ('4 Liquidität & Bilanz', 8,  'Kurzfristige Verbindlichkeiten', 1),
    'eigenkapital':   ('4 Liquidität & Bilanz', 13, 'Eigenkapital', 1),
    'bilanzsumme':    ('4 Liquidität & Bilanz', 14, 'Bilanzsumme', 1),
}

# Kontenbereiche. (von, bis, zielfeld). GESCHAETZT, siehe Kopf der Datei.
SKR04 = [
    (4000, 4299, 'hauptleistung'),
    (4300, 4499, 'warenverkauf'),
    (4500, 4999, 'sonstige_ertrag'),
    (5000, 5299, 'wareneinsatz'),
    (5300, 5999, 'fremdleistung'),
    (6000, 6199, 'personal'),
    (6200, 6299, 'afa'),
    (6300, 6349, 'miete'),
    (6350, 6399, 'energie'),
    (6400, 6499, 'wartung'),
    (6500, 6599, 'fahrzeuge'),
    (6600, 6699, 'marketing'),
    (6700, 6799, 'sonst_aufwand'),
    (6800, 6819, 'it'),
    (6820, 6849, 'beratung'),
    (6850, 6899, 'sonst_aufwand'),
    (6900, 6999, 'versicherung'),
    (7100, 7299, 'zinsertrag'),
    (7300, 7399, 'zinsaufwand'),
]
SKR03 = [
    (8000, 8799, 'hauptleistung'),
    (8800, 8899, 'warenverkauf'),
    (8900, 8999, 'sonstige_ertrag'),
    (3000, 3499, 'wareneinsatz'),
    (3500, 3999, 'fremdleistung'),
    (4100, 4199, 'personal'),
    (4200, 4249, 'miete'),
    (4250, 4299, 'energie'),
    (4300, 4399, 'versicherung'),
    (4400, 4499, 'wartung'),
    (4500, 4599, 'fahrzeuge'),
    (4600, 4699, 'marketing'),
    (4800, 4829, 'wartung'),
    (4830, 4899, 'afa'),
    (4900, 4949, 'it'),
    (4950, 4959, 'beratung'),
    (4960, 4999, 'sonst_aufwand'),
    (2100, 2199, 'zinsaufwand'),
    (2650, 2699, 'zinsertrag'),
]
# Bilanzkonten, in beiden Rahmen aehnlich genug fuer eine Schaetzung.
BILANZ = [
    (1200, 1299, 'liquide'),
    (1400, 1499, 'forderungen'),
    (1600, 1699, 'kurzfr_verb'),
    (2000, 2099, 'eigenkapital'),
]

# Wortmuster fuer BWA-Zeilen, wenn keine Kontonummer dabeisteht.
WORTREGELN = [
    (r'umsatzerl|erl[öo]se aus|haupterl', 'hauptleistung'),
    (r'warenverkauf|handelswaren', 'warenverkauf'),
    (r'sonstige.*ertr[äa]g|übrige ertr', 'sonstige_ertrag'),
    (r'wareneinsatz|materialaufwand|rohstoffe|bezogene waren', 'wareneinsatz'),
    (r'fremdleist|subunternehm|bezogene leistung', 'fremdleistung'),
    (r'personalaufwand|l[öo]hne|geh[äa]lter|soziale abgaben', 'personal'),
    (r'raumkosten|miete|pacht|nebenkosten', 'miete'),
    (r'energie|strom|heizung|gas\b', 'energie'),
    (r'fahrzeug|kfz|fuhrpark', 'fahrzeuge'),
    (r'reparatur|instandhalt|wartung', 'wartung'),
    (r'versicherung|beitr[äa]ge|berufsgenossen', 'versicherung'),
    (r'\bit\b|software|edv|telefon|kommunikation|porto', 'it'),
    (r'werbe|marketing|vertrieb|reisekosten', 'marketing'),
    (r'beratung|rechts|steuerberat|abschluss', 'beratung'),
    (r'abschreibung|\bafa\b', 'afa'),
    (r'zinsaufwand|zinsen und [äa]hnliche aufwend', 'zinsaufwand'),
    (r'zinsertr|zinsen und [äa]hnliche ertr', 'zinsertrag'),
    (r'sonstige betriebliche aufwend|übrige kosten', 'sonst_aufwand'),
    (r'\bbank\b|kasse|guthaben bei kreditinstitut', 'liquide'),
    (r'forderungen aus', 'forderungen'),
    (r'verbindlichkeiten aus', 'kurzfr_verb'),
    (r'eigenkapital', 'eigenkapital'),
    (r'bilanzsumme|summe aktiva|summe passiva', 'bilanzsumme'),
]


def kontonummer(text):
    """Holt eine Kontonummer aus einem Feld, wenn dort eine steht."""
    t = str(text or '').strip()
    m = re.fullmatch(r'0*(\d{4,5})', t)
    return int(m.group(1)) if m else None


def rahmen_erkennen(konten):
    """SKR03 oder SKR04. Erlöse liegen im SKR03 bei 8000, im SKR04 bei 4000."""
    achter = sum(1 for k in konten if 8000 <= k <= 8999)
    vierer = sum(1 for k in konten if 4000 <= k <= 4999)
    dreier = sum(1 for k in konten if 3000 <= k <= 3999)
    if achter or dreier > vierer:
        return 'SKR03'
    if vierer:
        return 'SKR04'
    return 'unbekannt'


def _aus_bereich(konto, bereiche):
    for von, bis, ziel in bereiche:
        if von <= konto <= bis:
            return ziel
    return None


def aus_konto(konto, rahmen):
    ziel = _aus_bereich(konto, BILANZ)
    if ziel:
        return ziel, 0.7
    bereiche = SKR03 if rahmen == 'SKR03' else SKR04
    ziel = _aus_bereich(konto, bereiche)
    return (ziel, 0.75) if ziel else (None, 0.0)


def aus_bezeichnung(text):
    t = str(text or '').lower()
    for muster, ziel in WORTREGELN:
        if re.search(muster, t):
            return ziel, 0.6
    return None, 0.0


def gelernte_regeln(mandant_id):
    with db.verbinden() as con:
        return {r['quelle']: r['zielfeld'] for r in con.execute(
            'SELECT quelle, zielfeld FROM mapping_regel WHERE mandant_id=?',
            (mandant_id,)).fetchall()}


def regel_merken(mandant_id, quelle, bezeichnung, zielfeld, von=None):
    if zielfeld not in ZIELFELDER:
        raise ValueError('Unbekanntes Zielfeld.')
    with db.verbinden() as con:
        con.execute('INSERT INTO mapping_regel (mandant_id, quelle, quellbezeichnung, '
                    'zielfeld, gesetzt_von, gesetzt_am) VALUES (?,?,?,?,?,?) '
                    'ON CONFLICT(mandant_id, quelle) DO UPDATE SET '
                    'zielfeld=excluded.zielfeld, quellbezeichnung=excluded.quellbezeichnung, '
                    'gesetzt_von=excluded.gesetzt_von, gesetzt_am=excluded.gesetzt_am',
                    (mandant_id, str(quelle), bezeichnung, zielfeld, von, db.jetzt()))
    db.protokollieren('mapping_gelernt', benutzer_id=von,
                      detail=f'mandant {mandant_id}, {quelle}', nachher=zielfeld)


def vorschlag(quelle, bezeichnung, rahmen, gelernt=None):
    """Gibt (zielfeld, konfidenz, woher). Gelernte Regeln schlagen alles."""
    schluessel = str(quelle or bezeichnung or '').strip()
    if gelernt and schluessel in gelernt:
        return gelernt[schluessel], 1.0, 'gelernt'
    konto = kontonummer(quelle)
    if konto:
        ziel, k = aus_konto(konto, rahmen)
        if ziel:
            return ziel, k, f'Kontenbereich {rahmen}'
    ziel, k = aus_bezeichnung(bezeichnung)
    if ziel:
        return ziel, k, 'Bezeichnung'
    return None, 0.0, 'offen'
