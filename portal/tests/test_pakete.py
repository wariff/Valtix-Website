#!/usr/bin/env python3
"""Tests fuer die Paketstaffelung und den Massnahmenplan.

Der Schwerpunkt liegt auf den Grenzen: welches Paket oeffnet was, und wer
darf an einer Massnahme etwas aendern.
"""
import os
import sys
import tempfile

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
PORTAL = os.path.dirname(HIER)
sys.path.insert(0, PORTAL)


@pytest.fixture()
def u():
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    for name in ('datenbank', 'benachrichtigung', 'pakete', 'massnahmen'):
        sys.modules.pop(name, None)
    import datenbank, pakete, massnahmen, benachrichtigung  # noqa: E402
    datenbank.anlegen()
    klein = datenbank.mandant_anlegen('Klein GmbH')
    gross = datenbank.mandant_anlegen('Gross GmbH', 'betreuung')
    eng = datenbank.mandant_anlegen('Eng GmbH', 'intensiv')

    def konto(email, name, rolle, mandant_id=None):
        datenbank.benutzer_anlegen(email, name, rolle, mandant_id)
        return next(b for b in datenbank.benutzer_liste() if b['email'] == email)

    return {'db': datenbank, 'pk': pakete, 'ma': massnahmen, 'bn': benachrichtigung,
            'klein': klein, 'gross': gross, 'eng': eng,
            'admin': konto('a@test.invalid', 'Adele Admin', 'admin'),
            'kunde_klein': konto('k@test.invalid', 'Kai Klein', 'mandant', klein),
            'kunde_gross': konto('g@test.invalid', 'Gerd Gross', 'mandant', gross)}


# ------------------------------------------------------------------- Pakete
def test_standard_ist_das_kleinste_paket(u):
    assert u['pk'].paket(u['klein']) == 'analyse'
    assert u['pk'].klar(u['klein']) == 'Analyse'


def test_analyse_oeffnet_weder_verlauf_noch_massnahmen(u):
    for was in ('verlauf', 'massnahmen'):
        assert u['pk'].kann(u['klein'], was) is False


def test_betreuung_und_intensiv_oeffnen_beides(u):
    for mid in (u['gross'], u['eng']):
        for was in ('verlauf', 'massnahmen'):
            assert u['pk'].kann(mid, was) is True


def test_unbekanntes_paket_oeffnet_nichts(u):
    # Ein Fehler in den Daten darf nicht versehentlich etwas freigeben.
    with u['db'].verbinden() as con:
        con.execute('UPDATE mandant SET paket=? WHERE id=?', ('gold', u['klein']))
    assert u['pk'].paket(u['klein']) == 'analyse'
    assert u['pk'].kann(u['klein'], 'massnahmen') is False


def test_pflicht_laesst_den_admin_durch_und_haelt_den_mandanten_auf(u):
    assert u['pk'].pflicht(u['admin'], 'massnahmen') is True
    assert u['pk'].pflicht(u['kunde_gross'], 'massnahmen') is True
    with pytest.raises(u['pk'].Verweigert):
        u['pk'].pflicht(u['kunde_klein'], 'massnahmen')


def test_paketwechsel_steht_im_protokoll(u):
    u['pk'].setzen(u['klein'], 'betreuung', u['admin']['id'])
    assert u['pk'].kann(u['klein'], 'massnahmen') is True
    e = [x for x in u['db'].protokoll(50) if x['ereignis'] == 'paket_geaendert']
    assert e and e[0]['vorher'] == 'analyse' and e[0]['nachher'] == 'betreuung'


def test_unbekanntes_paket_laesst_sich_nicht_setzen(u):
    with pytest.raises(ValueError):
        u['pk'].setzen(u['klein'], 'platin', u['admin']['id'])


# --------------------------------------------------------------- Massnahmen
def _eine(u, mandant=None):
    return u['ma'].anlegen(mandant or u['gross'], 'Zahlungsziele verkürzen',
                           'Von 48 auf 30 Tage.', u['admin'], rang=1)


def test_valtix_legt_an_der_mandant_nicht(u):
    mid = _eine(u)
    assert u['ma'].liste(u['gross'])[0]['id'] == mid
    with pytest.raises(u['ma'].Verweigert):
        u['ma'].anlegen(u['gross'], 'Eigene Idee', '', u['kunde_gross'])


def test_leerer_titel_wird_abgelehnt(u):
    for leer in ('', '   ', '\n'):
        with pytest.raises(u['ma'].Verweigert):
            u['ma'].anlegen(u['gross'], leer, '', u['admin'])


def test_beide_seiten_setzen_den_status(u):
    mid = _eine(u)
    assert u['ma'].status_setzen(mid, 'laeuft', u['kunde_gross']) == 'laeuft'
    assert u['ma'].status_setzen(mid, 'erledigt', u['admin']) == 'erledigt'
    assert u['ma'].liste(u['gross'])[0]['erledigt_am']


