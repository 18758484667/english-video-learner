import React, { useState } from 'react'
import { useAppStore } from '../store/useStore'
import axios from 'axios'
import nlp from 'compromise'

interface SubtitleWord {
  word: string
  level: string
  is_beyond: boolean
  meaning: string | null
  phonetic: string | null
}

interface ThreeLayerSubtitleProps {
  subtitle: {
    english: string
    chinese_translation: string
    words: SubtitleWord[]
  }
  isActive: boolean
  currentTime?: number
}

const API_BASE_URL = 'https://dull-zoos-melt.loca.lt/api'

// 词形还原：将时态变化还原为原形
const normalizeWord = (word: string): string => {
  const doc = nlp(word)
  let result: string = word

  if (doc.has('#Verb')) {
    result = doc.verbs().toInfinitive().text()
  } else if (doc.has('#Noun')) {
    result = doc.nouns().toSingular().text()
  }

  // 如果词形还原失败，返回原词
  return result || word
}

const ThreeLayerSubtitle: React.FC<ThreeLayerSubtitleProps> = ({
  subtitle,
  isActive,
  currentTime
}) => {
  const { showWordAnnotations, showChineseTranslation, user, addVocabularyItem } = useAppStore()
  const [toast, setToast] = useState<string | null>(null)
  const [addedWords, setAddedWords] = useState<Set<string>>(new Set())

  // 获取单词颜色 - 所有级别都有颜色
  const getWordColor = (level: string) => {
    switch (level) {
      case 'A1': return 'text-gray-400'
      case 'A2': return 'text-green-400'
      case 'B1': return 'text-yellow-400'
      case 'B2': return 'text-orange-400'
      case 'C1': return 'text-red-400'
      case 'C2': return 'text-red-600'
      default: return 'text-white'
    }
  }

  // 获取标注颜色（仅用于注释）
  const getAnnotationColor = (level: string) => {
    if (level === 'C1' || level === 'C2') {
      return 'text-red-500'
    } else if (level === 'B1' || level === 'B2') {
      return 'text-yellow-400'
    }
    return 'text-white'
  }

  // 添加生词到生词本（自动词形还原为原形）
  const handleAddToVocabulary = async (word: SubtitleWord) => {
    if (!user) {
      setToast('请先登录')
      setTimeout(() => setToast(null), 2000)
      return
    }

    // 词形还原：去掉时态变化
    const normalizedWord = normalizeWord(word.word)

    if (addedWords.has(normalizedWord)) {
      setToast('已添加到生词本')
      setTimeout(() => setToast(null), 2000)
      return
    }

    try {
      // 直接调用后端添加，由后端自动获取释义和音标
      const response = await axios.post(`${API_BASE_URL}/vocabulary/items/`, {
        user_id: user.id,
        word: normalizedWord,
        example_sentence: subtitle.english,
        source_video: '',
        source_timestamp: currentTime || 0
      })

      addVocabularyItem(response.data)
      setAddedWords(prev => new Set(prev).add(normalizedWord))

      const displayMsg = normalizedWord !== word.word
        ? `已添加 "${word.word}" → "${normalizedWord}" 到生词本`
        : `已添加 "${normalizedWord}" 到生词本`
      setToast(displayMsg)
      setTimeout(() => setToast(null), 3000)
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 400) {
        setToast(`"${normalizedWord}" 已在生词本中`)
      } else {
        setToast('添加失败')
      }
      setTimeout(() => setToast(null), 2000)
    }
  }

  return (
    <div className={`subtitle-container ${isActive ? 'active' : ''} relative`}>
      {/* Toast 提示 */}
      {toast && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-4 py-2 bg-green-600 text-white rounded-lg shadow-lg text-sm">
          {toast}
        </div>
      )}

      {/* 组合层：每个词的注释+英文垂直排列 */}
      <div className="words-layer flex flex-wrap gap-1 justify-center items-end">
        {subtitle.words.map((word, index) => (
          <div key={index} className="flex flex-col items-center min-h-[40px]">
            {/* 注释（顶部） */}
            {showWordAnnotations && word.is_beyond && word.meaning ? (
              <span
                className={`text-sm font-bold ${getAnnotationColor(word.level)} whitespace-nowrap cursor-pointer hover:underline leading-none mb-0.5`}
                onClick={() => handleAddToVocabulary(word)}
                title={`点击添加 "${word.word}" 到生词本`}
              >
                {word.meaning}
              </span>
            ) : (
              <span className="h-3"></span>
            )}
            {/* 英文单词（底部） */}
            <span
              className={`text-base font-medium cursor-pointer transition-colors hover:text-blue-400 ${getWordColor(word.level)} ${addedWords.has(word.word) ? 'border-b-2 border-green-400' : ''}`}
              onClick={() => handleAddToVocabulary(word)}
              title={`${word.word}${word.phonetic ? ` ${word.phonetic}` : ''}${word.meaning ? ` - ${word.meaning}` : ''}${addedWords.has(word.word) ? ' (已添加)' : ' - 点击添加到生词本'}`}
            >
              {word.word}
            </span>
          </div>
        ))}
      </div>

      {/* 第三层：整句中文翻译（底部，小字） */}
      {showChineseTranslation && subtitle.chinese_translation && (
        <div className="translation-layer mt-1">
          <p className="text-base text-gray-400 text-center">
            {subtitle.chinese_translation}
          </p>
        </div>
      )}
    </div>
  )
}

export default ThreeLayerSubtitle
