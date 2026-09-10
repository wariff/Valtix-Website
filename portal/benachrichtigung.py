#!/usr/bin/env python3
"""Meldungen in der Anwendung und per E-Mail.

Ohne gesetzte Zugangsdaten wird nur protokolliert, nichts versendet. So laeuft
M1 lokal, ohne dass irgendwo ein Passwort im Code steht.

    VALTIX_SMTP_HOST, VALTIX_SMTP_PORT, VALTIX_SMTP_USER,
    VALTIX_SMTP_PASS, VALTIX_ABSENDER
"""
import os
import smtplib
import sys
from email.message import EmailMessage

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import datenbank as db                                    # noqa: E402


def in_app(text, benutzer_id=None, rolle=None, ziel=None):
    """Meldung im Portal. Entweder an eine Person oder an eine ganze Rolle."""
    with db.verbinden() as con:
        con.execute('INSERT INTO meldung (benutzer_id, rolle, text, ziel, erstellt_am) '
                    'VALUES (?,?,?,?,?)', (benutzer_id, rolle, text, ziel, db.jetzt()))


def offene(benutzer):
    with db.verbinden() as con:
        return [dict(r) for r in con.execute(
            'SELECT * FROM meldung WHERE gelesen_am IS NULL '
            'AND (benutzer_id=? OR rolle=?) ORDER BY id DESC LIMIT 20',
            (benutzer['id'], benutzer['rolle'])).fetchall()]


def gelesen(benutzer):
    with db.verbinden() as con:
        con.execute('UPDATE meldung SET gelesen_am=? WHERE gelesen_am IS NULL '
                    'AND (benutzer_id=? OR rolle=?)',
                    (db.jetzt(), benutzer['id'], benutzer['rolle']))


def mail(an, betreff, text):
    """Versendet, wenn ein Server eingerichtet ist. Sonst nur ins Protokoll."""
    host = os.environ.get('VALTIX_SMTP_HOST')
    absender = os.environ.get('VALTIX_ABSENDER')
    if not host or not absender or not an:
        db.protokollieren('mail_nicht_versendet', email=an, detail=betreff)
        return False
    n = EmailMessage()
    n['From'] = absender
    n['To'] = an
    n['Subject'] = betreff
    n.set_content(text)
    with smtplib.SMTP(host, int(os.environ.get('VALTIX_SMTP_PORT', '587'))) as s:
        s.starttls()
        nutzer = os.environ.get('VALTIX_SMTP_USER')
        if nutzer:
            s.login(nutzer, os.environ.get('VALTIX_SMTP_PASS', ''))
        s.send_message(n)
    db.protokollieren('mail_versendet', email=an, detail=betreff)
    return True


def admins():
    return [b for b in db.benutzer_liste() if b['rolle'] == 'admin' and b['aktiv']]


def eingereicht(mandant_name, jahr_monat, anzahl, periode_id):
    """Nach F6: Eingangsmeldung an Valtix."""
    text = (f'{mandant_name} hat Unterlagen für {jahr_monat} eingereicht, '
            f'{anzahl} {"Datei" if anzahl == 1 else "Dateien"}.')
    in_app(text, rolle='admin', ziel=f'/uebersicht/{periode_id}')
    for a in admins():
        mail(a['email'], f'Unterlagen {jahr_monat}: {mandant_name}', text)


def nachtrag(mandant_name, jahr_monat, periode_id):
    text = f'{mandant_name} hat für {jahr_monat} einen Nachtrag angekündigt.'
    in_app(text, rolle='admin', ziel=f'/uebersicht/{periode_id}')
    for a in admins():
        mail(a['email'], f'Nachtrag {jahr_monat}: {mandant_name}', text)


def bestaetigung(email, mandant_name, jahr_monat, anzahl):
    """Bestaetigung an den Mandanten, ebenfalls F6."""
    mail(email, f'Eingang bestätigt: Unterlagen {jahr_monat}',
         f'Guten Tag,\n\nwir haben Ihre Unterlagen für {jahr_monat} erhalten, '
         f'{anzahl} {"Datei" if anzahl == 1 else "Dateien"}. '
         f'Sie hören von uns, sobald die Auswertung vorliegt.\n\n'
         f'Valtix Financial Management')


def erinnerung(email, mandant_name, jahr_monat, fehlend):
    liste = ', '.join(fehlend)
    mail(email, f'Erinnerung: Unterlagen {jahr_monat}',
         f'Guten Tag,\n\nfür {jahr_monat} fehlen uns noch: {liste}.\n\n'
         f'Sie können die Unterlagen jederzeit im Portal hochladen.\n\n'
         f'Valtix Financial Management')
