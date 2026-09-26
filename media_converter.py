# -*- coding: utf-8 -*-
"""
Конвертер медиафайлов с поддержкой ffmpeg.
Media file converter with ffmpeg support.

Поддерживаемые форматы / Supported formats:
  Видео / Video: WEBM, MP4, AVI, MOV, MKV
  Аудио / Audio: WAV, MP3, OGG
  Изображения / Images: TGA, PNG, JPEG, BMP
"""

import os
import subprocess
import shutil
import json
import tempfile
import struct
import wave
from typing import Optional, Tuple, List


def find_ffmpeg() -> Optional[str]:
    """Найти путь к ffmpeg / Find ffmpeg path."""
    return shutil.which("ffmpeg")


def find_ffprobe() -> Optional[str]:
    """Найти путь к ffprobe / Find ffprobe path."""
    return shutil.which("ffprobe")


FFMPEG = find_ffmpeg()
FFPROBE = find_ffprobe()


class MediaInfo:
    """Информация о медиафайле / Media file info."""

    def __init__(self):
        self.duration = 0.0
        self.width = 0
        self.height = 0
        self.fps = 0.0
        self.codec = ""
        self.audio_codec = ""
        self.sample_rate = 0
        self.channels = 0
        self.has_video = False
        self.has_audio = False
        self.frames = 0

    def __repr__(self):
        return (
            f"MediaInfo(duration={self.duration}, "
            f"size={self.width}x{self.height}, "
            f"fps={self.fps}, codec={self.codec}, "
            f"audio={self.audio_codec}, "
            f"sr={self.sample_rate}, ch={self.channels})"
        )


def get_media_info(filepath: str) -> MediaInfo:
    """Получить информацию о медиафайле через ffprobe / Get media info via ffprobe."""
    info = MediaInfo()
    if not FFPROBE:
        return info
    try:
        cmd = [
            FFPROBE, "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        info.duration = float(fmt.get("duration", 0))
        for stream in data.get("streams", []):
            ct = stream.get("codec_type", "")
            if ct == "video":
                info.has_video = True
                info.width = int(stream.get("width", 0))
                info.height = int(stream.get("height", 0))
                info.codec = stream.get("codec_name", "")
                fps_str = stream.get("avg_frame_rate", "0/1")
                try:
                    num, den = fps_str.split("/")
                    info.fps = float(num) / float(den) if float(den) != 0 else 0.0
                except Exception:
                    info.fps = 0.0
                nb_frames = stream.get("nb_frames")
                if nb_frames:
                    info.frames = int(nb_frames)
                elif info.duration > 0 and info.fps > 0:
                    info.frames = int(info.duration * info.fps)
            elif ct == "audio":
                info.has_audio = True
                info.audio_codec = stream.get("codec_name", "")
                info.sample_rate = int(stream.get("sample_rate", 0))
                info.channels = int(stream.get("channels", 0))
    except Exception:
        pass
    return info


# ============================================================
# Конвертация видео / Video conversion
# ============================================================

VIDEO_FORMATS = ["webm", "mp4", "avi", "mov", "mkv"]
VIDEO_CODECS = {
    "webm": "libvpx-vp9",
    "mp4": "libx264",
    "avi": "mpeg4",
    "mov": "libx264",
    "mkv": "libx264",
}

VIDEO_FORMAT_NAMES = {
    "webm": "WebM (VP9)",
    "mp4": "MP4 (H.264)",
    "avi": "AVI (MPEG-4)",
    "mov": "MOV (H.264)",
    "mkv": "MKV (H.264)",
}


def convert_video(input_path: str, output_path: str, target_format: str,
                  codec: Optional[str] = None, bitrate: Optional[str] = None,
                  fps: Optional[float] = None, scale: Optional[Tuple[int,int]] = None,
                  progress_callback=None) -> bool:
    """
    Конвертировать видео / Convert video.

    Args:
        input_path: путь к исходному файлу
        output_path: путь к выходному файлу
        target_format: целевой формат (webm, mp4, avi, mov, mkv)
        codec: кодек (если None, выбирается автоматически)
        bitrate: битрейт (например "2M")
        fps: частота кадров
        scale: масштаб (width, height)
        progress_callback: функция callback(progress_float 0..1)
    Returns:
        True при успехе
    """
    if not FFMPEG:
        raise RuntimeError("FFmpeg not found")

    if codec is None:
        codec = VIDEO_CODECS.get(target_format, "libx264")

    cmd = [FFMPEG, "-y", "-i", input_path]

    # Видеофильтры
    vf_parts = []
    if scale:
        vf_parts.append(f"scale={scale[0]}:{scale[1]}")
    if fps:
        vf_parts.append(f"fps={fps}")
    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])

    cmd.extend(["-c:v", codec])
    if codec == "libx264":
        cmd.extend(["-preset", "medium", "-crf", "23"])
    if codec == "libvpx-vp9":
        cmd.extend(["-b:v", bitrate or "1M"])
    elif bitrate:
        cmd.extend(["-b:v", bitrate])

    # Аудио — всегда копируем/перекодируем в AAC
    cmd.extend(["-c:a", "libmp3lame" if target_format == "webm" else "aac",
                "-b:a", "192k"])

    cmd.append(output_path)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        return proc.returncode == 0
    except Exception:
        return False


