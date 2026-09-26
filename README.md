# Just Dance Mashup Studio

# Just Dance Mashup Studio / Just Dance Mashup Studio

---

## Русский

Инструмент для создания мэшапов Just Dance. Включает графический интерфейс,
редакторы видео, аудио и пиктограмм, создание коучей и обложек, конвертер
форматов и таймлайн для смешивания.

### Возможности

- **Редактор видео** — обрезка, скорость, яркость, контраст, насыщенность,
  фильтры (оттенки серого, размытие, резкость, контуры, инверсия), объединение.
  Форматы: WEBM, MP4, AVI, MOV, MKV.
- **Редактор аудио** — обрезка, скорость, громкость, объединение.
  Форматы: WAV, MP3, OGG.
- **Редактор пиктограмм** — ресайз, поворот, отражение, удаление фона,
  хромакей, контур, прозрачность, сетка, замена цвета, фильтры,
  стили Just Dance (обычная, золотая, fever).
  Форматы: TGA, PNG, JPEG, BMP, GIF, TIFF.
- **Создание коуча** — извлечение силуэта танцора из кадра видео или
  изображения, удаление фона (хромакей или по цвету), контур, заливка цветом,
  свечение, спрайт-лист. Стандартные размеры коучей.
- **Создание обложек** — обложки песен, альбомов и мэшапов.
  Градиентные и изобразительные фоны, наложение коуча, логотипа,
  заголовок и подзаголовок с тенью, выбор шрифта и цвета.
- **Конвертер форматов** — конвертация между видео, аудио и графическими
  форматами через ffmpeg.
- **Таймлайн** — раздельные дорожки для видео, аудио и пиктограмм,
  добавление и удаление, экспорт готового мэшапа.
- **Локализация** — русский и английский языки, переключение в меню.

### Требования

- Python 3.8+
- **FFmpeg** — установлен и добавлен в PATH
  - Windows: [ffmpeg.org/download](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

### Установка

```bash
pip install -r requirements.txt
```

### Запуск

```bash
python main_app.py
```

### Структура проекта

```
just_dance_mashup_studio/
├── main_app.py            — главное окно с GUI
├── localization.py        — локализация RU/EN
├── media_converter.py     — конвертация и редактирование видео/аудио (ffmpeg)
├── pictogram_editor.py    — редактор пиктограмм (Pillow)
├── coach_creator.py       — создание коучей
├── cover_creator.py       — создание обложек
├── requirements.txt       — зависимости
└── README.md              — документация
```

### Использование

1. **Откройте редактор видео** через меню «Правка» → «Редактор видео».
   Выберите входной файл, настройте параметры, нажмите «Применить».
2. **Создайте коуча** через «Правка» → «Создание коуча». Укажите видео или
   изображение, выберите время кадра, настройте хромакей и контур.
3. **Создайте обложку** через «Правка» → «Создание обложки». Выберите тип,
   введите заголовок, настройте фон и коуча.
4. **Редактируйте пиктограммы** через «Правка» → «Редактор пиктограмм».
   Поддерживаются TGA, PNG, JPEG, удаление фона, стили Just Dance.
5. **Добавьте файлы в таймлайн** на соответствующие дорожки.
6. **Экспортируйте мэшап** через «Файл» → «Экспорт мэшапа».

---

## English

A tool for creating Just Dance mashups. Includes a graphical interface,
video, audio and pictogram editors, coach and cover creators, a format
converter, and a timeline for mixing.

### Features

- **Video editor** — trim, speed, brightness, contrast, saturation,
  filters (grayscale, blur, sharpen, edges, invert), merge.
  Formats: WEBM, MP4, AVI, MOV, MKV.
- **Audio editor** — trim, speed, volume, merge.
  Formats: WAV, MP3, OGG.
- **Pictogram editor** — resize, rotate, flip, background removal,
  chroma key, outline, transparency, grid, color replacement, filters,
  Just Dance styles (normal, gold, fever).
  Formats: TGA, PNG, JPEG, BMP, GIF, TIFF.
- **Coach creator** — extract dancer silhouette from a video frame or
  image, background removal (chroma key or by color), outline, color fill,
  glow, sprite sheet. Standard coach sizes.
- **Cover creator** — song, album and mashup covers.
  Gradient and image backgrounds, coach and logo overlay,
  title and subtitle with shadow, font and color selection.
- **Format converter** — convert between video, audio and image formats
  via ffmpeg.
- **Timeline** — separate tracks for video, audio and pictograms,
  add and remove, export the finished mashup.
- **Localization** — Russian and English, switchable from the menu.

### Requirements

- Python 3.8+
- **FFmpeg** — installed and in PATH
  - Windows: [ffmpeg.org/download](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python main_app.py
```

### Project structure

```
just_dance_mashup_studio/
├── main_app.py            — main window with GUI
├── localization.py        — RU/EN localization
├── media_converter.py     — video/audio conversion and editing (ffmpeg)
├── pictogram_editor.py    — pictogram editor (Pillow)
├── coach_creator.py       — coach creator
├── cover_creator.py       — cover creator
├── requirements.txt       — dependencies
└── README.md              — documentation
```

### Usage

1. **Open the video editor** via "Edit" → "Video Editor".
   Select an input file, adjust parameters, click "Apply".
2. **Create a coach** via "Edit" → "Coach Creator". Specify a video or image,
   select frame time, set up chroma key and outline.
3. **Create a cover** via "Edit" → "Cover Creator". Choose the type,
   enter a title, set up the background and coach.
4. **Edit pictograms** via "Edit" → "Pictogram Editor".
   Supports TGA, PNG, JPEG, background removal, Just Dance styles.
5. **Add files to the timeline** on the appropriate tracks.
6. **Export the mashup** via "File" → "Export Mashup".

---

## License

MIT
