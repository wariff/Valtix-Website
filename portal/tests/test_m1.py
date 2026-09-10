#!/usr/bin/env python3
"""Tests fuer M1: Upload, Mandantentrennung, Statuswechsel.

Jeder Lauf bekommt eine eigene Datenbank und eine eigene Ablage, damit nichts
aus einem frueheren Lauf durchschlaegt.

    python3 -m pytest portal/tests -q
"""
import importlib
import os
import sys
import tempfile

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
PORTAL = os.path.dirname(HIER)
sys.path.insert(0, PORTAL)


@pytest.fixture()
def umgebung():
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    os.environ['VALTIX_SECRET'] = 'test-nur-fuer-tests'
    os.environ['VALTIX_HTTPS'] = '0'
    for name in ('datenbank', 'speicher', 'perioden', 'benachrichtigung', 'app'):
        if name in sys.modules:
            del sys.modules[name]
    import datenbank, perioden, speicher, app                      # noqa: E402
    importlib.reload(datenbank)
    datenbank.anlegen()
    yield {'db': datenbank, 'pd': perioden, 'sp': speicher, 'app': app}


def _mandant(db, pd, name):
    mid = db.mandant_anlegen(name)
    pd.checkliste_uebernehmen(mid)
    return mid


PDF = b'%PDF-1.4\nnur ein Test\n'


