# Valtix – Financial Health Check Website

One-Pager für **Valtix Financial Management** (Leipzig): Kennzahlen-Analyse, Liquiditätsoptimierung und Wachstumsberatung für den Mittelstand.

## Struktur

```
index.html          # One-Pager (Hero, Stats, Leistungen, Ablauf, Warum Valtix, Kontakt)
impressum.html      # Platzhalter – Pflichtangaben ergänzen
datenschutz.html    # Platzhalter – DSGVO-Erklärung ergänzen
assets/
├── valtix-logo.png             # Logo auf Navy-Hintergrund
├── valtix-logo-transparent.png # Logo mit transparentem Hintergrund (Creme)
└── favicon.svg
```

## Design

- **Farben:** Navy `#232941` und Creme `#F5EBD0` – direkt aus dem Logo übernommen
- **Schriften:** Archivo (Headlines) + IBM Plex Sans (Text) via Google Fonts
- **Responsive:** Mobile (375px), Tablet (768px), Desktop (1024px/1440px)
- **Barrierefrei:** Kontrast > 4,5:1, Fokus-Ringe, Skip-Link, `prefers-reduced-motion`, 44px-Touch-Ziele

Keine Build-Tools nötig – statisches HTML/CSS, direkt deploybar (z. B. GitHub Pages).

## Vor dem Livegang anpassen

- [ ] E-Mail-Adresse `hallo@valtix.de` durch echte Adresse ersetzen
- [ ] Zahlen im Stats-Band und im Hero-Report prüfen/anpassen (aktuell Beispielwerte)
- [ ] Impressum und Datenschutzerklärung befüllen
- [ ] Google Fonts ggf. lokal hosten (DSGVO)
