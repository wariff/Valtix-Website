#!/usr/bin/env python3
"""Tests fuer Anmerkungen zu einzelnen Dateien.

Geprueft wird vor allem, wer was sehen und schreiben darf. Eine Anmerkung
haengt an einer Datei, und eine Datei gehoert genau einem Mandanten.
"""
import os
import sys
import tempfile

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
PORTAL = os.path.dirname(HIER)
sys.path.insert(0, PORTAL)
sys.path.insert(0, os.path.join(HIER, 'beispiele'))

import erzeugen                                            # noqa: E402


@pytest.fixture()
def umgebung():
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    for name in ('datenbank', 'speicher', 'perioden', 'benachrichtigung',
                 'aufgaben', 'kommentare'):
        sys.modules.pop(name, None)
    import datenbank, perioden, kommentare, benachrichtigung  # noqa: E402
    datenbank.anlegen()
    eins = datenbank.mandant_anlegen('Alpha GmbH')
    zwei = datenbank.mandant_anlegen('Beta GmbH')
    perioden.checkliste_uebernehmen(eins)
    perioden.checkliste_uebernehmen(zwei)
    def konto(email, name, rolle, mandant_id=None):
        datenbank.benutzer_anlegen(email, name, rolle, mandant_id)
        return next(b for b in datenbank.benutzer_liste() if b['email'] == email)

    admin = konto('a@test.invalid', 'Adele Admin', 'admin')
    kunde = konto('m@test.invalid', 'Mika Mandant', 'mandant', eins)
    fremd = konto('f@test.invalid', 'Finn Fremd', 'mandant', zwei)
    did = perioden.dokument_ablegen(eins, '2026-06', 'bwa', 'bwa.xlsx',
                                    'application/vnd.openxmlformats-officedocument.'
                                    'spreadsheetml.sheet', erzeugen.bwa_xlsx(),
                                    kunde['id'])
    yield {'db': datenbank, 'pd': perioden, 'km': kommentare, 'bn': benachrichtigung,
           'eins': eins, 'zwei': zwei,
           'admin': admin, 'kunde': kunde, 'fremd': fremd, 'dok': did}


