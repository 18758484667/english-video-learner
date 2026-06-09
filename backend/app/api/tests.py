from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random

from ..database import get_db
from ..models import TestRecord, VocabularyLevel, User

router = APIRouter()

# Pydantic模型
class TestQuestion(BaseModel):
    word: str
    options: List[str]
    correct_answer: str
    level: str

class TestAnswer(BaseModel):
    question_word: str
    selected_answer: str
    is_correct: bool

class TestStartRequest(BaseModel):
    user_id: str
    test_type: str = "vocabulary"  # vocabulary or adaptive

class TestSubmitRequest(BaseModel):
    user_id: str
    test_type: str
    answers: List[TestAnswer]

class TestResult(BaseModel):
    result_level: str
    estimated_vocab_size: int
    message: str

@router.post("/start/")
def start_test(request: TestStartRequest, db: Session = Depends(get_db)):
    """开始测试，生成测试题目（优化版：15题）"""
    # 题目分布：A1(2), A2(3), B1(4), B2(3), C1(2), C2(1) = 15题
    level_distribution = {'A1': 2, 'A2': 3, 'B1': 4, 'B2': 3, 'C1': 2, 'C2': 1}
    questions = []

    for level, count in level_distribution.items():
        words = db.query(VocabularyLevel).filter(
            VocabularyLevel.level == level
        ).all()

        if len(words) == 0:
            continue

        sampled_words = random.sample(words, min(count, len(words)))

        for word_obj in sampled_words:
            # 生成干扰选项
            other_words = db.query(VocabularyLevel).filter(
                VocabularyLevel.word != word_obj.word
            ).all()

            distractors = random.sample(other_words, min(3, len(other_words)))
            options = [word_obj.meaning] + [d.meaning for d in distractors]
            random.shuffle(options)

            questions.append(TestQuestion(
                word=word_obj.word,
                options=options,
                correct_answer=word_obj.meaning,
                level=level
            ))

    # 打乱题目顺序
    random.shuffle(questions)

    return {
        "questions": questions,
        "total_count": len(questions)
    }

@router.post("/submit/", response_model=TestResult)
def submit_test(request: TestSubmitRequest, db: Session = Depends(get_db)):
    """提交测试答案，计算结果"""
    # 统计各级别的正确率
    level_stats = {}

    for answer in request.answers:
        # 获取单词的CEFR级别
        vocab = db.query(VocabularyLevel).filter(
            VocabularyLevel.word == answer.question_word
        ).first()

        if vocab:
            level = vocab.level
            if level not in level_stats:
                level_stats[level] = {"correct": 0, "total": 0}

            level_stats[level]["total"] += 1
            if answer.is_correct:
                level_stats[level]["correct"] += 1

    # 计算掌握的级别（正确率>=70%）
    level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    vocab_estimates = {
        'A1': 500,
        'A2': 1500,
        'B1': 3000,
        'B2': 5000,
        'C1': 8000,
        'C2': 12000
    }

    mastered_levels = []
    for level, stats in level_stats.items():
        if stats["total"] > 0:
            rate = stats["correct"] / stats["total"]
            if rate >= 0.7:
                mastered_levels.append(level)

    # 确定最终等级
    if mastered_levels:
        result_level = max(mastered_levels, key=lambda x: level_order.index(x))
    else:
        result_level = 'A1'

    estimated_vocab_size = vocab_estimates.get(result_level, 500)

    # 保存测试记录
    user = db.query(User).filter(User.id == request.user_id).first()
    if user:
        user.cefr_level = result_level

        test_record = TestRecord(
            user_id=request.user_id,
            test_type=request.test_type,
            result_level=result_level,
            estimated_vocab_size=estimated_vocab_size,
            answers=str([a.dict() for a in request.answers])
        )

        db.add(test_record)
        db.commit()

    return TestResult(
        result_level=result_level,
        estimated_vocab_size=estimated_vocab_size,
        message=f"Your English level is {result_level}. Estimated vocabulary size: {estimated_vocab_size} words."
    )

@router.get("/history/{user_id}")
def get_test_history(user_id: str, db: Session = Depends(get_db)):
    """获取用户的测试历史"""
    records = db.query(TestRecord).filter(
        TestRecord.user_id == user_id
    ).order_by(TestRecord.taken_at.desc()).all()

    return [
        {
            "id": record.id,
            "test_type": record.test_type,
            "result_level": record.result_level,
            "estimated_vocab_size": record.estimated_vocab_size,
            "taken_at": record.taken_at
        }
        for record in records
    ]