# ------------------------------------------------------------------- Upload
def test_upload_legt_periode_an_und_setzt_status(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    assert pd.periode(mid, '2026-07') is None
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    p = pd.periode(mid, '2026-07')
    assert p['status'] == 'hochgeladen'
    assert pd.ampel(mid, '2026-07') == 'unvollstaendig'


def test_upload_lehnt_falsche_endung_ab(umgebung):
    db, pd, sp = umgebung['db'], umgebung['pd'], umgebung['sp']
    mid = _mandant(db, pd, 'Alpha GmbH')
    with pytest.raises(sp.Abgelehnt):
        pd.dokument_ablegen(mid, '2026-07', 'bwa', 'schad.exe',
                            'application/x-msdownload', b'MZ', None)


def test_upload_erkennt_doppelte_datei(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    with pytest.raises(pd.Verweigert) as e:
        pd.dokument_ablegen(mid, '2026-07', 'susa', 'Kopie.pdf', 'application/pdf',
                            PDF, None)
    assert 'bereits' in str(e.value)


def test_zweite_datei_im_selben_slot_wird_neue_fassung(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    a = pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf',
                            PDF, None)
    b = pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA korrigiert.pdf',
                            'application/pdf', PDF + b'x', None)
    s = pd.stand(mid, '2026-07')
    bwa = [x for x in s['slots'] if x['schluessel'] == 'bwa'][0]
    assert len(bwa['dateien']) == 1
    assert bwa['dateien'][0]['id'] == b
    assert bwa['dateien'][0]['version'] == 2
    alte = pd.dokument(a)
    assert alte['aktiv'] == 0            # bleibt erhalten, ist nur nicht mehr aktuell


def test_entfaellt_braucht_grund_und_zaehlt_als_erledigt(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    with pytest.raises(pd.Verweigert):
        pd.entfaellt_setzen(mid, '2026-07', 'lohnjournal', 'x', None)
    pd.entfaellt_setzen(mid, '2026-07', 'susa', 'Kein Steuerberater beauftragt', None)
    offen = [s['schluessel'] for s in pd.fehlende_pflichtslots(mid, '2026-07')]
    assert 'susa' not in offen


# --------------------------------------------------------- Mandantentrennung
def test_fremde_periode_ist_nicht_lesbar(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    a = _mandant(db, pd, 'Alpha GmbH')
    b = _mandant(db, pd, 'Beta GmbH')
    pd.dokument_ablegen(a, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    p = pd.periode(a, '2026-07')
    assert pd.periode_nach_id(p['id'], mandant_id=b) is None
    assert pd.periode_nach_id(p['id'], mandant_id=a) is not None


def test_fremdes_dokument_ist_nicht_lesbar(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    a = _mandant(db, pd, 'Alpha GmbH')
    b = _mandant(db, pd, 'Beta GmbH')
    did = pd.dokument_ablegen(a, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf',
                              PDF, None)
    assert pd.dokument(did, mandant_id=b) is None
    assert pd.dokument(did, mandant_id=a) is not None


def test_ablage_laesst_keinen_ausbruch_zu(umgebung):
    sp = umgebung['sp']
    with pytest.raises(sp.Abgelehnt):
        sp._pfad('../../../etc/passwd')


# ------------------------------------------------------------ Statuswechsel
def test_einreichen_sperrt_und_nachtrag_oeffnet_wieder(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    with pytest.raises(pd.Verweigert):
        pd.einreichen(mid, '2026-07', None)          # noch keine Datei
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    anzahl = pd.einreichen(mid, '2026-07', None)
    assert anzahl == 1
    p = pd.periode(mid, '2026-07')
    assert p['status'] == 'eingereicht' and p['eingereicht_am']

    with pytest.raises(pd.Verweigert):               # gesperrt
        pd.dokument_ablegen(mid, '2026-07', 'susa', 'SuSa.pdf', 'application/pdf',
                            PDF + b'y', None)
    pd.nachtrag_oeffnen(mid, '2026-07', None)
    pd.dokument_ablegen(mid, '2026-07', 'susa', 'SuSa.pdf', 'application/pdf',
                        PDF + b'y', None)
    assert pd.periode(mid, '2026-07')['status'] == 'eingereicht'   # Status bleibt


def test_status_wird_protokolliert(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    p = pd.periode(mid, '2026-07')
    pd.status_setzen(p['id'], 'in_pruefung', None)
    eintrag = [e for e in db.protokoll() if e['ereignis'] == 'periode_status'][0]
    assert eintrag['vorher'] == 'hochgeladen' and eintrag['nachher'] == 'in_pruefung'


def test_unbekannter_status_wird_abgelehnt(umgebung):
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    p = pd.periode(mid, '2026-07')
    with pytest.raises(pd.Verweigert):
        pd.status_setzen(p['id'], 'erledigt', None)


def test_paket_enthaelt_alle_aktiven_dateien(umgebung):
    import io, zipfile
    db, pd = umgebung['db'], umgebung['pd']
    mid = _mandant(db, pd, 'Alpha GmbH')
    pd.dokument_ablegen(mid, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf', PDF, None)
    pd.dokument_ablegen(mid, '2026-07', 'susa', 'SuSa.pdf', 'application/pdf',
                        PDF + b'y', None)
    p = pd.periode(mid, '2026-07')
    daten, anzahl = pd.paket(p['id'])
    assert anzahl == 2
    with zipfile.ZipFile(io.BytesIO(daten)) as z:
        assert sorted(z.namelist()) == ['BWA.pdf', 'SuSa.pdf']


# -------------------------------------------------------- Zugriff ueber HTTP
def _anmelden(client, db, email, passwort):
    token = db.benutzer_anlegen(email, 'Test', 'mandant', None)
    return token


def test_http_ohne_anmeldung_leitet_um(umgebung):
    from fastapi.testclient import TestClient
    c = TestClient(umgebung['app'].app)
    for pfad in ('/unterlagen', '/unterlagen/2026-07', '/uebersicht', '/datei/1'):
        r = c.get(pfad, follow_redirects=False)
        assert r.status_code == 303 and r.headers['location'] == '/anmelden', pfad


def test_http_mandant_sieht_fremde_datei_nicht(umgebung):
    from fastapi.testclient import TestClient
    db, pd, app = umgebung['db'], umgebung['pd'], umgebung['app']
    a = _mandant(db, pd, 'Alpha GmbH')
    b = _mandant(db, pd, 'Beta GmbH')
    did = pd.dokument_ablegen(a, '2026-07', 'bwa', 'BWA.pdf', 'application/pdf',
                              PDF, None)
    token = db.benutzer_anlegen('beta@vorschau.valtix', 'Beta', 'mandant', b)
    db.passwort_setzen(token, 'einlangespasswort')
    c = TestClient(app.app)
    c.post('/anmelden', data={'email': 'beta@vorschau.valtix',
                              'passwort': 'einlangespasswort'}, follow_redirects=False)
    r = c.get(f'/datei/{did}')
    assert r.status_code == 200
    assert 'Nicht gefunden' in r.text
    assert 'BWA' not in r.text
