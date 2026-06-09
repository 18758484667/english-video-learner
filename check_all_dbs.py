import sqlite3
import os

db_files = [
    "./backend/app/data/english_learner.db",
    "./backend/data/english_learner.db",
    "./backend/english_learner.db",
    "./backend/english_learning.db",
    "./data/english_learner.db",
]

for db_path in db_files:
    if not os.path.exists(db_path):
        print(f"=== {db_path} === NOT FOUND")
        continue
    print(f"=== {db_path} ===")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables: {tables}")

        if "vocabulary_levels" in tables:
            cursor.execute('SELECT COUNT(*) FROM vocabulary_levels')
            total = cursor.fetchone()[0]
            print(f"  vocabulary_levels rows: {total}")

            cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE phonetic IS NOT NULL AND phonetic != "" LIMIT 3')
            for row in cursor.fetchall():
                print(f"    word={row[0]}, phonetic={repr(row[1])}, meaning={row[2]}")

        conn.close()
    except Exception as e:
        print(f"  Error: {e}")
    print()
