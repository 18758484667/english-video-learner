import React, { useState, useRef } from 'react'
import axios from 'axios'
import { useAppStore } from '../store/useStore'
import { API_BASE_URL } from '../config'

interface UploadProgress {
  status: 'idle' | 'uploading' | 'downloading' | 'processing' | 'completed' | 'error' | 'downloading_audio' | 'processing_audio' | 'downloading_video'
  progress: number
  message: string
}

type UploadMode = 'file' | 'url'

const VideoUploader: React.FC = () => {
  const { user, setSubtitles, setCurrentVideoUrl } = useAppStore()
  const [uploadMode, setUploadMode] = useState<UploadMode>('file')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [videoUrl, setVideoUrl] = useState('')
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    status: 'idle',
    progress: 0,
    message: ''
  })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const processingProgressRef = useRef<number>(0) // 用于平滑递增进度

  // 处理文件选择
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('video/')) {
        alert('Please select a video file')
        return
      }
      setSelectedFile(file)
      setUploadProgress({ status: 'idle', progress: 0, message: '' })
    }
  }

  // 上传视频
  const handleUpload = async () => {
    if (!selectedFile || !user) {
      alert('Please select a video file and login first')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setUploadProgress({
        status: 'uploading',
        progress: 0,
        message: 'Uploading video...'
      })

      // 上传文件
      const uploadResponse = await axios.post(
        `${API_BASE_URL}/api/videos/upload/?user_id=${user.id}&user_level=${user.cefr_level}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 1)
            )
            setUploadProgress(prev => ({
              ...prev,
              progress: percentCompleted,
              message: `Uploading: ${percentCompleted}%`
            }))
          }
        }
      )

      const processId = uploadResponse.data.id

      setUploadProgress({
        status: 'processing',
        progress: 0,
        message: 'Processing video... This may take a few minutes.'
      })
      processingProgressRef.current = 0 // 重置进度

      // 轮询检查处理状态
      checkProcessingStatus(processId)

    } catch (error) {
      console.error('Upload failed:', error)
      setUploadProgress({
        status: 'error',
        progress: 0,
        message: 'Upload failed. Please try again.'
      })
    }
  }

  // 从URL下载视频
  const handleUrlDownload = async () => {
    if (!videoUrl.trim() || !user) {
      alert('Please enter a video URL and login first')
      return
    }

    try {
      setUploadProgress({
        status: 'downloading',
        progress: 0,
        message: 'Downloading video from URL... This may take a while.'
      })

      const response = await axios.post(
        `${API_BASE_URL}/api/videos/download-url/`,
        {
          url: videoUrl.trim(),
          user_id: user.id,
          user_level: user.cefr_level
        }
      )

      const processId = response.data.id

      setUploadProgress({
        status: 'processing',
        progress: 0,
        message: 'Download complete! Processing video...'
      })

      // 轮询检查处理状态
      checkProcessingStatus(processId)

    } catch (error: any) {
      console.error('Download failed:', error)
      const errorMsg = error.response?.data?.detail || 'Download failed. Please try again.'
      setUploadProgress({
        status: 'error',
        progress: 0,
        message: errorMsg
      })
    }
  }

  // 检查处理状态
  const checkProcessingStatus = async (id: number) => {
    // 重置进度
    processingProgressRef.current = 0
    let isChecking = true
    let lastUpdateTime = Date.now()
    let lastStep = 0
    let isStuck = false
    
    const interval = setInterval(async () => {
      if (!isChecking) return
      
      try {
        const response = await axios.get(`${API_BASE_URL}/api/videos/${id}`)
        const { status, subtitle_data, error_message, current_step, total_steps, step_name } = response.data

        if (status === 'completed') {
          clearInterval(interval)
          isChecking = false
          
          // 解析字幕数据
          if (subtitle_data) {
            const data = JSON.parse(subtitle_data)
            setSubtitles(data.subtitles)
            // 设置视频URL（如果有视频则优先视频，否则音频）
            setCurrentVideoUrl(`${API_BASE_URL}/api/videos/file/${id}`)
            
            setUploadProgress({
              status: 'completed',
              progress: 100,
              message: `Video processed successfully! Found ${data.subtitles?.length || 0} subtitle segments.`
            })
          }
        } else if (status === 'failed') {
          clearInterval(interval)
          isChecking = false
          setUploadProgress({
            status: 'error',
            progress: 0,
            message: `Processing failed: ${error_message || 'Unknown error'}`
          })
        } else if (status === 'downloading_audio') {
          // 正在下载音频
          setUploadProgress({
            status: 'downloading_audio',
            progress: 10,
            message: step_name || 'Downloading audio stream...'
          })
        } else if (status === 'processing_audio') {
          // 音频处理中/已完成 - 可以开始学习了！
          let audioReady = false
          
          // 如果有字幕数据，立即加载字幕和音频
          if (subtitle_data) {
            try {
              const data = JSON.parse(subtitle_data)
              setSubtitles(data.subtitles)
              // 设置音频播放URL
              setCurrentVideoUrl(`${API_BASE_URL}/api/videos/audio/${id}`)
              audioReady = true
            } catch (e) {
              console.error('Failed to parse subtitle data:', e)
            }
          }
          
          setUploadProgress({
            status: 'processing_audio',
            progress: audioReady ? 70 : 50,
            message: audioReady 
              ? 'Audio ready! You can start learning now. Video is downloading in background...' 
              : (step_name || 'Processing audio...')
          })
        } else if (status === 'downloading_video') {
          // 视频正在下载中（音频和字幕已就绪）
          setUploadProgress({
            status: 'downloading_video',
            progress: 80,
            message: step_name || 'Downloading video stream...'
          })
        } else if (status === 'downloading') {
          // 兼容旧状态
          setUploadProgress({
            status: 'downloading',
            progress: 10,
            message: step_name || 'Downloading video...'
          })
        } else if (status === 'processing') {
          // 使用后端返回的真实进度
          const progress = total_steps > 0 ? Math.round((current_step / total_steps) * 100) : 50
          
          // 检测是否有进展
          if (current_step !== lastStep) {
            lastStep = current_step
            lastUpdateTime = Date.now()
            isStuck = false
          }
          
          // 计算已等待时间
          const elapsed = Math.floor((Date.now() - lastUpdateTime) / 1000)
          let extraInfo = ''
          
          if (elapsed > 120 && !isStuck) {
            // 超过2分钟没有进展
            isStuck = true
          }
          
          if (isStuck) {
            const minutes = Math.floor(elapsed / 60)
            extraInfo = ` (stuck for ${minutes}m, may need refresh)`
          }
          
          setUploadProgress({
            status: 'processing',
            progress: progress,
            message: `Step ${current_step}/${total_steps}: ${step_name || 'Processing...'}${extraInfo}`
          })
        } else if (status === 'pending') {
          setUploadProgress({
            status: 'processing',
            progress: 5,
            message: 'Waiting in queue...'
          })
        }
        
      } catch (error) {
        console.error('Status check failed:', error)
        // 网络错误时不停止轮询，继续尝试
      }
    }, 3000) // 每3秒检查一次

    // 30分钟后停止轮询（视频处理可能需要较长时间）
    setTimeout(() => {
      clearInterval(interval)
      isChecking = false
      setUploadProgress(prev => {
        if (prev.status === 'processing') {
          return {
            ...prev,
            message: 'Checking timeout. Please refresh to see the latest status.'
          }
        }
        return prev
      })
    }, 1800000)
  }

  // 清除选择
  const handleClear = () => {
    setSelectedFile(null)
    setVideoUrl('')
    setUploadProgress({ status: 'idle', progress: 0, message: '' })
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="video-uploader p-6 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold text-white mb-4">Upload Video</h2>
      
      {/* 模式切换 */}
      <div className="flex mb-4 bg-gray-700 rounded-lg p-1">
        <button
          onClick={() => setUploadMode('file')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            uploadMode === 'file'
              ? 'bg-gray-600 text-white'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Local File
        </button>
        <button
          onClick={() => setUploadMode('url')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            uploadMode === 'url'
              ? 'bg-gray-600 text-white'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Video URL
        </button>
      </div>

      {/* URL输入区域 */}
      {uploadMode === 'url' && (
        <div className="mb-4">
          <input
            type="text"
            placeholder="Paste video URL here (YouTube, Bilibili, etc.)"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none placeholder-gray-500"
          />
          <p className="text-gray-500 text-xs mt-2">
            Supports: YouTube, Bilibili, Twitter, Instagram, and most video sites
          </p>
        </div>
      )}

      {/* 文件选择区域 */}
      {uploadMode === 'file' && (
        <div className="mb-4">
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
            id="video-upload"
          />
          <label
            htmlFor="video-upload"
            className="block w-full px-4 py-8 border-2 border-dashed border-gray-600 rounded-lg text-center cursor-pointer hover:border-blue-500 transition-colors"
          >
            {selectedFile ? (
              <div>
                <p className="text-white font-medium">{selectedFile.name}</p>
                <p className="text-gray-400 text-sm mt-1">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div>
                <p className="text-gray-400">Click to select a video file</p>
                <p className="text-gray-500 text-sm mt-1">MP4, AVI, MOV supported</p>
              </div>
            )}
          </label>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-2 mb-4">
        {uploadMode === 'file' ? (
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploadProgress.status === 'uploading' || uploadProgress.status === 'processing'}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploadProgress.status === 'uploading' ? 'Uploading...' : 
             uploadProgress.status === 'processing' ? 'Processing...' : 'Upload & Process'}
          </button>
        ) : (
          <button
            onClick={handleUrlDownload}
            disabled={!videoUrl.trim() || uploadProgress.status === 'downloading' || uploadProgress.status === 'processing' || uploadProgress.status === 'downloading_audio' || uploadProgress.status === 'processing_audio' || uploadProgress.status === 'downloading_video'}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploadProgress.status === 'downloading' || uploadProgress.status === 'downloading_audio' ? 'Downloading...' : 
             uploadProgress.status === 'processing' || uploadProgress.status === 'processing_audio' ? 'Processing...' : 
             uploadProgress.status === 'downloading_video' ? 'Downloading video...' : 'Download & Process'}
          </button>
        )}
        <button
          onClick={handleClear}
          disabled={!selectedFile && !videoUrl}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Clear
        </button>
      </div>

      {/* 进度显示 */}
      {uploadProgress.status !== 'idle' && (
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <span className={`text-sm ${
              uploadProgress.status === 'error' ? 'text-red-400' :
              uploadProgress.status === 'completed' ? 'text-green-400' :
              uploadProgress.status === 'processing_audio' ? 'text-yellow-400' :
              'text-blue-400'
            }`}>
              {uploadProgress.message}
            </span>
            <span className="text-sm text-gray-400">
              {uploadProgress.progress}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                uploadProgress.status === 'error' ? 'bg-red-500' :
                uploadProgress.status === 'completed' ? 'bg-green-500' :
                'bg-blue-500'
              }`}
              style={{ width: `${uploadProgress.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* 提示信息 */}
      <div className="mt-4 p-3 bg-gray-700 rounded-lg">
        <p className="text-gray-300 text-sm">
          <strong>Note:</strong> For URL downloads, audio is processed first so you can start learning immediately while the video downloads in the background.
        </p>
        <ul className="text-gray-400 text-sm mt-2 ml-4 list-disc">
          <li>Phase 1: Download audio & generate subtitles (you can start learning!)</li>
          <li>Phase 2: Download video in the background</li>
        </ul>
        <p className="text-gray-400 text-sm mt-2">
          Processing time: ~1-5 minutes for audio + subtitles, video may take longer
        </p>
      </div>
    </div>
  )
}

export default VideoUploader
