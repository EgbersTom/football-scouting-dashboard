import sqlalchemy
import pymysql

# Leeres Passwort:
password = "Start123!"

connection_string = f"mysql+pymysql://root:{password}@localhost:3306/football_scouting"
engine = sqlalchemy.create_engine(connection_string)

try:
    with engine.connect() as connection:
        print("🚀 Volltreffer: Python ist erfolgreich mit deiner MySQL-Datenbank verbunden!")
except Exception as e:
    print(f"❌ Verbindungsfehler: {e}")