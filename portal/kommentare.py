#!/usr/bin/env python3
"""Anmerkungen zu einzelnen Dateien.

Der Mandant erklaert damit seinen Upload, wir fragen damit nach. Beide Seiten
sehen denselben Verlauf an derselben Datei. Wer schreibt, loest eine Meldung
bei der anderen Seite aus, damit niemand die Seite im Auge behalten muss.

Geloescht wird nichts. Eine Anmerkung gehoert zum Vorgang und steht im
Protokoll, sonst waere spaeter nicht mehr nachvollziehbar, worauf eine
Korrektur zurueckging.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import perioden as pd                                     # noqa: E402

LAENGSTE = 2000


class Verweigert(pd.Verweigert):
    """Damit die Aufrufer nur eine Ausnahme kennen muessen."""


def _kuerzen(text):
    text = ' '.join((text or '').split())
    if not text:
        raise Verweigert('Die Anmerkung ist leer.')
    if len(text) > LAENGSTE:
        raise Verweigert(f'Bitte höchstens {LAENGSTE} Zeichen.')
    return text


def schreiben(dokument_id, text, benutzer):
    """Schreibt eine Anmerkung und meldet sie der jeweils anderen Seite."""
    text = _kuerzen(text)
    admin = benutzer['rolle'] == 'admin'
    d = pd.dokument(dokument_id, None if admin else benutzer['mandant_id'])
    if not d:
        db.protokollieren('zugriff_verweigert', benutzer_id=benutzer['id'],
                          detail=f'kommentar dokument {dokument_id}')
        raise Verweigert('Diese Datei gibt es nicht oder sie gehört nicht zu Ihrem Zugang.')
    p = pd.periode_nach_id(d['periode_id'])
    with db.verbinden() as con:
        cur = con.execute(
            'INSERT INTO dateikommentar (dokument_id, benutzer_id, rolle, text, '
            'erstellt_am) VALUES (?,?,?,?,?)',
            (dokument_id, benutzer['id'], benutzer['rolle'], text, db.jetzt()))
        neu = cur.lastrowid
    db.protokollieren('kommentar_geschrieben', benutzer_id=benutzer['id'],
                      detail=f'dokument {dokument_id}, {d["dateiname"]}', nachher=text[:200])
    _melden(d, p, text, benutzer, admin)
    return neu


def _melden(d, p, text, benutzer, admin):
    import benachrichtigung as bn
    name = next((m['name'] for m in db.mandanten() if m['id'] == p['mandant_id']), '')
    monat = pd.monatstext(p['jahr_monat'])
    if admin:
        bn.kommentar_an_mandant(p['mandant_id'], d['dateiname'], monat, text,
                                p['jahr_monat'])
    else:
        bn.kommentar_an_admin(name, d['dateiname'], monat, text, p['id'])


def liste(dokument_id, mandant_id=None):
    """Der Verlauf einer Datei, aeltester Eintrag zuerst."""
    if mandant_id is not None and not pd.dokument(dokument_id, mandant_id):
        return []
    with db.verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT k.*, b.name AS verfasser FROM dateikommentar k '
            'LEFT JOIN benutzer b ON b.id=k.benutzer_id '
            'WHERE k.dokument_id=? ORDER BY k.id', (dokument_id,)).fetchall()]


def je_dokument(periode_id):
    """Alle Anmerkungen einer Periode auf einmal, nach Dokument sortiert."""
    raus = {}
    with db.verbinden() as con:
        for r in con.execute(
                'SELECT k.*, b.name AS verfasser FROM dateikommentar k '
                'JOIN dokument d ON d.id=k.dokument_id '
                'LEFT JOIN benutzer b ON b.id=k.benutzer_id '
                'WHERE d.periode_id=? ORDER BY k.id', (periode_id,)).fetchall():
            raus.setdefault(r['dokument_id'], []).append(dict(r))
    return raus


def anzahl(periode_id):
    with db.verbinden() as con:
        return con.execute(
            'SELECT COUNT(*) FROM dateikommentar k JOIN dokument d '
            'ON d.id=k.dokument_id WHERE d.periode_id=?', (periode_id,)).fetchone()[0]
