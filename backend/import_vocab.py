import sqlite3
import openpyxl
import os

def import_vocabulary():
    db_path = 'data/english_learner.db'
    xlsx_path = 'English Vocabulary Profile Online.xlsx'

    print(f"Loading Excel file: {xlsx_path}")
    wb = openpyxl.load_workbook(xlsx_path)
    sheet = wb['total(15696)']

    # 读取所有词汇，按词取最高级别
    word_levels = {}  # word -> highest_level
    level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}

    for row in sheet.iter_rows(min_row=2, values_only=True):
        word = row[0]
        level = row[2]
        if not word or not level:
            continue

        word = word.lower().strip()
        if not word:
            continue

        # 取最低级别（基础用法）
        if word not in word_levels:
            word_levels[word] = level
        else:
            current_level = word_levels[word]
            if level_order.get(level, 6) < level_order.get(current_level, 6):
                word_levels[word] = level

    print(f"Total unique words: {len(word_levels)}")
    print(f"Level distribution:")
    for lvl in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        count = sum(1 for v in word_levels.values() if v == lvl)
        print(f"  {lvl}: {count}")

    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 清空现有词汇表
    print("\nClearing existing vocabulary_levels table...")
    cursor.execute("DELETE FROM vocabulary_levels")
    conn.commit()

    # 批量插入新数据
    print("Importing new vocabulary data...")
    data_to_insert = []
    for word, level in word_levels.items():
        data_to_insert.append((word, level, None, None, None))

    # 分批插入以提高性能
    batch_size = 1000
    for i in range(0, len(data_to_insert), batch_size):
        batch = data_to_insert[i:i+batch_size]
        cursor.executemany(
            "INSERT INTO vocabulary_levels (word, level, meaning, phonetic, example) VALUES (?, ?, ?, ?, ?)",
            batch
        )
        conn.commit()
        print(f"  Inserted {min(i+batch_size, len(data_to_insert))} / {len(data_to_insert)} words...")

    # 验证
    cursor.execute("SELECT COUNT(*) FROM vocabulary_levels")
    count = cursor.fetchone()[0]
    print(f"\nImport complete! Total words in database: {count}")

    conn.close()
    print("Done!")

if __name__ == "__main__":
    import_vocabulary()
