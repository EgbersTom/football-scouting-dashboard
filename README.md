# ⚽ Bayer 04 Leverkusen – Advanced Scouting & xG Dashboard

Eine interaktive Web-Anwendung zur datengestützten Spiel- und Spieleranalyse für die ungeschlagene Bundesliga-Saison 2023/24 von Bayer 04 Leverkusen (StatsBomb Open Data).

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Data_Analytics-003B57?style=flat&logo=sqlite&logoColor=white)

## 🚀 Key Features

* **Saison- & Spiel-Filter:** Nahtloser Wechsel zwischen der gesamten Bundesliga-Saison (34 Partien) und einzelnen Spieltagen.
* **Pass-Analysen & Heatmaps:**
  * Einzelspieler-Analysen & Side-by-Side Direktvergleiche.
  * Differenzierte Betrachtung von Passquoten unter Gegnerdruck vs. ohne Druck.
  * Räumliche Pass-Heatmaps (KDE-Dichtediagramme) via `mplsoccer`.
* **Shot-Map & Expected Goals (xG):**
  * Visualisierung von Torschüssen und Torgefahr auf dem Spielfeld (Punktgröße skaliert mit xG-Wert).
  * Automatisch generiertes Spieler-Leaderboard für Chancenqualität.

## 🛠 Tech Stack & Architektur

* **Data Pipeline (ETL):** Python (`statsbombpy`, `pandas`) zur Datenextraktion, Aufbereitung von Raumkoordinaten (`location_x`, `location_y`) und Ingestion.
* **Data Storage:** SQLite / MySQL (`SQLAlchemy`) für relationale Abfragen und Indizierung.
* **Frontend / BI App:** Streamlit, Matplotlib, Seaborn & `mplsoccer`.

## 📦 Lokale Installation

1. Repository klonen:
   ```bash
   git clone [https://github.com/DEIN_USERNAME/football-scouting-dashboard.git](https://github.com/EgbersTom/football-scouting-dashboard.git)
   cd football-scouting-dashboard