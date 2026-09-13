#!/usr/bin/env python3
"""Der gemeinsame Massnahmenplan.

Was aus dem Health Check an Massnahmen folgt, steht hier und nicht in einer
Mail. Beide Seiten sehen dieselbe Liste, beide schreiben Notizen daran, den
Status setzt wer will. Das ist der Teil, den ihr als gemeinsame Arbeit an den
Massnahmen verkauft, deshalb darf der Mandant hier auch etwas tun und nicht
nur zusehen.

Sichtbar ist die Liste nur fuer Pakete, die sie oeffnen. Geloescht wird
nichts: eine erledigte Massnahme bleibt stehen, sonst waere der Fortschritt
ueber die Monate nicht mehr zu sehen.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import pakete as pk                                       # noqa: E402

STATUS_TEXT = {
    'offen': 'offen',
    'laeuft': 'in Arbeit',
    'erledigt': 'erledigt',
    'verworfen': 'verworfen',
}
RANG_TEXT = {1: 'hoch', 2: 'mittel', 3: 'niedrig'}
LAENGSTER_TITEL = 200
LAENGSTE_NOTIZ = 2000


class Verweigert(Exception):
    """Fachlicher Fehler, dessen Text dem Nutzer gezeigt werden darf."""


def _text(wert, hoechstens, was):
    wert = ' '.join((wert or '').split())
    if not wert:
        raise Verweigert(f'{was} fehlt.')
    if len(wert) > hoechstens:
        raise Verweigert(f'Bitte höchstens {hoechstens} Zeichen für {was.lower()}.')
    return wert


def _zugriff(massnahme_id, nutzer):
    """Gibt die Massnahme zurueck, wenn der Zugang sie sehen darf."""
    with db.verbinden() as con:
        r = con.execute('SELECT * FROM massnahme WHERE id=?', (massnahme_id,)).fetchone()
    m = dict(r) if r else None
    if not m:
        raise Verweigert('Diese Maßnahme gibt es nicht.')
    if nutzer['rolle'] != 'admin':
        if m['mandant_id'] != nutzer.get('mandant_id'):
            db.protokollieren('zugriff_verweigert', benutzer_id=nutzer['id'],
                              detail=f'massnahme {massnahme_id}')
            raise Verweigert('Diese Maßnahme gehört nicht zu Ihrem Zugang.')
        if not pk.kann(nutzer['mandant_id'], 'massnahmen'):
            raise Verweigert('Maßnahmen gehören nicht zu Ihrem Paket.')
    return m


def anlegen(mandant_id, titel, beschreibung, von, rang=2, faellig_am=None):
    """Massnahmen legt Valtix an. Sie folgen aus dem Bericht, nicht umgekehrt."""
    if von['rolle'] != 'admin':
        raise Verweigert('Maßnahmen werden von Valtix angelegt.')
    titel = _text(titel, LAENGSTER_TITEL, 'Der Titel')
    if rang not in RANG_TEXT:
        raise Verweigert('Unbekannte Priorität.')
    with db.verbinden() as con:
        cur = con.execute(
            'INSERT INTO massnahme (mandant_id, titel, beschreibung, rang, '
            'faellig_am, erstellt_von, erstellt_am) VALUES (?,?,?,?,?,?,?)',
            (mandant_id, titel, (beschreibung or '').strip() or None, rang,
             faellig_am or None, von['id'], db.jetzt()))
        neu = cur.lastrowid
    db.protokollieren('massnahme_angelegt', benutzer_id=von['id'],
                      detail=f'mandant {mandant_id}, massnahme {neu}', nachher=titel)
    _melden_an_mandant(mandant_id, f'Neue Maßnahme: {titel}')
    return neu


def liste(mandant_id, offene_zuerst=True):
    """Alle Massnahmen des Mandanten, dazu die Anzahl der Notizen."""
    ordnung = ("CASE status WHEN 'offen' THEN 0 WHEN 'laeuft' THEN 1 ELSE 2 END, "
               'rang, id') if offene_zuerst else 'id'
    with db.verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT m.*, (SELECT COUNT(*) FROM massnahme_notiz n '
            'WHERE n.massnahme_id=m.id) AS notizen '
            f'FROM massnahme m WHERE m.mandant_id=? ORDER BY {ordnung}',
            (mandant_id,)).fetchall()]


def stand(mandant_id):
    """Wie viele offen, in Arbeit und erledigt sind. Fuer die Kopfzeile."""
    zaehler = {k: 0 for k in STATUS_TEXT}
    for m in liste(mandant_id):
        zaehler[m['status']] = zaehler.get(m['status'], 0) + 1
    return zaehler


def status_setzen(massnahme_id, neu, nutzer):
    if neu not in STATUS_TEXT:
        raise Verweigert('Unbekannter Status.')
    m = _zugriff(massnahme_id, nutzer)
    if m['status'] == neu:
        return m['status']
    with db.verbinden() as con:
        con.execute('UPDATE massnahme SET status=?, erledigt_am=? WHERE id=?',
                    (neu, db.jetzt() if neu == 'erledigt' else None, massnahme_id))
    db.protokollieren('massnahme_status', benutzer_id=nutzer['id'],
                      detail=f'massnahme {massnahme_id}, {m["titel"]}',
                      vorher=m['status'], nachher=neu)
    if nutzer['rolle'] != 'admin':
        _melden_an_admin(m['mandant_id'],
                         f'„{m["titel"]}" steht jetzt auf {STATUS_TEXT[neu]}.')
    else:
        _melden_an_mandant(m['mandant_id'],
                           f'„{m["titel"]}" steht jetzt auf {STATUS_TEXT[neu]}.')
    return neu


def notiz(massnahme_id, text, nutzer):
    m = _zugriff(massnahme_id, nutzer)
    text = _text(text, LAENGSTE_NOTIZ, 'Die Notiz')
    with db.verbinden() as con:
        con.execute('INSERT INTO massnahme_notiz (massnahme_id, benutzer_id, rolle, '
                    'text, erstellt_am) VALUES (?,?,?,?,?)',
                    (massnahme_id, nutzer['id'], nutzer['rolle'], text, db.jetzt()))
    db.protokollieren('massnahme_notiz', benutzer_id=nutzer['id'],
                      detail=f'massnahme {massnahme_id}', nachher=text[:200])
    if nutzer['rolle'] != 'admin':
        _melden_an_admin(m['mandant_id'], f'Notiz zu „{m["titel"]}": {text[:200]}')
    else:
        _melden_an_mandant(m['mandant_id'], f'Notiz zu „{m["titel"]}": {text[:200]}')
    return True


def notizen(massnahme_id):
    with db.verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT n.*, b.name AS verfasser FROM massnahme_notiz n '
            'LEFT JOIN benutzer b ON b.id=n.benutzer_id '
            'WHERE n.massnahme_id=? ORDER BY n.id', (massnahme_id,)).fetchall()]


def je_massnahme(mandant_id):
    raus = {}
    with db.verbinden() as con:
        for r in con.execute(
                'SELECT n.*, b.name AS verfasser FROM massnahme_notiz n '
                'JOIN massnahme m ON m.id=n.massnahme_id '
                'LEFT JOIN benutzer b ON b.id=n.benutzer_id '
                'WHERE m.mandant_id=? ORDER BY n.id', (mandant_id,)).fetchall():
            raus.setdefault(r['massnahme_id'], []).append(dict(r))
    return raus


def _melden_an_admin(mandant_id, text):
    import benachrichtigung as bn
    name = (db.mandant(mandant_id) or {}).get('name', '')
    bn.in_app(f'{name}: {text}', rolle='admin', ziel=f'/massnahmen/{mandant_id}')


def _melden_an_mandant(mandant_id, text):
    import benachrichtigung as bn
    for b in db.benutzer_liste():
        if b['rolle'] == 'mandant' and b['mandant_id'] == mandant_id and b['aktiv']:
            bn.in_app(text, benutzer_id=b['id'], ziel='/massnahmen')
