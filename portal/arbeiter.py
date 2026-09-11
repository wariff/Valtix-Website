#!/usr/bin/env python3
"""Arbeitet die Warteschlange ab.

    python3 portal/arbeiter.py            einmal
    python3 portal/arbeiter.py --dauer    laufen lassen, alle 10 Sekunden

Gedacht fuer einen Dienst oder einen Zeitplan auf dem Server. Der Webprozess
laesst das Lesen nie selbst laufen, damit eine grosse Datei keine Anfrage
blockiert.
"""
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402
import aufgaben                                           # noqa: E402


def main():
    db.anlegen()
    dauer = '--dauer' in sys.argv
    while True:
        gut, schlecht = aufgaben.abarbeiten()
        if gut or schlecht:
            print(f'{db.jetzt()}  gelesen {gut}, fehlgeschlagen {schlecht}')
        if not dauer:
            return 0 if schlecht == 0 else 1
        time.sleep(10)


if __name__ == '__main__':
    sys.exit(main())
