import pandas as pd
from sqlalchemy import create_engine

# Lokale MySQL-Datenbank lesen
mysql_engine = create_engine("mysql+pymysql://root:Start123!@localhost:3306/football_scouting")

# Lokale SQLite-Datei erstellen
sqlite_engine = create_engine("sqlite:///football_scouting.db")

print("Exportiere Daten aus MySQL in die Cloud-Datei...")
pd.read_sql("SELECT * FROM matches", mysql_engine).to_sql('matches', sqlite_engine, if_exists='replace', index=False)
pd.read_sql("SELECT * FROM events", mysql_engine).to_sql('events', sqlite_engine, if_exists='replace', index=False)

print("✅ Erfolgreich 'football_scouting.db' erstellt!")