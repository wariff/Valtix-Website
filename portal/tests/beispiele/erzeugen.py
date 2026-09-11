#!/usr/bin/env python3
"""Erzeugt anonymisierte Beispieldateien fuer die Tests.

Keine echten Mandantendaten. Die Zahlen sind erfunden, die Struktur folgt dem,
was BWA, Summen- und Saldenliste und ein DATEV-Export ueblicherweise haben.
"""
import io
import os
import zlib

import openpyxl

HIER = os.path.dirname(os.path.abspath(__file__))


def bwa_xlsx():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'BWA'
    for r in [['Position', 'Monat', 'Kumuliert'],
              ['Umsatzerlöse', 365057.97, 2153496.13],
              ['Materialaufwand', 116346.42, 692183.60],
              ['Personalaufwand', 142062.35, 955731.85],
              ['Betriebsergebnis', 36213.26, 108944.79]]:
        ws.append(r)
    puffer = io.BytesIO()
    wb.save(puffer)
    return puffer.getvalue()


def susa_csv():
    zeilen = ['Konto;Bezeichnung;Soll;Haben;Saldo',
              '1200;Bank;125.300,00;3.739,55;121.560,45',
              '1400;Forderungen aus L+L;584.092,75;0,00;584.092,75',
              '4000;Umsatzerlöse;0,00;365.057,97;-365.057,97',
              '6000;Löhne und Gehälter;142.062,35;0,00;142.062,35']
    return '\r\n'.join(zeilen).encode('cp1252')


def datev_txt():
    kopf = ('"EXTF";700;21;"Buchungsstapel";13;20260806;;"";"";"";1000;1;'
            '20260101;4;20260701;20260731;"Juli";"";1;0;0;"EUR"')
    spalten = ('Umsatz;Soll/Haben;WKZ;Kurs;Basisumsatz;WKZ Basis;Konto;'
               'Gegenkonto;BU;Belegdatum;Belegfeld1;Buchungstext')
    buchungen = [
        '1234,56;S;EUR;;;;1200;4000;;0107;RE-1001;"Verkauf Juli"',
        '890,10;H;EUR;;;;4000;1200;;1507;RE-1002;"Gutschrift"',
    ]
    return '\r\n'.join([kopf, spalten] + buchungen).encode('cp1252')


def _pdf(inhalt_strom, mit_text):
    """Baut ein minimales PDF von Hand, damit die Tests keine weitere
    Bibliothek brauchen."""
    objekte = []
    objekte.append(b'<< /Type /Catalog /Pages 2 0 R >>')
    objekte.append(b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>')
    objekte.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
                   b'/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>')
    strom = zlib.compress(inhalt_strom)
    objekte.append(b'<< /Length ' + str(len(strom)).encode() +
                   b' /Filter /FlateDecode >>\nstream\n' + strom + b'\nendstream')
    objekte.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')

    raus = bytearray(b'%PDF-1.4\n')
    versatz = []
    for i, o in enumerate(objekte, start=1):
        versatz.append(len(raus))
        raus += str(i).encode() + b' 0 obj\n' + o + b'\nendobj\n'
    start = len(raus)
    raus += b'xref\n0 ' + str(len(objekte) + 1).encode() + b'\n'
    raus += b'0000000000 65535 f \n'
    for v in versatz:
        raus += f'{v:010d} 00000 n \n'.encode()
    raus += (b'trailer\n<< /Size ' + str(len(objekte) + 1).encode() +
             b' /Root 1 0 R >>\nstartxref\n' + str(start).encode() + b'\n%%EOF\n')
    return bytes(raus)


def bwa_pdf_mit_text():
    zeilen = [
        'Betriebswirtschaftliche Auswertung Juli 2026',
        'Umsatzerloese                 365.057,97',
        'Materialaufwand               116.346,42',
        'Personalaufwand               142.062,35',
        'Betriebsergebnis               36.213,26',
    ]
    teile = [b'BT /F1 11 Tf 56 780 Td 16 TL']
    for z in zeilen:
        teile.append(b'(' + z.encode('latin-1', 'replace') + b') Tj T*')
    teile.append(b'ET')
    return _pdf(b'\n'.join(teile), True)


def scan_pdf_ohne_text():
    """Eine Seite mit einem Rechteck, kein Text. So sieht ein Scan aus."""
    return _pdf(b'0.9 g 56 600 480 180 re f', False)


def alle():
    return {
        'bwa.xlsx': bwa_xlsx(),
        'susa.csv': susa_csv(),
        'EXTF_Buchungsstapel.txt': datev_txt(),
        'bwa-digital.pdf': bwa_pdf_mit_text(),
        'scan.pdf': scan_pdf_ohne_text(),
    }


if __name__ == '__main__':
    for name, daten in alle().items():
        with open(os.path.join(HIER, name), 'wb') as f:
            f.write(daten)
        print(f'{name}: {len(daten)} Bytes')
