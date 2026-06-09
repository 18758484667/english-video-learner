import { create } from 'zustand'

interface User {
  id: string
  username: string
  email?: string
  cefr_level: string
}

interface SubtitleWord {
  word: string
  level: string
  is_beyond: boolean
  meaning: string | null
  phonetic: string | null
}

interface Subtitle {
  id: number
  start: number
  end: number
  english: string
  chinese_translation: string
  words: SubtitleWord[]
}

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

interface AppState {
  // 用户信息
  user: User | null
  setUser: (user: User | null) => void

  // 字幕数据
  subtitles: Subtitle[]
  setSubtitles: (subtitles: Subtitle[]) => void
  currentSubtitleIndex: number
  setCurrentSubtitleIndex: (index: number) => void

  // 当前视频URL
  currentVideoUrl: string
  setCurrentVideoUrl: (url: string) => void

  // 显示控制
  showWordAnnotations: boolean
  setShowWordAnnotations: (show: boolean) => void
  showChineseTranslation: boolean
  setShowChineseTranslation: (show: boolean) => void

  // 生词本
  vocabularyItems: VocabularyItem[]
  setVocabularyItems: (items: VocabularyItem[]) => void
  addVocabularyItem: (item: VocabularyItem) => void
  removeVocabularyItem: (id: number) => void

  // 视频播放速度
  playbackRate: number
  setPlaybackRate: (rate: number) => void
}

// 从 localStorage 恢复用户信息
const getStoredUser = () => {
  try {
    const stored = localStorage.getItem('evl_user')
    if (stored) {
      return JSON.parse(stored)
    }
  } catch {
    // ignore parse errors
  }
  return null
}

export const useAppStore = create<AppState>((set) => ({
  // 用户信息
  user: getStoredUser(),
  setUser: (user) => {
    // 保存到 localStorage
    if (user) {
      localStorage.setItem('evl_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('evl_user')
    }
    set({ user })
  },

  // 字幕数据
  subtitles: [],
  setSubtitles: (subtitles) => set({ subtitles }),
  currentSubtitleIndex: 0,
  setCurrentSubtitleIndex: (index) => set({ currentSubtitleIndex: index }),

  // 当前视频URL
  currentVideoUrl: '',
  setCurrentVideoUrl: (url: string) => set({ currentVideoUrl: url }),

  // 显示控制
  showWordAnnotations: true,
  setShowWordAnnotations: (show) => set({ showWordAnnotations: show }),
  showChineseTranslation: true,
  setShowChineseTranslation: (show) => set({ showChineseTranslation: show }),

  // 生词本
  vocabularyItems: [],
  setVocabularyItems: (items) => set({ vocabularyItems: items }),
  addVocabularyItem: (item) =>
    set((state) => ({
      vocabularyItems: [item, ...state.vocabularyItems]
    })),
  removeVocabularyItem: (id) =>
    set((state) => ({
      vocabularyItems: state.vocabularyItems.filter((item) => item.id !== id)
    })),

  // 视频播放速度
  playbackRate: 1.0,
  setPlaybackRate: (rate) => set({ playbackRate: rate })
}))
