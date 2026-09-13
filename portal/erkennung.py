#!/usr/bin/env python3
"""Gescannte Belege lesen lassen, wenn keine Textebene da ist.

Der Leser meldet ein PDF ohne Textebene als 'ocr_noetig' und raet nichts.
Hier wird daraus ein Vorschlag: Das PDF geht als Ganzes an Claude, zurueck
kommt eine feste Struktur, die in dieselbe Pruefansicht laeuft wie jedes
andere Ergebnis auch. Freigegeben wird weiterhin von Hand.

Ohne Zugangsdaten passiert nichts. Das Dokument bleibt dann auf 'ocr_noetig'
stehen, mit einem Hinweis. So laeuft das Portal auch ohne diesen Dienst.

    ANTHROPIC_API_KEY   Zugang. Fehlt er, ist die Erkennung aus.
    VALTIX_KI_MODELL    Modell, sonst claude-opus-5
    VALTIX_KI_REGION    Verarbeitungsregion, sonst die des Kontos
"""
import base64
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402

MODELL = os.environ.get('VALTIX_KI_MODELL', 'claude-opus-5')
# Ein Kontoauszug ist selten lang. Die Grenze haelt Ausreisser aus der
# Rechnung heraus, ein 200-Seiten-Scan ist ohnehin ein Fehlgriff.
HOECHSTENS_SEITEN = 40
HOECHSTENS_BYTES = 20 * 1024 * 1024

AUFTRAG = """Du liest einen eingescannten Beleg aus der Finanzbuchhaltung eines
deutschen Unternehmens. Gib zurueck, was tatsaechlich auf dem Blatt steht.

Regeln, die wichtiger sind als Vollstaendigkeit:
- Rate nichts. Was du nicht sicher lesen kannst, laesst du weg und
  vermerkst es unter hinweis.
- Betraege in deutscher Schreibweise (1.234,56) gibst du als Zahl zurueck:
  1234.56. Ein Minus bleibt ein Minus.
- Ist das Blatt kein Kontoauszug, setze art entsprechend und lass die
  Kontofelder leer.
- sicher setzt du nur auf true, wenn Anfangs- und Endsaldo klar lesbar sind
  und die Summe der Posten dazu passt."""

SCHEMA = {
    'type': 'object',
    'properties': {
        'art': {'type': 'string',
                'enum': ['kontoauszug', 'bwa', 'saldenliste', 'rechnung', 'unbekannt']},
        'iban': {'type': 'string'},
        'zeitraum': {'type': 'string'},
        'saldo_alt': {'type': ['number', 'null']},
        'saldo_neu': {'type': ['number', 'null']},
        'waehrung': {'type': 'string'},
        'posten': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'datum': {'type': 'string'},
                    'text': {'type': 'string'},
                    'betrag': {'type': 'number'},
                },
                'required': ['datum', 'text', 'betrag'],
                'additionalProperties': False,
            },
        },
        'sicher': {'type': 'boolean'},
        'hinweis': {'type': 'string'},
    },
    'required': ['art', 'iban', 'zeitraum', 'saldo_alt', 'saldo_neu', 'waehrung',
                 'posten', 'sicher', 'hinweis'],
    'additionalProperties': False,
}


class NichtMoeglich(Exception):
    """Die Erkennung steht nicht zur Verfuegung oder hat nichts geliefert."""


def verfuegbar():
    """Ohne Schluessel und ohne Bibliothek bleibt die Erkennung aus."""
    if not os.environ.get('ANTHROPIC_API_KEY'):
        return False
    try:
        import anthropic                                  # noqa: F401
    except ImportError:
        return False
    return True


def _kunde():
    import anthropic
    # Zehn Minuten sind der Standard. Ein langer Scan darf so lange brauchen.
    return anthropic.Anthropic()


def _anfrage(daten, dateiname):
    """Baut die Anfrage. Getrennt, damit sie ohne Netz geprueft werden kann."""
    inhalt = [
        {'type': 'document',
         'source': {'type': 'base64', 'media_type': 'application/pdf',
                    'data': base64.standard_b64encode(daten).decode('ascii')}},
        {'type': 'text', 'text': f'Dateiname: {dateiname}'},
    ]
    anfrage = {
        'model': MODELL,
        'max_tokens': 16000,
        'system': AUFTRAG,
        'messages': [{'role': 'user', 'content': inhalt}],
        'output_config': {'format': {'type': 'json_schema', 'schema': SCHEMA}},
        'thinking': {'type': 'adaptive'},
        # Lehnt das Modell ab, uebernimmt in derselben Anfrage ein anderes.
        # Ohne das bricht die Anfrage einfach ab.
        'betas': ['server-side-fallback-2026-07-01'],
        'fallbacks': 'default',
    }
    region = os.environ.get('VALTIX_KI_REGION')
    if region:
        anfrage['inference_geo'] = region
    return anfrage


