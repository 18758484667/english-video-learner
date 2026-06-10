import React, { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { useAppStore } from '../store/useStore'
import { API_BASE_URL } from '../config'

interface VocabularyItem {
  id: number
  user_id: string
  word: string
  meaning: string | null
  phonetic: string | null
  example_sentence: string | null
  cefr_level: string | null
  review_count: number
  added_at: string
}

interface CardResult {
  itemId: number
  status: 'mastered' | 'review'
}


const FlashCard: React.FC = () => {
  const { user } = useAppStore()

  const [items, setItems] = useState<VocabularyItem[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [results, setResults] = useState<CardResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isFinished, setIsFinished] = useState(false)
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [cardCount, setCardCount] = useState(10)
  const [showSettings, setShowSettings] = useState(true)

  // 加载闪卡单词
  const loadFlashCards = async () => {
    if (!user) return
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('count', String(cardCount))
      if (filterLevel !== 'all') {
        params.append('level', filterLevel)
      }
      const response = await axios.get(
        `${API_BASE_URL}/vocabulary/random/${user.id}?${params.toString()}`
      )
      setItems(response.data)
      setCurrentIndex(0)
      setIsFlipped(false)
      setResults([])
      setIsFinished(false)
      setShowSettings(false)
    } catch (error) {
      console.error('Failed to load flash cards:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // 键盘事件处理
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (isFinished) return
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault()
      setIsFlipped(prev => !prev)
    } else if (e.key === 'ArrowRight' || e.key === '1') {
      handleMark('mastered')
    } else if (e.key === 'ArrowLeft' || e.key === '2') {
      handleMark('review')
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      prevCard()
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      nextCard()
    }
  }, [isFinished, currentIndex, isFlipped, items, results])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  const nextCard = () => {
    if (currentIndex < items.length - 1) {
      setIsFlipped(false)
      setTimeout(() => setCurrentIndex(prev => prev + 1), 150)
    }
  }

  const prevCard = () => {
    if (currentIndex > 0) {
      setIsFlipped(false)
      setTimeout(() => setCurrentIndex(prev => prev - 1), 150)
    }
  }

  const handleMark = (status: 'mastered' | 'review') => {
    const currentItem = items[currentIndex]
    if (!currentItem) return

    // 更新结果
    setResults(prev => {
      const filtered = prev.filter(r => r.itemId !== currentItem.id)
      return [...filtered, { itemId: currentItem.id, status }]
    })

    // 自动下一页
    if (currentIndex < items.length - 1) {
      nextCard()
    } else {
      setIsFinished(true)
    }
  }

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
  }

  const restart = () => {
    setShowSettings(true)
    setIsFinished(false)
    setItems([])
    setResults([])
    setCurrentIndex(0)
    setIsFlipped(false)
  }

  if (!user) {
    return (
      <div className="p-8 bg-gray-800 rounded-lg text-center">
        <p className="text-gray-400">Please login to use flash cards</p>
      </div>
    )
  }

  // 设置界面
  if (showSettings) {
    return (
      <div className="p-6 bg-gray-800 rounded-lg max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Flash Card Study</h2>

        <div className="space-y-6">
          {/* 等级筛选 */}
          <div>
            <label className="block text-gray-300 mb-2">Filter by CEFR Level</label>
            <div className="flex flex-wrap gap-2">
              {['all', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map(level => (
                <button
                  key={level}
                  onClick={() => setFilterLevel(level)}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    filterLevel === level
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {level === 'all' ? 'All Levels' : level}
                </button>
              ))}
            </div>
          </div>

          {/* 数量选择 */}
          <div>
            <label className="block text-gray-300 mb-2">Number of Cards: {cardCount}</label>
            <input
              type="range"
              min="5"
              max="50"
              value={cardCount}
              onChange={(e) => setCardCount(Number(e.target.value))}
              className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-gray-500 text-sm mt-1">
              <span>5</span>
              <span>50</span>
            </div>
          </div>

          {/* 快捷键说明 */}
          <div className="bg-gray-700 p-4 rounded-lg">
            <h3 className="text-white font-semibold mb-2">Keyboard Shortcuts</h3>
            <div className="grid grid-cols-2 gap-2 text-sm text-gray-300">
              <div><kbd className="bg-gray-600 px-2 py-0.5 rounded text-xs">Space</kbd> Flip card</div>
              <div><kbd className="bg-gray-600 px-2 py-0.5 rounded text-xs">Enter</kbd> Flip card</div>
              <div><kbd className="bg-gray-600 px-2 py-0.5 rounded text-xs">Right / 1</kbd> Mastered</div>
              <div><kbd className="bg-gray-600 px-2 py-0.5 rounded text-xs">Left / 2</kbd> Need Review</div>
              <div><kbd className="bg-gray-600 px-2 py-0.5 rounded text-xs">Up</kbd> Previous card</div>
              <div><kbd className="bg-gray-600 px-2 py-0.5 rounded text-xs">Down</kbd> Next card</div>
            </div>
          </div>

          <button
            onClick={loadFlashCards}
            disabled={isLoading}
            className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
          >
            {isLoading ? 'Loading...' : 'Start Learning'}
          </button>
        </div>
      </div>
    )
  }

  // 完成界面
  if (isFinished || items.length === 0) {
    const mastered = results.filter(r => r.status === 'mastered').length
    const review = results.filter(r => r.status === 'review').length
    const unmarked = items.length - results.length

    return (
      <div className="p-6 bg-gray-800 rounded-lg max-w-2xl mx-auto text-center">
        <h2 className="text-2xl font-bold text-white mb-6">Study Complete!</h2>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-green-700 p-4 rounded-lg">
            <div className="text-3xl font-bold text-white">{mastered}</div>
            <div className="text-green-200 text-sm">Mastered</div>
          </div>
          <div className="bg-yellow-700 p-4 rounded-lg">
            <div className="text-3xl font-bold text-white">{review}</div>
            <div className="text-yellow-200 text-sm">Need Review</div>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg">
            <div className="text-3xl font-bold text-white">{unmarked}</div>
            <div className="text-gray-400 text-sm">Unmarked</div>
          </div>
        </div>

        <div className="flex gap-4 justify-center">
          <button
            onClick={restart}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            Study Again
          </button>
          <button
            onClick={() => setShowSettings(true)}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-semibold"
          >
            Change Settings
          </button>
        </div>
      </div>
    )
  }

  const currentItem = items[currentIndex]
  const currentResult = results.find(r => r.itemId === currentItem.id)

  return (
    <div className="p-6 bg-gray-800 rounded-lg max-w-2xl mx-auto">
      {/* 进度条 */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>Card {currentIndex + 1} / {items.length}</span>
          <span>{Math.round((currentIndex / items.length) * 100)}% Complete</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / items.length) * 100}%` }}
          />
        </div>
      </div>

      {/* 闪卡 */}
      <div
        onClick={handleFlip}
        className="relative h-80 cursor-pointer perspective-1000 mb-6"
      >
        <div
          className={`w-full h-full transition-transform duration-500 transform-style-preserve-3d ${
            isFlipped ? 'rotate-y-180' : ''
          }`}
          style={{ transformStyle: 'preserve-3d' }}
        >
          {/* 正面 */}
          <div
            className="absolute inset-0 bg-gray-700 rounded-xl flex flex-col items-center justify-center p-8 backface-hidden"
            style={{ backfaceVisibility: 'hidden' }}
          >
            <div className="text-sm text-gray-400 mb-4">Click to flip</div>
            <h3 className="text-4xl font-bold text-white mb-4">{currentItem.word}</h3>
            {currentItem.phonetic && (
              <p className="text-xl text-gray-400">{currentItem.phonetic}</p>
            )}
            {currentItem.cefr_level && (
              <span className="mt-4 px-3 py-1 bg-blue-600 text-white text-sm rounded-full">
                {currentItem.cefr_level}
              </span>
            )}
          </div>

          {/* 背面 */}
          <div
            className="absolute inset-0 bg-gray-600 rounded-xl flex flex-col items-center justify-center p-8"
            style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
          >
            <div className="text-sm text-gray-400 mb-4">Click to flip back</div>
            <h3 className="text-3xl font-bold text-white mb-4">{currentItem.word}</h3>
            {currentItem.meaning && (
              <p className="text-xl text-blue-300 mb-4 text-center">{currentItem.meaning}</p>
            )}
            {currentItem.example_sentence && (
              <p className="text-sm text-gray-300 italic text-center">"{currentItem.example_sentence}"</p>
            )}
          </div>
        </div>
      </div>

      {/* 标记状态 */}
      {currentResult && (
        <div className={`text-center mb-4 py-2 rounded-lg ${
          currentResult.status === 'mastered' ? 'bg-green-700 text-green-200' : 'bg-yellow-700 text-yellow-200'
        }`}>
          Marked as: {currentResult.status === 'mastered' ? 'Mastered' : 'Needs Review'}
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-3 justify-center">
        <button
          onClick={(e) => { e.stopPropagation(); handleMark('review') }}
          className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-semibold flex items-center gap-2"
        >
          <span>Left / 2</span>
          Need Review
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); handleMark('mastered') }}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold flex items-center gap-2"
        >
          <span>Right / 1</span>
          Mastered
        </button>
      </div>

      {/* 导航 */}
      <div className="flex justify-between mt-6">
        <button
          onClick={prevCard}
          disabled={currentIndex === 0}
          className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50"
        >
          Previous
        </button>
        <button
          onClick={nextCard}
          disabled={currentIndex === items.length - 1}
          className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50"
        >
          Next
        </button>
      </div>

      {/* 快捷结束 */}
      <div className="text-center mt-4">
        <button
          onClick={restart}
          className="text-gray-500 hover:text-gray-300 text-sm underline"
        >
          End session
        </button>
      </div>
    </div>
  )
}

export default FlashCard