# -*- coding: utf-8 -*-
"""
Редактор пиктограмм для Just Dance.
Pictogram editor for Just Dance.

Поддерживаемые форматы / Supported formats: TGA, PNG, JPEG, BMP, GIF, TIFF
"""

import os
import math
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageChops


# Поддерживаемые форматы изображений
IMAGE_FORMATS = ["tga", "png", "jpeg", "jpg", "bmp", "gif", "tiff"]
IMAGE_FORMAT_NAMES = {
    "tga": "TGA (Truevision Targa)",
    "png": "PNG (Portable Network Graphics)",
    "jpeg": "JPEG (Joint Photographic Experts Group)",
    "jpg": "JPEG (Joint Photographic Experts Group)",
    "bmp": "BMP (Bitmap)",
    "gif": "GIF (Graphics Interchange Format)",
    "tiff": "TIFF (Tagged Image File Format)",
}

# Типы пиктограмм Just Dance
PICTOGRAM_TYPES = {
    "normal": {"name_ru": "Обычная", "name_en": "Normal", "color": (255, 255, 255)},
    "gold": {"name_ru": "Золотая", "name_en": "Gold", "color": (255, 215, 0)},
    "fever": {"name_ru": "Fever", "name_en": "Fever", "color": (255, 100, 200)},
}


def load_image(filepath: str) -> Optional[Image.Image]:
    """Загрузить изображение / Load image."""
    try:
        img = Image.open(filepath)
        if img.mode == "P":
            img = img.convert("RGBA")
        elif img.mode == "L":
            img = img.convert("RGBA")
        elif img.mode == "RGB":
            img = img.convert("RGBA")
        return img
    except Exception:
        return None


