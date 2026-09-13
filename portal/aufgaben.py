#!/usr/bin/env python3
"""Warteschlange fuer das Auslesen der Dokumente.

Das Lesen laeuft nicht in der Anfrage. Beim Hochladen wird nur eine Aufgabe
eingereiht; ein Arbeiter holt sie ab. Faellt etwas um, wird es wiederholt und
der Fehler bleibt sichtbar.

    python3 portal/arbeiter.py          einmal alles abarbeiten
    python3 portal/arbeiter.py --dauer  laufen lassen
"""
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import leser                                              # noqa: E402
import speicher as sp                                     # noqa: E402

HOECHSTENS_VERSUCHE = 3


def einreihen(dokument_id, art='lesen'):
    with db.verbinden() as con:
        offen = con.execute("SELECT id FROM aufgabe WHERE dokument_id=? AND art=? "
                            "AND status IN ('wartet','laeuft')",
                            (dokument_id, art)).fetchone()
        if offen:
            return offen['id']
        cur = con.execute('INSERT INTO aufgabe (art, dokument_id, erstellt_am) '
                          'VALUES (?,?,?)', (art, dokument_id, db.jetzt()))
        return cur.lastrowid


def naechste():
    """Holt eine Aufgabe und markiert sie, damit zwei Arbeiter sich nicht in
    die Quere kommen."""
    with db.verbinden() as con:
        r = con.execute("SELECT * FROM aufgabe WHERE status='wartet' "
                        'ORDER BY id LIMIT 1').fetchone()
        if not r:
            return None
        con.execute("UPDATE aufgabe SET status='laeuft', versuche=versuche+1 "
                    "WHERE id=? AND status='wartet'", (r['id'],))
        if con.total_changes == 0:
            return None
        return dict(r)


def _fertig(aufgabe_id, fehler=None):
    with db.verbinden() as con:
        if fehler is None:
            con.execute("UPDATE aufgabe SET status='fertig', beendet_am=?, fehler=NULL "
                        'WHERE id=?', (db.jetzt(), aufgabe_id))
            return
        versuche = con.execute('SELECT versuche FROM aufgabe WHERE id=?',
                               (aufgabe_id,)).fetchone()['versuche']
        neu = 'fehler' if versuche >= HOECHSTENS_VERSUCHE else 'wartet'
        con.execute('UPDATE aufgabe SET status=?, fehler=?, beendet_am=? WHERE id=?',
                    (neu, str(fehler)[:500],
                     db.jetzt() if neu == 'fehler' else None, aufgabe_id))


def _ablegen(dokument_id, ergebnis):
    with db.verbinden() as con:
        con.execute('DELETE FROM extraktion WHERE dokument_id=?', (dokument_id,))
        con.execute(
            'INSERT INTO extraktion (dokument_id, weg, seiten, tabellen, rohtext, '
            'konfidenz, status, hinweis, erstellt_am) VALUES (?,?,?,?,?,?,?,?,?)',
            (dokument_id, ergebnis.get('weg', '?'), ergebnis.get('seiten'),
             json.dumps(ergebnis.get('tabellen', []), ensure_ascii=False),
             (ergebnis.get('rohtext') or '')[:200000],
             ergebnis.get('konfidenz'), ergebnis.get('status', 'roh'),
             ergebnis.get('hinweis'), db.jetzt()))


def _erkennung_anstossen(dokument_id, ergebnis):
    """Ein Scan ohne Textebene bekommt einen zweiten Anlauf, falls die
    Erkennung eingerichtet ist. Ist sie es nicht, bleibt der Hinweis stehen
    und jemand kuemmert sich von Hand darum."""
    if ergebnis.get('status') != 'ocr_noetig':
        return
    try:
        import erkennung
    except ImportError:
        return
    if erkennung.verfuegbar():
        einreihen(dokument_id, 'erkennen')


def _lesen(d):
    daten = sp.lesen(d['speicher_schluessel'])
    ergebnis = leser.lesen(d['dateiname'], daten)
    _ablegen(d['id'], ergebnis)
    db.protokollieren('dokument_gelesen',
                      detail=f'dokument {d["id"]}, Weg {ergebnis.get("weg")}',
                      nachher=ergebnis.get('hinweis'))
    _erkennung_anstossen(d['id'], ergebnis)


def _erkennen(d):
    import erkennung
    daten = sp.lesen(d['speicher_schluessel'])
    _ablegen(d['id'], erkennung.nachholen(d['id'], daten, d['dateiname']))


ARTEN = {'lesen': _lesen, 'erkennen': _erkennen}


def bearbeiten(aufgabe):
    d = None
    with db.verbinden() as con:
        r = con.execute('SELECT * FROM dokument WHERE id=?',
                        (aufgabe['dokument_id'],)).fetchone()
        d = dict(r) if r else None
    if not d:
        _fertig(aufgabe['id'], 'Das Dokument gibt es nicht mehr.')
        return False
    tun = ARTEN.get(aufgabe['art'])
    if not tun:
        _fertig(aufgabe['id'], f'Unbekannte Art „{aufgabe["art"]}".')
        return False
    try:
        tun(d)
        _fertig(aufgabe['id'])
        return True
    except Exception as e:                       # noqa: BLE001
        _fertig(aufgabe['id'], e)
        db.protokollieren(f'{aufgabe["art"]}_fehlgeschlagen',
                          detail=f'dokument {d["id"]}', nachher=str(e)[:200])
        return False


def abarbeiten(grenze=50):
    """Arbeitet die Warteschlange ab und meldet, was durchgelaufen ist."""
    gut = schlecht = 0
    for _ in range(grenze):
        a = naechste()
        if not a:
            break
        if bearbeiten(a):
            gut += 1
        else:
            schlecht += 1
    return gut, schlecht


def stand(periode_id):
    """Was von dieser Periode schon gelesen ist, fuer die Verwaltung."""
    with db.verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT d.id AS dokument_id, d.dateiname, d.aktiv, '
            'a.status AS aufgabe, a.fehler, '
            'e.weg, e.seiten, e.konfidenz, e.status AS extraktion, e.hinweis '
            'FROM dokument d '
            # Die jeweils letzte Aufgabe, damit ein zweiter Anlauf ueber die
            # Erkennung den Stand des ersten nicht verdeckt.
            'LEFT JOIN aufgabe a ON a.id = (SELECT MAX(id) FROM aufgabe '
            'WHERE dokument_id=d.id) '
            'LEFT JOIN extraktion e ON e.dokument_id=d.id '
            'WHERE d.periode_id=? AND d.aktiv=1 ORDER BY d.id', (periode_id,)).fetchall()]


def extraktion(dokument_id):
    with db.verbinden() as con:
        r = con.execute('SELECT * FROM extraktion WHERE dokument_id=?',
                        (dokument_id,)).fetchone()
        if not r:
            return None
        e = dict(r)
        e['tabellen'] = json.loads(e['tabellen'] or '[]')
        return e