def edit_video(input_path: str, output_path: str,
               start_time: Optional[float] = None,
               end_time: Optional[float] = None,
               speed: Optional[float] = None,
               brightness: Optional[float] = None,
               contrast: Optional[float] = None,
               saturation: Optional[float] = None,
               filters: Optional[List[str]] = None,
               target_format: Optional[str] = None) -> bool:
    """
    Редактировать видео / Edit video.

    Args:
        start_time: начало в секундах
        end_time: конец в секундах
        speed: скорость (1.0 = нормальная)
        brightness: яркость (-1.0..1.0)
        contrast: контраст (-1.0..1.0)
        saturation: насыщенность (-1.0..1.0)
        filters: список фильтров (grayscale, blur, sharpen, edges, invert)
        target_format: целевой формат выходного файла
    Returns:
        True при успехе
    """
    if not FFMPEG:
        raise RuntimeError("FFmpeg not found")

    cmd = [FFMPEG, "-y"]

    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    cmd.extend(["-i", input_path])
    if end_time is not None and start_time is not None:
        cmd.extend(["-t", str(end_time - start_time)])
    elif end_time is not None:
        cmd.extend(["-t", str(end_time)])

    # Видеофильтры
    vf_parts = []
    if speed and speed != 1.0:
        vf_parts.append(f"setpts={1.0/speed}*PTS")
    if brightness is not None:
        vf_parts.append(f"eq=brightness={brightness}")
    if contrast is not None:
        vf_parts.append(f"eq=contrast={max(0, 1.0 + contrast)}")
    if saturation is not None:
        vf_parts.append(f"eq=saturation={max(0, 1.0 + saturation)}")
    if filters:
        for f in filters:
            if f == "grayscale":
                vf_parts.append("hue=s=0")
            elif f == "blur":
                vf_parts.append("boxblur=5:1")
            elif f == "sharpen":
                vf_parts.append("unsharp=5:5:1.0:5:5:0.0")
            elif f == "edges":
                vf_parts.append("edge_detect")
            elif f == "invert":
                vf_parts.append("negate")

    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])

    # Аудио — корректируем скорость
    if speed and speed != 1.0:
        cmd.extend(["-af", f"atempo={speed}"])

    # Кодек
    fmt = target_format or os.path.splitext(output_path)[1].lstrip(".")
    codec = VIDEO_CODECS.get(fmt, "libx264")
    cmd.extend(["-c:v", codec, "-c:a", "aac", "-b:a", "192k"])
    cmd.append(output_path)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        return proc.returncode == 0
    except Exception:
        return False


def merge_videos(input_paths: List[str], output_path: str,
                 target_format: Optional[str] = None) -> bool:
    """
    Объединить несколько видео / Merge multiple videos.
    """
    if not FFMPEG or not input_paths:
        return False

    # Создаём файл-список
    list_fd, list_path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(list_fd, "w") as f:
        for p in input_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
           "-c", "copy", output_path]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        ok = proc.returncode == 0
    except Exception:
        ok = False
    finally:
        os.unlink(list_path)
    return ok


def extract_frames(input_path: str, output_dir: str,
                   start_time: float = 0, count: int = 1,
                   prefix: str = "frame") -> List[str]:
    """
    Извлечь кадры из видео / Extract frames from video.
    """
    if not FFMPEG:
        return []
    os.makedirs(output_dir, exist_ok=True)
    pattern = os.path.join(output_dir, f"{prefix}_%04d.png")
    cmd = [FFMPEG, "-y", "-ss", str(start_time), "-i", input_path,
           "-frames:v", str(count), "-q:v", "2", pattern]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if proc.returncode == 0:
            return sorted([
                os.path.join(output_dir, f) for f in os.listdir(output_dir)
                if f.startswith(prefix) and f.endswith(".png")
            ])
    except Exception:
        pass
    return []


# ============================================================
# Конвертация аудио / Audio conversion
# ============================================================

