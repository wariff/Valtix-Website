#!/usr/bin/env python3
"""Perioden, Checkliste, Dokumente, Einreichen.

Eine Periode ist ein Mandant und ein Monat im Format YYYY-MM. Rueckwirkende
Monate sind ausdruecklich erlaubt; es gibt keinen Zwang zur Reihenfolge.

Die Mandantentrennung wird hier durchgesetzt: jede Funktion, die etwas
herausgibt, bekommt die Mandantennummer und prueft sie. Auf der Datenbank
selbst kommt die Trennung mit dem Umzug auf PostgreSQL dazu.
"""
import io
import os
import re
import sys
import zipfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import speicher as sp                                     # noqa: E402

MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
          'August', 'September', 'Oktober', 'November', 'Dezember']
STATUS_TEXT = {
    'offen': 'offen',
    'hochgeladen': 'hochgeladen',
    'eingereicht': 'eingereicht',
    'in_pruefung': 'in Bearbeitung',
    'freigegeben': 'freigegeben',
    'bericht_gestellt': 'Bericht liegt vor',
}
# Solange die Periode in einem dieser Zustaende ist, darf der Mandant hochladen.
OFFEN_FUER_UPLOAD = ('offen', 'hochgeladen')


class Verweigert(Exception):
    """Fachlicher Fehler, dessen Text dem Nutzer gezeigt werden darf."""


def monatstext(jahr_monat):
    jahr, monat = jahr_monat.split('-')
    return f'{MONATE[int(monat) - 1]} {jahr}'


