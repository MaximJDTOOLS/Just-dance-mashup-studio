# -*- coding: utf-8 -*-
"""
Создание коучей для Just Dance.
Coach creator for Just Dance.

Коуч — это изображение силуэта танцора, извлечённое из кадра видео.
Coach is a dancer silhouette image extracted from a video frame.
"""

import os
import math
import tempfile
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops

from pictogram_editor import (
    load_image, save_image, remove_background, chroma_key,
    add_outline, resize_image, rotate_image, flip_image
)
from media_converter import extract_frames, get_media_info


# Стандартные размеры коучей Just Dance
COACH_SIZES = {
    "full": (1024, 1024),
    "standard": (512, 512),
    "small": (256, 256),
    "preview": (128, 128),
}

COACH_SIZES_NAMES = {
    "full": "Full (1024x1024)",
    "standard": "Standard (512x512)",
    "small": "Small (256x256)",
    "preview": "Preview (128x128)",
}


def extract_coach_from_frame(frame_path: str,
                              bg_color: Optional[Tuple[int,int,int]] = None,
                              tolerance: int = 30,
                              smooth_edges: bool = True,
                              outline_color: Optional[Tuple[int,int,int]] = None,
                              outline_width: int = 3,
                              coach_color: Optional[Tuple[int,int,int]] = None) -> Optional[Image.Image]:
    """
    Извлечь коуча из кадра / Extract coach from frame.
    Удаляет фон, добавляет контур и заливку.
    """
    img = load_image(frame_path)
    if img is None:
        return None

    # Удаляем фон
    img = remove_background(img, bg_color, tolerance, smooth_edges)

    # Если указан цвет коуча — заливаем силуэт
    if coach_color is not None:
        r, g, b, a = img.split()
        filled = Image.new("RGBA", img.size, (*coach_color, 255))
        filled.putalpha(a)
        img = filled

    # Добавляем контур
    if outline_color is not None or outline_width > 0:
        oc = outline_color or (255, 255, 255)
        img = add_outline(img, oc, outline_width)

    return img


def extract_coach_from_video(video_path: str,
                              output_dir: str,
                              frame_time: float = 0.0,
                              bg_color: Optional[Tuple[int,int,int]] = None,
                              tolerance: int = 30,
                              smooth_edges: bool = True,
                              outline_color: Optional[Tuple[int,int,int]] = None,
                              outline_width: int = 3,
                              coach_color: Optional[Tuple[int,int,int]] = None,
                              size_key: str = "standard",
                              coach_name: str = "coach") -> Optional[str]:
    """
    Извлечь коуча из видео / Extract coach from video.
    Извлекает кадр по времени, удаляет фон, сохраняет результат.
    """
    # Извлекаем кадр
    frames = extract_frames(video_path, output_dir, start_time=frame_time, count=1, prefix=coach_name)
    if not frames:
        return None

    frame_path = frames[0]
    coach = extract_coach_from_frame(
        frame_path, bg_color, tolerance, smooth_edges,
        outline_color, outline_width, coach_color
    )
    if coach is None:
        return None

    # Ресайз
    target_size = COACH_SIZES.get(size_key, COACH_SIZES["standard"])
    coach = resize_image(coach, target_size[0], target_size[1], fit_mode="fit")

    # Сохраняем
    output_path = os.path.join(output_dir, f"{coach_name}.png")
    if save_image(coach, output_path):
        # Удаляем промежуточный кадр
        try:
            os.unlink(frame_path)
        except Exception:
            pass
        return output_path
    return None


def extract_multiple_poses(video_path: str, output_dir: str,
                             pose_times: List[float],
                             bg_color: Optional[Tuple[int,int,int]] = None,
                             tolerance: int = 30,
                             smooth_edges: bool = True,
                             outline_color: Optional[Tuple[int,int,int]] = None,
                             outline_width: int = 3,
                             coach_color: Optional[Tuple[int,int,int]] = None,
                             size_key: str = "standard",
                             coach_name: str = "coach") -> List[str]:
    """
    Извлечь несколько поз коуча / Extract multiple coach poses.
    """
    results = []
    for i, t in enumerate(pose_times):
        name = f"{coach_name}_pose{i+1}"
        path = extract_coach_from_video(
            video_path, output_dir, t, bg_color, tolerance,
            smooth_edges, outline_color, outline_width,
            coach_color, size_key, name
        )
        if path:
            results.append(path)
    return results


def create_coach_sprite_sheet(coach_paths: List[str],
                               output_path: str,
                               columns: int = 4,
                               padding: int = 10,
                               bg_color: Tuple[int,int,int,int] = (0, 0, 0, 0)) -> bool:
    """
    Создать спрайт-лист коучей / Create coach sprite sheet.
    """
    if not coach_paths:
        return False

    images = [load_image(p) for p in coach_paths]
    images = [img for img in images if img is not None]
    if not images:
        return False

    cell_w = max(img.width for img in images) + padding * 2
    cell_h = max(img.height for img in images) + padding * 2
    rows = math.ceil(len(images) / columns)

    sheet = Image.new("RGBA", (cell_w * columns, cell_h * rows), bg_color)
    for i, img in enumerate(images):
        col = i % columns
        row = i // columns
        x = col * cell_w + (cell_w - img.width) // 2
        y = row * cell_h + (cell_h - img.height) // 2
        sheet.paste(img, (x, y), img)

    return save_image(sheet, output_path)


def apply_coach_glow(img: Image.Image,
                     glow_color: Tuple[int,int,int] = (255, 200, 50),
                     glow_radius: int = 10) -> Image.Image:
    """
    Добавить свечение коучу / Add glow to coach.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.split()[3]
    glow = Image.new("RGBA", img.size, (*glow_color, 0))
    glow_alpha = alpha.filter(ImageFilter.GaussianBlur(radius=glow_radius))
    glow_alpha = glow_alpha.point(lambda x: int(x * 0.6))
    glow.putalpha(glow_alpha)
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(glow, (0, 0), glow)
    result.paste(img, (0, 0), img)
    return result