def test_unbekannter_status_wird_abgelehnt(u):
    mid = _eine(u)
    with pytest.raises(u['ma'].Verweigert):
        u['ma'].status_setzen(mid, 'halbfertig', u['admin'])


def test_mandant_ohne_paket_kommt_nicht_an_die_massnahme(u):
    mid = _eine(u, u['klein'])
    for tun in (lambda: u['ma'].status_setzen(mid, 'laeuft', u['kunde_klein']),
                lambda: u['ma'].notiz(mid, 'Hallo', u['kunde_klein'])):
        with pytest.raises(u['ma'].Verweigert):
            tun()


def test_fremder_mandant_kommt_nicht_heran(u):
    mid = _eine(u)
    with pytest.raises(u['ma'].Verweigert):
        u['ma'].status_setzen(mid, 'erledigt', u['kunde_klein'])


def test_notizen_von_beiden_seiten_in_einem_verlauf(u):
    mid = _eine(u)
    u['ma'].notiz(mid, 'Wir haben mit zwei Kunden gesprochen.', u['kunde_gross'])
    u['ma'].notiz(mid, 'Gut, dann nehmen wir die restlichen im Pitch durch.',
                  u['admin'])
    assert [n['rolle'] for n in u['ma'].notizen(mid)] == ['mandant', 'admin']
    assert u['ma'].liste(u['gross'])[0]['notizen'] == 2


def test_offene_stehen_oben(u):
    erst = _eine(u)
    zweit = u['ma'].anlegen(u['gross'], 'Lager abbauen', '', u['admin'], rang=3)
    u['ma'].status_setzen(erst, 'erledigt', u['admin'])
    assert [m['id'] for m in u['ma'].liste(u['gross'])] == [zweit, erst]


def test_stand_zaehlt_nach_status(u):
    a = _eine(u)
    u['ma'].anlegen(u['gross'], 'Zweite', '', u['admin'])
    u['ma'].status_setzen(a, 'erledigt', u['admin'])
    s = u['ma'].stand(u['gross'])
    assert s['offen'] == 1 and s['erledigt'] == 1


def test_meldungen_gehen_an_die_andere_seite(u):
    mid = _eine(u)
    # Valtix legt an, der Mandant bekommt es mit.
    assert any('Zahlungsziele' in m['text'] for m in u['bn'].offene(u['kunde_gross']))
    u['bn'].gelesen(u['kunde_gross'])
    # Der Mandant schreibt, Valtix bekommt es mit.
    u['ma'].notiz(mid, 'Erledigt bis Freitag.', u['kunde_gross'])
    assert any('Erledigt bis Freitag.' in m['text'] for m in u['bn'].offene(u['admin']))
    # Und der Mandant bekommt seine eigene Notiz nicht als Meldung zurueck.
    assert not any('Erledigt bis Freitag.' in m['text']
                   for m in u['bn'].offene(u['kunde_gross']))


def test_je_massnahme_gruppiert(u):
    a = _eine(u)
    b = u['ma'].anlegen(u['gross'], 'Zweite', '', u['admin'])
    u['ma'].notiz(a, 'Zur ersten.', u['admin'])
    u['ma'].notiz(b, 'Zur zweiten.', u['admin'])
    nach = u['ma'].je_massnahme(u['gross'])
    assert nach[b][0]['text'] == 'Zur zweiten.'


# ---------------------------------------------------------------- Ueber HTTP
@pytest.fixture()
def web():
    import importlib
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    os.environ['VALTIX_SECRET'] = 'test-nur-fuer-tests'
    os.environ['VALTIX_HTTPS'] = '0'
    for name in ('datenbank', 'speicher', 'perioden', 'benachrichtigung', 'aufgaben',
                 'kommentare', 'uebernahme', 'pakete', 'massnahmen', 'app'):
        sys.modules.pop(name, None)
    import datenbank, pakete, massnahmen, app               # noqa: E402
    importlib.reload(datenbank)
    datenbank.anlegen()
    klein = datenbank.mandant_anlegen('Klein GmbH')
    gross = datenbank.mandant_anlegen('Gross GmbH', 'betreuung')

    def konto(email, name, rolle, mandant_id=None):
        token = datenbank.benutzer_anlegen(email, name, rolle, mandant_id)
        datenbank.passwort_setzen(token, 'einlangespasswort')
        return next(b for b in datenbank.benutzer_liste() if b['email'] == email)

    konto('a@test.invalid', 'Adele Admin', 'admin')
    konto('k@test.invalid', 'Kai Klein', 'mandant', klein)
    konto('g@test.invalid', 'Gerd Gross', 'mandant', gross)
    return {'db': datenbank, 'pk': pakete, 'ma': massnahmen, 'app': app,
            'klein': klein, 'gross': gross}


