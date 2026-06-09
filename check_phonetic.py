import sqlite3
import os

db_path = "./backend/data/english_learner.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 先获取表结构
print("=== vocabulary_levels 表结构 ===")
cursor.execute("PRAGMA table_info(vocabulary_levels)")
for row in cursor.fetchall():
    print(row)

# 查看有音标的数据（写入文件避免编码问题）
with open("db_phonetic_check.txt", "w", encoding="utf-8") as f:
    cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE phonetic IS NOT NULL AND phonetic != "" LIMIT 10')
    f.write("=== 有音标的数据示例 ===\n")
    for row in cursor.fetchall():
        f.write(f"word={row[0]}, phonetic={repr(row[1])}, meaning={row[2]}\n")

    # 查看 drumsticks
    cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE word="drumsticks"')
    f.write("\n=== drumsticks 数据 ===\n")
    row = cursor.fetchone()
    if row:
        f.write(f"word={row[0]}, phonetic={repr(row[1])}, meaning={row[2]}\n")
    else:
        f.write("drumsticks 不在 vocabulary_levels 表中\n")

    # 统计数据
    cursor.execute('SELECT COUNT(*) FROM vocabulary_levels')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM vocabulary_levels WHERE phonetic IS NOT NULL AND phonetic != ""')
    with_phonetic = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM vocabulary_levels WHERE meaning IS NOT NULL AND meaning != ""')
    with_meaning = cursor.fetchone()[0]

    f.write(f"\n总词数: {total}\n")
    f.write(f"有音标的词数: {with_phonetic}\n")
    f.write(f"有释义的词数: {with_meaning}\n")

    # 查看几个有音标的词的原始字节
    cursor.execute('SELECT word, phonetic FROM vocabulary_levels WHERE phonetic IS NOT NULL AND phonetic != "" LIMIT 3')
    f.write("\n=== 音标原始字节 ===\n")
    for row in cursor.fetchall():
        word = row[0]
        phonetic = row[1]
        f.write(f"word={word}, phonetic={phonetic}, bytes={phonetic.encode('utf-8')}\n")

conn.close()

print("结果已写入 db_phonetic_check.txt")
