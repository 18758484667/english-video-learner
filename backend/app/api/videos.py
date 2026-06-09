from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os
import json

import subprocess
import traceback as tb_module
import threading
from concurrent.futures import ThreadPoolExecutor

import yt_dlp

from ..database import get_db
from ..models import VideoProcess
from ..services.transcriber import transcriber
from ..services.translator import translator
from ..services.subtitle_formatter import convert_to_json
from ..services.vocabulary_assessor import assessor

# 全局线程池，支持并行下载多个视频
# max_workers=3 表示最多同时下载3个视频
download_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="video_download")

router = APIRouter()

# Pydantic模型
class VideoProcessResponse(BaseModel):
    id: int
    user_id: str
    video_url: Optional[str]
    video_path: Optional[str]
    audio_path: Optional[str]
    status: str
    subtitle_data: Optional[str]
    error_message: Optional[str]
    current_step: int
    total_steps: int
    step_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

def process_video_task(process_id: int, media_path: str, user_level: str = "A1", is_audio: bool = False):
    """后台处理视频/音频任务"""
    from ..database import SessionLocal
    from ..models import VideoProcess
    import traceback
    
    db = SessionLocal()
    try:
        process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
        if not process:
            print(f"[ERROR] Process {process_id} not found in database")
            return
        
        # 更新状态为处理中
        process.status = "processing"
        process.current_step = 1
        process.total_steps = 5
        process.step_name = "Extracting audio from video..."
        process.updated_at = datetime.utcnow()
        db.commit()
        
        try:
            if is_audio:
                # 直接使用音频文件
                audio_path = media_path
                print(f"[Process {process_id}] Step 1/5: Using existing audio file: {audio_path}")
            else:
                # 步骤1: 从视频中提取音频并转录
                print(f"[Process {process_id}] Step 1/5: Extracting audio from video...")
                audio_path = transcriber.extract_audio_from_video(media_path)
                print(f"[Process {process_id}] Audio extracted: {audio_path}")
            
            process.step_name = "Transcribing audio to text (this may take a while)..."
            process.updated_at = datetime.utcnow()
            db.commit()
            
            print(f"[Process {process_id}] Step 1/5: Transcribing audio with Whisper...")
            transcription = transcriber.transcribe_audio(audio_path)
            segments = transcription.get('segments', [])
            print(f"[Process {process_id}] Transcription complete: {len(segments)} segments")
            
            # 步骤2: 转换为JSON格式
            process.current_step = 2
            process.step_name = "Converting to JSON format..."
            process.updated_at = datetime.utcnow()
            db.commit()
            
            print(f"[Process {process_id}] Step 2/5: Converting to JSON format...")
            english_texts = [seg['text'] for seg in segments]
            print(f"[Process {process_id}] Extracted {len(english_texts)} text segments")
            
            # 步骤3: 翻译英文字幕为中文
            process.current_step = 3
            process.step_name = "Translating to Chinese..."
            process.updated_at = datetime.utcnow()
            db.commit()
            
            print(f"[Process {process_id}] Step 3/5: Translating {len(english_texts)} segments to Chinese...")
            chinese_translations = []
            for i, text in enumerate(english_texts):
                translation = translator.translate_text(text)
                chinese_translations.append(translation)
                if (i + 1) % 10 == 0:
                    print(f"[Process {process_id}] Translated {i + 1}/{len(english_texts)} segments...")
            print(f"[Process {process_id}] Translation complete")
            
            # 步骤4: 构建字幕数据结构
            process.current_step = 4
            process.step_name = "Building subtitle data..."
            process.updated_at = datetime.utcnow()
            db.commit()
            
            print(f"[Process {process_id}] Step 4/5: Building subtitle data...")
            subtitles = convert_to_json(segments, chinese_translations)
            print(f"[Process {process_id}] Built {len(subtitles)} subtitle entries")
            
            # 步骤5: 评估单词难度
            process.current_step = 5
            process.step_name = "Assessing word difficulty..."
            process.updated_at = datetime.utcnow()
            db.commit()
            
            print(f"[Process {process_id}] Step 5/5: Assessing word difficulty for {len(subtitles)} subtitles...")
            assessed_subtitles = assessor.assess_subtitles(subtitles, user_level)
            print(f"[Process {process_id}] Word assessment complete")
            
            # 保存结果
            process.status = "completed"
            process.step_name = "Completed!"
            process.subtitle_data = json.dumps({
                "subtitles": assessed_subtitles,
                "language": transcription.get('language', 'en'),
                "total_segments": len(assessed_subtitles)
            }, ensure_ascii=False)
            process.completed_at = datetime.utcnow()
            process.updated_at = datetime.utcnow()
            db.commit()
            
            print(f"[Process {process_id}] Video processing completed successfully!")
            
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"[Process {process_id}] Error during processing: {error_msg}")
            process.status = "failed"
            process.error_message = str(e)[:500]
            process.updated_at = datetime.utcnow()
            db.commit()
            
    finally:
        db.close()

