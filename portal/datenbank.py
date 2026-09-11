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

-- ---------------------------------------------------------------- M1
-- Eine Periode ist ein Mandant und ein Monat. Rueckwirkende Monate sind
-- ausdruecklich erlaubt, deshalb kein Zwang zur Reihenfolge.
CREATE TABLE IF NOT EXISTS periode (
  id             INTEGER PRIMARY KEY,
  mandant_id     INTEGER NOT NULL REFERENCES mandant(id),
  jahr_monat     TEXT NOT NULL,                 -- YYYY-MM
  status         TEXT NOT NULL DEFAULT 'offen'
                 CHECK (status IN ('offen','hochgeladen','eingereicht',
                                   'in_pruefung','freigegeben','bericht_gestellt')),
  eingereicht_am TEXT,
  notiz          TEXT,
  angelegt_am    TEXT NOT NULL,
  UNIQUE (mandant_id, jahr_monat)
);
-- Die Checkliste ist je Mandant einstellbar. Ein Eintrag ohne mandant_id ist
-- die Vorlage, die fuer neue Mandanten kopiert wird.
CREATE TABLE IF NOT EXISTS checkliste_slot (
  id          INTEGER PRIMARY KEY,
  mandant_id  INTEGER REFERENCES mandant(id),
  schluessel  TEXT NOT NULL,
  bezeichnung TEXT NOT NULL,
  pflicht     INTEGER NOT NULL DEFAULT 1,
  reihenfolge INTEGER NOT NULL DEFAULT 0,
  UNIQUE (mandant_id, schluessel)
);
CREATE TABLE IF NOT EXISTS dokument (
  id                  INTEGER PRIMARY KEY,
  periode_id          INTEGER NOT NULL REFERENCES periode(id),
  slot_schluessel     TEXT,
  dateiname           TEXT NOT NULL,
  mime                TEXT NOT NULL,
  groesse             INTEGER NOT NULL,
  hash                TEXT NOT NULL,
  version             INTEGER NOT NULL DEFAULT 1,
  ersetzt_id          INTEGER REFERENCES dokument(id),
  speicher_schluessel TEXT NOT NULL,
  hochgeladen_von     INTEGER REFERENCES benutzer(id),
  hochgeladen_am      TEXT NOT NULL,
  aktiv               INTEGER NOT NULL DEFAULT 1
);
-- Ein Slot, den der Mandant begruendet auf "entfaellt" setzt.
CREATE TABLE IF NOT EXISTS slot_entfaellt (
  id              INTEGER PRIMARY KEY,
  periode_id      INTEGER NOT NULL REFERENCES periode(id),
  slot_schluessel TEXT NOT NULL,
  grund           TEXT NOT NULL,
  gesetzt_von     INTEGER REFERENCES benutzer(id),
  gesetzt_am      TEXT NOT NULL,
  UNIQUE (periode_id, slot_schluessel)
);
CREATE TABLE IF NOT EXISTS meldung (
  id          INTEGER PRIMARY KEY,
  benutzer_id INTEGER REFERENCES benutzer(id),
  rolle       TEXT,                              -- an alle dieser Rolle
  text        TEXT NOT NULL,
  ziel        TEXT,
  erstellt_am TEXT NOT NULL,
  gelesen_am  TEXT
);
CREATE INDEX IF NOT EXISTS idx_periode_mandant ON periode(mandant_id, jahr_monat);
CREATE INDEX IF NOT EXISTS idx_dokument_periode ON dokument(periode_id, aktiv);

