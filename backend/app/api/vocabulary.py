from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import random

from ..database import get_db
from ..models import VocabularyItem, VocabularyLevel

router = APIRouter()

# Pydantic模型
class VocabularyItemCreate(BaseModel):
    user_id: str
    word: str
    meaning: Optional[str] = None
    phonetic: Optional[str] = None
    example_sentence: Optional[str] = None
    source_video: Optional[str] = None
    source_timestamp: Optional[float] = None

class VocabularyItemResponse(BaseModel):
    id: int
    user_id: str
    word: str
    meaning: Optional[str]
    phonetic: Optional[str]
    example_sentence: Optional[str]
    source_video: Optional[str]
    source_timestamp: Optional[float]
    cefr_level: Optional[str]
    review_count: int
    added_at: datetime

    class Config:
        from_attributes = True

@router.post("/items/", response_model=VocabularyItemResponse)
def add_vocabulary_item(item: VocabularyItemCreate, db: Session = Depends(get_db)):
    """添加生词到生词本"""
    # 检查是否已存在
    existing = db.query(VocabularyItem).filter(
        VocabularyItem.user_id == item.user_id,
        VocabularyItem.word == item.word
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Word already in vocabulary list")

    # 从词汇等级表获取CEFR级别
    search_word = item.word.lower().strip()
    vocab_level = db.query(VocabularyLevel).filter(
        VocabularyLevel.word == search_word
    ).first()

    # 复数形式 fallback
    if not vocab_level and search_word.endswith('es'):
        singular = search_word[:-2]
        if singular:
            vocab_level = db.query(VocabularyLevel).filter(
                VocabularyLevel.word == singular
            ).first()
        if not vocab_level and search_word.endswith('ies'):
            singular = search_word[:-3] + 'y'
            vocab_level = db.query(VocabularyLevel).filter(
                VocabularyLevel.word == singular
            ).first()
    if not vocab_level and search_word.endswith('s') and not search_word.endswith('ss'):
        singular = search_word[:-1]
        if singular:
            vocab_level = db.query(VocabularyLevel).filter(
                VocabularyLevel.word == singular
            ).first()

    cefr_level = vocab_level.level if vocab_level else None
    meaning = item.meaning or (vocab_level.meaning if vocab_level else None)
    phonetic = item.phonetic or (vocab_level.phonetic if vocab_level else None)
    example = item.example_sentence or (vocab_level.example if vocab_level else None)

    # 尝试从词典API获取音标和英文释义
    dictionary_definitions = []
    if not phonetic or not meaning:
        try:
            from ..services.translator import translator
            word_info = translator.get_word_info(item.word)
            if word_info:
                # 获取音标
                if not phonetic and word_info.get("phonetic"):
                    phonetic = word_info["phonetic"]
                # 获取英文释义
                if word_info.get("definitions"):
                    dictionary_definitions = word_info["definitions"]
                    # 使用第一个释义作为例句
                    if not example and len(word_info["definitions"]) > 0:
                        example = word_info["definitions"][0]
        except Exception as e:
            import traceback
            print(f"[Vocabulary] Dictionary API failed for '{item.word}': {e}")
            print(f"[Vocabulary] Trace: {traceback.format_exc()}")

    # 如果没有释义，自动调用翻译API
    if not meaning:
        try:
            from ..services.translator import translator
            # 优先使用词典API的释义，根据上下文选择最相关的
            if dictionary_definitions:
                selected_def = None
                
                # 如果有例句，选择最相关的释义
                if item.example_sentence and len(dictionary_definitions) > 1:
                    # 提取例句中的关键词（小写、去标点的简单分词）
                    import re
                    example_lower = item.example_sentence.lower()
                    example_words = set(re.findall(r'\b[a-z]+\b', example_lower))
                    
                    best_match = None
                    best_score = -1
                    for def_text in dictionary_definitions:
                        # 去掉词性前缀，提取纯释义
                        clean_def = def_text
                        if ") " in clean_def:
                            clean_def = clean_def.split(") ", 1)[1]
                        
                        # 计算释义与例句的关键词匹配度
                        def_words = set(re.findall(r'\b[a-z]+\b', clean_def.lower()))
                        common = example_words & def_words
                        score = len(common)
                        
                        if score > best_score:
                            best_score = score
                            best_match = def_text
                    
                    selected_def = best_match
                
                # 如果没有例句或匹配失败，使用第一个释义
                if not selected_def:
                    selected_def = dictionary_definitions[0]
                
                # 提取纯英文释义（去掉词性前缀）
                english_def = selected_def
                if ") " in english_def:
                    english_def = english_def.split(") ", 1)[1]
                meaning = translator.translate_text(english_def, "en", "zh")
                if not meaning or meaning.startswith("["):
                    # 如果翻译释义失败，翻译单词本身
                    meaning = translator.translate_text(item.word, "en", "zh")
            else:
                # 没有词典释义，直接翻译单词
                meaning = translator.translate_text(item.word, "en", "zh")

            if meaning and meaning != item.word and not meaning.startswith("[翻译]"):
                # 更新数据库中的释义（如果单词在数据库中）
                if vocab_level and not vocab_level.meaning:
                    vocab_level.meaning = meaning
                    db.commit()
            else:
                meaning = None
        except Exception as e:
            import traceback
            print(f"[Vocabulary] Translation failed for '{item.word}': {e}")
            print(f"[Vocabulary] Trace: {traceback.format_exc()}")
            meaning = None

    db_item = VocabularyItem(
        user_id=item.user_id,
        word=item.word,
        meaning=meaning,
        phonetic=phonetic,
        example_sentence=example,
        source_video=item.source_video,
        source_timestamp=item.source_timestamp,
        cefr_level=cefr_level
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@router.get("/items/{user_id}", response_model=List[VocabularyItemResponse])
def get_vocabulary_items(
    user_id: str,
    level: Optional[str] = None,
    sort_by: Optional[str] = "added_at",
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取用户的生词本，支持筛选、搜索和排序"""
    query = db.query(VocabularyItem).filter(VocabularyItem.user_id == user_id)

    # 按等级筛选
    if level:
        query = query.filter(VocabularyItem.cefr_level == level.upper())

    # 搜索（单词或释义）
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (VocabularyItem.word.ilike(search_term)) |
            (VocabularyItem.meaning.ilike(search_term))
        )

    # 排序
    if sort_by == "added_at":
        query = query.order_by(VocabularyItem.added_at.desc())
    elif sort_by == "word":
        query = query.order_by(VocabularyItem.word.asc())
    elif sort_by == "review_count":
        query = query.order_by(VocabularyItem.review_count.desc())
    elif sort_by == "level":
        query = query.order_by(VocabularyItem.cefr_level.asc())
    else:
        query = query.order_by(VocabularyItem.added_at.desc())

    return query.all()

@router.delete("/items/{item_id}")
def delete_vocabulary_item(item_id: int, db: Session = Depends(get_db)):
    """删除生词"""
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")

    db.delete(item)
    db.commit()

    return {"message": "Vocabulary item deleted successfully"}

@router.post("/items/{item_id}/review")
def mark_reviewed(item_id: int, db: Session = Depends(get_db)):
    """标记单词已复习"""
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")

    item.review_count += 1
    db.commit()

    return {"message": "Review marked successfully", "review_count": item.review_count}

@router.get("/word-info/{word}")
def get_word_info(word: str, db: Session = Depends(get_db)):
    """获取单词的详细信息"""
    vocab = db.query(VocabularyLevel).filter(
        VocabularyLevel.word == word.lower()
    ).first()

    if not vocab:
        return {
            "word": word,
            "level": "unknown",
            "meaning": None,
            "phonetic": None,
            "example": None
        }

    return {
        "word": vocab.word,
        "level": vocab.level,
        "meaning": vocab.meaning,
        "phonetic": vocab.phonetic,
        "example": vocab.example
    }


class VocabularyItemUpdate(BaseModel):
    """更新生词本的请求模型"""
    word: Optional[str] = None
    meaning: Optional[str] = None
    phonetic: Optional[str] = None
    example_sentence: Optional[str] = None


@router.put("/items/{item_id}", response_model=VocabularyItemResponse)
def update_vocabulary_item(item_id: int, item_update: VocabularyItemUpdate, db: Session = Depends(get_db)):
    """编辑生词本中的单词"""
    item = db.query(VocabularyItem).filter(VocabularyItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")

    # 更新字段
    if item_update.word is not None:
        item.word = item_update.word
    if item_update.meaning is not None:
        item.meaning = item_update.meaning
    if item_update.phonetic is not None:
        item.phonetic = item_update.phonetic
    if item_update.example_sentence is not None:
        item.example_sentence = item_update.example_sentence

    db.commit()
    db.refresh(item)

    return item


@router.get("/random/{user_id}", response_model=List[VocabularyItemResponse])
def get_random_vocabulary_items(
    user_id: str,
    count: int = 10,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """随机抽取指定数量的生词用于闪卡学习"""
    query = db.query(VocabularyItem).filter(VocabularyItem.user_id == user_id)

    if level:
        query = query.filter(VocabularyItem.cefr_level == level.upper())

    items = query.all()
    if len(items) <= count:
        return items

    return random.sample(items, count)


@router.get("/stats/{user_id}")
def get_vocabulary_stats(user_id: str, db: Session = Depends(get_db)):
    """获取用户单词本统计信息"""
    total = db.query(VocabularyItem).filter(VocabularyItem.user_id == user_id).count()

    # 按等级统计
    level_stats = {}
    for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        count = db.query(VocabularyItem).filter(
            VocabularyItem.user_id == user_id,
            VocabularyItem.cefr_level == level
        ).count()
        if count > 0:
            level_stats[level] = count

    return {
        "total": total,
        "level_stats": level_stats
    }


@router.get("/test-reload")
def test_reload():
    return {"status": "reloaded v3 with dict api"}


class TranslateRequest(BaseModel):
    text: str
    from_lang: str = "en"
    to_lang: str = "zh"


@router.post("/translate")
def translate_text(request: TranslateRequest):
    """手动翻译文本"""
    try:
        from ..services.translator import translator
        result = translator.translate_text(request.text, request.from_lang, request.to_lang)
        return {"text": request.text, "translation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