def gueltig(jahr_monat):
    return bool(re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', jahr_monat or ''))


# ------------------------------------------------------------------ Periode
def periode(mandant_id, jahr_monat, anlegen=False):
    if not gueltig(jahr_monat):
        raise Verweigert('Der Monat muss die Form 2026-07 haben.')
    with db.verbinden() as con:
        r = con.execute('SELECT * FROM periode WHERE mandant_id=? AND jahr_monat=?',
                        (mandant_id, jahr_monat)).fetchone()
        if r or not anlegen:
            return dict(r) if r else None
        con.execute('INSERT INTO periode (mandant_id, jahr_monat, status, angelegt_am) '
                    'VALUES (?,?,?,?)', (mandant_id, jahr_monat, 'offen', db.jetzt()))
        r = con.execute('SELECT * FROM periode WHERE mandant_id=? AND jahr_monat=?',
                        (mandant_id, jahr_monat)).fetchone()
        return dict(r)


def periode_nach_id(periode_id, mandant_id=None):
    """mandant_id gesetzt heisst: fremde Perioden gibt es nicht, auch nicht als
    Fehlermeldung. Der Aufrufer sieht None und kann nicht raten."""
    with db.verbinden() as con:
        if mandant_id is None:
            r = con.execute('SELECT * FROM periode WHERE id=?', (periode_id,)).fetchone()
        else:
            r = con.execute('SELECT * FROM periode WHERE id=? AND mandant_id=?',
                            (periode_id, mandant_id)).fetchone()
        return dict(r) if r else None


def perioden(mandant_id, jahr=None):
    with db.verbinden() as con:
        if jahr:
            r = con.execute('SELECT * FROM periode WHERE mandant_id=? '
                            'AND jahr_monat LIKE ? ORDER BY jahr_monat DESC',
                            (mandant_id, f'{jahr}-%')).fetchall()
        else:
            r = con.execute('SELECT * FROM periode WHERE mandant_id=? '
                            'ORDER BY jahr_monat DESC', (mandant_id,)).fetchall()
        return [dict(x) for x in r]


def status_setzen(periode_id, neu, von=None):
    if neu not in STATUS_TEXT:
        raise Verweigert('Unbekannter Status.')
    alt = periode_nach_id(periode_id)
    if not alt:
        raise Verweigert('Diese Periode gibt es nicht.')
    with db.verbinden() as con:
        con.execute('UPDATE periode SET status=? WHERE id=?', (neu, periode_id))
    db.protokollieren('periode_status', benutzer_id=von,
                      detail=f'periode {periode_id}', vorher=alt['status'], nachher=neu)


def notiz_setzen(periode_id, text, von=None):
    with db.verbinden() as con:
        con.execute('UPDATE periode SET notiz=? WHERE id=?', (text or None, periode_id))
    db.protokollieren('periode_notiz', benutzer_id=von, detail=f'periode {periode_id}')


# ---------------------------------------------------------------- Checkliste
def checkliste(mandant_id):
    """Die Liste des Mandanten, sonst die Vorlage."""
    with db.verbinden() as con:
        r = con.execute('SELECT * FROM checkliste_slot WHERE mandant_id=? '
                        'ORDER BY reihenfolge, id', (mandant_id,)).fetchall()
        if not r:
            r = con.execute('SELECT * FROM checkliste_slot WHERE mandant_id IS NULL '
                            'ORDER BY reihenfolge, id').fetchall()
        return [dict(x) for x in r]


def checkliste_uebernehmen(mandant_id):
    """Kopiert die Vorlage auf den Mandanten, damit sie dort geaendert werden kann."""
    with db.verbinden() as con:
        if con.execute('SELECT COUNT(*) FROM checkliste_slot WHERE mandant_id=?',
                       (mandant_id,)).fetchone()[0]:
            return
        for s in con.execute('SELECT * FROM checkliste_slot WHERE mandant_id IS NULL '
                             'ORDER BY reihenfolge, id').fetchall():
            con.execute('INSERT INTO checkliste_slot '
                        '(mandant_id, schluessel, bezeichnung, pflicht, reihenfolge) '
                        'VALUES (?,?,?,?,?)',
                        (mandant_id, s['schluessel'], s['bezeichnung'],
                         s['pflicht'], s['reihenfolge']))


def stand(mandant_id, jahr_monat):
    """Was in dieser Periode vorliegt, Slot für Slot."""
    p = periode(mandant_id, jahr_monat)
    slots = checkliste(mandant_id)
    dok, entf = {}, {}
    if p:
        with db.verbinden() as con:
            for d in con.execute('SELECT * FROM dokument WHERE periode_id=? AND aktiv=1 '
                                 'ORDER BY hochgeladen_am', (p['id'],)).fetchall():
                dok.setdefault(d['slot_schluessel'] or '', []).append(dict(d))
            for e in con.execute('SELECT * FROM slot_entfaellt WHERE periode_id=?',
                                 (p['id'],)).fetchall():
                entf[e['slot_schluessel']] = dict(e)
    raus = []
    for s in slots:
        dateien = dok.get(s['schluessel'], [])
        raus.append({**s, 'dateien': dateien, 'entfaellt': entf.get(s['schluessel']),
                     'erledigt': bool(dateien) or s['schluessel'] in entf})
    return {'periode': p, 'slots': raus, 'ohne_slot': dok.get('', [])}


def fehlende_pflichtslots(mandant_id, jahr_monat):
    return [s for s in stand(mandant_id, jahr_monat)['slots']
            if s['pflicht'] and not s['erledigt']]


def ampel(mandant_id, jahr_monat):
    """vollstaendig, unvollstaendig oder fehlt, fuer die Monatsauswahl."""
    p = periode(mandant_id, jahr_monat)
    if not p:
        return 'fehlt'
    if not fehlende_pflichtslots(mandant_id, jahr_monat):
        return 'vollstaendig'
    s = stand(mandant_id, jahr_monat)
    return 'unvollstaendig' if any(x['erledigt'] for x in s['slots']) else 'fehlt'


# ----------------------------------------------------------------- Dokumente
def darf_hochladen(p):
    return bool(p) and (p['status'] in OFFEN_FUER_UPLOAD or p['nachtrag_offen'])


def dokument_ablegen(mandant_id, jahr_monat, slot, dateiname, mime, daten, von):
    sp.pruefen(dateiname, mime, len(daten))
    p = periode(mandant_id, jahr_monat, anlegen=True)
    if not darf_hochladen(p):
        raise Verweigert('Diese Periode ist eingereicht. Über „Nachtrag" können Sie '
                         'weitere Unterlagen nachreichen.')
    pruef = sp.pruefsumme(daten)
    with db.verbinden() as con:
        doppelt = con.execute('SELECT id, dateiname FROM dokument '
                              'WHERE periode_id=? AND hash=? AND aktiv=1',
                              (p['id'], pruef)).fetchone()
        if doppelt:
            raise Verweigert(f'Diese Datei liegt bereits vor, als „{doppelt["dateiname"]}".')
        vorher = None
        if slot:
            vorher = con.execute('SELECT * FROM dokument WHERE periode_id=? '
                                 'AND slot_schluessel=? AND aktiv=1 '
                                 'ORDER BY version DESC LIMIT 1',
                                 (p['id'], slot)).fetchone()
    schluessel = sp.ablegen(daten, mandant_id, jahr_monat, dateiname)
    with db.verbinden() as con:
        version = (vorher['version'] + 1) if vorher else 1
        cur = con.execute(
            'INSERT INTO dokument (periode_id, slot_schluessel, dateiname, mime, '
            'groesse, hash, version, ersetzt_id, speicher_schluessel, '
            'hochgeladen_von, hochgeladen_am, aktiv) VALUES (?,?,?,?,?,?,?,?,?,?,?,1)',
            (p['id'], slot or None, dateiname, mime, len(daten), pruef, version,
             vorher['id'] if vorher else None, schluessel, von, db.jetzt()))
        neu_id = cur.lastrowid
        if vorher:
            # Die alte Fassung bleibt erhalten, sie ist nur nicht mehr die aktuelle.
            con.execute('UPDATE dokument SET aktiv=0 WHERE id=?', (vorher['id'],))
        con.execute('DELETE FROM slot_entfaellt WHERE periode_id=? AND slot_schluessel=?',
                    (p['id'], slot or ''))
        if p['status'] == 'offen':
            con.execute("UPDATE periode SET status='hochgeladen' WHERE id=?", (p['id'],))
    db.protokollieren('dokument_hochgeladen', benutzer_id=von,
                      detail=f'periode {p["id"]}, dokument {neu_id}, {dateiname}',
                      nachher=f'version {version}')
    # Gelesen wird ausserhalb der Anfrage. Faellt das Einreihen um, ist der
    # Upload trotzdem gelungen; nachgeholt wird es vom Arbeiter.
    try:
        import aufgaben
        aufgaben.einreihen(neu_id)
    except Exception as e:                       # noqa: BLE001
        db.protokollieren('aufgabe_nicht_eingereiht', detail=f'dokument {neu_id}',
                          nachher=str(e)[:200])
    return neu_id


def dokument(dokument_id, mandant_id=None):
    with db.verbinden() as con:
        if mandant_id is None:
            r = con.execute('SELECT * FROM dokument WHERE id=?', (dokument_id,)).fetchone()
        else:
            r = con.execute('SELECT d.* FROM dokument d JOIN periode p ON p.id=d.periode_id '
                            'WHERE d.id=? AND p.mandant_id=?',
                            (dokument_id, mandant_id)).fetchone()
        return dict(r) if r else None


def versionen(periode_id, slot):
    with db.verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT * FROM dokument WHERE periode_id=? AND slot_schluessel=? '
            'ORDER BY version DESC', (periode_id, slot)).fetchall()]


