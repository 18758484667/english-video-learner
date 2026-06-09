import { useState, useEffect } from 'react'
import { useAppStore } from './store/useStore'
import VideoPlayer from './components/VideoPlayer'
import VocabularyTest from './components/VocabularyTest'
import VocabularyList from './components/VocabularyList'
import VideoUploader from './components/VideoUploader'
import DownloadQueue from './components/DownloadQueue'
import FlashCard from './components/FlashCard'

type TabType = 'video' | 'test' | 'vocabulary' | 'flashcard'
type CEFRLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'

const CEFR_LEVELS: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const CEFR_DESCRIPTIONS: Record<CEFRLevel, string> = {
  A1: 'Beginner - Basic phrases and expressions',
  A2: 'Elementary - Simple everyday expressions',
  B1: 'Intermediate - Main points of clear standard input',
  B2: 'Upper Intermediate - Complex text and abstract topics',
  C1: 'Advanced - Implicit meaning and fluent expression',
  C2: 'Proficiency - Virtually everything heard or read'
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('video')
  const [username, setUsername] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<CEFRLevel>('B1')
  const [showLogin, setShowLogin] = useState(true)

  const { user, setUser, currentVideoUrl, subtitles } = useAppStore()

  // 页面加载时从 localStorage 恢复登录状态
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('evl_user')
      if (storedUser) {
        const userData = JSON.parse(storedUser)
        setUser(userData)
        setShowLogin(false)
      }
    } catch {
      // ignore parse errors
    }
  }, [setUser])

  // 登录/注册 (简化版 - 无需后端)
  const handleLogin = () => {
    if (!username.trim()) {
      alert('Please enter a username')
      return
    }

    // 使用基于用户名的固定ID，确保刷新页面后单词本不会丢失
    const userId = 'user-' + username.trim().toLowerCase().replace(/\s+/g, '-')
    const userData = {
      id: userId,
      username: username.trim(),
      cefr_level: selectedLevel
    }

    // 持久化到 localStorage
    localStorage.setItem('evl_user', JSON.stringify(userData))

    setUser(userData)
    setShowLogin(false)
  }

  // 加载示例字幕数据
  const loadSampleSubtitles = () => {
    const sampleSubtitles = [
      {
        id: 1,
        start: 0.0,
        end: 2.5,
        english: "The quick brown fox jumps over the lazy dog",
        chinese_translation: "那只敏捷的棕色狐狸跳过了懒惰的狗",
        words: [
          { word: "The", level: "A1", is_beyond: false, meaning: null, phonetic: "/ðə/" },
          { word: "quick", level: "A2", is_beyond: false, meaning: null, phonetic: "/kwɪk/" },
          { word: "brown", level: "A1", is_beyond: false, meaning: null, phonetic: "/braʊn/" },
          { word: "fox", level: "B1", is_beyond: true, meaning: "狐狸", phonetic: "/fɑːks/" },
          { word: "jumps", level: "B1", is_beyond: true, meaning: "跳跃", phonetic: "/dʒʌmps/" },
          { word: "over", level: "A2", is_beyond: false, meaning: null, phonetic: "/ˈoʊvər/" },
          { word: "the", level: "A1", is_beyond: false, meaning: null, phonetic: "/ðə/" },
          { word: "lazy", level: "A2", is_beyond: false, meaning: null, phonetic: "/ˈleɪzi/" },
          { word: "dog", level: "A1", is_beyond: false, meaning: null, phonetic: "/dɔːɡ/" }
        ]
      },
      {
        id: 2,
        start: 2.5,
        end: 5.0,
        english: "This is a sample transcription for testing purposes",
        chinese_translation: "这是一个用于测试目的的示例转录",
        words: [
          { word: "This", level: "A1", is_beyond: false, meaning: null, phonetic: "/ðɪs/" },
          { word: "is", level: "A1", is_beyond: false, meaning: null, phonetic: "/ɪz/" },
          { word: "a", level: "A1", is_beyond: false, meaning: null, phonetic: "/ə/" },
          { word: "sample", level: "B1", is_beyond: true, meaning: "样本", phonetic: "/ˈsæmpl/" },
          { word: "transcription", level: "B2", is_beyond: true, meaning: "转录", phonetic: "/trænˈskrɪpʃən/" },
          { word: "for", level: "A1", is_beyond: false, meaning: null, phonetic: "/fɔːr/" },
          { word: "testing", level: "B1", is_beyond: true, meaning: "测试", phonetic: "/ˈtestɪŋ/" },
          { word: "purposes", level: "B2", is_beyond: true, meaning: "目的", phonetic: "/ˈpɜːrpəsɪz/" }
        ]
      }
    ]

    useAppStore.getState().setSubtitles(sampleSubtitles)
    alert('Sample subtitles loaded! You can now see the three-layer subtitle display.')
  }

  if (showLogin) {
    return (
      <div className="login-container">
        <div className="login-box">
          <h1 className="login-title">
            English Video Learner
          </h1>
          <p className="login-subtitle">
            Learn English through videos with smart subtitles
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
              className="input-field"
            />
            
            {/* Level Selection */}
            <div>
              <label className="block text-gray-300 mb-2 text-sm">Select your English level:</label>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value as CEFRLevel)}
                className="input-field w-full"
              >
                {CEFR_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level} - {CEFR_DESCRIPTIONS[level]}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={handleLogin}
              className="btn-primary"
            >
              Start Learning
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">English Video Learner</h1>
            <div className="flex items-center gap-4">
              {user && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Level:</span>
                  <select
                    value={user.cefr_level}
                    onChange={(e) => setUser({ ...user, cefr_level: e.target.value as CEFRLevel })}
                    className="px-3 py-1 bg-gray-700 text-blue-400 font-bold rounded border border-gray-600 hover:border-gray-500 focus:outline-none focus:border-blue-500"
                  >
                    {CEFR_LEVELS.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <button
                onClick={() => {
                  localStorage.removeItem('evl_user')
                  setUser(null)
                  setShowLogin(true)
                }}
                className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('video')}
              className={`px-6 py-3 transition ${
                activeTab === 'video'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Video Player
            </button>
            <button
              onClick={() => setActiveTab('test')}
              className={`px-6 py-3 transition ${
                activeTab === 'test'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Level Test
            </button>
            <button
              onClick={() => setActiveTab('vocabulary')}
              className={`px-6 py-3 transition ${
                activeTab === 'vocabulary'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Vocabulary List
            </button>
            <button
              onClick={() => setActiveTab('flashcard')}
              className={`px-6 py-3 transition ${
                activeTab === 'flashcard'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Flash Cards
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'video' && (
          <div>
            {/* 视频上传组件 */}
            <VideoUploader />

            {/* 下载队列 */}
            <DownloadQueue />

            {/* 示例字幕加载按钮 */}
            <div className="mt-6 bg-gray-800 p-6 rounded-lg">
              <h2 className="text-xl font-bold text-white mb-4">Or Try Sample</h2>
              <p className="text-gray-400 mb-4">
                Don't have a video? Click below to load sample subtitles and see the three-layer display in action.
              </p>
              <button
                onClick={loadSampleSubtitles}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Load Sample Subtitles
              </button>
            </div>

            {/* 视频播放器 */}
            {subtitles.length > 0 && (
              <div className="mt-6">
                <VideoPlayer videoUrl={currentVideoUrl} />
              </div>
            )}
          </div>
        )}

        {activeTab === 'test' && <VocabularyTest />}

        {activeTab === 'vocabulary' && <VocabularyList />}

        {activeTab === 'flashcard' && <FlashCard />}
      </main>
    </div>
  )
}

export default App
