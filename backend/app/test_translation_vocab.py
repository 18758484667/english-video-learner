#!/usr/bin/env python3
"""
测试脚本：验证翻译和生词释义功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.translator import translator
from app.services.vocabulary_assessor import assessor
from app.database import SessionLocal
from app.models import VocabularyLevel

def test_translation():
    """测试翻译功能"""
    print("=" * 60)
    print("测试 1: 翻译功能 (deep-translator)")
    print("=" * 60)

    test_texts = [
        "Hello world",
        "The quick brown fox jumps over the lazy dog",
        "I want to improve my English skills",
        "This is a significant change in our plan",
        "Knowledge is power",
    ]

    for text in test_texts:
        try:
            result = translator.translate_text(text)
            status = "OK" if not result.startswith("[翻译]") else "FAIL"
            print(f"  [{status}] '{text}'")
            print(f"       → '{result}'")
        except Exception as e:
            print(f"  [ERROR] '{text}' → {e}")
    print()


def test_vocabulary_lookup():
    """测试词汇库查询"""
    print("=" * 60)
    print("测试 2: 词汇库查询")
    print("=" * 60)

    db = SessionLocal()
    try:
        total = db.query(VocabularyLevel).count()
        print(f"  词汇库总词数: {total}")

        # 测试几个常见词
        test_words = ["take", "significant", "environment", "quick", "the"]
        for word in test_words:
            vocab = db.query(VocabularyLevel).filter(VocabularyLevel.word == word).first()
            if vocab:
                print(f"  [OK] '{word}' → level={vocab.level}, meaning={vocab.meaning}")
            else:
                print(f"  [MISSING] '{word}' → 未找到")
    finally:
        db.close()
    print()


def test_vocabulary_assessment():
    """测试生词评估功能"""
    print("=" * 60)
    print("测试 3: 生词评估 (用户级别 A1)")
    print("=" * 60)

    test_sentences = [
        "I want to take a break",
        "This is a significant challenge",
        "The environment needs protection",
    ]

    for sentence in test_sentences:
        try:
            result = assessor.assess_sentence(sentence, "A1")
            print(f"  句子: '{sentence}'")
            print(f"  单词分析:")
            for word_info in result["words"]:
                word = word_info["word"]
                level = word_info["level"]
                is_beyond = word_info["is_beyond"]
                meaning = word_info.get("meaning")
                if is_beyond:
                    print(f"    [{level}] {word} → {meaning or '释义缺失'}")
                else:
                    print(f"    [{level}] {word} → (已掌握)")
        except Exception as e:
            print(f"  [ERROR] '{sentence}' → {e}")
    print()


def test_vocabulary_assessment_a2():
    """测试用户级别 A2 时的生词评估"""
    print("=" * 60)
    print("测试 4: 生词评估 (用户级别 A2)")
    print("=" * 60)

    sentence = "I want to take a significant challenge in the environment"
    try:
        result = assessor.assess_sentence(sentence, "A2")
        print(f"  句子: '{sentence}'")
        print(f"  单词分析:")
        for word_info in result["words"]:
            word = word_info["word"]
            level = word_info["level"]
            is_beyond = word_info["is_beyond"]
            meaning = word_info.get("meaning")
            if is_beyond:
                print(f"    [{level}] {word} → {meaning or '释义缺失'}")
            else:
                print(f"    [{level}] {word} → (已掌握)")
    except Exception as e:
        print(f"  [ERROR] '{sentence}' → {e}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("翻译与生词释义功能测试")
    print("=" * 60 + "\n")

    test_translation()
    test_vocabulary_lookup()
    test_vocabulary_assessment()
    test_vocabulary_assessment_a2()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)