def entfaellt_setzen(mandant_id, jahr_monat, slot, grund, von):
    grund = (grund or '').strip()
    if len(grund) < 3:
        raise Verweigert('Bitte schreiben Sie kurz, warum diese Unterlage entfällt.')
    p = periode(mandant_id, jahr_monat, anlegen=True)
    if not darf_hochladen(p):
        raise Verweigert('Diese Periode ist eingereicht.')
    with db.verbinden() as con:
        if con.execute('SELECT COUNT(*) FROM dokument WHERE periode_id=? '
                       'AND slot_schluessel=? AND aktiv=1', (p['id'], slot)).fetchone()[0]:
            raise Verweigert('Für diese Unterlage liegt bereits eine Datei vor.')
        con.execute('INSERT OR REPLACE INTO slot_entfaellt '
                    '(periode_id, slot_schluessel, grund, gesetzt_von, gesetzt_am) '
                    'VALUES (?,?,?,?,?)', (p['id'], slot, grund, von, db.jetzt()))
    db.protokollieren('slot_entfaellt', benutzer_id=von,
                      detail=f'periode {p["id"]}, {slot}', nachher=grund[:200])


def entfaellt_aufheben(mandant_id, jahr_monat, slot, von):
    p = periode(mandant_id, jahr_monat)
    if not p or not darf_hochladen(p):
        raise Verweigert('Diese Periode lässt sich nicht mehr ändern.')
    with db.verbinden() as con:
        con.execute('DELETE FROM slot_entfaellt WHERE periode_id=? AND slot_schluessel=?',
                    (p['id'], slot))
    db.protokollieren('slot_entfaellt_aufgehoben', benutzer_id=von,
                      detail=f'periode {p["id"]}, {slot}')


