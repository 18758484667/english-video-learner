import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { useAppStore } from '../store/useStore'

interface VideoProcess {
  id: number
  user_id: string
  video_url: string | null
  video_path: string | null
  audio_path: string | null
  status: string
  subtitle_data: string | null
  error_message: string | null
  current_step: number
  total_steps: number
  step_name: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Waiting...',
  downloading: 'Downloading...',
  processing: 'Processing...',
  completed: 'Completed',
  failed: 'Failed'
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-500',
  downloading: 'bg-blue-500',
  processing: 'bg-yellow-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500'
}

const DownloadQueue: React.FC = () => {
  const { user } = useAppStore()
  const [videos, setVideos] = useState<VideoProcess[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchUserVideos = async () => {
    if (!user) return

    try {
      const response = await axios.get(`http://localhost:8000/api/videos/user/${user.id}`)
      const allVideos: VideoProcess[] = response.data

      // 过滤出正在处理中的视频（非 completed 和 failed）
      const activeVideos = allVideos.filter(
        (v) => v.status !== 'completed' && v.status !== 'failed'
      )

      setVideos(activeVideos)
    } catch (error) {
      console.error('Failed to fetch video queue:', error)
    }
  }

  useEffect(() => {
    if (!user) return

    // 初始加载
    fetchUserVideos()

    // 每3秒轮询一次
    intervalRef.current = setInterval(() => {
      fetchUserVideos()
    }, 3000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [user])

  const getProgressPercent = (video: VideoProcess) => {
    if (video.total_steps > 0) {
      return Math.round((video.current_step / video.total_steps) * 100)
    }
    // 根据状态估算
    if (video.status === 'downloading') return 20
    if (video.status === 'processing') return 60
    if (video.status === 'pending') return 5
    return 0
  }

  const getVideoTitle = (video: VideoProcess) => {
    if (video.video_url) {
      // 尝试从URL提取域名作为标题
      try {
        const url = new URL(video.video_url)
        return `${url.hostname} - Video #${video.id}`
      } catch {
        return `Video #${video.id}`
      }
    }
    return `Video #${video.id}`
  }

  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } catch {
      return ''
    }
  }

  if (!user) return null

  return (
    <div className="mt-6 bg-gray-800 p-6 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>Download Queue</span>
          {videos.length > 0 && (
            <span className="text-sm font-normal px-2 py-0.5 bg-blue-600 text-white rounded-full">
              {videos.length}
            </span>
          )}
        </h2>
        <button
          onClick={() => {
            setIsLoading(true)
            fetchUserVideos().then(() => setIsLoading(false))
          }}
          className="text-sm text-gray-400 hover:text-white transition-colors"
          disabled={isLoading}
        >
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {videos.length === 0 ? (
        <p className="text-gray-500 text-sm">No active downloads. Start downloading a video to see it here.</p>
      ) : (
        <div className="space-y-3">
          {videos.map((video) => (
            <div
              key={video.id}
              className="bg-gray-700 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-medium text-sm truncate" title={getVideoTitle(video)}>
                    {getVideoTitle(video)}
                  </h3>
                  <p className="text-gray-400 text-xs mt-1">
                    {video.video_url || 'Local file'}
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded text-white ${STATUS_COLORS[video.status] || 'bg-gray-500'}`}
                  >
                    {STATUS_LABELS[video.status] || video.status}
                  </span>
                </div>
              </div>

              {/* 进度条 */}
              <div className="mt-3">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-gray-400 text-xs">
                    {video.step_name || 'Processing...'}
                  </span>
                  <span className="text-gray-400 text-xs">
                    {getProgressPercent(video)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${STATUS_COLORS[video.status] || 'bg-gray-500'}`}
                    style={{ width: `${getProgressPercent(video)}%` }}
                  />
                </div>
              </div>

              {/* 步骤信息 */}
              {video.total_steps > 0 && (
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1">
                    <div className="flex gap-1">
                      {Array.from({ length: video.total_steps }).map((_, index) => (
                        <div
                          key={index}
                          className={`h-1.5 flex-1 rounded-full ${
                            index < video.current_step
                              ? 'bg-blue-500'
                              : index === video.current_step - 1
                                ? 'bg-blue-400 animate-pulse'
                                : 'bg-gray-600'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                  <span className="text-gray-500 text-xs whitespace-nowrap">
                    Step {video.current_step}/{video.total_steps}
                  </span>
                </div>
              )}

              {/* 时间信息 */}
              <div className="mt-2 flex items-center gap-4 text-gray-500 text-xs">
                <span>Created: {formatTime(video.created_at)}</span>
                {video.updated_at !== video.created_at && (
                  <span>Updated: {formatTime(video.updated_at)}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DownloadQueue
