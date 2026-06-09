import sys
import os

# 设置正确的路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.vocabulary_assessor import assessor

print("=" * 60)
print("测试: 生词评估功能")
print("=" * 60)

sentences = [
    "I want to take a break",
    "This is a significant challenge",
    "The environment needs protection",
]

for sentence in sentences:
    print(f"\n句子: '{sentence}'")
    result = assessor.assess_sentence(sentence, "A1")
    print("单词分析:")
    for w in result["words"]:
        if w["is_beyond"]:
            print(f"  [{w['level']}] {w['word']} → {w.get('meaning') or '释义缺失'}")
        else:
            print(f"  [{w['level']}] {w['word']} → (已掌握)")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