-- ---------------------------------------------------------------- M2 / M3
-- Einstellungen, die sich zur Laufzeit aendern lassen sollen.
CREATE TABLE IF NOT EXISTS einstellung (
  schluessel TEXT PRIMARY KEY,
  wert       TEXT NOT NULL
);
-- Warteschlange. Verarbeitet wird ausserhalb der Anfrage, mit Wiederholung.
CREATE TABLE IF NOT EXISTS aufgabe (
  id          INTEGER PRIMARY KEY,
  art         TEXT NOT NULL,
  dokument_id INTEGER REFERENCES dokument(id),
  status      TEXT NOT NULL DEFAULT 'wartet'
              CHECK (status IN ('wartet','laeuft','fertig','fehler')),
  versuche    INTEGER NOT NULL DEFAULT 0,
  fehler      TEXT,
  erstellt_am TEXT NOT NULL,
  beendet_am  TEXT
);
-- Ergebnis der Extraktion. Roh, noch nicht gemappt und nie automatisch produktiv.
CREATE TABLE IF NOT EXISTS extraktion (
  id          INTEGER PRIMARY KEY,
  dokument_id INTEGER NOT NULL REFERENCES dokument(id),
  weg         TEXT NOT NULL,        -- xlsx, csv, datev, pdf_text, ocr
  seiten      INTEGER,
  tabellen    TEXT,                 -- JSON
  rohtext     TEXT,
  konfidenz   REAL,
  status      TEXT NOT NULL DEFAULT 'roh'
              CHECK (status IN ('roh','geprueft','verworfen','ocr_noetig')),
  hinweis     TEXT,
  erstellt_am TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_aufgabe_status ON aufgabe(status, id);
CREATE INDEX IF NOT EXISTS idx_extraktion_dokument ON extraktion(dokument_id);
'''


def jetzt():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def verbinden():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


SPALTEN_NACHTRAG = [
    ('protokoll', 'vorher', 'TEXT'),
    ('protokoll', 'nachher', 'TEXT'),
    # Ein Nachtrag oeffnet das Hochladen wieder, ohne dass die Periode ihren
    # Status verliert. Sonst waere nicht mehr zu sehen, dass schon eingereicht war.
    ('periode', 'nachtrag_offen', 'INTEGER NOT NULL DEFAULT 0'),
    # Stichtag fuer die Erinnerung, je Mandant. Leer heisst: globaler Wert.
    ('mandant', 'erinnerung_tag', 'INTEGER'),
]


def _spalten_nachziehen(con):
    """Fehlende Spalten ergaenzen, damit eine bestehende Datei weiterlaeuft."""
    for tabelle, spalte, art in SPALTEN_NACHTRAG:
        vorhanden = [r[1] for r in con.execute(f'PRAGMA table_info({tabelle})')]
        if spalte not in vorhanden:
            con.execute(f'ALTER TABLE {tabelle} ADD COLUMN {spalte} {art}')


def anlegen():
    with verbinden() as con:
        con.executescript(SCHEMA)
        _spalten_nachziehen(con)
        _standardcheckliste(con)


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


# Standardliste nach F4 der Spezifikation. Sie liegt ohne mandant_id in der
# Tabelle und wird beim Anlegen eines Mandanten kopiert, damit sie danach je
# Mandant angepasst werden kann.
STANDARD_SLOTS = [
    ('bwa', 'BWA', 1),
    ('susa', 'Summen- und Saldenliste', 1),
    ('opos_debitoren', 'OPOS Debitoren', 1),
    ('opos_kreditoren', 'OPOS Kreditoren', 1),
    ('kontensalden', 'Kontensaldenliste oder Kontoauszüge', 1),
    ('bestandsliste', 'Bestandsliste', 0),
    ('lohnjournal', 'Lohnjournal', 0),
    ('investitionsliste', 'Investitionsliste', 0),
]


def _standardcheckliste(con):
    vorhanden = con.execute(
        'SELECT COUNT(*) FROM checkliste_slot WHERE mandant_id IS NULL').fetchone()[0]
    if vorhanden:
        return
    for i, (schluessel, bezeichnung, pflicht) in enumerate(STANDARD_SLOTS):
        con.execute('INSERT INTO checkliste_slot '
                    '(mandant_id, schluessel, bezeichnung, pflicht, reihenfolge) '
                    'VALUES (NULL,?,?,?,?)', (schluessel, bezeichnung, pflicht, i))


def einstellung(schluessel, standard=None):
    with verbinden() as con:
        r = con.execute('SELECT wert FROM einstellung WHERE schluessel=?',
                        (schluessel,)).fetchone()
        return r['wert'] if r else standard


def einstellung_setzen(schluessel, wert):
    with verbinden() as con:
        con.execute('INSERT INTO einstellung (schluessel, wert) VALUES (?,?) '
                    'ON CONFLICT(schluessel) DO UPDATE SET wert=excluded.wert',
                    (schluessel, str(wert)))


def protokollieren(ereignis, benutzer_id=None, email=None, detail=None,
                   vorher=None, nachher=None):
    with verbinden() as con:
        con.execute('INSERT INTO protokoll '
                    '(zeitpunkt,benutzer_id,email,ereignis,detail,vorher,nachher) '
                    'VALUES (?,?,?,?,?,?,?)',
                    (jetzt(), benutzer_id, email, ereignis, detail, vorher, nachher))


def protokoll(grenze=60):
    with verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT * FROM protokoll ORDER BY id DESC LIMIT ?', (grenze,))]