AUDIO_FORMATS = ["wav", "mp3", "ogg"]
AUDIO_CODECS = {
    "wav": "pcm_s16le",
    "mp3": "libmp3lame",
    "ogg": "libvorbis",
}

AUDIO_FORMAT_NAMES = {
    "wav": "WAV (PCM)",
    "mp3": "MP3 (MPEG)",
    "ogg": "OGG (Vorbis)",
}


def convert_audio(input_path: str, output_path: str, target_format: str,
                  bitrate: Optional[str] = None,
                  sample_rate: Optional[int] = None,
                  channels: Optional[int] = None) -> bool:
    """
    Конвертировать аудио / Convert audio.
    """
    if not FFMPEG:
        raise RuntimeError("FFmpeg not found")

    codec = AUDIO_CODECS.get(target_format, "pcm_s16le")
    cmd = [FFMPEG, "-y", "-i", input_path, "-c:a", codec]
    if bitrate and target_format != "wav":
        cmd.extend(["-b:a", bitrate])
    if sample_rate:
        cmd.extend(["-ar", str(sample_rate)])
    if channels:
        cmd.extend(["-ac", str(channels)])
    cmd.append(output_path)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        return proc.returncode == 0
    except Exception:
        return False


def edit_audio(input_path: str, output_path: str,
               start_time: Optional[float] = None,
               end_time: Optional[float] = None,
               speed: Optional[float] = None,
               volume: Optional[float] = None,
               target_format: Optional[str] = None) -> bool:
    """
    Редактировать аудио / Edit audio.
    """
    if not FFMPEG:
        raise RuntimeError("FFmpeg not found")

    cmd = [FFMPEG, "-y"]
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    cmd.extend(["-i", input_path])
    if end_time is not None and start_time is not None:
        cmd.extend(["-t", str(end_time - start_time)])
    elif end_time is not None:
        cmd.extend(["-t", str(end_time)])

    af_parts = []
    if speed and speed != 1.0:
        af_parts.append(f"atempo={speed}")
    if volume is not None and volume != 1.0:
        af_parts.append(f"volume={volume}")
    if af_parts:
        cmd.extend(["-af", ",".join(af_parts)])

    fmt = target_format or os.path.splitext(output_path)[1].lstrip(".")
    codec = AUDIO_CODECS.get(fmt, "pcm_s16le")
    cmd.extend(["-c:a", codec])
    cmd.append(output_path)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        return proc.returncode == 0
    except Exception:
        return False


def merge_audio(input_paths: List[str], output_path: str,
                 target_format: Optional[str] = None) -> bool:
    """
    Объединить аудиофайлы / Merge audio files.
    """
    if not FFMPEG or not input_paths:
        return False

    list_fd, list_path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(list_fd, "w") as f:
        for p in input_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    fmt = target_format or os.path.splitext(output_path)[1].lstrip(".")
    codec = AUDIO_CODECS.get(fmt, "pcm_s16le")

    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
           "-c:a", codec, output_path]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        ok = proc.returncode == 0
    except Exception:
        ok = False
    finally:
        os.unlink(list_path)
    return ok


def get_wav_info(filepath: str) -> dict:
    """Получить информацию о WAV файле / Get WAV file info (без ffmpeg)."""
    info = {"duration": 0.0, "channels": 0, "sample_rate": 0, "frames": 0}
    try:
        with wave.open(filepath, "rb") as wf:
            info["channels"] = wf.getnchannels()
            info["sample_rate"] = wf.getframerate()
            info["frames"] = wf.getnframes()
            info["duration"] = info["frames"] / info["sample_rate"] if info["sample_rate"] > 0 else 0
    except Exception:
        pass
    return info


# ============================================================
# Общий конвертер / Universal converter
# ============================================================

def convert_media(input_path: str, output_path: str,
                  target_format: Optional[str] = None,
                  **kwargs) -> bool:
    """
    Универсальная конвертация / Universal conversion.
    Определяет тип файла и вызывает соответствующую функцию.
    """
    ext = (target_format or os.path.splitext(output_path)[1]).lstrip(".").lower()

    if ext in VIDEO_FORMATS:
        return convert_video(input_path, output_path, ext, **kwargs)
    elif ext in AUDIO_FORMATS:
        return convert_audio(input_path, output_path, ext, **kwargs)
    else:
        # Пробуем как видео (ffmpeg сам разберётся)
        if not FFMPEG:
            raise RuntimeError("FFmpeg not found")
        cmd = [FFMPEG, "-y", "-i", input_path, output_path]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            return proc.returncode == 0
        except Exception:
            return False


def check_ffmpeg() -> bool:
    """Проверить доступность ffmpeg / Check ffmpeg availability."""
    return FFMPEG is not None
