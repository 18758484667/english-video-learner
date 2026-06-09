import sqlite3
import json

conn = sqlite3.connect("./backend/data/english_learner.db")
cursor = conn.cursor()

with open("check_specific_result.txt", "w", encoding="utf-8") as f:
    # 查看 specific 这个词的数据
    cursor.execute('SELECT word, phonetic, meaning FROM vocabulary_levels WHERE word="specific"')
    row = cursor.fetchone()
    if row:
        word, phonetic, meaning = row
        f.write(f"word={word}\n")
        f.write(f"phonetic={repr(phonetic)}\n")
        f.write(f"phonetic bytes={phonetic.encode('utf-8') if phonetic else None}\n")
        f.write(f"meaning={repr(meaning)}\n")
        f.write(f"meaning bytes={meaning.encode('utf-8') if meaning else None}\n")

        # 模拟API返回的JSON
        data = {
            "word": word,
            "phonetic": phonetic,
            "meaning": meaning,
        }
        f.write(f"\nJSON ensure_ascii=False: {json.dumps(data, ensure_ascii=False)}\n")
        f.write(f"JSON ensure_ascii=True: {json.dumps(data, ensure_ascii=True)}\n")
    else:
        f.write("specific not found\n")

conn.close()
print("结果写入 check_specific_result.txt")
