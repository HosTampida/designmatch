#!/usr/bin/env python3
\"\"\"One-time SQLite to PostgreSQL migration script for DesignMatch.
Run locally: Edit SQLITE_PATH and PG_URL, then python migrate_local_data.py
Assumes tables exist in PG (run app once with PG).
Dumps ALL data - use only if needed. Fresh start recommended for MVP.\"\"\"

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json

SQLITE_PATH = 'designmatch.db'  # Local SQLite
PG_URL = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/designmatch')  # Edit or set env

TABLE_ORDER = [
    'skills', 'styles',  # No FK
    'users', 
    'designers',
    'designer_skills', 'designer_styles',
    'projects', 
    'matches'
]

def migrate():
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    pg_conn = psycopg2.connect(PG_URL, cursor_factory=RealDictCursor)

    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    for table in TABLE_ORDER:
        print(f"Migrating {table}...")
        sqlite_cur.execute(f"SELECT * FROM {table}")
        rows = sqlite_cur.fetchall()

        if rows:
            # Get PG cols for INSERT
            pg_cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
            cols = [row['column_name'] for row in pg_cur.fetchall()]
            col_names = ', '.join(cols)
            placeholders = ', '.join(['%s'] * len(cols))

            for row in rows:
                # Handle JSON cols (projects.skill_ids etc.)
                values = list(row)
                for i, col in enumerate(cols):
                    if col in ['required_skill_ids', 'preferred_style_ids'] and values[i]:
                        values[i] = json.dumps(json.loads(values[i]))  # Ensure str JSON
                pg_cur.execute(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", values)

        pg_conn.commit()
        print(f"  Migrated {len(rows)} rows from {table}")

    sqlite_conn.close()
    pg_conn.close()
    print("Migration complete. Test app with PG.")

if __name__ == '__main__':
    migrate()

