import sqlite3

conn = sqlite3.connect("./backend/data/english_learner.db")
cursor = conn.cursor()

cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE word="specific"')
row = cursor.fetchone()
if row:
    word, phonetic, meaning = row
    with open("check_specific_detail.txt", "w", encoding="utf-8") as f:
        f.write(f"word={word}\n")
        f.write(f"phonetic={repr(phonetic)}\n")
        f.write(f"meaning={repr(meaning)}\n")
        if meaning:
            f.write("meaning characters:\n")
            for i, c in enumerate(meaning):
                f.write(f"  char[{i}]={repr(c)} u={ord(c):04x}\n")
            f.write(f"meaning bytes={meaning.encode('utf-8')}\n")
        f.write(f"phonetic bytes={phonetic.encode('utf-8') if phonetic else None}\n")

conn.close()
print("done")
