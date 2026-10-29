from statsbombpy import sb
import pandas as pd
from sqlalchemy import create_engine

# Datenbankverbindung
engine = create_engine("mysql+pymysql://root:Start123!@localhost:3306/football_scouting")

print("1. Lade Spielplan für Bundesliga 2023/24...")
matches = sb.matches(competition_id=9, season_id=281)

# Tabelle 'matches' in MySQL aktualisieren
matches_clean = matches[[
    'match_id', 'match_date', 'match_week', 
    'home_team', 'away_team', 'home_score', 'away_score'
]].copy()
matches_clean.to_sql('matches', con=engine, if_exists='replace', index=False)

print(f"{len(matches)} Spiele gefunden. Starte Event-Download...")

# 2. Schleife über alle Partien
first_match = True

for idx, match_id in enumerate(matches['match_id'], start=1):
    try:
        events = sb.events(match_id=match_id)
        
        # Koordinaten aufteilen
        events['location_x'] = events['location'].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
        events['location_y'] = events['location'].apply(lambda loc: loc[1] if isinstance(loc, list) else None)
        events['match_id'] = match_id
        
        # Relevante Spalten filtern
        scouting_columns = [
            'id', 'match_id', 'minute', 'second', 'team', 'player', 'position', 
            'type', 'location_x', 'location_y', 'duration', 'under_pressure', 
            'pass_outcome', 'pass_recipient', 'shot_statsbomb_xg', 'shot_outcome'
        ]
        
        events_clean = events[[c for c in scouting_columns if c in events.columns]].copy()
        
        # Beim ersten Spiel Tabelle ersetzen, danach anhängen ('append')
        if first_match:
            events_clean.to_sql('events', con=engine, if_exists='replace', index=False)
            first_match = False
        else:
            events_clean.to_sql('events', con=engine, if_exists='append', index=False)
            
        print(f"[{idx}/{len(matches)}] Match ID {match_id} erfolgreich importiert.")
        
    except Exception as e:
        print(f"Fehler bei Match ID {match_id}: {e}")

print("✅ Saison-Upload erfolgreich abgeschlossen!")