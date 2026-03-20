import os
from dotenv import load_dotenv
import psycopg2

load_dotenv(os.path.join('pipeline', '..', '.env'))
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute('SELECT current_database()')
print('Connected to:', cur.fetchone()[0])

cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
print('Tables:', [r[0] for r in cur.fetchall()])

conn.close()