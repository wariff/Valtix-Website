#!/usr/bin/env python3
"""Erstinbetriebnahme: Datenbank anlegen und den ersten Administrator einrichten.

    python3 portal/einrichten.py "Sharif Ibrahim" info@valtixfm.de

Gibt einen einmaligen Einladungslink aus. Ein Passwort wird nicht vergeben,
die Person setzt es selbst. Damit kennt es niemand sonst, auch der Betreiber nicht.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datenbank as db

if len(sys.argv) < 3:
    sys.exit('Aufruf: einrichten.py "<Name>" <E-Mail>')
name, email = sys.argv[1], sys.argv[2]
db.anlegen()
if any(b['rolle'] == 'admin' for b in db.benutzer_liste()):
    print('Es gibt bereits einen Administrator. Weitere Zugänge über die Verwaltung anlegen.')
    sys.exit(1)
token = db.benutzer_anlegen(email, name, 'admin')
db.protokollieren('erster_admin_angelegt', email=email)
basis = os.environ.get('VALTIX_BASIS', 'https://portal.valtixfm.de')
print(f'Administrator angelegt: {name} <{email}>')
print(f'Einladungslink (einmalig): {basis}/einladung/{token}')
