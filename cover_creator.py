# -*- coding: utf-8 -*-
"""
Создание обложек для Just Dance.
Cover creator for Just Dance.

Типы обложек: песня, альбом, мэшап.
Cover types: song, album, mashup.
"""

import os
import math
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

from pictogram_editor import load_image, save_image, resize_image


# Стандартные размеры обложек
COVER_SIZES = {
    "song": (256, 256),
    "album": (512, 512),
    "mashup": (512, 512),
    "banner": (1024, 256),
    "thumb": (128, 128),
}

COVER_SIZES_NAMES = {
    "song": "Song Cover (256x256)",
    "album": "Album Cover (512x512)",
    "mashup": "Mashup Cover (512x512)",
    "banner": "Banner (1024x256)",
    "thumb": "Thumbnail (128x128)",
}

# Предустановленные шаблоны фона
BG_TEMPLATES = {
    "gradient_blue": {"name_ru": "Синий градиент", "name_en": "Blue Gradient",
                       "start": (20, 30, 80), "end": (10, 10, 40)},
    "gradient_purple": {"name_ru": "Фиолетовый градиент", "name_en": "Purple Gradient",
                         "start": (80, 20, 80), "end": (30, 10, 50)},
    "gradient_orange": {"name_ru": "Оранжевый градиент", "name_en": "Orange Gradient",
                         "start": (200, 100, 20), "end": (80, 30, 10)},
    "gradient_green": {"name_ru": "Зелёный градиент", "name_en": "Green Gradient",
                        "start": (20, 100, 50), "end": (10, 40, 20)},
    "solid_black": {"name_ru": "Чёрный", "name_en": "Black",
                     "start": (0, 0, 0), "end": (0, 0, 0)},
    "solid_white": {"name_ru": "Белый", "name_en": "White",
                     "start": (255, 255, 255), "end": (255, 255, 255)},
}


def create_gradient_bg(width: int, height: int,
                        start_color: Tuple[int,int,int],
                        end_color: Tuple[int,int,int],
                        direction: str = "vertical") -> Image.Image:
    """
    Создать градиентный фон / Create gradient background.
    direction: 'vertical', 'horizontal', 'diagonal'
    """
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)
    if direction == "horizontal":
        for x in range(width):
            t = x / max(width - 1, 1)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))
    elif direction == "diagonal":
        for y in range(height):
            for x in range(0, width, 2):
                t = (x / max(width - 1, 1) + y / max(height - 1, 1)) / 2
                r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
                draw.point([(x, y), (x+1, y)], fill=(r, g, b, 255))
    else:  # vertical
        for y in range(height):
            t = y / max(height - 1, 1)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return bg


