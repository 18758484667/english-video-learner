from typing import List, Dict


def format_timestamp(seconds: float) -> str:
    """
    格式化时间为 WebVTT 格式 (HH:MM:SS.mmm)

    Args:
        seconds: 秒数

    Returns:
        格式化的时间字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def convert_to_vtt(segments: List[Dict], translations: List[str] = None) -> str:
    """
    将转录结果转换为WebVTT格式

    Args:
        segments: 转录片段列表
        translations: 对应的翻译列表（可选）

    Returns:
        WebVTT格式的字符串
    """
    vtt_lines = ["WEBVTT\n"]

    for i, segment in enumerate(segments):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])

        english = segment['text']
        chinese = translations[i] if translations and i < len(translations) else ''

        vtt_lines.append(f"{start} --> {end}")
        vtt_lines.append(english)
        if chinese:
            vtt_lines.append(chinese)
        vtt_lines.append("")

    return "\n".join(vtt_lines)


def convert_to_json(segments: List[Dict], translations: List[str] = None) -> List[Dict]:
    """
    将转录结果转换为JSON格式（供前端使用）

    Args:
        segments: 转录片段列表
        translations: 对应的翻译列表（可选）

    Returns:
        JSON格式的字幕列表
    """
    subtitles = []

    for i, segment in enumerate(segments):
        subtitle = {
            "id": i + 1,
            "start": segment['start'],
            "end": segment['end'],
            "english": segment['text'],
            "chinese_translation": translations[i] if translations and i < len(translations) else "",
            "words": segment.get('words', [])
        }
        subtitles.append(subtitle)

    return subtitles


def merge_word_timestamps(segments: List[Dict]) -> List[Dict]:
    """
    合并单词级时间戳到句子级别

    Args:
        segments: 包含单词时间戳的转录片段

    Returns:
        合并后的片段列表
    """
    merged = []

    for segment in segments:
        words = segment.get('words', [])

        if words:
            # 使用第一个和最后一个单词的时间戳
            merged_segment = {
                'start': words[0]['start'],
                'end': words[-1]['end'],
                'text': segment['text'],
                'words': words
            }
            merged.append(merged_segment)
        else:
            merged.append(segment)

    return merged