@router.post("/upload/", response_model=VideoProcessResponse)
async def upload_video(
    user_id: str,
    user_level: Optional[str] = "A1",
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传本地视频文件并开始处理"""
    
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # 使用绝对路径确保目录正确
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(base_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'mp4'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # 创建处理记录
    process = VideoProcess(
        user_id=user_id,
        video_path=file_path,
        status="pending"
    )
    
    db.add(process)
    db.commit()
    db.refresh(process)
    
    # 使用线程池并行处理，不阻塞其他请求
    download_executor.submit(process_video_task, process.id, file_path, user_level)
    
    return process

@router.get("/{process_id}", response_model=VideoProcessResponse)
def get_video_process(process_id: int, db: Session = Depends(get_db)):
    """获取视频处理状态和结果"""
    process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Video process not found")
    return process

@router.get("/user/{user_id}", response_model=List[VideoProcessResponse])
def get_user_videos(user_id: str, db: Session = Depends(get_db)):
    """获取用户的所有视频处理记录"""
    processes = db.query(VideoProcess).filter(
        VideoProcess.user_id == user_id
    ).order_by(VideoProcess.created_at.desc()).all()
    
    return processes

@router.delete("/{process_id}")
def delete_video_process(process_id: int, db: Session = Depends(get_db)):
    """删除视频处理记录"""
    process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Video process not found")
    
    # 删除视频文件
    if process.video_path and os.path.exists(process.video_path):
        try:
            os.remove(process.video_path)
        except:
            pass
    
    db.delete(process)
    db.commit()
    
    return {"message": "Video process deleted successfully"}

@router.get("/file/{process_id}")
def get_video_file(request: Request, process_id: int, db: Session = Depends(get_db)):
    """获取视频文件（支持HTTP Range请求）"""
    process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Video process not found")
    
    if not process.video_path or not os.path.exists(process.video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    file_path = process.video_path
    file_size = os.path.getsize(file_path)
    
    # 检查是否有Range请求头
    range_header = request.headers.get("range")
    
    if range_header:
        # 解析Range头，格式: bytes=start-end
        try:
            range_value = range_header.replace("bytes=", "")
            start_str, end_str = range_value.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
        except (ValueError, IndexError):
            start = 0
            end = file_size - 1
        
        # 确保范围有效
        if start >= file_size:
            raise HTTPException(status_code=416, detail="Range not satisfiable")
        
        end = min(end, file_size - 1)
        content_length = end - start + 1
        
        def file_iterator():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                chunk_size = 8192
                while remaining > 0:
                    read_size = min(chunk_size, remaining)
                    data = f.read(read_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "video/mp4",
        }
        
        return StreamingResponse(
            file_iterator(),
            status_code=206,
            headers=headers
        )
    
    # 没有Range请求，返回完整文件（带Accept-Ranges头）
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": "video/mp4",
    }
    
    def full_file_iterator():
        with open(file_path, "rb") as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                yield data
    
    return StreamingResponse(
        full_file_iterator(),
        headers=headers
    )


class VideoUrlRequest(BaseModel):
    url: str
    user_id: str
    user_level: Optional[str] = "A1"


def download_video_task(process_id: int, video_url: str, user_level: str = "A1"):
    """后台下载音频并处理任务 - 只下载音频，不下载视频"""
    from ..database import SessionLocal
    from ..models import VideoProcess
    import traceback
    
    db = SessionLocal()
    try:
        process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
        if not process:
            print(f"[ERROR] Process {process_id} not found in database")
            return
        
        # 更新状态为下载中
        process.status = "downloading"
        process.step_name = "Downloading audio from URL..."
        process.updated_at = datetime.utcnow()
        db.commit()
        
        # 使用绝对路径确保目录正确
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_dir = os.path.join(base_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        unique_id = str(uuid.uuid4())
        audio_path = os.path.join(upload_dir, f"{unique_id}_audio.aac")
        
        print(f"[Process {process_id}] Downloading audio from: {video_url}")
        
        # 获取视频信息中的音频流 URL
        info_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            audio_m3u8 = None
            
            for fmt in info.get('formats', []):
                fid = fmt.get('format_id', '')
                url = fmt.get('url', '')
                
                # 找音频流（format_id 包含 audio）
                if 'audio' in fid.lower() and url and 'm3u8' in url:
                    if not audio_m3u8:
                        audio_m3u8 = url
            
            if not audio_m3u8:
                raise Exception("No audio stream found")
            
            print(f"[Process {process_id}] Audio m3u8: {audio_m3u8[:100]}...")
            
            # 使用 ffmpeg 下载音频流
            referer_header = f"Referer: {video_url}\r\n"
            
            audio_cmd = [
                'ffmpeg', '-y',
                '-headers', referer_header,
                '-i', audio_m3u8,
                '-vn',
                '-c:a', 'copy',
                audio_path
            ]
            
            result = subprocess.run(audio_cmd, capture_output=True, text=True, timeout=3600)
            if result.returncode != 0:
                raise Exception(f"Audio download failed: {result.stderr[:500]}")
            
            print(f"[Process {process_id}] Audio downloaded: {audio_path}")
        
        # 检查文件是否存在
        if not os.path.exists(audio_path):
            raise Exception("Downloaded audio file not found")
        
        # 更新路径 - 音频文件同时作为 video_path（前端播放器可直接播放）
        process.audio_path = audio_path
        process.video_path = audio_path  # 让前端播放器可以直接播放音频
        process.status = "pending"
        process.updated_at = datetime.utcnow()
        db.commit()
        
        # 使用音频文件直接处理（跳过从视频提取音频步骤）
        process_video_task(process_id, audio_path, user_level, is_audio=True)
        
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[Process {process_id}] Error during download: {error_msg}")
        process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
        if process:
            process.status = "failed"
            process.error_message = str(e)[:500]
            process.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/download-url/", response_model=VideoProcessResponse)
async def download_video_from_url(
    request: VideoUrlRequest,
    db: Session = Depends(get_db)
):
    """从URL下载视频并处理（使用线程池并行处理）"""
    
    # 验证URL
    url = request.url.strip()
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
    
    # 创建处理记录
    process = VideoProcess(
        user_id=request.user_id,
        video_url=url,
        status="pending"
    )
    
    db.add(process)
    db.commit()
    db.refresh(process)
    
    # 使用线程池并行处理，不阻塞其他请求
    download_executor.submit(download_video_task, process.id, url, request.user_level)
    
    return process


@router.get("/audio/{process_id}")
def get_audio_file(request: Request, process_id: int, db: Session = Depends(get_db)):
    """获取音频文件（支持HTTP Range请求）"""
    process = db.query(VideoProcess).filter(VideoProcess.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Video process not found")
    
    if not process.audio_path or not os.path.exists(process.audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    file_path = process.audio_path
    file_size = os.path.getsize(file_path)
    
    # 检查是否有Range请求头
    range_header = request.headers.get("range")
    
    if range_header:
        # 解析Range头，格式: bytes=start-end
        try:
            range_value = range_header.replace("bytes=", "")
            start_str, end_str = range_value.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
        except (ValueError, IndexError):
            start = 0
            end = file_size - 1
        
        # 确保范围有效
        if start >= file_size:
            raise HTTPException(status_code=416, detail="Range not satisfiable")
        
        end = min(end, file_size - 1)
        content_length = end - start + 1
        
        def file_iterator():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                chunk_size = 8192
                while remaining > 0:
                    read_size = min(chunk_size, remaining)
                    data = f.read(read_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "audio/aac",
        }
        
        return StreamingResponse(
            file_iterator(),
            status_code=206,
            headers=headers
        )
    
    # 没有Range请求，返回完整文件（带Accept-Ranges头）
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": "audio/aac",
    }
    
    def full_file_iterator():
        with open(file_path, "rb") as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                yield data
    
    return StreamingResponse(
        full_file_iterator(),
        headers=headers
    )


@router.post("/cleanup-uploads/")
def cleanup_uploads(db: Session = Depends(get_db)):
    """清理 uploads 目录中未被数据库引用的旧文件"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(base_dir, "uploads")
    
    if not os.path.exists(upload_dir):
        return {"message": "Uploads directory does not exist", "deleted": []}
    
    # 获取数据库中所有被引用的文件路径
    referenced_files = set()
    processes = db.query(VideoProcess).all()
    for p in processes:
        if p.video_path:
            referenced_files.add(p.video_path)
        if p.audio_path:
            referenced_files.add(p.audio_path)
    
    # 清理未被引用的文件
    deleted = []
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path) and file_path not in referenced_files:
            try:
                os.remove(file_path)
                deleted.append(filename)
            except Exception as e:
                print(f"Failed to delete {filename}: {e}")
    
    return {
        "message": f"Cleanup complete. Deleted {len(deleted)} files.",
        "deleted": deleted
    }
