import sqlite3

conn = sqlite3.connect("english_learning.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("=== Tables in database ===")
tables = cursor.fetchall()
for row in tables:
    print(row[0])

# Check if vocabulary_levels exists
if any(row[0] == 'vocabulary_levels' for row in tables):
    cursor.execute("PRAGMA table_info(vocabulary_levels)")
    print("\n=== vocabulary_levels table structure ===")
    for row in cursor.fetchall():
        print(row)

    cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE phonetic IS NOT NULL AND phonetic != "" LIMIT 5')
    print("\n=== Sample data with phonetics ===")
    for row in cursor.fetchall():
        print(f"word={row[0]}, phonetic={repr(row[1])}, meaning={row[2]}")

    cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE word="drumsticks"')
    print("\n=== drumsticks data ===")
    row = cursor.fetchone()
    if row:
        print(f"word={row[0]}, phonetic={repr(row[1])}, meaning={row[2]}")
    else:
        print("drumsticks not in vocabulary_levels table")

    cursor.execute('SELECT COUNT(*) FROM vocabulary_levels')
    print(f"\nTotal words: {cursor.fetchone()[0]}")

    cursor.execute('SELECT COUNT(*) FROM vocabulary_levels WHERE phonetic IS NOT NULL AND phonetic != ""')
    print(f"Words with phonetic: {cursor.fetchone()[0]}")

    cursor.execute('SELECT COUNT(*) FROM vocabulary_levels WHERE meaning IS NOT NULL AND meaning != ""')
    print(f"Words with meaning: {cursor.fetchone()[0]}")
else:
    print("\nvocabulary_levels table does not exist!")

conn.close()
