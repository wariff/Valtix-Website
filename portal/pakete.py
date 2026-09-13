#!/usr/bin/env python3
"""Welches Paket welche Ansicht oeffnet.

Die drei Pakete stehen so auf der Website: Analyse als einmalige
Bestandsaufnahme, Betreuung mit einem Pitch im Monat, Intensiv mit zwei.
Zwischen Betreuung und Intensiv liegt kein Unterschied im Portal, der liegt
in der Taktung der Gespraeche. Das ist Absicht und keine Luecke.

An einer Stelle steht, was ein Paket oeffnet. Wer eine Ansicht absichert,
fragt hier und nicht an der Oberflaeche nach.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402

# 'verlauf'     mehr als der letzte Monat, also die Entwicklung ueber die Zeit
# 'massnahmen'  der gemeinsame Massnahmenplan
PAKETE = {
    'analyse': {
        'klar': 'Analyse',
        'beschreibung': 'Der Financial Health Check als einmalige Bestandsaufnahme.',
        'kann': set(),
    },
    'betreuung': {
        'klar': 'Betreuung',
        'beschreibung': 'Health Check plus ein Pitch pro Monat.',
        'kann': {'verlauf', 'massnahmen'},
    },
    'intensiv': {
        'klar': 'Intensiv',
        'beschreibung': 'Health Check plus zwei Pitches pro Monat.',
        'kann': {'verlauf', 'massnahmen'},
    },
}
STANDARD = 'analyse'


class Verweigert(Exception):
    """Das Paket des Mandanten oeffnet diese Ansicht nicht."""


def gueltig(schluessel):
    return schluessel in PAKETE


def paket(mandant_id):
    """Das Paket des Mandanten. Unbekanntes faellt auf das kleinste zurueck,
    damit ein Fehler in den Daten nicht versehentlich etwas oeffnet."""
    m = db.mandant(mandant_id) if mandant_id else None
    schluessel = (m or {}).get('paket') or STANDARD
    return schluessel if gueltig(schluessel) else STANDARD


def klar(mandant_id):
    return PAKETE[paket(mandant_id)]['klar']


def kann(mandant_id, was):
    return was in PAKETE[paket(mandant_id)]['kann']


def pflicht(nutzer, was):
    """Fuer Ansichten. Ein Administrator sieht alles, ein Mandant sein Paket."""
    if nutzer and nutzer['rolle'] == 'admin':
        return True
    if not nutzer or not kann(nutzer.get('mandant_id'), was):
        raise Verweigert('Diese Ansicht gehört nicht zu Ihrem Paket.')
    return True


def setzen(mandant_id, neu, von=None):
    if not gueltig(neu):
        raise ValueError(f'Unbekanntes Paket „{neu}".')
    alt = paket(mandant_id)
    with db.verbinden() as con:
        con.execute('UPDATE mandant SET paket=? WHERE id=?', (neu, mandant_id))
    db.protokollieren('paket_geaendert', benutzer_id=von,
                      detail=f'mandant {mandant_id}', vorher=alt, nachher=neu)
