#!/usr/bin/env python3
"""Tests fuer die Erkennung gescannter Belege.

Die Anfrage an das Modell wird hier nicht gestellt. Geprueft wird alles,
was drumherum haengt: dass ohne Zugang nichts passiert, dass die Anfrage
richtig gebaut wird, dass eine Ablehnung als solche ankommt und dass aus
dem Gelesenen eine Extraktion wird, die die Uebernahme versteht.
"""
import base64
import json
import os
import sys
import tempfile

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
PORTAL = os.path.dirname(HIER)
sys.path.insert(0, PORTAL)
sys.path.insert(0, os.path.join(HIER, 'beispiele'))

import erzeugen                                            # noqa: E402


class FalscheAntwort:
    """Was der Kunde zurueckgibt, ohne dass jemand das Netz braucht."""

    def __init__(self, text=None, stop_reason='end_turn', kategorie=None):
        self.stop_reason = stop_reason
        self.content = [type('B', (), {'type': 'text', 'text': text})()] if text else []
        self.stop_details = (type('S', (), {'category': kategorie})()
                             if stop_reason == 'refusal' else None)
        self.usage = type('U', (), {'input_tokens': 19000, 'output_tokens': 3000})()


class FalscherKunde:
    def __init__(self, antwort):
        self.antwort = antwort
        self.gesehen = None
        aussen = self

        class Nachrichten:
            def create(self, **anfrage):
                aussen.gesehen = anfrage
                return aussen.antwort

        self.beta = type('Beta', (), {'messages': Nachrichten()})()


GELESEN = {
    'art': 'kontoauszug', 'iban': 'DE00 0000 0000 0000 0000 00',
    'zeitraum': '01.06.2026 bis 30.06.2026',
    'saldo_alt': 120000.0, 'saldo_neu': 121560.45, 'waehrung': 'EUR',
    'posten': [{'datum': '03.06.2026', 'text': 'Rechnung 2026-114', 'betrag': 4760.0},
               {'datum': '11.06.2026', 'text': 'Miete', 'betrag': -3200.0}],
    'sicher': True, 'hinweis': '',
}


@pytest.fixture()
def ki():
    for name in ('datenbank', 'erkennung'):
        sys.modules.pop(name, None)
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ.pop('VALTIX_KI_REGION', None)
    import datenbank, erkennung                            # noqa: E402
    datenbank.anlegen()
    return erkennung


# ------------------------------------------------------------------ Zugang
def test_ohne_schluessel_ist_die_erkennung_aus(ki, monkeypatch):
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    assert ki.verfuegbar() is False
    with pytest.raises(ki.NichtMoeglich):
        ki.lesen(b'%PDF-1.4', 'scan.pdf')


def test_zu_grosse_datei_wird_abgelehnt(ki):
    with pytest.raises(ki.NichtMoeglich):
        ki.lesen(b'x' * (ki.HOECHSTENS_BYTES + 1), 'riesig.pdf')


# ------------------------------------------------------------------ Anfrage
def test_anfrage_enthaelt_das_pdf_und_das_schema(ki):
    daten = erzeugen.scan_pdf_ohne_text()
    a = ki._anfrage(daten, 'Kontoauszug.pdf')
    dok = a['messages'][0]['content'][0]
    assert dok['type'] == 'document'
    assert dok['source']['media_type'] == 'application/pdf'
    assert base64.standard_b64decode(dok['source']['data']) == daten
    assert '\n' not in dok['source']['data']
    assert a['output_config']['format']['schema'] == ki.SCHEMA
    assert a['model'] == ki.MODELL
    assert 'Kontoauszug.pdf' in a['messages'][0]['content'][1]['text']


def test_region_nur_wenn_gesetzt(ki, monkeypatch):
    assert 'inference_geo' not in ki._anfrage(b'x', 'a.pdf')
    monkeypatch.setenv('VALTIX_KI_REGION', 'us')
    assert ki._anfrage(b'x', 'a.pdf')['inference_geo'] == 'us'


def test_anfrage_hat_einen_ausweichweg(ki):
    a = ki._anfrage(b'x', 'a.pdf')
    assert a['fallbacks'] == 'default'
    assert 'server-side-fallback-2026-07-01' in a['betas']


# ------------------------------------------------------------------ Antwort
def test_antwort_wird_gelesen(ki):
    kunde = FalscherKunde(FalscheAntwort(json.dumps(GELESEN)))
    gelesen, verbrauch = ki.lesen(b'%PDF-1.4', 'scan.pdf', kunde=kunde)
    assert gelesen['saldo_neu'] == 121560.45
    assert verbrauch == {'ein': 19000, 'aus': 3000}
    assert kunde.gesehen['model'] == ki.MODELL


