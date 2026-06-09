import React, { useEffect, useState } from 'react'
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
  source_video: string | null
  source_timestamp: number | null
  cefr_level: string | null
  review_count: number
  added_at: string
}

interface StatsData {
  total: number
  level_stats: Record<string, number>
}

const BASE_URL = `${API_BASE_URL}/api`
const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const VocabularyList: React.FC = () => {
  const { user, vocabularyItems, setVocabularyItems, removeVocabularyItem, addVocabularyItem } = useAppStore()

  // 搜索、筛选、排序状态
  const [searchQuery, setSearchQuery] = useState('')
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('added_at')
  const [stats, setStats] = useState<StatsData | null>(null)

  // 手动添加相关状态
  const [newWord, setNewWord] = useState('')
  const [isTranslating, setIsTranslating] = useState(false)
  const [addToast, setAddToast] = useState<string | null>(null)

  // 编辑相关状态
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editWord, setEditWord] = useState('')
  const [editMeaning, setEditMeaning] = useState('')
  const [editPhonetic, setEditPhonetic] = useState('')
  const [editExample, setEditExample] = useState('')

  // 加载生词本（带筛选参数）
  const loadVocabularyItems = async () => {
    if (!user) return
    try {
      const params = new URLSearchParams()
      if (filterLevel !== 'all') params.append('level', filterLevel)
      params.append('sort_by', sortBy)
      if (searchQuery.trim()) params.append('search', searchQuery.trim())

      const response = await axios.get(
        `${API_BASE_URL}/vocabulary/items/${user.id}?${params.toString()}`
      )
      setVocabularyItems(response.data)
    } catch (error) {
      console.error('Failed to load vocabulary items:', error)
    }
  }

  // 加载统计信息
  const loadStats = async () => {
    if (!user) return
    try {
      const response = await axios.get(`${API_BASE_URL}/vocabulary/stats/${user.id}`)
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  useEffect(() => {
    if (user) {
      loadVocabularyItems()
      loadStats()
    }
  }, [user, filterLevel, sortBy])

  // 搜索防抖
  useEffect(() => {
    const timer = setTimeout(() => {
      if (user) {
        loadVocabularyItems()
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // 手动添加单词
  const handleAddNewWord = async () => {
    if (!newWord.trim() || !user) return

    const word = newWord.trim()
    setIsTranslating(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/vocabulary/items/`, {
        user_id: user.id,
        word: word,
        source_video: '',
        source_timestamp: 0
      })

      addVocabularyItem(response.data)
      setNewWord('')
      setAddToast(`已添加 "${word}" 到生词本`)
      setTimeout(() => setAddToast(null), 2000)
      loadStats() // 刷新统计
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 400) {
        setAddToast(`"${word}" 已在生词本中`)
      } else {
        setAddToast('添加失败')
      }
      setTimeout(() => setAddToast(null), 2000)
    } finally {
      setIsTranslating(false)
    }
  }

  // 开始编辑
  const startEdit = (item: VocabularyItem) => {
    setEditingId(item.id)
    setEditWord(item.word)
    setEditMeaning(item.meaning || '')
    setEditPhonetic(item.phonetic || '')
    setEditExample(item.example_sentence || '')
  }

  // 保存编辑
  const saveEdit = async (itemId: number) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/vocabulary/items/${itemId}`, {
        word: editWord || undefined,
        meaning: editMeaning || null,
        phonetic: editPhonetic || null,
        example_sentence: editExample || null
      })

      const updatedItems = vocabularyItems.map(item =>
        item.id === itemId ? response.data : item
      )
      setVocabularyItems(updatedItems)
      setEditingId(null)
      setAddToast('已保存修改')
      setTimeout(() => setAddToast(null), 2000)
    } catch (error) {
      console.error('Failed to update vocabulary item:', error)
      setAddToast('保存失败')
      setTimeout(() => setAddToast(null), 2000)
    }
  }

  // 取消编辑
  const cancelEdit = () => {
    setEditingId(null)
    setEditWord('')
    setEditMeaning('')
    setEditPhonetic('')
    setEditExample('')
  }

  // 删除单词
  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${API_BASE_URL}/vocabulary/items/${id}`)
      removeVocabularyItem(id)
      loadStats() // 刷新统计
    } catch (error) {
      console.error('Failed to delete vocabulary item:', error)
    }
  }

  // 导出为CSV
  const exportToCSV = () => {
    const headers = ['Word', 'Meaning', 'Phonetic', 'Level', 'Added At']
    const rows = vocabularyItems.map(item => [
      item.word,
      item.meaning || '',
      item.phonetic || '',
      item.cefr_level || '',
      new Date(item.added_at).toLocaleDateString()
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vocabulary_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (!user) {
    return (
      <div className="p-8 bg-gray-800 rounded-lg text-center">
        <p className="text-gray-400">Please login to view your vocabulary list</p>
      </div>
    )
  }

  return (
    <div className="vocabulary-list p-6 bg-gray-800 rounded-lg">
      {/* Toast 提示 */}
      {addToast && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-4 py-2 bg-green-600 text-white rounded-lg shadow-lg text-sm">
          {addToast}
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">My Vocabulary List</h2>
        <div className="flex gap-2">
          <span className="text-gray-400 mr-4">
            Total: {vocabularyItems.length} words
          </span>
          {vocabularyItems.length > 0 && (
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Export CSV
            </button>
          )}
        </div>
      </div>

      {/* 统计概览 */}
      {stats && stats.total > 0 && (
        <div className="mb-6 p-4 bg-gray-700 rounded-lg">
          <div className="flex flex-wrap gap-2">
            <div className="px-3 py-1 bg-gray-600 rounded-full text-sm text-white">
              Total: {stats.total}
            </div>
            {Object.entries(stats.level_stats).map(([level, count]) => (
              <div
                key={level}
                className="px-3 py-1 bg-blue-600 rounded-full text-sm text-white"
              >
                {level}: {count}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 搜索、筛选、排序 */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* 搜索框 */}
          <div className="flex-1">
            <label className="block text-gray-300 text-sm mb-1">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by word or meaning..."
              className="w-full px-4 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* 等级筛选 */}
          <div className="w-full md:w-40">
            <label className="block text-gray-300 text-sm mb-1">CEFR Level</label>
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Levels</option>
              {CEFR_LEVELS.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>

          {/* 排序 */}
          <div className="w-full md:w-48">
            <label className="block text-gray-300 text-sm mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none"
            >
              <option value="added_at">Added Date (Newest)</option>
              <option value="word">Word (A-Z)</option>
              <option value="review_count">Review Count</option>
              <option value="level">CEFR Level</option>
            </select>
          </div>
        </div>
      </div>

      {/* 手动添加区域 */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-3">Add New Word / Phrase</h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={newWord}
            onChange={(e) => setNewWord(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddNewWord()}
            placeholder="Enter a word or phrase..."
            className="flex-1 px-4 py-2 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none"
          />
          <button
            onClick={handleAddNewWord}
            disabled={isTranslating || !newWord.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isTranslating ? 'Translating...' : 'Add'}
          </button>
        </div>
        <p className="text-gray-400 text-sm mt-2">
          Enter an English word or phrase, and it will be automatically translated.
        </p>
      </div>

      {vocabularyItems.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No words in your vocabulary list yet</p>
          <p className="text-gray-500 mt-2">Click on unknown words while watching videos to add them here</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {vocabularyItems.map((item) => (
            <div
              key={item.id}
              className="bg-gray-700 p-4 rounded-lg hover:bg-gray-600 transition relative group"
            >
              {/* 删除按钮 */}
              <button
                onClick={() => handleDelete(item.id)}
                className="absolute top-2 right-2 text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition"
                title="Delete word"
              >
                x
              </button>

              {/* 编辑按钮 */}
              {editingId !== item.id && (
                <button
                  onClick={() => startEdit(item)}
                  className="absolute top-2 right-8 text-blue-400 hover:text-blue-300 opacity-0 group-hover:opacity-100 transition"
                  title="Edit word"
                >
                  Edit
                </button>
              )}

              {editingId === item.id ? (
                // 编辑模式
                <div className="space-y-3">
                  <div>
                    <label className="block text-gray-400 text-sm mb-1">Word</label>
                    <input
                      type="text"
                      value={editWord}
                      onChange={(e) => setEditWord(e.target.value)}
                      className="w-full px-3 py-1 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none font-bold text-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 text-sm mb-1">Meaning</label>
                    <input
                      type="text"
                      value={editMeaning}
                      onChange={(e) => setEditMeaning(e.target.value)}
                      className="w-full px-3 py-1 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 text-sm mb-1">Phonetic</label>
                    <input
                      type="text"
                      value={editPhonetic}
                      onChange={(e) => setEditPhonetic(e.target.value)}
                      className="w-full px-3 py-1 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 text-sm mb-1">Example</label>
                    <textarea
                      value={editExample}
                      onChange={(e) => setEditExample(e.target.value)}
                      rows={2}
                      className="w-full px-3 py-1 bg-gray-600 text-white rounded border border-gray-500 focus:border-blue-500 focus:outline-none resize-none"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => saveEdit(item.id)}
                      className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                    >
                      Save
                    </button>
                    <button
                      onClick={cancelEdit}
                      className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                // 展示模式
                <>
                  <h3 className="text-xl font-bold text-white mb-1">{item.word}</h3>
                  {item.phonetic && (
                    <p className="text-gray-400 text-sm mb-2">{item.phonetic}</p>
                  )}
                  {item.meaning && (
                    <p className="text-blue-300 mb-2">{item.meaning}</p>
                  )}
                  <div className="flex flex-wrap gap-2 mt-2">
                    {item.cefr_level && (
                      <span className="inline-block px-2 py-1 bg-blue-600 text-white text-xs rounded">
                        {item.cefr_level}
                      </span>
                    )}
                    {item.review_count > 0 && (
                      <span className="inline-block px-2 py-1 bg-green-600 text-white text-xs rounded">
                        Reviewed: {item.review_count}
                      </span>
                    )}
                  </div>
                  {item.example_sentence && (
                    <p className="text-gray-400 text-sm mt-2 italic">
                      "{item.example_sentence}"
                    </p>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default VocabularyList