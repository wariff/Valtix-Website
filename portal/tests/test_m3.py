#!/usr/bin/env python3
"""Tests fuer M2 und M3: Leser, Warteschlange, Erinnerungen.

Die Beispieldateien sind anonymisiert und werden im Test erzeugt.
"""
import os
import sys
import tempfile
from datetime import date

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
PORTAL = os.path.dirname(HIER)
sys.path.insert(0, PORTAL)
sys.path.insert(0, os.path.join(HIER, 'beispiele'))

import erzeugen                                            # noqa: E402
import leser                                               # noqa: E402


@pytest.fixture()
def umgebung():
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    for name in ('datenbank', 'speicher', 'perioden', 'benachrichtigung',
                 'aufgaben', 'erinnerungen'):
        sys.modules.pop(name, None)
    import datenbank, perioden, aufgaben, erinnerungen      # noqa: E402
    datenbank.anlegen()
    mid = datenbank.mandant_anlegen('Alpha GmbH')
    perioden.checkliste_uebernehmen(mid)
    yield {'db': datenbank, 'pd': perioden, 'auf': aufgaben, 'er': erinnerungen,
           'mid': mid}


# --------------------------------------------------------------------- Leser
def test_zahlen_in_deutscher_schreibweise():
    for text, soll in [('1.234,56', 1234.56), ('-1.234,56', -1234.56),
                       ('(89,10)', -89.1), ('12,5 €', 12.5), ('1.200', 1200.0),
                       ('1.234.567', 1234567.0), ('0,00', 0.0)]:
        assert leser._zahl(text) == soll, text


def test_punkt_ohne_komma_ist_kein_tausender():
    # 1234.56 darf nicht zu 123456 werden, das waere ein Faktor hundert.
    assert leser._zahl('1234.56') == 1234.56
    assert leser._zahl('1.2') == 1.2


def test_xlsx_wird_gelesen():
    e = leser.lesen('bwa.xlsx', erzeugen.bwa_xlsx())
    assert e['weg'] == 'xlsx'
    zeilen = e['tabellen'][0]['zeilen']
    assert zeilen[0][0] == 'Position'
    assert any('Umsatzerlöse' in z[0] for z in zeilen)


def test_csv_erkennt_semikolon_und_cp1252():
    e = leser.lesen('susa.csv', erzeugen.susa_csv())
    assert e['weg'] == 'csv'
    assert 'Trennzeichen „;"' in e['hinweis']
    assert any('Umsatzerlöse' in z[1] for z in e['tabellen'][0]['zeilen'])


def test_datev_wird_als_datev_erkannt():
    e = leser.lesen('EXTF_Buchungsstapel.txt', erzeugen.datev_txt())
    assert e['weg'] == 'datev'
    assert 'Buchungsstapel' in e['hinweis']
    assert 'Berater 1000' in e['hinweis']
    assert len(e['tabellen'][0]['zeilen']) == 3      # Spaltennamen und zwei Buchungen


def test_pdf_mit_textebene_braucht_kein_ocr():
    e = leser.lesen('bwa-digital.pdf', erzeugen.bwa_pdf_mit_text())
    assert e['weg'] == 'pdf_text'
    assert e.get('status', 'roh') == 'roh'
    assert 'Umsatzerloese' in e['rohtext']


def test_scan_wird_als_ocr_noetig_gemeldet():
    e = leser.lesen('scan.pdf', erzeugen.scan_pdf_ohne_text())
    assert e['status'] == 'ocr_noetig'
    assert e['konfidenz'] == 0.0


def test_bild_meldet_ocr_und_zip_wird_verworfen():
    assert leser.lesen('foto.jpg', b'\xff\xd8\xff')['status'] == 'ocr_noetig'
    assert leser.lesen('alles.zip', b'PK')['status'] == 'verworfen'


def test_unbekannte_endung_wirft():
    with pytest.raises(leser.NichtLesbar):
        leser.lesen('daten.xyz', b'irgendwas')


# ------------------------------------------------------------ Warteschlange
def test_upload_reiht_ein_und_arbeiter_liest(umgebung):
    pd, auf, mid = umgebung['pd'], umgebung['auf'], umgebung['mid']
    did = pd.dokument_ablegen(mid, '2026-07', 'bwa', 'bwa.xlsx',
                              'application/vnd.openxmlformats-officedocument.'
                              'spreadsheetml.sheet', erzeugen.bwa_xlsx(), None)
    gut, schlecht = auf.abarbeiten()
    assert (gut, schlecht) == (1, 0)
    e = auf.extraktion(did)
    assert e['weg'] == 'xlsx' and e['status'] == 'roh'
    assert e['tabellen'][0]['zeilen'][0][0] == 'Position'