def test_ablehnung_wird_gemeldet_und_nicht_geraten(ki):
    kunde = FalscherKunde(FalscheAntwort(stop_reason='refusal', kategorie='cyber'))
    with pytest.raises(ki.NichtMoeglich) as e:
        ki.lesen(b'%PDF-1.4', 'scan.pdf', kunde=kunde)
    assert 'cyber' in str(e.value)


def test_kaputte_antwort_wirft_statt_zu_raten(ki):
    for text in ('kein json', ''):
        kunde = FalscherKunde(FalscheAntwort(text))
        with pytest.raises(ki.NichtMoeglich):
            ki.lesen(b'%PDF-1.4', 'scan.pdf', kunde=kunde)


# ------------------------------------------------------------------ Ergebnis
def test_aus_dem_gelesenen_wird_eine_extraktion(ki):
    e = ki.als_extraktion(GELESEN, {'ein': 19000, 'aus': 3000})
    assert e['weg'] == 'ki'
    assert e['status'] == 'roh'
    blaetter = {t['blatt']: t['zeilen'] for t in e['tabellen']}
    assert blaetter['Erkannt'][0] == ['Datum', 'Text', 'Betrag']
    assert blaetter['Erkannt'][1][2] == 4760.0
    assert blaetter['Saldo'][1][2] == 121560.45
    assert 'kontoauszug' in e['hinweis']
    assert 'IBAN' in e['hinweis']


def test_unsicheres_ergebnis_bekommt_weniger_konfidenz(ki):
    sicher = ki.als_extraktion({**GELESEN, 'sicher': True})
    unsicher = ki.als_extraktion({**GELESEN, 'sicher': False})
    assert unsicher['konfidenz'] < sicher['konfidenz']
    # Auch das sicherste Ergebnis bleibt unter einer gelesenen Tabelle.
    assert sicher['konfidenz'] <= 0.5


def test_ohne_posten_keine_leere_tabelle(ki):
    e = ki.als_extraktion({**GELESEN, 'posten': [], 'saldo_neu': None})
    assert e['tabellen'] == []


def test_die_posten_sind_fuer_die_uebernahme_lesbar(ki):
    import uebernahme as ue
    e = ki.als_extraktion(GELESEN)
    saldo = next(t for t in e['tabellen'] if t['blatt'] == 'Saldo')
    posten = ue.posten(saldo)
    assert posten == [('1800', 'Bank, Endsaldo laut Auszug', 121560.45)]


# ------------------------------------------------------------------ Warteschlange
def test_scan_reiht_einen_zweiten_anlauf_ein(ki, monkeypatch):
    for name in ('speicher', 'perioden', 'benachrichtigung', 'aufgaben'):
        sys.modules.pop(name, None)
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    import datenbank, perioden, aufgaben                   # noqa: E402
    datenbank.anlegen()
    mid = datenbank.mandant_anlegen('Alpha GmbH')
    perioden.checkliste_uebernehmen(mid)
    did = perioden.dokument_ablegen(mid, '2026-06', 'kontensalden', 'scan.pdf',
                                    'application/pdf',
                                    erzeugen.scan_pdf_ohne_text(), None)
    monkeypatch.setattr(ki, 'verfuegbar', lambda: True)
    aufgaben.abarbeiten()
    with datenbank.verbinden() as con:
        arten = [r['art'] for r in con.execute(
            'SELECT art FROM aufgabe WHERE dokument_id=? ORDER BY id',
            (did,)).fetchall()]
    assert arten == ['lesen', 'erkennen']


def test_ohne_erkennung_bleibt_es_bei_einem_anlauf(ki, monkeypatch):
    for name in ('speicher', 'perioden', 'benachrichtigung', 'aufgaben'):
        sys.modules.pop(name, None)
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    import datenbank, perioden, aufgaben                   # noqa: E402
    datenbank.anlegen()
    mid = datenbank.mandant_anlegen('Alpha GmbH')
    perioden.checkliste_uebernehmen(mid)
    did = perioden.dokument_ablegen(mid, '2026-06', 'kontensalden', 'scan.pdf',
                                    'application/pdf',
                                    erzeugen.scan_pdf_ohne_text(), None)
    monkeypatch.setattr(ki, 'verfuegbar', lambda: False)
    aufgaben.abarbeiten()
    with datenbank.verbinden() as con:
        arten = [r['art'] for r in con.execute(
            'SELECT art FROM aufgabe WHERE dokument_id=?', (did,)).fetchall()]
    assert arten == ['lesen']
    assert aufgaben.extraktion(did)['status'] == 'ocr_noetig'
