import React, { useRef, useEffect } from 'react'
import { useAppStore } from '../store/useStore'
import ThreeLayerSubtitle from './ThreeLayerSubtitle'

interface VideoPlayerProps {
  videoUrl: string
  onTimeUpdate?: (currentTime: number) => void
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, onTimeUpdate }) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const {
    playbackRate,
    subtitles,
    currentSubtitleIndex,
    setCurrentSubtitleIndex,
    showWordAnnotations,
    showChineseTranslation
  } = useAppStore()

  // 调试输出
  console.log('VideoPlayer rendered, videoUrl:', videoUrl)

  // 设置播放速度
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = playbackRate
    }
  }, [playbackRate])

  // 根据当前时间找到对应的字幕
  const getCurrentSubtitle = (time: number) => {
    const index = subtitles.findIndex(
      (sub) => time >= sub.start && time <= sub.end
    )
    return index !== -1 ? index : null
  }

  return (
    <div className="video-player-container">
      {/* 视频播放器 - 固定高度，避免过大 */}
      <div className="relative w-full bg-black rounded-lg overflow-hidden" style={{ height: '420px' }}>
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            controls
            style={{ width: '100%', height: '100%' }}
            onTimeUpdate={(e) => {
              const time = e.currentTarget.currentTime
              const subtitleIndex = getCurrentSubtitle(time)
              if (subtitleIndex !== null && subtitleIndex !== currentSubtitleIndex) {
                setCurrentSubtitleIndex(subtitleIndex)
              }
              onTimeUpdate?.(time)
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            No video URL provided
          </div>
        )}
      </div>

      {/* 字幕显示区域 - 紧凑高度 */}
      <div className="subtitle-display-area mt-1 px-2 py-1 bg-gray-900 rounded-lg min-h-[60px] flex items-center justify-center">
        {subtitles.length > 0 && currentSubtitleIndex >= 0 ? (
          <ThreeLayerSubtitle
            subtitle={subtitles[currentSubtitleIndex]}
            isActive={true}
            currentTime={videoRef.current?.currentTime}
          />
        ) : (
          <p className="text-gray-500 text-sm">No subtitles available</p>
        )}
      </div>

      {/* 控制按钮和播放速度 - 合并到一行 */}
      <div className="control-bar mt-2 p-2 bg-gray-800 rounded-lg flex flex-wrap items-center justify-center gap-1">
        <button onClick={() => { if (videoRef.current) videoRef.current.currentTime -= 5 }} className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">-5s</button>
        <button onClick={() => { if (videoRef.current) videoRef.current.currentTime += 5 }} className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">+5s</button>
        <button onClick={() => { if (currentSubtitleIndex >= 0 && videoRef.current) videoRef.current.currentTime = subtitles[currentSubtitleIndex].start }} className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">Repeat</button>
        
        <div className="w-px h-4 bg-gray-600 mx-1" />
        
        <button onClick={() => useAppStore.getState().setShowWordAnnotations(!showWordAnnotations)} className={`px-2 py-1 text-xs rounded ${showWordAnnotations ? 'bg-purple-600' : 'bg-gray-600'} text-white hover:opacity-80`}>Annotations</button>
        <button onClick={() => useAppStore.getState().setShowChineseTranslation(!showChineseTranslation)} className={`px-2 py-1 text-xs rounded ${showChineseTranslation ? 'bg-purple-600' : 'bg-gray-600'} text-white hover:opacity-80`}>Translation</button>
        
        <div className="w-px h-4 bg-gray-600 mx-1" />
        
        {[0.5, 0.75, 1.0, 1.25, 1.5].map((rate) => (
          <button key={rate} onClick={() => useAppStore.getState().setPlaybackRate(rate)} className={`px-2 py-1 text-xs rounded ${playbackRate === rate ? 'bg-blue-600' : 'bg-gray-700'} text-white hover:opacity-80`}>{rate}x</button>
        ))}
      </div>
    </div>
  )
}

export default VideoPlayer
