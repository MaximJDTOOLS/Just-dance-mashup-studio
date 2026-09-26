# -*- coding: utf-8 -*-
"""
Локализация / Localization
Поддержка русского и английского языков.
Support for Russian and English languages.
"""

LANG_RU = "ru"
LANG_EN = "en"

# Все строки интерфейса / All UI strings
STRINGS = {
    # --- Меню / Menu ---
    "menu_file": {
        "ru": "Файл",
        "en": "File"
    },
    "menu_new_project": {
        "ru": "Новый проект",
        "en": "New Project"
    },
    "menu_open_project": {
        "ru": "Открыть проект",
        "en": "Open Project"
    },
    "menu_save_project": {
        "ru": "Сохранить проект",
        "en": "Save Project"
    },
    "menu_save_as": {
        "ru": "Сохранить как...",
        "en": "Save As..."
    },
    "menu_export": {
        "ru": "Экспорт мэшапа",
        "en": "Export Mashup"
    },
    "menu_exit": {
        "ru": "Выход",
        "en": "Exit"
    },
    "menu_edit": {
        "ru": "Правка",
        "en": "Edit"
    },
    "menu_language": {
        "ru": "Язык",
        "en": "Language"
    },
    "menu_lang_ru": {
        "ru": "Русский",
        "en": "Russian"
    },
    "menu_lang_en": {
        "ru": "English",
        "en": "English"
    },
    "menu_tools": {
        "ru": "Инструменты",
        "en": "Tools"
    },
    "menu_video_editor": {
        "ru": "Редактор видео",
        "en": "Video Editor"
    },
    "menu_audio_editor": {
        "ru": "Редактор аудио",
        "en": "Audio Editor"
    },
    "menu_pictogram_editor": {
        "ru": "Редактор пиктограмм",
        "en": "Pictogram Editor"
    },
    "menu_coach_creator": {
        "ru": "Создание коуча",
        "en": "Coach Creator"
    },
    "menu_cover_creator": {
        "ru": "Создание обложки",
        "en": "Cover Creator"
    },
    "menu_converter": {
        "ru": "Конвертер форматов",
        "en": "Format Converter"
    },
    "menu_timeline": {
        "ru": "Таймлайн",
        "en": "Timeline"
    },
    "menu_help": {
        "ru": "Справка",
        "en": "Help"
    },
    "menu_about": {
        "ru": "О программе",
        "en": "About"
    },

    # --- Кнопки / Buttons ---
    "btn_add": {"ru": "Добавить", "en": "Add"},
    "btn_remove": {"ru": "Удалить", "en": "Remove"},
    "btn_apply": {"ru": "Применить", "en": "Apply"},
    "btn_cancel": {"ru": "Отмена", "en": "Cancel"},
    "btn_ok": {"ru": "OK", "en": "OK"},
    "btn_save": {"ru": "Сохранить", "en": "Save"},
    "btn_load": {"ru": "Загрузить", "en": "Load"},
    "btn_convert": {"ru": "Конвертировать", "en": "Convert"},
    "btn_preview": {"ru": "Предпросмотр", "en": "Preview"},
    "btn_export": {"ru": "Экспорт", "en": "Export"},
    "btn_import": {"ru": "Импорт", "en": "Import"},
    "btn_close": {"ru": "Закрыть", "en": "Close"},
    "btn_browse": {"ru": "Обзор...", "en": "Browse..."},
    "btn_create": {"ru": "Создать", "en": "Create"},
    "btn_add_to_timeline": {"ru": "Добавить в таймлайн", "en": "Add to Timeline"},

    # --- Заголовки / Labels ---
    "lbl_title": {"ru": "Just Dance Mashup Studio", "en": "Just Dance Mashup Studio"},
    "lbl_video_tracks": {"ru": "Видеодорожки", "en": "Video Tracks"},
    "lbl_audio_tracks": {"ru": "Аудиодорожки", "en": "Audio Tracks"},
    "lbl_pictogram_tracks": {"ru": "Дорожки пиктограмм", "en": "Pictogram Tracks"},
    "lbl_input_file": {"ru": "Входной файл", "en": "Input File"},
    "lbl_output_file": {"ru": "Выходной файл", "en": "Output File"},
    "lbl_format": {"ru": "Формат", "en": "Format"},
    "lbl_start_time": {"ru": "Начало (сек)", "en": "Start (sec)"},
    "lbl_end_time": {"ru": "Конец (сек)", "en": "End (sec)"},
    "lbl_speed": {"ru": "Скорость", "en": "Speed"},
    "lbl_volume": {"ru": "Громкость", "en": "Volume"},
    "lbl_brightness": {"ru": "Яркость", "en": "Brightness"},
    "lbl_contrast": {"ru": "Контраст", "en": "Contrast"},
    "lbl_saturation": {"ru": "Насыщенность", "en": "Saturation"},
    "lbl_rotate": {"ru": "Поворот (град)", "en": "Rotate (deg)"},
    "lbl_resize": {"ru": "Размер", "en": "Resize"},
    "lbl_flip": {"ru": "Отражение", "en": "Flip"},
    "lbl_remove_bg": {"ru": "Удалить фон", "en": "Remove Background"},
    "lbl_outline": {"ru": "Контур", "en": "Outline"},
    "lbl_transparency": {"ru": "Прозрачность", "en": "Transparency"},
    "lbl_grid": {"ru": "Сетка", "en": "Grid"},
    "lbl_replace_color": {"ru": "Замена цвета", "en": "Replace Color"},
    "lbl_filter": {"ru": "Фильтр", "en": "Filter"},
    "lbl_width": {"ru": "Ширина", "en": "Width"},
    "lbl_height": {"ru": "Высота", "en": "Height"},
    "lbl_bg_color": {"ru": "Цвет фона", "en": "Background Color"},
    "lbl_outline_color": {"ru": "Цвет контура", "en": "Outline Color"},
    "lbl_outline_width": {"ru": "Толщина контура", "en": "Outline Width"},

    # --- Coach Creator ---
    "lbl_coach_source": {"ru": "Источник (видео/изображение)", "en": "Source (video/image)"},
    "lbl_coach_name": {"ru": "Имя коуча", "en": "Coach Name"},
    "lbl_coach_color": {"ru": "Цвет коуча", "en": "Coach Color"},
    "lbl_extract_frame": {"ru": "Извлечь кадр", "en": "Extract Frame"},
    "lbl_chroma_key": {"ru": "Хромакей (зелёный фон)", "en": "Chroma Key (green screen)"},
    "lbl_tolerance": {"ru": "Допуск цвета", "en": "Color Tolerance"},
    "lbl_smooth_edges": {"ru": "Сгладить края", "en": "Smooth Edges"},
    "lbl_coach_output": {"ru": "Папка вывода", "en": "Output Folder"},
    "lbl_coach_preview": {"ru": "Предпросмотр коуча", "en": "Coach Preview"},
    "lbl_coach_pose": {"ru": "Поза (номер кадра)", "en": "Pose (frame number)"},
    "lbl_coach silhouette": {"ru": "Силуэт", "en": "Silhouette"},

    # --- Cover Creator ---
    "lbl_cover_type": {"ru": "Тип обложки", "en": "Cover Type"},
    "lbl_cover_song": {"ru": "Обложка песни", "en": "Song Cover"},
    "lbl_cover_album": {"ru": "Обложка альбома", "en": "Album Cover"},
    "lbl_cover_mashup": {"ru": "Обложка мэшапа", "en": "Mashup Cover"},
    "lbl_cover_background": {"ru": "Фон обложки", "en": "Cover Background"},
    "lbl_cover_title": {"ru": "Заголовок", "en": "Title"},
    "lbl_cover_subtitle": {"ru": "Подзаголовок", "en": "Subtitle"},
    "lbl_cover_font": {"ru": "Шрифт", "en": "Font"},
    "lbl_cover_font_size": {"ru": "Размер шрифта", "en": "Font Size"},
    "lbl_cover_font_color": {"ru": "Цвет шрифта", "en": "Font Color"},
    "lbl_cover_logo": {"ru": "Логотип", "en": "Logo"},
    "lbl_cover_image": {"ru": "Изображение", "en": "Image"},

    # --- Сообщения / Messages ---
    "msg_saved": {"ru": "Сохранено успешно", "en": "Saved successfully"},
    "msg_loaded": {"ru": "Загружено успешно", "en": "Loaded successfully"},
    "msg_converted": {"ru": "Конвертация завершена", "en": "Conversion complete"},
    "msg_no_file": {"ru": "Файл не выбран", "en": "No file selected"},
    "msg_error": {"ru": "Ошибка", "en": "Error"},
    "msg_done": {"ru": "Готово", "en": "Done"},
    "msg_ffmpeg_not_found": {
        "ru": "FFmpeg не найден! Установите ffmpeg и добавьте в PATH.",
        "en": "FFmpeg not found! Install ffmpeg and add to PATH."
    },
    "msg_export_done": {"ru": "Мэшап экспортирован", "en": "Mashup exported"},
    "msg_coach_created": {"ru": "Коуч создан", "en": "Coach created"},
    "msg_cover_created": {"ru": "Обложка создана", "en": "Cover created"},

    # --- Фильтры / Filters ---
    "filter_none": {"ru": "Нет", "en": "None"},
    "filter_grayscale": {"ru": "Оттенки серого", "en": "Grayscale"},
    "filter_blur": {"ru": "Размытие", "en": "Blur"},
    "filter_sharpen": {"ru": "Резкость", "en": "Sharpen"},
    "filter_edges": {"ru": "Контуры", "en": "Edges"},
    "filter_invert": {"ru": "Инверсия", "en": "Invert"},

    # --- Форматы / Formats ---
    "fmt_video": {"ru": "Видео", "en": "Video"},
    "fmt_audio": {"ru": "Аудио", "en": "Audio"},
    "fmt_image": {"ru": "Изображение", "en": "Image"},

    # --- О программе / About ---
    "about_text": {
        "ru": "Just Dance Mashup Studio\n\nИнструмент для создания мэшапов Just Dance.\n\nВозможности:\n— Редактор видео (WEBM, MP4, AVI, MOV)\n— Редактор аудио (WAV, MP3, OGG)\n— Редактор пиктограмм (TGA, PNG, JPEG, BMP)\n— Создание коучей\n— Создание обложек\n— Конвертер форматов (ffmpeg)\n— Таймлайн для смешивания\n— Локализация RU/EN\n\nВерсия 2.0",
        "en": "Just Dance Mashup Studio\n\nTool for creating Just Dance mashups.\n\nFeatures:\n— Video editor (WEBM, MP4, AVI, MOV)\n— Audio editor (WAV, MP3, OGG)\n— Pictogram editor (TGA, PNG, JPEG, BMP)\n— Coach creator\n— Cover creator\n— Format converter (ffmpeg)\n— Timeline for mixing\n— RU/EN localization\n\nVersion 2.0"
    },

    # --- Доп. / Misc ---
    "lbl_flip_none": {"ru": "Нет", "en": "None"},
    "lbl_flip_h": {"ru": "По горизонтали", "en": "Horizontal"},
    "lbl_flip_v": {"ru": "По вертикали", "en": "Vertical"},
    "lbl_flip_both": {"ru": "Оба", "en": "Both"},
    "lbl_smooth": {"ru": "Сглаживание", "en": "Smoothing"},
    "lbl_remove_bg_color": {"ru": "Цвет фона для удаления", "en": "Background color to remove"},
    "lbl_tolerance": {"ru": "Допуск", "en": "Tolerance"},
    "lbl_merge": {"ru": "Объединить", "en": "Merge"},
    "lbl_duration": {"ru": "Длительность", "en": "Duration"},
    "lbl_fps": {"ru": "FPS", "en": "FPS"},
    "lbl_frames": {"ru": "Кадры", "en": "Frames"},
    "lbl_frame": {"ru": "Кадр", "en": "Frame"},
    "lbl_preview": {"ru": "Предпросмотр", "en": "Preview"},
    "lbl_pictogram_type": {"ru": "Тип пиктограммы", "en": "Pictogram Type"},
    "lbl_pictogram_gold": {"ru": "Золотая", "en": "Gold"},
    "lbl_pictogram_normal": {"ru": "Обычная", "en": "Normal"},
    "lbl_pictogram_fever": {"ru": "Fever", "en": "Fever"},
    "lbl_fit": {"ru": "Вписать", "en": "Fit"},
    "lbl_stretch": {"ru": "Растянуть", "en": "Stretch"},
    "lbl_crop": {"ru": "Обрезать", "en": "Crop"},
    "lbl_alignment": {"ru": "Выравнивание", "en": "Alignment"},
    "lbl_opacity": {"ru": "Непрозрачность", "en": "Opacity"},
    "lbl_shadow": {"ru": "Тень", "en": "Shadow"},
    "lbl_glow": {"ru": "Свечение", "en": "Glow"},
}


def get_string(key, lang=LANG_RU):
    """Получить строку по ключу и языку / Get string by key and language."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get(LANG_EN, key))


class Localization:
    """Менеджер локализации / Localization manager."""

    def __init__(self, lang=LANG_RU):
        self.lang = lang

    def set_lang(self, lang):
        self.lang = lang

    def get(self, key):
        return get_string(key, self.lang)

    def get_all(self):
        return {k: get_string(k, self.lang) for k in STRINGS}