def test_mandant_schreibt_und_sieht_die_eigene_anmerkung(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Die Januarrechnung fehlt noch.', u['kunde'])
    liste = u['km'].liste(u['dok'])
    assert len(liste) == 1
    assert liste[0]['text'] == 'Die Januarrechnung fehlt noch.'
    assert liste[0]['rolle'] == 'mandant'
    assert liste[0]['verfasser'] == 'Mika Mandant'


def test_beide_seiten_schreiben_in_denselben_verlauf(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Hier fehlt eine Position.', u['kunde'])
    u['km'].schreiben(u['dok'], 'Danke, wir fragen beim Lieferanten nach.', u['admin'])
    liste = u['km'].liste(u['dok'])
    assert [k['rolle'] for k in liste] == ['mandant', 'admin']


def test_fremder_mandant_kommt_nicht_an_die_datei(umgebung):
    u = umgebung
    with pytest.raises(u['pd'].Verweigert):
        u['km'].schreiben(u['dok'], 'Neugierig.', u['fremd'])
    assert u['km'].liste(u['dok']) == []


def test_fremder_mandant_sieht_den_verlauf_nicht(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Intern.', u['kunde'])
    assert u['km'].liste(u['dok'], u['zwei']) == []
    assert len(u['km'].liste(u['dok'], u['eins'])) == 1


def test_leere_anmerkung_wird_abgelehnt(umgebung):
    u = umgebung
    for leer in ('', '   ', '\n\t '):
        with pytest.raises(u['pd'].Verweigert):
            u['km'].schreiben(u['dok'], leer, u['kunde'])


def test_zu_lange_anmerkung_wird_abgelehnt(umgebung):
    u = umgebung
    with pytest.raises(u['pd'].Verweigert):
        u['km'].schreiben(u['dok'], 'x' * (u['km'].LAENGSTE + 1), u['kunde'])


def test_zeilenumbrueche_werden_zu_leerzeichen(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Erste Zeile\n\nzweite   Zeile', u['kunde'])
    assert u['km'].liste(u['dok'])[0]['text'] == 'Erste Zeile zweite Zeile'


def test_anmerkung_des_mandanten_meldet_sich_beim_admin(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Bitte prüfen.', u['kunde'])
    offen = u['bn'].offene(u['admin'])
    assert any('Bitte prüfen.' in m['text'] for m in offen)


def test_anmerkung_von_uns_meldet_sich_beim_mandanten(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Welcher Zeitraum ist das?', u['admin'])
    offen = u['bn'].offene(u['kunde'])
    assert any('Welcher Zeitraum' in m['text'] for m in offen)
    # Der fremde Mandant bekommt davon nichts mit.
    assert not u['bn'].offene(u['fremd'])


def test_je_dokument_gruppiert_nach_datei(umgebung):
    u = umgebung
    zweite = u['pd'].dokument_ablegen(
        u['eins'], '2026-06', 'susa', 'susa.csv', 'text/csv',
        erzeugen.susa_csv(), u['kunde']['id'])
    u['km'].schreiben(u['dok'], 'Zur BWA.', u['kunde'])
    u['km'].schreiben(zweite, 'Zur Saldenliste.', u['kunde'])
    p = u['pd'].periode(u['eins'], '2026-06')
    nach_datei = u['km'].je_dokument(p['id'])
    assert set(nach_datei) == {u['dok'], zweite}
    assert nach_datei[zweite][0]['text'] == 'Zur Saldenliste.'
    assert u['km'].anzahl(p['id']) == 2


def test_anmerkung_steht_im_protokoll(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Nachvollziehbar.', u['kunde'])
    ereignisse = [e['ereignis'] for e in u['db'].protokoll(50)]
    assert 'kommentar_geschrieben' in ereignisse


def test_verlauf_ueberlebt_eine_neue_fassung(umgebung):
    u = umgebung
    u['km'].schreiben(u['dok'], 'Gilt für Fassung eins.', u['kunde'])
    neu = u['pd'].dokument_ablegen(
        u['eins'], '2026-06', 'bwa', 'bwa-korrigiert.pdf', 'application/pdf',
        erzeugen.bwa_pdf_mit_text(), u['kunde']['id'])
    assert neu != u['dok']
    # Die alte Fassung ist nicht mehr aktiv, ihre Anmerkung bleibt aber lesbar.
    assert len(u['km'].liste(u['dok'])) == 1
    p = u['pd'].periode(u['eins'], '2026-06')
    assert u['dok'] in u['km'].je_dokument(p['id'])


# ---------------------------------------------------------------- Ueber HTTP
@pytest.fixture()
def web():
    """Dieselbe Lage, aber ueber die Anwendung statt ueber die Module."""
    import importlib
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    os.environ['VALTIX_SECRET'] = 'test-nur-fuer-tests'
    os.environ['VALTIX_HTTPS'] = '0'
    for name in ('datenbank', 'speicher', 'perioden', 'benachrichtigung',
                 'aufgaben', 'kommentare', 'uebernahme', 'app'):
        sys.modules.pop(name, None)
    import datenbank, perioden, kommentare, app              # noqa: E402
    importlib.reload(datenbank)
    datenbank.anlegen()
    eins = datenbank.mandant_anlegen('Alpha GmbH')
    zwei = datenbank.mandant_anlegen('Beta GmbH')
    perioden.checkliste_uebernehmen(eins)
    perioden.checkliste_uebernehmen(zwei)

    def konto(email, name, rolle, mandant_id=None):
        token = datenbank.benutzer_anlegen(email, name, rolle, mandant_id)
        datenbank.passwort_setzen(token, 'einlangespasswort')
        return next(b for b in datenbank.benutzer_liste() if b['email'] == email)

    kunde = konto('m@test.invalid', 'Mika Mandant', 'mandant', eins)
    fremd = konto('f@test.invalid', 'Finn Fremd', 'mandant', zwei)
    konto('a@test.invalid', 'Adele Admin', 'admin')
    did = perioden.dokument_ablegen(eins, '2026-06', 'bwa', 'bwa.xlsx',
                                    'application/vnd.openxmlformats-officedocument.'
                                    'spreadsheetml.sheet', erzeugen.bwa_xlsx(),
                                    kunde['id'])
    yield {'db': datenbank, 'pd': perioden, 'km': kommentare, 'app': app,
           'eins': eins, 'zwei': zwei, 'kunde': kunde, 'fremd': fremd, 'dok': did}


def _anmelden(app, email):
    from fastapi.testclient import TestClient
    c = TestClient(app.app)
    c.post('/anmelden', data={'email': email, 'passwort': 'einlangespasswort'},
           follow_redirects=False)
    return c


def _marke(text):
    import re
    treffer = re.search(r'name="csrf" value="([^"]+)"', text)
    return treffer.group(1) if treffer else ''


def test_web_mandant_schreibt_admin_liest(web):
    u = web
    c = _anmelden(u['app'], 'm@test.invalid')
    seite = c.get('/unterlagen/2026-06').text
    assert 'Anmerkung zu dieser Datei' in seite
    c.post('/kommentar', data={'dokument': u['dok'], 'text': 'Beleg folgt morgen.',
                               'zurueck': '/unterlagen/2026-06',
                               'csrf': _marke(seite)}, follow_redirects=False)
    assert 'Beleg folgt morgen.' in c.get('/unterlagen/2026-06').text

    p = u['pd'].periode(u['eins'], '2026-06')
    a = _anmelden(u['app'], 'a@test.invalid')
    assert 'Beleg folgt morgen.' in a.get(f'/uebersicht/{p["id"]}').text


def test_web_ohne_marke_wird_nichts_geschrieben(web):
    u = web
    c = _anmelden(u['app'], 'm@test.invalid')
    r = c.post('/kommentar', data={'dokument': u['dok'], 'text': 'Ohne Marke.',
                                   'zurueck': '/unterlagen/2026-06', 'csrf': 'falsch'},
               follow_redirects=False)
    assert r.headers['location'] == '/anmelden'
    assert u['km'].liste(u['dok']) == []


def test_web_fremder_mandant_schreibt_nicht(web):
    u = web
    c = _anmelden(u['app'], 'f@test.invalid')
    marke = _marke(c.get('/unterlagen/2026-06').text)
    c.post('/kommentar', data={'dokument': u['dok'], 'text': 'Fremd.',
                               'zurueck': '/unterlagen/2026-06', 'csrf': marke},
           follow_redirects=False)
    assert u['km'].liste(u['dok']) == []


def test_web_rueckziel_bleibt_auf_der_eigenen_seite(web):
    u = web
    c = _anmelden(u['app'], 'm@test.invalid')
    marke = _marke(c.get('/unterlagen/2026-06').text)
    for boese in ('https://fremde.example/', '//fremde.example/', '/verwaltung',
                  '/unterlagen/2026-06/../../etc'):
        r = c.post('/kommentar', data={'dokument': u['dok'], 'text': 'Ziel prüfen.',
                                       'zurueck': boese, 'csrf': marke},
                   follow_redirects=False)
        assert r.headers['location'].startswith('/unterlagen'), boese
        assert 'fremde.example' not in r.headers['location']


def test_web_upload_meldet_sich_beim_admin(web):
    import io as _io
    u = web
    c = _anmelden(u['app'], 'm@test.invalid')
    marke = _marke(c.get('/unterlagen/2026-07').text)
    c.post('/unterlagen/2026-07/hochladen',
           data={'slot': 'susa', 'csrf': marke},
           files={'dateien': ('susa.csv', _io.BytesIO(erzeugen.susa_csv()), 'text/csv')},
           follow_redirects=False)
    import benachrichtigung as bn
    admin = next(b for b in u['db'].benutzer_liste() if b['rolle'] == 'admin')
    texte = [m['text'] for m in bn.offene(admin)]
    assert any('hochgeladen' in t and 'susa.csv' in t for t in texte), texte
