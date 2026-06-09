import sqlite3
import os

conn = sqlite3.connect("./backend/data/english_learner.db")
cursor = conn.cursor()

cursor.execute("SELECT id, video_path, status FROM video_processes LIMIT 5")
rows = cursor.fetchall()

with open("video_check.txt", "w", encoding="utf-8") as f:
    f.write(f"Total video processes: {len(rows)}\n\n")
    for row in rows:
        vid, path, status = row
        f.write(f"ID: {vid}\n")
        f.write(f"  Path: {path}\n")
        f.write(f"  Status: {status}\n")
        f.write(f"  Exists: {os.path.exists(path) if path else 'N/A'}\n\n")

conn.close()
print("done")
