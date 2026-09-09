#!/usr/bin/env python3
"""Vergleicht die Ausgabe des Modells mit dem veröffentlichten Word-Bericht.

Aufruf: python3 tools/bericht/test_abgleich.py
Der Prüfdatensatz enthält im Juli exakt die Zahlen des Berichts, deshalb müssen
alle Juli-Größen bis auf Rundung übereinstimmen.
"""
import os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from modell import Bericht

SOLL = [   # Bezeichnung, Sollwert aus dem Bericht, zulässige Abweichung
    ('Umsatzerlöse',            365057.97, 0.01),
    ('Gesamtleistung',          367403.57, 0.01),
    ('Deckungsbeitrag',         224499.81, 0.01),
    ('DB-Quote in %',               61.10, 0.05),
    ('Fixkosten ohne AfA',      181605.65, 0.01),
    ('Fixkosten inkl. AfA',     188286.55, 0.01),
    ('EBITDA',                   42894.16, 0.01),
    ('EBIT',                     36213.26, 0.01),
    ('EBT',                      33645.81, 0.01),
    ('EBT-Marge in %',               9.20, 0.05),
    ('Auslastung in %',             81.60, 0.05),
    ('DSO in Tagen',                48.00, 0.50),
    ('Eigenkapitalquote in %',      35.80, 0.05),
    ('DB je Monteurstunde',         79.05, 0.01),
    ('Umsatz je Monteurstunde',    129.90, 0.01),
    ('Gewinnschwelle in Stunden', 2381.87, 0.01),
    ('Cash-Gewinnschwelle',      2297.35, 0.01),
    ('Sicherheitsabstand Std.',   428.43, 0.01),
    ('Sicherheitsabstand in %',     15.20, 0.05),
    ('Umsatzpuffer',            55653.06, 1.00),
]

b = Bericht(os.path.join(HIER, 'beispiel_lueftungstechnik.xlsx'))
m, be = b.m, b.break_even()
ist = {
    'Umsatzerlöse': m['umsatz'], 'Gesamtleistung': m['gesamtleistung'],
    'Deckungsbeitrag': m['db'], 'DB-Quote in %': m['db_quote'],
    'Fixkosten ohne AfA': m['fix_summe'], 'Fixkosten inkl. AfA': m['fix_inkl_afa'],
    'EBITDA': m['ebitda'], 'EBIT': m['ebit'], 'EBT': m['ebt'],
    'EBT-Marge in %': m['ebt_marge'], 'Auslastung in %': m['auslastung'],
    'DSO in Tagen': m['dso'], 'Eigenkapitalquote in %': m['ek_quote'],
    'DB je Monteurstunde': be['db_je_einheit'],
    'Umsatz je Monteurstunde': be['umsatz_je_einheit'],
    'Gewinnschwelle in Stunden': be['schwelle'],
    'Cash-Gewinnschwelle': be['cash_schwelle'],
    'Sicherheitsabstand Std.': be['abstand'],
    'Sicherheitsabstand in %': be['abstand_proz'],
    'Umsatzpuffer': be['puffer_umsatz'],
}
fehler = 0
for name, soll, toleranz in SOLL:
    hab = ist[name]
    ok = abs(hab - soll) <= toleranz
    if not ok:
        fehler += 1
    print(f'{"OK " if ok else "ABW"}  {name:26} Soll {soll:>12,.2f}  Ist {hab:>12,.2f}'
          .replace(',', '.'))
print(f'\n{len(SOLL) - fehler} von {len(SOLL)} Werten stimmen überein.')
sys.exit(1 if fehler else 0)
