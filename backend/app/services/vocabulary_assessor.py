from typing import List, Dict, Optional
from ..database import SessionLocal
from ..models import VocabularyLevel
import re


# 缓存未知词汇的翻译结果
_unknown_word_cache = {}

# 常见缩写的拆解映射
CONTRACTION_SPLIT = {
    "n't": ('not',),
    "'m": ('am',),
    "'re": ('are',),
    "'ll": ('will',),
    "'ve": ('have',),
    "'d": ('would', 'had'),
    "'s": ('is', 'has', 'us'),
}

def clear_unknown_word_cache():
    """清除未知词汇翻译缓存（在翻译服务更新后调用）"""
    _unknown_word_cache.clear()

# 应用启动时自动清除缓存（确保使用最新的翻译服务）


class VocabularyAssessor:
    """词汇难度评估服务"""

    def __init__(self):
        self.level_order = {
            'A1': 1, 'A2': 2, 'B1': 3,
            'B2': 4, 'C1': 5, 'C2': 6
        }

    def _get_word_level(self, word: str, db) -> Optional[tuple]:
        """查询单词的CEFR级别，返回 VocabularyLevel 对象或 None"""
        search_word = word.lower().strip()
        if not search_word:
            return None
        
        # 直接查询
        vocab = db.query(VocabularyLevel).filter(
            VocabularyLevel.word == search_word
        ).first()
        if vocab:
            return vocab
        
        # 复数形式 fallback（简单规则）
        # 1. 以 -es 结尾（如 chefs -> chef, knives -> knive）
        if search_word.endswith('es'):
            singular = search_word[:-2]
            if singular:
                vocab = db.query(VocabularyLevel).filter(
                    VocabularyLevel.word == singular
                ).first()
                if vocab:
                    return vocab
            # 处理 -ies -> -y（如 cities -> city）
            if search_word.endswith('ies'):
                singular = search_word[:-3] + 'y'
                vocab = db.query(VocabularyLevel).filter(
                    VocabularyLevel.word == singular
                ).first()
                if vocab:
                    return vocab
        
        # 2. 以 -s 结尾（如 artists -> artist）
        if search_word.endswith('s') and not search_word.endswith('ss'):
            singular = search_word[:-1]
            if singular:
                vocab = db.query(VocabularyLevel).filter(
                    VocabularyLevel.word == singular
                ).first()
                if vocab:
                    return vocab
        
        return None

    def _assess_contraction(self, word: str, user_level: str, db) -> Optional[Dict]:
        """评估缩写形式，拆解成基础词取最高级别"""
        word_lower = word.lower()
        
        # 先检查数据库中是否已有该缩写的完整记录（如 let's）
        vocab_direct = self._get_word_level(word_lower, db)
        if vocab_direct:
            word_level = vocab_direct.level
            is_beyond = self.level_order.get(word_level, 6) > self.level_order.get(user_level, 1)
            return {
                "word": word,
                "level": word_level,
                "is_beyond": is_beyond,
                "meaning": vocab_direct.meaning if is_beyond else None,
                "phonetic": vocab_direct.phonetic,
                "example": vocab_direct.example
            }
        
        # 检查是否包含已知的缩写后缀
        for suffix, base_words in CONTRACTION_SPLIT.items():
            if word_lower.endswith(suffix):
                # 去掉后缀得到前缀
                prefix = word_lower[:-len(suffix)]
                all_words = [prefix] + list(base_words)
                
                # 查询所有部分的级别
                max_level_num = 0
                best_level = 'unknown'
                for w in all_words:
                    vocab = self._get_word_level(w, db)
                    if vocab:
                        level_num = self.level_order.get(vocab.level, 0)
                        if level_num > max_level_num:
                            max_level_num = level_num
                            best_level = vocab.level
                
                if max_level_num > 0:
                    is_beyond = max_level_num > self.level_order.get(user_level, 1)
                    # 查找音标（优先使用完整缩写，否则用前缀）
                    phonetic = vocab_direct.phonetic if vocab_direct else None
                    
                    return {
                        "word": word,
                        "level": best_level,
                        "is_beyond": is_beyond,
                        "meaning": None,  # 缩写不单独显示含义
                        "phonetic": phonetic,
                        "example": None
                    }
        
        return None

    def assess_word(self, word: str, user_level: str, db=None) -> Dict:
        """
        评估单个单词的难度
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            # 先尝试拆解缩写（如 don't = do + not）
            if "'" in word:
                contraction_result = self._assess_contraction(word, user_level, db)
                if contraction_result:
                    return contraction_result
            
            # 查询CEFR词库
            vocab = self._get_word_level(word, db)
            
            # fallback：去掉撇号查询（如 I've -> Ive）
            if not vocab and "'" in word:
                no_apostrophe = word.lower().replace("'", "").strip()
                if no_apostrophe:
                    vocab = db.query(VocabularyLevel).filter(
                        VocabularyLevel.word == no_apostrophe
                    ).first()
            
            if vocab:
                word_level = vocab.level
                is_beyond = self.level_order.get(word_level, 6) > self.level_order.get(user_level, 1)

                # 生词缺少含义时，实时翻译并保存
                meaning = vocab.meaning
                # 如果 meaning 为空或是 mock 翻译（以 [翻译] 开头），则重新翻译
                if is_beyond and (not meaning or meaning.startswith("[翻译]")):
                    try:
                        from .translator import translator
                        meaning = translator.translate_text(word, "en", "zh")
                        if meaning and meaning != word and not meaning.startswith("[翻译]"):
                            vocab.meaning = meaning
                            db.commit()
                    except Exception:
                        pass  # 翻译失败不影响评估

                return {
                    "word": word,
                    "level": word_level,
                    "is_beyond": is_beyond,
                    "meaning": meaning if is_beyond else None,
                    "phonetic": vocab.phonetic,
                    "example": vocab.example
                }
            
            # 不在数据库中的词，自动翻译并标记为生词
            meaning = None
            try:
                from .translator import translator
                meaning = translator.translate_text(word, "en", "zh")
                if meaning == word or meaning.startswith("["):
                    meaning = None
            except Exception:
                pass

            return {
                "word": word,
                "level": "unknown",
                "is_beyond": True,
                "meaning": meaning,
                "phonetic": None,
                "example": None
            }
        finally:
            if should_close:
                db.close()

    def assess_sentence(self, sentence: str, user_level: str, db=None) -> Dict:
        """
        评估句子中每个单词的难度
        """
        import re

        # 提取单词，保留缩写形式（如 I've, don't, it's）和数字
        words = re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b|\b\d+(?:\.\d+)?\b", sentence)

        assessed_words = []
        for word in words:
            assessment = self.assess_word(word, user_level, db=db)
            assessed_words.append(assessment)

        return {
            "sentence": sentence,
            "words": assessed_words,
            "total_words": len(words),
            "unknown_words": sum(1 for w in assessed_words if w["is_beyond"])
        }

    def assess_subtitles(self, subtitles: List[Dict], user_level: str) -> List[Dict]:
        """
        批量评估字幕中的单词难度

        Args:
            subtitles: 字幕列表，每个字幕包含english文本
            user_level: 用户的CEFR等级

        Returns:
            标注了单词难度的字幕列表
        """
        assessed_subtitles = []
        db = SessionLocal()
        try:
            for subtitle in subtitles:
                english_text = subtitle.get("english", "")
                chinese_translation = subtitle.get("chinese_translation", "")

                # 评估句子（复用数据库连接）
                assessment = self.assess_sentence(english_text, user_level, db=db)

                # 构建标注后的字幕
                assessed_subtitle = {
                    "id": subtitle.get("id"),
                    "start": subtitle.get("start"),
                    "end": subtitle.get("end"),
                    "english": english_text,
                    "chinese_translation": chinese_translation,
                    "words": assessment["words"]
                }

                assessed_subtitles.append(assessed_subtitle)
        finally:
            db.close()

        return assessed_subtitles


# 创建全局实例
assessor = VocabularyAssessor()