def save_image(img: Image.Image, filepath: str, format_hint: Optional[str] = None) -> bool:
    """Сохранить изображение / Save image."""
    try:
        fmt = format_hint or os.path.splitext(filepath)[1].lstrip(".").upper()
        if fmt == "JPG":
            fmt = "JPEG"
        if fmt == "JPEG" and img.mode == "RGBA":
            # JPEG не поддерживает прозрачность
            background = Image.new("RGB", img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            img = background
        img.save(filepath, format=fmt if fmt else None)
        return True
    except Exception:
        return False


def resize_image(img: Image.Image, width: int, height: int,
                 fit_mode: str = "fit") -> Image.Image:
    """
    Изменить размер / Resize image.
    fit_mode: 'fit' (вписать), 'stretch' (растянуть), 'crop' (обрезать)
    """
    if fit_mode == "stretch":
        return img.resize((width, height), Image.LANCZOS)
    elif fit_mode == "crop":
        return ImageOps.fit(img, (width, height), Image.LANCZOS)
    else:  # fit
        img_ratio = img.width / img.height
        target_ratio = width / height
        if img_ratio > target_ratio:
            new_width = width
            new_height = int(width / img_ratio)
        else:
            new_height = height
            new_width = int(height * img_ratio)
        resized = img.resize((new_width, new_height), Image.LANCZOS)
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        offset = ((width - new_width) // 2, (height - new_height) // 2)
        result.paste(resized, offset)
        return result


def rotate_image(img: Image.Image, degrees: float) -> Image.Image:
    """Повернуть изображение / Rotate image."""
    return img.rotate(-degrees, expand=True, fillcolor=(0, 0, 0, 0))


def flip_image(img: Image.Image, mode: str) -> Image.Image:
    """
    Отразить изображение / Flip image.
    mode: 'horizontal', 'vertical', 'both'
    """
    if mode == "horizontal":
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    elif mode == "vertical":
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    elif mode == "both":
        return img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    return img


def remove_background(img: Image.Image, bg_color: Tuple[int,int,int] = None,
                      tolerance: int = 30, smooth_edges: bool = True) -> Image.Image:
    """
    Удалить фон по цвету / Remove background by color.
    Если bg_color не указан, используется цвет угловых пикселей.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    if bg_color is None:
        # Определяем цвет фона по угловым пикселям
        pixels = [
            img.getpixel((0, 0)),
            img.getpixel((img.width - 1, 0)),
            img.getpixel((0, img.height - 1)),
            img.getpixel((img.width - 1, img.height - 1)),
        ]
        # Средний цвет углов
        r = sum(p[0] for p in pixels) // len(pixels)
        g = sum(p[1] for p in pixels) // len(pixels)
        b = sum(p[2] for p in pixels) // len(pixels)
        bg_color = (r, g, b)

    data = img.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item[:4]
        # Расстояние до цвета фона
        dist = math.sqrt((r - bg_color[0])**2 + (g - bg_color[1])**2 + (b - bg_color[2])**2)
        if dist < tolerance:
            new_data.append((r, g, b, 0))
        elif dist < tolerance * 1.5:
            # Полупрозрачные края
            alpha = int(255 * (dist - tolerance) / (tolerance * 0.5))
            new_data.append((r, g, b, min(alpha, 255)))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)

    if smooth_edges:
        # Лёгкое размытие альфа-канала для сглаживания
        alpha = img.split()[3]
        alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1))
        img.putalpha(alpha)

    return img


def chroma_key(img: Image.Image, key_color: Tuple[int,int,int] = (0, 255, 0),
               tolerance: int = 40, smooth_edges: bool = True) -> Image.Image:
    """
    Хромакей — удалить фон указанного цвета / Chroma key.
    По умолчанию — зелёный экран.
    """
    return remove_background(img, key_color, tolerance, smooth_edges)


def add_outline(img: Image.Image, color: Tuple[int,int,int] = (0, 0, 0),
                width: int = 3) -> Image.Image:
    """
    Добавить контур / Add outline.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    alpha = img.split()[3]
    # Создаём контур из альфа-канала
    outline_mask = alpha.filter(ImageFilter.MaxFilter(size=width * 2 + 1))
    # Вычитаем оригинальный альфа
    outline_only = ImageChops.subtract(outline_mask, alpha)

    outline_img = Image.new("RGBA", img.size, (*color, 255))
    outline_img.putalpha(outline_only)

    # Композит: контур снизу, оригинал сверху
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(outline_img, (0, 0), outline_img)
    result.paste(img, (0, 0), img)
    return result


def set_transparency(img: Image.Image, opacity: int) -> Image.Image:
    """
    Установить прозрачность / Set transparency.
    opacity: 0 (полностью прозрачно) .. 255 (полностью непрозрачно)
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * opacity / 255))
    img.putalpha(a)
    return img


def add_grid(img: Image.Image, grid_size: int = 32,
              color: Tuple[int,int,int] = (200, 200, 200, 128)) -> Image.Image:
    """
    Добавить сетку / Add grid overlay.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(0, img.width, grid_size):
        draw.line([(x, 0), (x, img.height)], fill=color, width=1)
    for y in range(0, img.height, grid_size):
        draw.line([(0, y), (img.width, y)], fill=color, width=1)
    return Image.alpha_composite(img, overlay)


def replace_color(img: Image.Image, old_color: Tuple[int,int,int],
                  new_color: Tuple[int,int,int], tolerance: int = 20) -> Image.Image:
    """
    Заменить цвет / Replace color.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item[:4]
        dist = math.sqrt((r - old_color[0])**2 + (g - old_color[1])**2 + (b - old_color[2])**2)
        if dist < tolerance:
            new_data.append((*new_color, a))
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    return img


def apply_filter(img: Image.Image, filter_name: str) -> Image.Image:
    """
    Применить фильтр / Apply filter.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    if filter_name == "grayscale":
        return ImageOps.grayscale(img).convert("RGBA")
    elif filter_name == "blur":
        return img.filter(ImageFilter.GaussianBlur(radius=3))
    elif filter_name == "sharpen":
        return img.filter(ImageFilter.UnsharpMask(radius=3, percent=150, threshold=3))
    elif filter_name == "edges":
        gray = ImageOps.grayscale(img)
        return gray.filter(ImageFilter.FIND_EDGES).convert("RGBA")
    elif filter_name == "invert":
        return ImageOps.invert(img.convert("RGB")).convert("RGBA")
    return img


def apply_pictogram_style(img: Image.Image, style: str = "normal",
                           outline_color: Optional[Tuple[int,int,int]] = None,
                           outline_width: int = 3) -> Image.Image:
    """
    Применить стиль пиктограммы Just Dance / Apply JD pictogram style.
    """
    info = PICTOGRAM_TYPES.get(style, PICTOGRAM_TYPES["normal"])
    if style == "gold":
        # Золотое свечение
        tint = info["color"]
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        r, g, b, a = img.split()
        # Добавляем золотистый оттенок
        tinted = Image.new("RGBA", img.size, (*tint, 0))
        tinted.putalpha(a.point(lambda x: int(x * 0.3)))
        img = Image.alpha_composite(img, tinted)
        if outline_color is None:
            outline_color = (255, 215, 0)
        img = add_outline(img, outline_color, outline_width)
    elif style == "fever":
        # Розовое свечение
        tint = info["color"]
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        r, g, b, a = img.split()
        tinted = Image.new("RGBA", img.size, (*tint, 0))
        tinted.putalpha(a.point(lambda x: int(x * 0.4)))
        img = Image.alpha_composite(img, tinted)
        if outline_color is None:
            outline_color = (255, 100, 200)
        img = add_outline(img, outline_color, outline_width)
    else:
        # Обычная — просто контур
        if outline_color is None:
            outline_color = (255, 255, 255)
        img = add_outline(img, outline_color, outline_width)
    return img


def convert_image_format(input_path: str, output_path: str,
                          target_format: str = None) -> bool:
    """Конвертировать формат изображения / Convert image format."""
    img = load_image(input_path)
    if img is None:
        return False
    return save_image(img, output_path, target_format)


def get_image_info(filepath: str) -> dict:
    """Получить информацию об изображении / Get image info."""
    info = {"width": 0, "height": 0, "mode": "", "format": "", "size_bytes": 0}
    try:
        img = Image.open(filepath)
        info["width"] = img.width
        info["height"] = img.height
        info["mode"] = img.mode
        info["format"] = img.format or ""
        info["size_bytes"] = os.path.getsize(filepath)
    except Exception:
        pass
    return info
