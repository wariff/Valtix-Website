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


def bearbeiten(aufgabe):
    d = None
    with db.verbinden() as con:
        r = con.execute('SELECT * FROM dokument WHERE id=?',
                        (aufgabe['dokument_id'],)).fetchone()
        d = dict(r) if r else None
    if not d:
        _fertig(aufgabe['id'], 'Das Dokument gibt es nicht mehr.')
        return False
    try:
        daten = sp.lesen(d['speicher_schluessel'])
        ergebnis = leser.lesen(d['dateiname'], daten)
        _ablegen(d['id'], ergebnis)
        _fertig(aufgabe['id'])
        db.protokollieren('dokument_gelesen',
                          detail=f'dokument {d["id"]}, Weg {ergebnis.get("weg")}',
                          nachher=ergebnis.get('hinweis'))
        return True
    except Exception as e:                       # noqa: BLE001
        _fertig(aufgabe['id'], e)
        db.protokollieren('lesen_fehlgeschlagen', detail=f'dokument {d["id"]}',
                          nachher=str(e)[:200])
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
            'LEFT JOIN aufgabe a ON a.dokument_id=d.id AND a.art=\'lesen\' '
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
