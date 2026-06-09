import os
import sys
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models import VocabularyLevel
from app.services.translator import translator

session = SessionLocal()

# 获取B2以上且缺少含义的词汇（优先处理高频词）
words = session.query(VocabularyLevel).filter(
    VocabularyLevel.level.in_(['B2', 'C1', 'C2']),
    VocabularyLevel.meaning == None
).order_by(VocabularyLevel.word).all()

print(f"Found {len(words)} B2+ words without meaning")
print("Starting batch translation...")

success = 0
failed = 0

for i, vocab in enumerate(words):
    try:
        # 翻译单词
        meaning = translator.translate_text(vocab.word, "en", "zh")
        if meaning and meaning != vocab.word:
            vocab.meaning = meaning
            success += 1
        else:
            failed += 1
            
        # 每10个词提交一次
        if (i + 1) % 10 == 0:
            session.commit()
            print(f"  Progress: {i+1}/{len(words)} ({success} success, {failed} failed)")
        
        # 避免API限制，适当延迟
        time.sleep(0.3)
        
    except Exception as e:
        failed += 1
        print(f"  Error translating '{vocab.word}': {e}")
        time.sleep(1)

# 提交剩余
session.commit()
print(f"\nDone! {success} translated, {failed} failed")