def test_scan_landet_als_ocr_noetig_in_der_extraktion(umgebung):
    pd, auf, mid = umgebung['pd'], umgebung['auf'], umgebung['mid']
    did = pd.dokument_ablegen(mid, '2026-07', 'bwa', 'scan.pdf', 'application/pdf',
                              erzeugen.scan_pdf_ohne_text(), None)
    auf.abarbeiten()
    assert auf.extraktion(did)['status'] == 'ocr_noetig'


def test_kaputte_datei_wird_wiederholt_und_dann_fehler(umgebung):
    pd, auf, mid, db = umgebung['pd'], umgebung['auf'], umgebung['mid'], umgebung['db']
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'kaputt.xlsx',
                        'application/vnd.openxmlformats-officedocument.'
                        'spreadsheetml.sheet', b'keine gueltige Arbeitsmappe', None)
    for _ in range(auf.HOECHSTENS_VERSUCHE):
        auf.abarbeiten()
    with db.verbinden() as con:
        a = con.execute('SELECT * FROM aufgabe ORDER BY id DESC LIMIT 1').fetchone()
    assert a['status'] == 'fehler'
    assert a['versuche'] == auf.HOECHSTENS_VERSUCHE
    assert a['fehler']


def test_einreihen_ist_idempotent(umgebung):
    pd, auf, mid = umgebung['pd'], umgebung['auf'], umgebung['mid']
    did = pd.dokument_ablegen(mid, '2026-07', 'bwa', 'susa.csv', 'text/csv',
                              erzeugen.susa_csv(), None)
    a = auf.einreihen(did)
    b = auf.einreihen(did)
    assert a == b


def test_stand_zeigt_jede_aktive_datei(umgebung):
    pd, auf, mid = umgebung['pd'], umgebung['auf'], umgebung['mid']
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'bwa.xlsx',
                        'application/vnd.openxmlformats-officedocument.'
                        'spreadsheetml.sheet', erzeugen.bwa_xlsx(), None)
    pd.dokument_ablegen(mid, '2026-07', 'susa', 'susa.csv', 'text/csv',
                        erzeugen.susa_csv(), None)
    auf.abarbeiten()
    p = pd.periode(mid, '2026-07')
    zeilen = auf.stand(p['id'])
    assert len(zeilen) == 2
    assert all(z['aufgabe'] == 'fertig' for z in zeilen)


# -------------------------------------------------------------- Erinnerungen
def test_erinnerung_erst_ab_stichtag_und_nur_einmal(umgebung):
    pd, er, mid, db = umgebung['pd'], umgebung['er'], umgebung['mid'], umgebung['db']
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'bwa.xlsx',
                        'application/vnd.openxmlformats-officedocument.'
                        'spreadsheetml.sheet', erzeugen.bwa_xlsx(), None)
    assert er.faellig(date(2026, 8, 5)) == []
    assert len(er.faellig(date(2026, 8, 12))) == 1
    assert er.versenden(date(2026, 8, 12)) == 1
    assert er.versenden(date(2026, 8, 12)) == 0


def test_eingereichte_periode_erinnert_nicht(umgebung):
    pd, er, mid = umgebung['pd'], umgebung['er'], umgebung['mid']
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'bwa.xlsx',
                        'application/vnd.openxmlformats-officedocument.'
                        'spreadsheetml.sheet', erzeugen.bwa_xlsx(), None)
    pd.einreichen(mid, '2026-07', None)
    assert er.faellig(date(2026, 8, 12)) == []


def test_eigener_stichtag_schlaegt_den_globalen(umgebung):
    pd, er, mid, db = umgebung['pd'], umgebung['er'], umgebung['mid'], umgebung['db']
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'bwa.xlsx',
                        'application/vnd.openxmlformats-officedocument.'
                        'spreadsheetml.sheet', erzeugen.bwa_xlsx(), None)
    with db.verbinden() as con:
        con.execute('UPDATE mandant SET erinnerung_tag=20 WHERE id=?', (mid,))
    assert er.faellig(date(2026, 8, 12)) == []
    assert len(er.faellig(date(2026, 8, 21))) == 1
