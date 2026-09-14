#!/usr/bin/env python3
"""Tests fuer das Lesen einer DATEV-BWA als PDF.

Die Zahlen hier sind erfunden, der Aufbau ist der einer echten DATEV-Ausgabe:
erst die Kurzfristige Erfolgsrechnung, dann derselbe Zeilensatz noch einmal im
Vorjahresvergleich, danach die Summen- und Saldenliste und dieselbe noch
einmal als Jahresuebersicht. Genau diese Wiederholungen haben beim ersten
Lauf an echten Daten jeden Posten mehrfach gezaehlt.
"""
import os
import sys
import tempfile

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))

import leser                                               # noqa: E402
import mapping as mp                                       # noqa: E402

TEXT = """223735/13633/2026 Kurzfristige Erfolgsrechnung 14.08.2026
Beispiel GbR Blatt 1
Juni 2026 - Handelsrecht
SKR: 03 BWA-Nr.: 1 BWA-Form: DATEV-BWA Wareneinsatz: Wareneinkauf
Bezeichnung Jun/2026 % Ges.- Jan/2026 - % Ges.-
Umsatzerlöse 10.000,00 100,00 60.000,00 100,00
Gesamtleistung 10.000,00 100,00 60.000,00 100,00
Material-/Wareneinkauf 3.000,00 30,00 18.000,00 30,00
Rohertrag 7.000,00 70,00 42.000,00 70,00
So. betr. Erlöse 200,00 2,00 1.200,00 2,00
Kostenarten:
Personalkosten 2.500,00 25,00 15.000,00 25,00
Raumkosten 1.500,00 15,00 9.000,00 15,00
Abschreibungen 300,00 3,00 1.800,00 3,00
Sonstige Kosten 700,00 7,00 4.200,00 7,00
Gesamtkosten 5.000,00 50,00 30.000,00 50,00
Betriebsergebnis 2.200,00 22,00 13.200,00 22,00
223735/13633/2026 Vorjahresvergleich 14.08.2026
Bezeichnung Jun/2026 Jun/2025 Veränderung
Umsatzerlöse 10.000,00 9.000,00 1.000,00 11,11
Material-/Wareneinkauf 3.000,00 2.800,00 200,00 7,14
Personalkosten 2.500,00 2.400,00 100,00 4,17
Beispiel GbR Summen und Salden (pro Monat) Juni 2026 - Handelsrecht Blatt 1
KontoBeschriftung EB-Wert Jun 2026 kum. Werte Saldo
1000 Kasse 100,00S 500,00 400,00 3.000,00 2.800,00 300,00 S
1200 Bank 5.000,00S 2.000,00 1.500,00 9.000,00 8.500,00 5.500,00 S
1400 Forderungen aus L+L 0,00 1.200,00 0,00 1.200,00 S
1600 Verbindlichkeiten aus L+L 900,00H 400,00 700,00 2.000,00 2.400,00 1.200,00 H
1576 Abziehbare Vorsteuer 19% 570,00 3.420,00 3.420,00 S
1776 Umsatzsteuer 19% 1.900,00 11.400,00 11.400,00 H
0880 Variables Kapital (VH), EK 20.000,00H 20.000,00 H
9000 Saldenvorträge Sachkonten 4.000,00 4.000,00 S
70041 Lieferant Nord 800,00H 800,00 H
3980 Bestand Waren 1.500,00S 1.500,00 S
8400 Erlöse 19% USt 10.000,00 60.000,00 60.000,00 H
Beispiel GbR SUSA Jahresübersicht Juni 2026 - Handelsrecht Blatt 1
Konto Beschriftung EB-Wert Jan/2026 Jun/2026 Gesamtsaldo
1000Kasse 100,00 S 42,00 S 100,80 H 300,00 S
1200Bank 5.000,00 S 500,00 S 1.000,00 S 5.500,00 S
"""


def test_datev_bwa_wird_erkannt():
    t = leser.aus_datev_auswertung(TEXT)
    assert [x['art'] for x in t] == ['bwa', 'saldenliste']


def test_der_monatswert_zaehlt_nicht_der_jahreswert():
    bwa = next(x for x in leser.aus_datev_auswertung(TEXT) if x['art'] == 'bwa')
    werte = {z[1]: z[2] for z in bwa['zeilen'][1:]}
    assert werte['Umsatzerlöse'] == 10000.00
    assert werte['Material-/Wareneinkauf'] == 3000.00
    assert werte['Personalkosten'] == 2500.00


def test_wiederholte_zeilen_zaehlen_einmal():
    # Umsatzerlöse stehen in der Erfolgsrechnung und im Vorjahresvergleich.
    bwa = next(x for x in leser.aus_datev_auswertung(TEXT) if x['art'] == 'bwa')
    namen = [z[1] for z in bwa['zeilen'][1:]]
    assert namen.count('Umsatzerlöse') == 1
    assert namen.count('Personalkosten') == 1


def test_summenzeilen_sind_keine_posten():
    bwa = next(x for x in leser.aus_datev_auswertung(TEXT) if x['art'] == 'bwa')
    namen = [z[1].lower() for z in bwa['zeilen'][1:]]
    for summe in ('gesamtleistung', 'rohertrag', 'gesamtkosten',
                  'betriebsergebnis'):
        assert summe not in namen, summe


