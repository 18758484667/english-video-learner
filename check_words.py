import sqlite3

conn = sqlite3.connect("./backend/data/english_learner.db")
cursor = conn.cursor()

# 检查几个常见的词的音标和释义
cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE word IN ("specific", "analysis", "hello", "world")')
with open("check_words.txt", "w", encoding="utf-8") as f:
    for row in cursor.fetchall():
        word, phonetic, meaning = row
        f.write(f"word={word}\n")
        f.write(f"  phonetic={repr(phonetic)}\n")
        f.write(f"  meaning={repr(meaning)}\n\n")

conn.close()
print("结果写入 check_words.txt")