def _auswerten(antwort):
    """Holt die Struktur aus der Antwort und meldet eine Ablehnung ehrlich."""
    if getattr(antwort, 'stop_reason', None) == 'refusal':
        grund = getattr(getattr(antwort, 'stop_details', None), 'category', None)
        raise NichtMoeglich(f'Die Anfrage wurde abgelehnt ({grund or "ohne Angabe"}).')
    text = next((b.text for b in antwort.content if b.type == 'text'), '')
    if not text:
        raise NichtMoeglich('Die Antwort enthielt keinen Text.')
    try:
        return json.loads(text)
    except ValueError as e:
        raise NichtMoeglich(f'Die Antwort war kein gültiges JSON: {e}')


def _verbrauch(antwort):
    v = getattr(antwort, 'usage', None)
    return {'ein': getattr(v, 'input_tokens', None),
            'aus': getattr(v, 'output_tokens', None)} if v else {}


def lesen(daten, dateiname, kunde=None):
    """Schickt den Scan hin und gibt zurueck, was gelesen wurde."""
    if len(daten) > HOECHSTENS_BYTES:
        raise NichtMoeglich('Die Datei ist zu groß für die Erkennung.')
    if kunde is None:
        if not verfuegbar():
            raise NichtMoeglich('Für die Erkennung ist kein Zugang hinterlegt.')
        kunde = _kunde()
    antwort = kunde.beta.messages.create(**_anfrage(daten, dateiname))
    return _auswerten(antwort), _verbrauch(antwort)


def als_extraktion(gelesen, verbrauch=None):
    """Bringt das Gelesene in die Form, die die Warteschlange ablegt.

    Die Posten werden zu einer Tabelle, damit die Uebernahme sie genauso
    verarbeitet wie eine eingelesene Saldenliste. Der Saldo kommt als eigene
    Zeile dazu, weil er der eigentliche Zweck des Auszugs ist.
    """
    zeilen = [['Datum', 'Text', 'Betrag']]
    for p in gelesen.get('posten') or []:
        zeilen.append([p.get('datum', ''), p.get('text', ''), p.get('betrag')])
    tabellen = [{'blatt': 'Erkannt', 'zeilen': zeilen}] if len(zeilen) > 1 else []
    if gelesen.get('saldo_neu') is not None:
        tabellen.append({'blatt': 'Saldo',
                         'zeilen': [['Konto', 'Bezeichnung', 'Betrag'],
                                    ['1800', 'Bank, Endsaldo laut Auszug',
                                     gelesen['saldo_neu']]]})
    teile = [f'Erkannt als {gelesen.get("art", "unbekannt")}']
    if gelesen.get('zeitraum'):
        teile.append(str(gelesen['zeitraum']))
    if gelesen.get('iban'):
        teile.append(f'IBAN {gelesen["iban"]}')
    if gelesen.get('hinweis'):
        teile.append(str(gelesen['hinweis']))
    if verbrauch and verbrauch.get('ein'):
        teile.append(f'{verbrauch["ein"]} Token ein, {verbrauch.get("aus")} aus')
    return {
        'weg': 'ki',
        'seiten': None,
        'tabellen': tabellen,
        'rohtext': json.dumps(gelesen, ensure_ascii=False)[:200000],
        # Ein erkannter Scan ist nie so sicher wie eine gelesene Tabelle.
        # Der Wert steht in der Pruefansicht und soll dort auffallen.
        'konfidenz': 0.5 if gelesen.get('sicher') else 0.3,
        'status': 'roh',
        'hinweis': ' · '.join(teile)[:500],
    }


def nachholen(dokument_id, daten, dateiname):
    """Ein Dokument, das der Leser als 'ocr_noetig' abgelegt hat."""
    gelesen, verbrauch = lesen(daten, dateiname)
    ergebnis = als_extraktion(gelesen, verbrauch)
    db.protokollieren('scan_erkannt', detail=f'dokument {dokument_id}, {dateiname}',
                      nachher=ergebnis['hinweis'][:200])
    return ergebnis