def test_saldenliste_traegt_das_vorzeichen():
    su = next(x for x in leser.aus_datev_auswertung(TEXT) if x['art'] == 'saldenliste')
    salden = {z[0]: z[2] for z in su['zeilen'][1:]}
    assert salden['1200'] == 5500.00          # S, also im Soll
    assert salden['1600'] == -1200.00         # H, also im Haben
    assert salden['880'] == -20000.00


def test_jedes_konto_nur_einmal():
    # Kasse und Bank stehen in beiden Saldenlisten des Dokuments.
    su = next(x for x in leser.aus_datev_auswertung(TEXT) if x['art'] == 'saldenliste')
    konten = [z[0] for z in su['zeilen'][1:]]
    assert konten.count('1000') == 1
    assert konten.count('1200') == 1


def test_pdf_ohne_datev_bleibt_beim_alten_weg():
    assert leser.aus_datev_auswertung('Irgendein Text ohne Auswertung') == []


# ------------------------------------------------------ Kontenrahmen SKR03
def test_skr03_bilanz_liegt_anders_als_skr04():
    assert mp.aus_konto(1000, 'SKR03')[0] == 'liquide'      # Kasse
    assert mp.aus_konto(1200, 'SKR03')[0] == 'liquide'      # Bank
    assert mp.aus_konto(880, 'SKR03')[0] == 'eigenkapital'
    assert mp.aus_konto(1600, 'SKR04')[0] == 'liquide'      # im SKR04 die Kasse
    assert mp.aus_konto(2000, 'SKR04')[0] == 'eigenkapital'


def test_dreistellige_konten_werden_erkannt():
    assert mp.kontonummer('880') == 880
    assert mp.kontonummer('0880') == 880


def test_durchlaufende_und_statistische_konten_fallen_raus():
    for konto, teil in [(1576, 'Vorsteuer'), (1776, 'Umsatzsteuer'),
                        (9000, 'Saldenvortrag'), (70041, 'Personenkonto'),
                        (3980, 'Bestandskonto')]:
        assert teil in (mp.uebergehen(konto) or ''), konto


def test_privatkonten_bleiben_zur_entscheidung_stehen():
    # Entnahmen mindern das Eigenkapital, die gehoeren nicht stillschweigend weg.
    assert mp.uebergehen(1800) is None
    assert mp.uebergehen(1890) is None


# ----------------------------------------------------- Die ganze Kette
@pytest.fixture()
def kette():
    os.environ['VALTIX_DB'] = tempfile.mktemp(suffix='.sqlite3')
    os.environ['VALTIX_ABLAGE'] = tempfile.mkdtemp()
    for name in ('datenbank', 'speicher', 'perioden', 'benachrichtigung',
                 'aufgaben', 'uebernahme', 'mapping'):
        sys.modules.pop(name, None)
    import datenbank, perioden, aufgaben, uebernahme        # noqa: E402
    datenbank.anlegen()
    mid = datenbank.mandant_anlegen('Beispiel GbR')
    perioden.checkliste_uebernehmen(mid)
    return {'db': datenbank, 'pd': perioden, 'auf': aufgaben, 'ue': uebernahme,
            'mid': mid}


def _einspielen(k, monkeypatch):
    """Schiebt den Text an pdfplumber vorbei direkt in die Extraktion."""
    ergebnis = {'weg': 'pdf_datev', 'tabellen': leser.aus_datev_auswertung(TEXT),
                'rohtext': TEXT, 'seiten': 3, 'konfidenz': 0.85,
                'hinweis': 'DATEV-Auswertung als PDF'}
    monkeypatch.setattr(leser, 'lesen', lambda name, daten: ergebnis)
    did = k['pd'].dokument_ablegen(k['mid'], '2026-06', 'bwa', 'bwa.pdf',
                                   'application/pdf', b'%PDF-1.4 Platzhalter', None)
    k['auf'].abarbeiten()
    return did


def test_bwa_und_saldenliste_zaehlen_nicht_doppelt(kette, monkeypatch):
    k = kette
    _einspielen(k, monkeypatch)
    v = k['ue'].vorschlagen(k['pd'].periode(k['mid'], '2026-06')['id'])
    assert v['rahmen'] == 'SKR03'
    # Der Umsatz steht in der BWA mit 10.000 und in der Saldenliste als
    # Jahreswert mit 60.000. Gelten darf nur der Monat.
    assert v['felder']['hauptleistung']['wert'] == 10000.00
    assert v['felder']['wareneinsatz']['wert'] == 3000.00
    assert v['felder']['personal']['wert'] == 2500.00


def test_bestaende_kommen_aus_der_saldenliste(kette, monkeypatch):
    k = kette
    _einspielen(k, monkeypatch)
    v = k['ue'].vorschlagen(k['pd'].periode(k['mid'], '2026-06')['id'])
    assert v['felder']['liquide']['wert'] == 5800.00        # Kasse 300 + Bank 5.500
    assert v['felder']['forderungen']['wert'] == 1200.00
    assert v['felder']['kurzfr_verb']['wert'] == 1200.00


def test_was_die_bwa_nicht_trennt_wird_nicht_nachgefuellt(kette, monkeypatch):
    k = kette
    _einspielen(k, monkeypatch)
    v = k['ue'].vorschlagen(k['pd'].periode(k['mid'], '2026-06')['id'])
    # Die BWA fasst Energie und Beratung in "Sonstige Kosten" zusammen. Aus der
    # Saldenliste nachzufuellen hiesse, einen Jahreswert danebenzustellen.
    assert 'energie' not in v['felder']
    assert v['felder']['sonst_aufwand']['wert'] == 700.00
