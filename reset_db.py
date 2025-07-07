# reset_db.py
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("DATABASE_URL non défini dans les variables d'environnement")

# Important: Enlève les \n éventuels
DATABASE_URL = DATABASE_URL.strip()

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

with conn.cursor() as cur:
    print("⚠️  Suppression du schéma public...")
    cur.execute("DROP SCHEMA public CASCADE;")
    print("✅ Schéma supprimé.")

    print("✅ Création d'un schéma public vide...")
    cur.execute("CREATE SCHEMA public;")
    print("🎉 Base de données réinitialisée.")

conn.close()
