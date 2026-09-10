#!/usr/bin/env python3
"""Legt einen Demo-Mandanten mit Testdaten an.

    VALTIX_DB=demo.sqlite3 VALTIX_ABLAGE=demo-ablage python3 portal/demo_daten.py

Gibt am Ende zwei Einladungslinks aus. Passwoerter werden nie vergeben, die
Personen setzen sie selbst. Nichts davon gehoert in eine echte Datenbank.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import perioden as pd                                     # noqa: E402

PDF = b'%PDF-1.4\n% Testdatei ohne Inhalt\n'


def main():
    db.anlegen()
    mid = db.mandant_anlegen('Muster Lüftungstechnik GmbH')
    pd.checkliste_uebernehmen(mid)

    admin = db.benutzer_anlegen('admin@vorschau.valtix', 'Administrator', 'admin')
    mandant = db.benutzer_anlegen('mandant@vorschau.valtix',
                                  'Ansprechpartner Muster', 'mandant', mid)

    # Juni: vollstaendig und eingereicht. Juli: angefangen.
    for slot in ('bwa', 'susa', 'opos_debitoren', 'opos_kreditoren', 'kontensalden'):
        pd.dokument_ablegen(mid, '2026-06', slot, f'{slot}-Juni.pdf',
                            'application/pdf', PDF + slot.encode(), None)
    pd.einreichen(mid, '2026-06', None)
    p = pd.periode(mid, '2026-06')
    pd.status_setzen(p['id'], 'in_pruefung', None)

    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA-Juli.pdf',
                        'application/pdf', PDF + b'juli', None)
    pd.entfaellt_setzen(mid, '2026-07', 'bestandsliste',
                        'Wir führen kein Lager', None)

    print('Mandant angelegt:', mid)
    print('Juni:', pd.ampel(mid, '2026-06'), '·', pd.periode(mid, '2026-06')['status'])
    print('Juli:', pd.ampel(mid, '2026-07'), '·', pd.periode(mid, '2026-07')['status'])
    basis = os.environ.get('VALTIX_BASIS', 'http://127.0.0.1:8000')
    print()
    print('Einladung Administrator:', f'{basis}/einladung/{admin}')
    print('Einladung Mandant:      ', f'{basis}/einladung/{mandant}')


if __name__ == '__main__':
    main()