def get_font(size: int = 24, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Получить шрифт / Get font."""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial_Bold.ttf" if bold else "C:/Windows/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def create_cover(cover_type: str = "song",
                 title: str = "",
                 subtitle: str = "",
                 bg_template: str = "gradient_blue",
                 bg_image_path: Optional[str] = None,
                 overlay_image_path: Optional[str] = None,
                 coach_image_path: Optional[str] = None,
                 logo_image_path: Optional[str] = None,
                 font_size: int = 24,
                 font_color: Tuple[int,int,int] = (255, 255, 255),
                 title_pos: str = "bottom",
                 overlay_opacity: int = 200,
                 output_path: str = "cover.png",
                 custom_size: Optional[Tuple[int,int]] = None,
                 bg_direction: str = "vertical") -> bool:
    """
    Создать обложку / Create cover.

    Args:
        cover_type: "song", "album", "mashup", "banner", "thumb"
        title: заголовок
        subtitle: подзаголовок
        bg_template: ключ из BG_TEMPLATES
        bg_image_path: путь к изображению фона (если None — градиент)
        overlay_image_path: наложение поверх фона
        coach_image_path: изображение коуча
        logo_image_path: логотип
        font_size: размер шрифта
        font_color: цвет шрифта
        title_pos: "top", "center", "bottom"
        overlay_opacity: непрозрачность наложения (0-255)
        output_path: путь сохранения
        custom_size: кастомный размер (width, height)
        bg_direction: направление градиента
    Returns:
        True при успехе
    """
    size = custom_size or COVER_SIZES.get(cover_type, (256, 256))
    width, height = size

    # 1. Фон
    if bg_image_path and os.path.exists(bg_image_path):
        bg = load_image(bg_image_path)
        if bg:
            bg = resize_image(bg, width, height, "crop")
        else:
            template = BG_TEMPLATES.get(bg_template, BG_TEMPLATES["gradient_blue"])
            bg = create_gradient_bg(width, height, template["start"], template["end"], bg_direction)
    else:
        template = BG_TEMPLATES.get(bg_template, BG_TEMPLATES["gradient_blue"])
        bg = create_gradient_bg(width, height, template["start"], template["end"], bg_direction)

    # 2. Наложение
    if overlay_image_path and os.path.exists(overlay_image_path):
        overlay = load_image(overlay_image_path)
        if overlay:
            overlay = resize_image(overlay, width, height, "stretch")
            overlay = overlay.point(lambda p: p if isinstance(p, int) and p < 256 else p)
            # Регулируем непрозрачность
            r, g, b, a = overlay.split()
            a = a.point(lambda x: int(x * overlay_opacity / 255))
            overlay.putalpha(a)
            bg = Image.alpha_composite(bg, overlay)

    # 3. Коуч
    if coach_image_path and os.path.exists(coach_image_path):
        coach = load_image(coach_image_path)
        if coach:
            coach_w = int(width * 0.7)
            coach_h = int(height * 0.9)
            coach = resize_image(coach, coach_w, coach_h, "fit")
            x = (width - coach.width) // 2
            y = (height - coach.height) // 2
            bg.paste(coach, (x, y), coach)

    # 4. Логотип
    if logo_image_path and os.path.exists(logo_image_path):
        logo = load_image(logo_image_path)
        if logo:
            logo_w = int(width * 0.3)
            logo_h = int(logo.height * (logo_w / max(logo.width, 1)))
            logo = resize_image(logo, logo_w, logo_h, "stretch")
            bg.paste(logo, (width - logo.width - 10, 10), logo)

    # 5. Текст
    if title or subtitle:
        draw = ImageDraw.Draw(bg)
        font_title = get_font(font_size, bold=True)
        font_sub = get_font(max(font_size - 6, 10), bold=False)

        # Позиция текста
        if title_pos == "top":
            y_start = 10
        elif title_pos == "center":
            y_start = (height - font_size * 3) // 2
        else:  # bottom
            y_start = height - font_size * 3 - 10

        # Тень для текста
        if title:
            shadow_offset = 2
            # Тень
            draw.text((width // 2 + shadow_offset, y_start + shadow_offset),
                      title, fill=(0, 0, 0, 180), font=font_title, anchor="mm")
            # Основной текст
            draw.text((width // 2, y_start), title, fill=(*font_color, 255),
                      font=font_title, anchor="mm")
            y_start += font_size + 4

        if subtitle:
            shadow_offset = 1
            draw.text((width // 2 + shadow_offset, y_start + shadow_offset),
                      subtitle, fill=(0, 0, 0, 160), font=font_sub, anchor="mm")
            draw.text((width // 2, y_start), subtitle, fill=(*font_color, 220),
                      font=font_sub, anchor="mm")

    return save_image(bg, output_path)


def create_mashup_cover(title: str = "MASHUP",
                          subtitle: str = "",
                          coach_paths: Optional[List[str]] = None,
                          bg_template: str = "gradient_purple",
                          font_size: int = 28,
                          font_color: Tuple[int,int,int] = (255, 255, 255),
                          output_path: str = "mashup_cover.png",
                          custom_size: Optional[Tuple[int,int]] = None) -> bool:
    """
    Создать обложку мэшапа с несколькими коучами / Create mashup cover with multiple coaches.
    """
    size = custom_size or COVER_SIZES["mashup"]
    width, height = size

    template = BG_TEMPLATES.get(bg_template, BG_TEMPLATES["gradient_purple"])
    bg = create_gradient_bg(width, height, template["start"], template["end"], "diagonal")

    # Добавляем коучей
    if coach_paths:
        n = min(len(coach_paths), 4)
        coach_w = width // (n + 1)
        for i in range(n):
            coach = load_image(coach_paths[i])
            if coach:
                coach = resize_image(coach, coach_w, int(height * 0.7), "fit")
                x = (i + 1) * (width // (n + 1)) - coach.width // 2
                y = (height - coach.height) // 2 + 10
                bg.paste(coach, (x, y), coach)

    # Текст
    draw = ImageDraw.Draw(bg)
    font = get_font(font_size, bold=True)

    # Полоса для текста
    overlay = Image.new("RGBA", (width, font_size + 16), (0, 0, 0, 120))
    bg.paste(overlay, (0, height - font_size - 20), overlay)

    draw.text((width // 2, height - font_size - 12), title,
              fill=(*font_color, 255), font=font, anchor="mm")
    if subtitle:
        font_sub = get_font(max(font_size - 8, 10), bold=False)
        draw.text((width // 2, height - 12), subtitle,
                  fill=(*font_color, 200), font=font_sub, anchor="mm")

    return save_image(bg, output_path)
