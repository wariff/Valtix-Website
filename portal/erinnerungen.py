#!/usr/bin/env python3
"""Erinnert Mandanten an fehlende Unterlagen.

Einmal taeglich aufrufen, etwa aus einem Zeitplan auf dem Server:

    python3 portal/erinnerungen.py            versenden
    python3 portal/erinnerungen.py --probe    nur zeigen, was anstuende

Stichtag ist standardmaessig der 10. des Folgemonats, global ueber die
Einstellung `erinnerung_tag` und je Mandant ueber `mandant.erinnerung_tag`.
Erinnert wird hoechstens einmal je Mandant und Monat; das steht im Protokoll.
"""
import os
import sys
from datetime import date

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import perioden as pd                                     # noqa: E402
import benachrichtigung as bn                             # noqa: E402

STANDARD_TAG = 10


def stichtag(mandant):
    eigener = mandant.get('erinnerung_tag') if isinstance(mandant, dict) else None
    if eigener:
        return int(eigener)
    return int(db.einstellung('erinnerung_tag', STANDARD_TAG))


def _schon_erinnert(mandant_id, jahr_monat):
    kennung = f'mandant {mandant_id}, {jahr_monat}'
    with db.verbinden() as con:
        return bool(con.execute(
            "SELECT 1 FROM protokoll WHERE ereignis='erinnerung_versendet' "
            'AND detail=? LIMIT 1', (kennung,)).fetchone())


def faellig(heute=None):
    """Wer heute eine Erinnerung bekaeme, ohne etwas zu versenden."""
    heute = heute or date.today()
    jahr, monat = (heute.year, heute.month - 1) if heute.month > 1 else (heute.year - 1, 12)
    jahr_monat = f'{jahr}-{monat:02d}'
    raus = []
    for m in db.mandanten():
        if heute.day < stichtag(m):
            continue
        p = pd.periode(m['id'], jahr_monat)
        if p and (p['status'] not in pd.OFFEN_FUER_UPLOAD):
            continue                                  # schon eingereicht
        fehlend = pd.fehlende_pflichtslots(m['id'], jahr_monat)
        if not fehlend:
            continue
        if _schon_erinnert(m['id'], jahr_monat):
            continue
        raus.append({'mandant': m, 'jahr_monat': jahr_monat,
                     'fehlend': [f['bezeichnung'] for f in fehlend]})
    return raus


def versenden(heute=None):
    anzahl = 0
    for e in faellig(heute):
        empfaenger = [b for b in db.benutzer_liste()
                      if b['rolle'] == 'mandant' and b['mandant_id'] == e['mandant']['id']
                      and b['aktiv'] and not b['einladung']]
        for b in empfaenger:
            bn.erinnerung(b['email'], e['mandant']['name'], e['jahr_monat'], e['fehlend'])
        bn.in_app(f'Für {e["jahr_monat"]} fehlen noch: {", ".join(e["fehlend"])}.',
                  rolle='mandant')
        db.protokollieren('erinnerung_versendet',
                          detail=f'mandant {e["mandant"]["id"]}, {e["jahr_monat"]}',
                          nachher=', '.join(e['fehlend'])[:200])
        anzahl += 1
    return anzahl


def main():
    db.anlegen()
    probe = '--probe' in sys.argv
    if probe:
        for e in faellig():
            print(f'{e["mandant"]["name"]}  {e["jahr_monat"]}  fehlt: '
                  f'{", ".join(e["fehlend"])}')
        return 0
    print(f'{versenden()} Erinnerungen versendet')
    return 0


if __name__ == '__main__':
    sys.exit(main())
