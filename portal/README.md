# Valtix Mandantenportal

Login-geschützter Bereich, in dem Mandanten ihre Monatsberichte einsehen.
Erzeugt wird der Bericht vom Generator in `tools/bericht/`.

## Rollen

| Rolle | Sieht | Darf |
|---|---|---|
| **Administrator** | alle Mandanten und alle Berichte | Mandanten und Zugänge anlegen, Zugänge sperren, Berichte einstellen, Protokoll einsehen |
| **Mandant** | ausschließlich die Berichte des eigenen Unternehmens | Berichte ansehen |

Es gibt **keine Registrierung von außen**. Ein Zugang wird von einem Administrator
angelegt und erzeugt dabei einen einmaligen Einladungslink. Über diesen Link setzt
die Person ihr Passwort selbst. Valtix kennt es zu keinem Zeitpunkt.

## Was zur Sicherheit umgesetzt ist

- Passwörter als **Argon2id**-Hash, mindestens zwölf Zeichen, nie im Klartext gespeichert
- Sitzungen als **signiertes Cookie**, HttpOnly, SameSite Lax, Secure, acht Stunden gültig
- **CSRF-Token** auf allen verändernden Formularen
- **Bremse gegen Durchprobieren**: fünf Fehlversuche je IP in fünf Minuten
- **Gleiche Antwortzeit**, ob ein Konto existiert oder nicht, damit sich keine
  gültigen Adressen erraten lassen
- **Rechteprüfung bei jedem Bericht**: Ein Mandant, der eine fremde Nummer aufruft,
  bekommt „Nicht gefunden" und der Versuch landet im Protokoll
- **Protokoll** über Anmeldungen, geöffnete Berichte und Änderungen an Zugängen
- Kopfzeilen `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`,
  `Cache-Control: no-store`
- `noindex, nofollow` auf allen Seiten

## Lokal starten

```bash
pip install fastapi "uvicorn[standard]" python-multipart itsdangerous argon2-cffi openpyxl
export VALTIX_SECRET="$(python3 -c 'import secrets;print(secrets.token_urlsafe(48))')"
export VALTIX_HTTPS=0                 # nur lokal, ohne TLS
export VALTIX_BASIS=http://127.0.0.1:8000
python3 portal/einrichten.py "Vorname Nachname" adresse@valtixfm.de
python3 -m uvicorn app:app --app-dir portal --host 127.0.0.1 --port 8000
```

`einrichten.py` gibt den Einladungslink für den ersten Administrator aus. Alle
weiteren Zugänge entstehen danach in der Verwaltung.

## Umgebungsvariablen

| Variable | Bedeutung |
|---|---|
| `VALTIX_SECRET` | Schlüssel für Sitzungs- und CSRF-Signaturen. **Pflicht im Betrieb.** Ohne ihn wird bei jedem Start ein flüchtiger erzeugt und alle Sitzungen brechen ab. |
| `VALTIX_DB` | Pfad zur SQLite-Datei, Vorgabe `portal/portal.sqlite3` |
| `VALTIX_HTTPS` | `1` setzt das Secure-Flag am Cookie, Vorgabe `1`. Lokal ohne TLS auf `0`. |
| `VALTIX_BASIS` | Adresse für die Einladungslinks, Vorgabe `https://portal.valtixfm.de` |

## Was für den Betrieb im Netz noch fehlt

Das ist keine Programmierarbeit mehr, sondern Einrichtung und Entscheidungen.

1. **Server**, sinnvollerweise in Deutschland, etwa Hetzner. Rund 5 bis 20 Euro im Monat.
2. **Subdomain** `portal.valtixfm.de` bei IONOS auf den Server zeigen lassen.
3. **TLS**, üblicherweise über Caddy oder nginx mit Let's Encrypt.
4. **`VALTIX_SECRET`** dauerhaft und geheim hinterlegen.
5. **Datensicherung** der Datenbank, täglich, verschlüsselt, an einen zweiten Ort.
6. **PostgreSQL statt SQLite**, sobald mehrere Personen gleichzeitig schreiben.
   Betrifft nur `datenbank.py`.
7. **Datenschutz**: Verzeichnis der Verarbeitungstätigkeiten, Löschkonzept,
   technische und organisatorische Maßnahmen, Auftragsverarbeitungsvertrag mit
   dem Hoster, Ergänzung der Datenschutzerklärung.

## Bewusst noch nicht gebaut

- **Passwort vergessen**: braucht E-Mail-Versand. Bis dahin legt ein Administrator
  einen neuen Einladungslink an.
- **Zwei-Faktor-Anmeldung**: bei Finanzdaten mittelfristig sinnvoll.
- **E-Mail-Benachrichtigung**, wenn ein neuer Bericht vorliegt.
- **Löschen von Berichten**: bisher nur Anlegen, damit nichts versehentlich verschwindet.

## Vertraulichkeit

Die Datenbank enthält Zahlen fremder Unternehmen. Sie gehört **nicht ins
Repository**; `.gitignore` schließt `*.sqlite3` aus.


## Verhältnis zur Portalvorschau

`portal-vorschau.html` im Wurzelverzeichnis zeigt einen Entwurf der Oberfläche:
Seitenleiste, Kennzahlenkacheln, Monatsverlauf und ein aufklappbares Raster mit
den Monaten als Spalten. Dieser Entwurf ist hier noch nicht umgesetzt, das
laufende Portal zeigt Berichte als einfache Liste.

Die Daten dafür liefert `tools/bericht/matrix.py`. Wer den Entwurf übernimmt,
baut die Ansicht auf dieser Klasse auf und muss den Generator nicht anfassen.
