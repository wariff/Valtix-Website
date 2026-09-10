#!/usr/bin/env python3
"""Dateiablage des Portals.

Heute liegt alles im Dateisystem, weil M1 ohne Anbieterentscheidung lokal
lauffaehig sein soll. Der Rest der Anwendung spricht nur ueber die drei
Funktionen unten mit der Ablage. Beim Umzug auf einen Objektspeicher wird
diese Datei ersetzt, sonst nichts.

Ausserhalb des Web-Wurzelverzeichnisses, nichts davon wird direkt
ausgeliefert. Zugriff laeuft immer ueber die Anwendung, die vorher die
Rechte prueft.
"""
import hashlib
import os
import re
import secrets

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.environ.get('VALTIX_ABLAGE', os.path.join(HIER, 'ablage'))

# Was hochgeladen werden darf. Endung und gemeldeter Typ muessen beide passen,
# sonst wird abgelehnt. Ausgefuehrt wird serverseitig nichts davon.
ERLAUBT = {
    '.pdf':  {'application/pdf'},
    '.jpg':  {'image/jpeg'},
    '.jpeg': {'image/jpeg'},
    '.png':  {'image/png'},
    '.xlsx': {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    '.xls':  {'application/vnd.ms-excel'},
    '.csv':  {'text/csv', 'application/csv', 'text/plain',
              'application/vnd.ms-excel'},
    '.txt':  {'text/plain'},          # DATEV-Exporte kommen oft als .txt
    '.zip':  {'application/zip', 'application/x-zip-compressed'},
}
GROESSTE_DATEI = 25 * 1024 * 1024


class Abgelehnt(Exception):
    """Die Datei erfuellt die Bedingungen nicht. Der Text geht an den Nutzer."""


def endung(dateiname):
    return os.path.splitext(dateiname or '')[1].lower()


def pruefen(dateiname, mime, groesse):
    """Wirft Abgelehnt mit einem Satz, der sagt, was zu tun ist."""
    e = endung(dateiname)
    if e not in ERLAUBT:
        erlaubt = ', '.join(sorted(ERLAUBT))
        raise Abgelehnt(f'Dateien mit der Endung „{e or "ohne"}" nehmen wir nicht an. '
                        f'Erlaubt sind {erlaubt}.')
    if mime and mime not in ERLAUBT[e]:
        raise Abgelehnt(f'Die Datei gibt sich als „{mime}" aus, das passt nicht zur '
                        f'Endung {e}. Bitte laden Sie die Originaldatei hoch.')
    if groesse <= 0:
        raise Abgelehnt('Die Datei ist leer.')
    if groesse > GROESSTE_DATEI:
        raise Abgelehnt(f'Die Datei ist {groesse / 1048576:.1f} MB gross. '
                        f'Mehr als {GROESSTE_DATEI // 1048576} MB nehmen wir nicht an. '
                        f'Bitte teilen Sie sie auf.')


def pruefsumme(daten):
    return hashlib.sha256(daten).hexdigest()


def _sicher(teil):
    return re.sub(r'[^A-Za-z0-9._-]', '_', str(teil))[:60]


def ablegen(daten, mandant_id, jahr_monat, dateiname):
    """Legt die Datei ab und gibt den Schluessel zurueck, unter dem sie liegt.

    Der Name aus dem Upload wird nie als Pfad verwendet. Er steht nur in der
    Datenbank, damit der Mandant seine Datei wiedererkennt.
    """
    schluessel = (f'{_sicher(mandant_id)}/{_sicher(jahr_monat)}/'
                  f'{secrets.token_hex(16)}{endung(dateiname)}')
    ziel = os.path.join(WURZEL, schluessel)
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    with open(ziel, 'wb') as f:
        f.write(daten)
    os.chmod(ziel, 0o600)
    return schluessel


def lesen(schluessel):
    with open(_pfad(schluessel), 'rb') as f:
        return f.read()


def loeschen(schluessel):
    p = _pfad(schluessel)
    if os.path.exists(p):
        os.remove(p)


def groesse(schluessel):
    return os.path.getsize(_pfad(schluessel))


def _pfad(schluessel):
    """Loest den Schluessel auf und laesst nichts ausserhalb der Wurzel zu."""
    ziel = os.path.realpath(os.path.join(WURZEL, schluessel))
    wurzel = os.path.realpath(WURZEL)
    if not (ziel == wurzel or ziel.startswith(wurzel + os.sep)):
        raise Abgelehnt('Ungültiger Ablageschlüssel.')
    return ziel
