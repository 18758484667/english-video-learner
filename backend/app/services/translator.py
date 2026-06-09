import os
import hashlib
import random
import requests
import json
import urllib.request
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# 确保环境变量已加载（从当前文件所在路径向上查找 .env）
_base_dir = os.path.dirname(os.path.abspath(__file__))

# 尝试多个可能的 .env 路径
_possible_paths = [
    os.path.join(_base_dir, "..", "..", ".env"),      # backend/.env
    os.path.join(_base_dir, "..", "..", "..", ".env"), # 项目根目录/.env
]
for _p in _possible_paths:
    _p = os.path.normpath(_p)
    if os.path.exists(_p):
        load_dotenv(_p)
        break


class BaiduTranslator:
    """百度翻译API客户端 - 正确编码版本"""

    def __init__(self, appid: str = None, appkey: str = None):
        self._appid = appid
        self._appkey = appkey
        self.api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    @property
    def appid(self):
        if not self._appid:
            self._appid = os.getenv("BAIDU_TRANSLATE_APPID")
        return self._appid

    @property
    def appkey(self):
        if not self._appkey:
            self._appkey = os.getenv("BAIDU_TRANSLATE_SECRET_KEY")
        return self._appkey

    def translate(self, text: str, from_lang: str = "en", to_lang: str = "zh") -> str:
        """翻译文本"""
        # 每次翻译时重新读取环境变量，避免缓存旧值
        appid = os.getenv("BAIDU_TRANSLATE_APPID")
        appkey = os.getenv("BAIDU_TRANSLATE_SECRET_KEY")
        if not appid or not appkey:
            raise ValueError("BAIDU_TRANSLATE_APPID and BAIDU_TRANSLATE_SECRET_KEY must be set")

        # 生成随机数（salt）
        salt = random.randint(32768, 65536)

        # 计算签名
        sign_str = appid + text + str(salt) + appkey
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        # 构建请求参数
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': appid,
            'salt': salt,
            'sign': sign
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            # 使用原始字节正确解码UTF-8，避免requests自动编码检测错误
            result = json.loads(response.content.decode('utf-8'))

            if 'trans_result' in result and result['trans_result']:
                return result['trans_result'][0]['dst']
            else:
                error_msg = result.get('error_msg', 'Unknown error')
                raise Exception(f"Baidu API error: {error_msg}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def translate_batch(self, texts: List[str], from_lang: str = "en", to_lang: str = "zh") -> List[str]:
        """批量翻译（百度API支持）"""
        # 百度翻译API支持通过换行符分隔多个查询
        combined_text = '\n'.join(texts)
        result = self.translate(combined_text, from_lang, to_lang)
        return result.split('\n')


class DictionaryService:
    """Free Dictionary API 服务 - 获取单词音标和英文释义"""

    def __init__(self):
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    def get_word_info(self, word: str) -> Optional[Dict[str, Any]]:
        """
        获取单词信息，包括音标和释义
        返回: {"phonetic": str, "definitions": List[str]} 或 None
        """
        try:
            url = self.api_url.format(word=word.lower().strip())
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if not data or not isinstance(data, list):
                    return None

                entry = data[0]
                result = {
                    "phonetic": None,
                    "definitions": []
                }

                # 提取音标
                if "phonetic" in entry and entry["phonetic"]:
                    result["phonetic"] = entry["phonetic"]
                elif "phonetics" in entry and entry["phonetics"]:
                    for p in entry["phonetics"]:
                        if "text" in p and p["text"]:
                            result["phonetic"] = p["text"]
                            break

                # 提取释义（最多取前3个）
                if "meanings" in entry:
                    for meaning in entry["meanings"]:
                        part_of_speech = meaning.get("partOfSpeech", "")
                        for definition in meaning.get("definitions", [])[:3]:
                            def_text = definition.get("definition", "")
                            if def_text:
                                result["definitions"].append(f"({part_of_speech}) {def_text}")

                # 如果没有获取到任何信息，返回None
                if not result["phonetic"] and not result["definitions"]:
                    return None

                return result

        except Exception as e:
            print(f"[DictionaryService] Failed to get word info for '{word}': {e}")
            return None


class Translator:
    """翻译服务 - 使用百度翻译API + Free Dictionary API"""

    def __init__(self):
        self._translator = None
        self._dictionary = None

    @property
    def translator(self):
        if self._translator is None:
            self._translator = BaiduTranslator()
        return self._translator

    @property
    def dictionary(self):
        if self._dictionary is None:
            self._dictionary = DictionaryService()
        return self._dictionary

    def translate_text(self, text: str, from_lang: str = "en", to_lang: str = "zh") -> str:
        """翻译文本"""
        try:
            return self.translator.translate(text, from_lang, to_lang)
        except Exception as e:
            import traceback
            print(f"[Translator] Translation failed for '{text}': {e}")
            print(f"[Translator] Stack trace: {traceback.format_exc()}")
            print(f"[Translator] Using mock fallback")
            return self._mock_translate(text)

    def get_word_info(self, word: str) -> Optional[Dict[str, Any]]:
        """
        获取单词的音标和释义（英文）
        返回: {"phonetic": str, "definitions": List[str]} 或 None
        """
        return self.dictionary.get_word_info(word)

    def translate_subtitles(self, subtitles: List[str]) -> List[str]:
        """批量翻译字幕"""
        translations = []
        for subtitle in subtitles:
            translation = self.translate_text(subtitle)
            translations.append(translation)
        return translations

    def _mock_translate(self, text: str) -> str:
        """模拟翻译（用于测试）"""
        mock_translations = {
            "The quick brown fox jumps over the lazy dog": "那只敏捷的棕色狐狸跳过了懒惰的狗",
            "This is a sample transcription for testing purposes": "这是一个用于测试目的的示例转录",
            "Hello world": "你好世界",
            "How are you?": "你好吗？",
            "Good morning": "早上好",
            "Thank you": "谢谢你",
            "You're welcome": "不客气",
        }
        return mock_translations.get(text, f"[翻译] {text}")


# 创建全局实例
translator = Translator()