def _an(app, email):
    from fastapi.testclient import TestClient
    c = TestClient(app.app)
    c.post('/anmelden', data={'email': email, 'passwort': 'einlangespasswort'},
           follow_redirects=False)
    return c


def _marke(text):
    import re
    treffer = re.search(r'name="csrf" value="([^"]+)"', text)
    return treffer.group(1) if treffer else ''


def test_web_analyse_sieht_den_punkt_massnahmen_nicht(web):
    c = _an(web['app'], 'k@test.invalid')
    seite = c.get('/').text
    assert 'Unterlagen' in seite
    assert '/massnahmen' not in seite
    assert 'Paket Analyse' in seite


def test_web_betreuung_sieht_ihn(web):
    c = _an(web['app'], 'g@test.invalid')
    assert '/massnahmen' in c.get('/').text


def test_web_analyse_kommt_auch_ueber_die_adresse_nicht_hinein(web):
    c = _an(web['app'], 'k@test.invalid')
    r = c.get('/massnahmen')
    assert r.status_code == 200
    assert 'gehört zu den Paketen' in r.text


def test_web_mandant_kommt_nicht_an_die_adminansicht(web):
    c = _an(web['app'], 'g@test.invalid')
    r = c.get(f'/massnahmen/{web["gross"]}', follow_redirects=False)
    assert r.status_code == 303 and r.headers['location'] == '/anmelden'


def test_web_mandant_legt_keine_massnahme_an(web):
    c = _an(web['app'], 'g@test.invalid')
    # Die eigene Marke des Mandanten ist gueltig, die Rolle reicht trotzdem nicht.
    marke = _marke(c.get('/unterlagen/2026-06').text)
    assert marke
    r = c.post('/massnahme', data={'mandant_id': web['gross'], 'titel': 'Meine',
                                   'csrf': marke}, follow_redirects=False)
    assert r.headers['location'] == '/anmelden'
    assert web['ma'].liste(web['gross']) == []


def test_web_beide_seiten_arbeiten_an_derselben_massnahme(web):
    a = _an(web['app'], 'a@test.invalid')
    marke = _marke(a.get(f'/massnahmen/{web["gross"]}').text)
    a.post('/massnahme', data={'mandant_id': web['gross'],
                               'titel': 'Zahlungsziele verkürzen',
                               'beschreibung': 'Von 48 auf 30 Tage.', 'rang': 1,
                               'csrf': marke}, follow_redirects=False)
    mid = web['ma'].liste(web['gross'])[0]['id']

    c = _an(web['app'], 'g@test.invalid')
    seite = c.get('/massnahmen').text
    assert 'Zahlungsziele verkürzen' in seite
    marke = _marke(seite)
    c.post('/massnahme/status', data={'massnahme': mid, 'status': 'laeuft',
                                      'zurueck': '/massnahmen', 'csrf': marke},
           follow_redirects=False)
    c.post('/massnahme/notiz', data={'massnahme': mid, 'text': 'Zwei Kunden umgestellt.',
                                     'zurueck': '/massnahmen', 'csrf': marke},
           follow_redirects=False)
    assert web['ma'].liste(web['gross'])[0]['status'] == 'laeuft'
    assert 'Zwei Kunden umgestellt.' in a.get(f'/massnahmen/{web["gross"]}').text


def test_web_fremde_massnahme_bleibt_unberuehrt(web):
    a = _an(web['app'], 'a@test.invalid')
    marke = _marke(a.get(f'/massnahmen/{web["gross"]}').text)
    a.post('/massnahme', data={'mandant_id': web['gross'], 'titel': 'Fremd',
                               'csrf': marke}, follow_redirects=False)
    mid = web['ma'].liste(web['gross'])[0]['id']
    c = _an(web['app'], 'k@test.invalid')
    marke = _marke(c.get('/unterlagen/2026-06').text)
    c.post('/massnahme/status', data={'massnahme': mid, 'status': 'erledigt',
                                      'zurueck': '/massnahmen', 'csrf': marke},
           follow_redirects=False)
    assert web['ma'].liste(web['gross'])[0]['status'] == 'offen'


def test_web_admin_setzt_das_paket(web):
    a = _an(web['app'], 'a@test.invalid')
    marke = _marke(a.get('/verwaltung').text)
    a.post('/paket', data={'mandant_id': web['klein'], 'paket': 'intensiv',
                           'csrf': marke}, follow_redirects=False)
    assert web['pk'].paket(web['klein']) == 'intensiv'
    c = _an(web['app'], 'k@test.invalid')
    assert '/massnahmen' in c.get('/').text


def test_web_erfundenes_paket_wird_nicht_gesetzt(web):
    a = _an(web['app'], 'a@test.invalid')
    marke = _marke(a.get('/verwaltung').text)
    a.post('/paket', data={'mandant_id': web['klein'], 'paket': 'platin',
                           'csrf': marke}, follow_redirects=False)
    assert web['pk'].paket(web['klein']) == 'analyse'