# ----------------------------------------------------------------- Einreichen
def einreichen(mandant_id, jahr_monat, von):
    p = periode(mandant_id, jahr_monat)
    if not p:
        raise Verweigert('Für diesen Monat liegt noch nichts vor.')
    if not darf_hochladen(p):
        raise Verweigert('Diese Periode ist bereits eingereicht.')
    with db.verbinden() as con:
        anzahl = con.execute('SELECT COUNT(*) FROM dokument WHERE periode_id=? AND aktiv=1',
                             (p['id'],)).fetchone()[0]
    if not anzahl:
        raise Verweigert('Es liegt noch keine Datei vor.')
    with db.verbinden() as con:
        con.execute("UPDATE periode SET status='eingereicht', eingereicht_am=?, "
                    "nachtrag_offen=0 WHERE id=?", (db.jetzt(), p['id']))
    db.protokollieren('periode_eingereicht', benutzer_id=von,
                      detail=f'periode {p["id"]}, {anzahl} Dateien',
                      vorher=p['status'], nachher='eingereicht')
    return anzahl


def nachtrag_oeffnen(mandant_id, jahr_monat, von):
    p = periode(mandant_id, jahr_monat)
    if not p:
        raise Verweigert('Für diesen Monat liegt noch nichts vor.')
    if darf_hochladen(p):
        raise Verweigert('Diese Periode ist noch offen, ein Nachtrag ist nicht nötig.')
    with db.verbinden() as con:
        con.execute('UPDATE periode SET nachtrag_offen=1 WHERE id=?', (p['id'],))
    db.protokollieren('nachtrag_geoeffnet', benutzer_id=von, detail=f'periode {p["id"]}')


# --------------------------------------------------------------------- Admin
def matrix(jahr):
    """Alle Mandanten gegen alle Monate des Jahres."""
    mandanten = db.mandanten()
    raus = []
    for m in mandanten:
        zeile = {'mandant': m, 'monate': []}
        for monat in range(1, 13):
            jm = f'{jahr}-{monat:02d}'
            p = periode(m['id'], jm)
            zeile['monate'].append({
                'jahr_monat': jm,
                'status': p['status'] if p else 'offen',
                'ampel': ampel(m['id'], jm),
                'periode_id': p['id'] if p else None,
                'nachtrag_offen': bool(p['nachtrag_offen']) if p else False,
            })
        raus.append(zeile)
    return raus


def paket(periode_id):
    """Alle aktiven Dateien einer Periode als ZIP im Speicher."""
    p = periode_nach_id(periode_id)
    if not p:
        raise Verweigert('Diese Periode gibt es nicht.')
    with db.verbinden() as con:
        dateien = [dict(r) for r in con.execute(
            'SELECT * FROM dokument WHERE periode_id=? AND aktiv=1 ORDER BY id',
            (periode_id,)).fetchall()]
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, 'w', zipfile.ZIP_DEFLATED) as z:
        vergeben = set()
        for d in dateien:
            name = d['dateiname']
            n = 1
            while name in vergeben:
                stamm, endung = os.path.splitext(d['dateiname'])
                name = f'{stamm} ({n}){endung}'
                n += 1
            vergeben.add(name)
            z.writestr(name, sp.lesen(d['speicher_schluessel']))
    puffer.seek(0)
    return puffer.read(), len(dateien)
