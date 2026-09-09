#!/usr/bin/env python3
"""Datenhaltung des Mandantenportals.

SQLite genuegt fuer den Anfang und laesst sich spaeter ohne Aenderung am
uebrigen Code gegen PostgreSQL tauschen. Passwoerter werden mit Argon2id
gehasht, niemals im Klartext gespeichert und auch von Valtix nicht eingesehen.
"""
import os, secrets, sqlite3
from datetime import datetime, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

HIER = os.path.dirname(os.path.abspath(__file__))
DB   = os.environ.get('VALTIX_DB', os.path.join(HIER, 'portal.sqlite3'))
ph   = PasswordHasher()

SCHEMA = '''
CREATE TABLE IF NOT EXISTS mandant (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE,
  angelegt_am TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS benutzer (
  id            INTEGER PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  rolle         TEXT NOT NULL CHECK (rolle IN ('admin','mandant')),
  mandant_id    INTEGER REFERENCES mandant(id),
  passwort_hash TEXT,
  einladung     TEXT,
  aktiv         INTEGER NOT NULL DEFAULT 1,
  angelegt_am   TEXT NOT NULL,
  letzter_login TEXT
);
CREATE TABLE IF NOT EXISTS bericht (
  id          INTEGER PRIMARY KEY,
  mandant_id  INTEGER NOT NULL REFERENCES mandant(id),
  zeitraum    TEXT NOT NULL,
  dateiname   TEXT NOT NULL,
  html        TEXT NOT NULL,
  erstellt_am TEXT NOT NULL,
  erstellt_von INTEGER REFERENCES benutzer(id)
);
CREATE TABLE IF NOT EXISTS protokoll (
  id          INTEGER PRIMARY KEY,
  zeitpunkt   TEXT NOT NULL,
  benutzer_id INTEGER,
  email       TEXT,
  ereignis    TEXT NOT NULL,
  detail      TEXT
);
CREATE INDEX IF NOT EXISTS idx_bericht_mandant ON bericht(mandant_id);
'''


def jetzt():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def verbinden():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


def anlegen():
    with verbinden() as con:
        con.executescript(SCHEMA)


# ---------- Benutzer ----------
def benutzer_anlegen(email, name, rolle, mandant_id=None):
    """Legt ein Konto ohne Passwort an und gibt ein Einladungstoken zurueck.
    Das Passwort setzt die Person selbst; niemand sonst kennt es."""
    token = secrets.token_urlsafe(32)
    with verbinden() as con:
        con.execute(
            'INSERT INTO benutzer (email,name,rolle,mandant_id,einladung,angelegt_am) '
            'VALUES (?,?,?,?,?,?)',
            (email.lower().strip(), name, rolle, mandant_id, token, jetzt()))
    return token


def passwort_setzen(token, passwort):
    if len(passwort) < 12:
        raise ValueError('Das Passwort muss mindestens zwölf Zeichen haben.')
    with verbinden() as con:
        r = con.execute('SELECT id FROM benutzer WHERE einladung=? AND aktiv=1',
                        (token,)).fetchone()
        if not r:
            return None
        con.execute('UPDATE benutzer SET passwort_hash=?, einladung=NULL WHERE id=?',
                    (ph.hash(passwort), r['id']))
        return r['id']


def pruefen(email, passwort):
    with verbinden() as con:
        r = con.execute('SELECT * FROM benutzer WHERE email=? AND aktiv=1',
                        (email.lower().strip(),)).fetchone()
    if not r or not r['passwort_hash']:
        ph.hash('platzhalter')          # gleiche Laufzeit, egal ob Konto existiert
        return None
    try:
        ph.verify(r['passwort_hash'], passwort)
    except (VerifyMismatchError, InvalidHashError):
        return None
    with verbinden() as con:
        con.execute('UPDATE benutzer SET letzter_login=? WHERE id=?', (jetzt(), r['id']))
    return dict(r)


def benutzer(bid):
    with verbinden() as con:
        r = con.execute('SELECT * FROM benutzer WHERE id=? AND aktiv=1', (bid,)).fetchone()
    return dict(r) if r else None


def benutzer_liste():
    with verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT b.*, m.name AS mandant_name FROM benutzer b '
            'LEFT JOIN mandant m ON m.id=b.mandant_id ORDER BY b.rolle, b.name')]


def benutzer_sperren(bid, aktiv):
    with verbinden() as con:
        con.execute('UPDATE benutzer SET aktiv=? WHERE id=?', (1 if aktiv else 0, bid))


# ---------- Mandanten und Berichte ----------
def mandant_anlegen(name):
    with verbinden() as con:
        cur = con.execute('INSERT INTO mandant (name,angelegt_am) VALUES (?,?)',
                          (name.strip(), jetzt()))
        return cur.lastrowid


def mandanten():
    with verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT m.*, (SELECT COUNT(*) FROM bericht b WHERE b.mandant_id=m.id) AS anzahl '
            'FROM mandant m ORDER BY m.name')]


def bericht_speichern(mandant_id, zeitraum, dateiname, html, von):
    with verbinden() as con:
        cur = con.execute(
            'INSERT INTO bericht (mandant_id,zeitraum,dateiname,html,erstellt_am,erstellt_von) '
            'VALUES (?,?,?,?,?,?)', (mandant_id, zeitraum, dateiname, html, jetzt(), von))
        return cur.lastrowid


def berichte(mandant_id=None):
    sql = ('SELECT b.id,b.mandant_id,b.zeitraum,b.dateiname,b.erstellt_am,m.name AS mandant_name '
           'FROM bericht b JOIN mandant m ON m.id=b.mandant_id')
    args = ()
    if mandant_id is not None:
        sql += ' WHERE b.mandant_id=?'
        args = (mandant_id,)
    sql += ' ORDER BY b.erstellt_am DESC'
    with verbinden() as con:
        return [dict(r) for r in con.execute(sql, args)]


def bericht(bid):
    with verbinden() as con:
        r = con.execute('SELECT * FROM bericht WHERE id=?', (bid,)).fetchone()
    return dict(r) if r else None


def protokollieren(ereignis, benutzer_id=None, email=None, detail=None):
    with verbinden() as con:
        con.execute('INSERT INTO protokoll (zeitpunkt,benutzer_id,email,ereignis,detail) '
                    'VALUES (?,?,?,?,?)', (jetzt(), benutzer_id, email, ereignis, detail))


def protokoll(grenze=60):
    with verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT * FROM protokoll ORDER BY id DESC LIMIT ?', (grenze,))]
