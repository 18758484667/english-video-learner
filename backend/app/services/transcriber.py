from typing import List, Dict
import os
import platform
import re

# 设置 Hugging Face 国内镜像（如果需要翻墙）
# 取消下面一行的注释来使用国内镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 常见缩写修复映射：Whisper 会把 "don't" 拆成 "don" 和 "t"
CONTRACTION_PATTERNS = [
    # n't contractions
    (r'\b(don|won|can|isn|aren|wasn|weren|haven|hasn|hadn|wouldn|shouldn|couldn|mustn|didn|doesn) t\b', r"\1't"),
    # 's contractions
    (r'\b(let|it|that|he|she|here|there|what|this|these|those) s\b', r"\1's"),
    # 'm contractions
    (r'\b(i) m\b', r"\1'm"),
    # 're contractions
    (r'\b(you|we|they|what|who|where|here) re\b', r"\1're"),
    # 'll contractions
    (r'\b(i|you|we|they|he|she|it|that|what|there) ll\b', r"\1'll"),
    # 've contractions
    (r'\b(i|you|we|they|could|should|would|might|must) ve\b', r"\1've"),
    # 'd contractions
    (r'\b(i|you|we|they|he|she|it|that|what|would|could|should|had) d\b', r"\1'd"),
]


def fix_contractions(text: str) -> str:
    """修复 Whisper 转录中被拆开的缩写形式"""
    for pattern, replacement in CONTRACTION_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


class Transcriber:
    """视频转录服务 - 使用 openai-whisper"""

    # 常见的 FFmpeg 安装路径
    FFMPEG_PATHS = [
        "ffmpeg",  # PATH 环境变量中的 ffmpeg
        r"D:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"D:\Downloads\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe",
    ]

    def __init__(self, model_size: str = "small"):
        """
        初始化转录器

        Args:
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self) -> str:
        """查找 FFmpeg 可执行文件路径"""
        for path in self.FFMPEG_PATHS:
            if os.path.isfile(path) or (platform.system() == "Windows" and os.path.isfile(path)):
                print(f"Found FFmpeg at: {path}")
                return path
        print("Warning: FFmpeg not found in common locations. Using 'ffmpeg' command.")
        return "ffmpeg"

    def load_model(self):
        """加载Whisper模型"""
        try:
            import whisper

            self.model = whisper.load_model(self.model_size)
            print(f"Whisper model '{self.model_size}' loaded successfully")
        except ImportError:
            print("openai-whisper not installed. Using mock transcription.")
            self.model = None
        except Exception as e:
            print(f"Failed to load Whisper model (network issue or missing files): {e}")
            print("Using mock transcription instead.")
            self.model = None

    def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict:
        """
        转录音频文件

        Args:
            audio_path: 音频文件路径
            language: 语言代码 (默认英语)

        Returns:
            包含转录结果的字典
        """
        if self.model is None:
            self.load_model()

        if self.model is None:
            # 如果没有安装whisper，返回模拟数据
            return self._mock_transcription(audio_path)

        try:
            print(f"[Transcriber] Starting transcription of: {audio_path}")
            print(f"[Transcriber] Model: {self.model_size}, Language: {language}")

            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True  # 启用单词级时间戳
            )

            segments = []
            segment_count = 0
            for seg in result.get("segments", []):
                # 修复 Whisper 拆开的缩写
                fixed_text = fix_contractions(seg.get("text", "").strip())
                words = []
                for w in seg.get("words", []):
                    words.append({
                        "word": w.get("word", ""),
                        "start": w.get("start", 0.0),
                        "end": w.get("end", 0.0)
                    })
                segments.append({
                    "start": seg.get("start", 0.0),
                    "end": seg.get("end", 0.0),
                    "text": fixed_text,
                    "words": words
                })
                segment_count += 1
                if segment_count % 10 == 0:
                    print(f"[Transcriber] Processed {segment_count} segments...")

            print(f"[Transcriber] Transcription complete: {segment_count} segments")
            return {
                "language": result.get("language", language),
                "segments": segments
            }

        except Exception as e:
            print(f"[Transcriber] Transcription error: {e}")
            raise

    def extract_audio_from_video(self, video_path: str, output_path: str = None) -> str:
        """
        从视频中提取音频

        Args:
            video_path: 视频文件路径
            output_path: 输出音频路径（可选）

        Returns:
            音频文件路径
        """
        import subprocess

        if output_path is None:
            output_path = video_path.rsplit('.', 1)[0] + '.mp3'

        cmd = [
            self.ffmpeg_path, '-i', video_path,
            '-vn',  # 无视频
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-y',  # 覆盖输出
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Audio extracted to: {output_path}")
            return output_path
        except FileNotFoundError:
            raise Exception("FFmpeg not found. Please install FFmpeg first.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error: {e.stderr.decode()}")

    def _mock_transcription(self, audio_path: str) -> Dict:
        """模拟转录结果（用于测试）"""
        return {
            "language": "en",
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.5,
                    "text": "The quick brown fox jumps over the lazy dog",
                    "words": [
                        {"word": "The", "start": 0.0, "end": 0.2},
                        {"word": "quick", "start": 0.2, "end": 0.6},
                        {"word": "brown", "start": 0.6, "end": 1.0},
                        {"word": "fox", "start": 1.0, "end": 1.4},
                        {"word": "jumps", "start": 1.4, "end": 1.8},
                        {"word": "over", "start": 1.8, "end": 2.1},
                        {"word": "the", "start": 2.1, "end": 2.2},
                        {"word": "lazy", "start": 2.2, "end": 2.4},
                        {"word": "dog", "start": 2.4, "end": 2.5}
                    ]
                },
                {
                    "start": 2.5,
                    "end": 5.0,
                    "text": "This is a sample transcription for testing purposes",
                    "words": [
                        {"word": "This", "start": 2.5, "end": 2.7},
                        {"word": "is", "start": 2.7, "end": 2.9},
                        {"word": "a", "start": 2.9, "end": 3.0},
                        {"word": "sample", "start": 3.0, "end": 3.4},
                        {"word": "transcription", "start": 3.4, "end": 4.0},
                        {"word": "for", "start": 4.0, "end": 4.2},
                        {"word": "testing", "start": 4.2, "end": 4.6},
                        {"word": "purposes", "start": 4.6, "end": 5.0}
                    ]
                }
            ]
        }


# 创建全局实例（使用 small 模型，已有缓存）
transcriber = Transcriber(model_size="small")
