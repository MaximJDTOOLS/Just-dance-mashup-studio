# -*- coding: utf-8 -*-
"""
Just Dance Mashup Studio — главное приложение.
Main application with GUI for creating Just Dance mashups.

Возможности / Features:
  — Редактор видео (WEBM, MP4, AVI, MOV, MKV)
  — Редактор аудио (WAV, MP3, OGG)
  — Редактор пиктограмм (TGA, PNG, JPEG, BMP)
  — Создание коучей (извлечение силуэта из видео/кадра)
  — Создание обложек (песня, альбом, мэшап)
  — Конвертер форматов (ffmpeg)
  — Таймлайн для смешивания
  — Локализация RU/EN
"""

import os
import sys
import json
import threading
import tempfile
from typing import Optional, List

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

from localization import Localization, LANG_RU, LANG_EN, get_string
from media_converter import (
    FFMPEG, check_ffmpeg, convert_video, convert_audio, convert_media,
    edit_video, edit_audio, merge_videos, merge_audio, get_media_info,
    extract_frames,
    VIDEO_FORMATS, VIDEO_FORMAT_NAMES, VIDEO_CODECS,
    AUDIO_FORMATS, AUDIO_FORMAT_NAMES, AUDIO_CODECS,
)
from pictogram_editor import (
    IMAGE_FORMATS, IMAGE_FORMAT_NAMES, PICTOGRAM_TYPES,
    load_image, save_image, resize_image, rotate_image, flip_image,
    remove_background, chroma_key, add_outline, set_transparency,
    add_grid, replace_color, apply_filter, apply_pictogram_style,
    convert_image_format, get_image_info,
)
from coach_creator import (
    COACH_SIZES, COACH_SIZES_NAMES,
    extract_coach_from_frame, extract_coach_from_video,
    extract_multiple_poses, create_coach_sprite_sheet, apply_coach_glow,
)
from cover_creator import (
    COVER_SIZES, COVER_SIZES_NAMES, BG_TEMPLATES,
    create_cover, create_mashup_cover, create_gradient_bg,
)


class VideoEditorDialog(tk.Toplevel):
    """Диалог редактора видео / Video editor dialog."""

    def __init__(self, parent, loc: Localization):
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("menu_video_editor"))
        self.geometry("500x650")
        self.resizable(True, True)
        self.input_path = None
        self.output_path = None
        self._build_ui()

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # Входной файл
        ttk.Label(frm, text=L.get("lbl_input_file")).grid(row=0, column=0, sticky="w", pady=2)
        self.ent_input = ttk.Entry(frm, width=40)
        self.ent_input.grid(row=1, column=0, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_input).grid(row=1, column=1, padx=5)

        # Выходной файл
        ttk.Label(frm, text=L.get("lbl_output_file")).grid(row=2, column=0, sticky="w", pady=2)
        self.ent_output = ttk.Entry(frm, width=40)
        self.ent_output.grid(row=3, column=0, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_output).grid(row=3, column=1, padx=5)

        ttk.Separator(frm, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # Параметры
        ttk.Label(frm, text=L.get("lbl_start_time")).grid(row=5, column=0, sticky="w", pady=2)
        self.ent_start = ttk.Entry(frm, width=15)
        self.ent_start.grid(row=5, column=1, sticky="w", pady=2)
        self.ent_start.insert(0, "0")

        ttk.Label(frm, text=L.get("lbl_end_time")).grid(row=6, column=0, sticky="w", pady=2)
        self.ent_end = ttk.Entry(frm, width=15)
        self.ent_end.grid(row=6, column=1, sticky="w", pady=2)
        self.ent_end.insert(0, "0")

        ttk.Label(frm, text=L.get("lbl_speed")).grid(row=7, column=0, sticky="w", pady=2)
        self.ent_speed = ttk.Entry(frm, width=15)
        self.ent_speed.grid(row=7, column=1, sticky="w", pady=2)
        self.ent_speed.insert(0, "1.0")

        ttk.Label(frm, text=L.get("lbl_brightness")).grid(row=8, column=0, sticky="w", pady=2)
        self.ent_brightness = ttk.Entry(frm, width=15)
        self.ent_brightness.grid(row=8, column=1, sticky="w", pady=2)
        self.ent_brightness.insert(0, "0.0")

        ttk.Label(frm, text=L.get("lbl_contrast")).grid(row=9, column=0, sticky="w", pady=2)
        self.ent_contrast = ttk.Entry(frm, width=15)
        self.ent_contrast.grid(row=9, column=1, sticky="w", pady=2)
        self.ent_contrast.insert(0, "0.0")

        ttk.Label(frm, text=L.get("lbl_saturation")).grid(row=10, column=0, sticky="w", pady=2)
        self.ent_saturation = ttk.Entry(frm, width=15)
        self.ent_saturation.grid(row=10, column=1, sticky="w", pady=2)
        self.ent_saturation.insert(0, "0.0")

        ttk.Label(frm, text=L.get("lbl_filter")).grid(row=11, column=0, sticky="w", pady=2)
        self.cmb_filter = ttk.Combobox(frm, width=20, state="readonly")
        self.cmb_filter["values"] = [
            L.get("filter_none"), L.get("filter_grayscale"),
            L.get("filter_blur"), L.get("filter_sharpen"),
            L.get("filter_edges"), L.get("filter_invert")
        ]
        self.cmb_filter.current(0)
        self.cmb_filter.grid(row=11, column=1, sticky="w", pady=2)

        ttk.Separator(frm, orient="horizontal").grid(row=12, column=0, columnspan=2, sticky="ew", pady=10)

        # Информация о файле
        self.lbl_info = ttk.Label(frm, text="", wraplength=400)
        self.lbl_info.grid(row=13, column=0, columnspan=2, pady=5)

        # Кнопки
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=14, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text=L.get("btn_preview"), command=self._show_info).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_apply"), command=self._apply).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_close"), command=self.destroy).pack(side="left", padx=5)

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title=self.loc.get("menu_video_editor"),
            filetypes=[("Video", "*.webm *.mp4 *.avi *.mov *.mkv"), ("All", "*.*")]
        )
        if path:
            self.ent_input.delete(0, "end")
            self.ent_input.insert(0, path)
            self.input_path = path
            self._show_info()

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title=self.loc.get("lbl_output_file"),
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4"), ("WebM", "*.webm"), ("AVI", "*.avi"), ("All", "*.*")]
        )
        if path:
            self.ent_output.delete(0, "end")
            self.ent_output.insert(0, path)
            self.output_path = path

    def _show_info(self):
        path = self.ent_input.get()
        if not path or not os.path.exists(path):
            self.lbl_info.config(text=self.loc.get("msg_no_file"))
            return
        info = get_media_info(path)
        L = self.loc
        txt = (f"{L.get('lbl_duration')}: {info.duration:.1f}s | "
               f"{info.width}x{info.height} | {L.get('lbl_fps')}: {info.fps:.1f} | "
               f"{L.get('lbl_frames')}: {info.frames}")
        self.lbl_info.config(text=txt)

    def _apply(self):
        inp = self.ent_input.get()
        outp = self.ent_output.get()
        if not inp or not os.path.exists(inp):
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if not outp:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if not check_ffmpeg():
            messagebox.showerror(self.loc.get("msg_error"), self.loc.get("msg_ffmpeg_not_found"))
            return

        start = float(self.ent_start.get() or 0)
        end = float(self.ent_end.get() or 0)
        speed = float(self.ent_speed.get() or 1.0)
        brightness = float(self.ent_brightness.get() or 0.0)
        contrast = float(self.ent_contrast.get() or 0.0)
        saturation = float(self.ent_saturation.get() or 0.0)

        filter_map = {
            0: None, 1: "grayscale", 2: "blur", 3: "sharpen", 4: "edges", 5: "invert"
        }
        filt = filter_map.get(self.cmb_filter.current())

        self.config(cursor="watch")
        self.update()

        ok = edit_video(
            inp, outp,
            start_time=start if start > 0 else None,
            end_time=end if end > 0 else None,
            speed=speed if speed != 1.0 else None,
            brightness=brightness if brightness != 0 else None,
            contrast=contrast if contrast != 0 else None,
            saturation=saturation if saturation != 0 else None,
            filters=[filt] if filt else None,
        )

        self.config(cursor="")
        if ok:
            messagebox.showinfo("", self.loc.get("msg_done"))
        else:
            messagebox.showerror(self.loc.get("msg_error"), "FFmpeg error")


class AudioEditorDialog(tk.Toplevel):
    """Диалог редактора аудио / Audio editor dialog."""

    def __init__(self, parent, loc: Localization):
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("menu_audio_editor"))
        self.geometry("450x500")
        self.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=L.get("lbl_input_file")).grid(row=0, column=0, sticky="w", pady=2)
        self.ent_input = ttk.Entry(frm, width=40)
        self.ent_input.grid(row=1, column=0, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_input).grid(row=1, column=1, padx=5)

        ttk.Label(frm, text=L.get("lbl_output_file")).grid(row=2, column=0, sticky="w", pady=2)
        self.ent_output = ttk.Entry(frm, width=40)
        self.ent_output.grid(row=3, column=0, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_output).grid(row=3, column=1, padx=5)

        ttk.Separator(frm, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(frm, text=L.get("lbl_start_time")).grid(row=5, column=0, sticky="w")
        self.ent_start = ttk.Entry(frm, width=15)
        self.ent_start.grid(row=5, column=1, sticky="w")
        self.ent_start.insert(0, "0")

        ttk.Label(frm, text=L.get("lbl_end_time")).grid(row=6, column=0, sticky="w")
        self.ent_end = ttk.Entry(frm, width=15)
        self.ent_end.grid(row=6, column=1, sticky="w")
        self.ent_end.insert(0, "0")

        ttk.Label(frm, text=L.get("lbl_speed")).grid(row=7, column=0, sticky="w")
        self.ent_speed = ttk.Entry(frm, width=15)
        self.ent_speed.grid(row=7, column=1, sticky="w")
        self.ent_speed.insert(0, "1.0")

        ttk.Label(frm, text=L.get("lbl_volume")).grid(row=8, column=0, sticky="w")
        self.ent_volume = ttk.Entry(frm, width=15)
        self.ent_volume.grid(row=8, column=1, sticky="w")
        self.ent_volume.insert(0, "1.0")

        self.lbl_info = ttk.Label(frm, text="", wraplength=380)
        self.lbl_info.grid(row=9, column=0, columnspan=2, pady=5)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=10, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text=L.get("btn_preview"), command=self._show_info).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_apply"), command=self._apply).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_close"), command=self.destroy).pack(side="left", padx=5)

    def _browse_input(self):
        path = filedialog.askopenfilename(
            filetypes=[("Audio", "*.wav *.mp3 *.ogg"), ("All", "*.*")]
        )
        if path:
            self.ent_input.delete(0, "end")
            self.ent_input.insert(0, path)
            self._show_info()

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV", "*.wav"), ("MP3", "*.mp3"), ("OGG", "*.ogg")]
        )
        if path:
            self.ent_output.delete(0, "end")
            self.ent_output.insert(0, path)

    def _show_info(self):
        path = self.ent_input.get()
        if not path or not os.path.exists(path):
            self.lbl_info.config(text=self.loc.get("msg_no_file"))
            return
        info = get_media_info(path)
        self.lbl_info.config(
            text=f"{self.loc.get('lbl_duration')}: {info.duration:.1f}s | "
                 f"{info.audio_codec} | {info.sample_rate}Hz | {info.channels}ch"
        )

    def _apply(self):
        inp = self.ent_input.get()
        outp = self.ent_output.get()
        if not inp or not os.path.exists(inp):
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if not outp:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if not check_ffmpeg():
            messagebox.showerror(self.loc.get("msg_error"), self.loc.get("msg_ffmpeg_not_found"))
            return

        start = float(self.ent_start.get() or 0)
        end = float(self.ent_end.get() or 0)
        speed = float(self.ent_speed.get() or 1.0)
        volume = float(self.ent_volume.get() or 1.0)

        self.config(cursor="watch")
        self.update()
        ok = edit_audio(
            inp, outp,
            start_time=start if start > 0 else None,
            end_time=end if end > 0 else None,
            speed=speed if speed != 1.0 else None,
            volume=volume if volume != 1.0 else None,
        )
        self.config(cursor="")
        if ok:
            messagebox.showinfo("", self.loc.get("msg_done"))
        else:
            messagebox.showerror(self.loc.get("msg_error"), "FFmpeg error")


class PictogramEditorDialog(tk.Toplevel):
    """Диалог редактора пиктограмм / Pictogram editor dialog."""

    def __init__(self, parent, loc: Localization):
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("menu_pictogram_editor"))
        self.geometry("550x700")
        self.resizable(True, True)
        self.preview_label = None
        self._build_ui()

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # Файлы
        row = 0
        ttk.Label(frm, text=L.get("lbl_input_file")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_input = ttk.Entry(frm, width=45)
        self.ent_input.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_input).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Label(frm, text=L.get("lbl_output_file")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_output = ttk.Entry(frm, width=45)
        self.ent_output.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_output).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)

        # Параметры
        row += 1
        ttk.Label(frm, text=L.get("lbl_width")).grid(row=row, column=0, sticky="w")
        self.ent_width = ttk.Entry(frm, width=10)
        self.ent_width.grid(row=row, column=1, sticky="w")
        self.ent_width.insert(0, "256")

        row += 1
        ttk.Label(frm, text=L.get("lbl_height")).grid(row=row, column=0, sticky="w")
        self.ent_height = ttk.Entry(frm, width=10)
        self.ent_height.grid(row=row, column=1, sticky="w")
        self.ent_height.insert(0, "256")

        row += 1
        ttk.Label(frm, text=L.get("lbl_rotate")).grid(row=row, column=0, sticky="w")
        self.ent_rotate = ttk.Entry(frm, width=10)
        self.ent_rotate.grid(row=row, column=1, sticky="w")
        self.ent_rotate.insert(0, "0")

        row += 1
        ttk.Label(frm, text=L.get("lbl_flip")).grid(row=row, column=0, sticky="w")
        self.cmb_flip = ttk.Combobox(frm, width=15, state="readonly")
        self.cmb_flip["values"] = [L.get("lbl_flip_none"), L.get("lbl_flip_h"),
                                    L.get("lbl_flip_v"), L.get("lbl_flip_both")]
        self.cmb_flip.current(0)
        self.cmb_flip.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_remove_bg")).grid(row=row, column=0, sticky="w")
        self.chk_remove_bg = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, variable=self.chk_remove_bg).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_remove_bg_color")).grid(row=row, column=0, sticky="w")
        self.bg_color_btn = tk.Button(frm, text="...", command=self._pick_bg_color, width=3)
        self.bg_color_btn.grid(row=row, column=1, sticky="w")
        self.bg_color = None

        row += 1
        ttk.Label(frm, text=L.get("lbl_chroma_key")).grid(row=row, column=0, sticky="w")
        self.chk_chroma = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, variable=self.chk_chroma).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_tolerance")).grid(row=row, column=0, sticky="w")
        self.ent_tolerance = ttk.Entry(frm, width=10)
        self.ent_tolerance.grid(row=row, column=1, sticky="w")
        self.ent_tolerance.insert(0, "30")

        row += 1
        ttk.Label(frm, text=L.get("lbl_smooth_edges")).grid(row=row, column=0, sticky="w")
        self.chk_smooth = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, variable=self.chk_smooth).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_outline")).grid(row=row, column=0, sticky="w")
        self.chk_outline = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, variable=self.chk_outline).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_outline_color")).grid(row=row, column=0, sticky="w")
        self.outline_color_btn = tk.Button(frm, text="...", command=self._pick_outline_color, width=3)
        self.outline_color_btn.grid(row=row, column=1, sticky="w")
        self.outline_color = (255, 255, 255)

        row += 1
        ttk.Label(frm, text=L.get("lbl_outline_width")).grid(row=row, column=0, sticky="w")
        self.ent_outline_w = ttk.Entry(frm, width=10)
        self.ent_outline_w.grid(row=row, column=1, sticky="w")
        self.ent_outline_w.insert(0, "3")

        row += 1
        ttk.Label(frm, text=L.get("lbl_transparency")).grid(row=row, column=0, sticky="w")
        self.ent_opacity = ttk.Entry(frm, width=10)
        self.ent_opacity.grid(row=row, column=1, sticky="w")
        self.ent_opacity.insert(0, "255")

        row += 1
        ttk.Label(frm, text=L.get("lbl_grid")).grid(row=row, column=0, sticky="w")
        self.chk_grid = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, variable=self.chk_grid).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_filter")).grid(row=row, column=0, sticky="w")
        self.cmb_filter = ttk.Combobox(frm, width=15, state="readonly")
        self.cmb_filter["values"] = [
            L.get("filter_none"), L.get("filter_grayscale"),
            L.get("filter_blur"), L.get("filter_sharpen"),
            L.get("filter_edges"), L.get("filter_invert")
        ]
        self.cmb_filter.current(0)
        self.cmb_filter.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_pictogram_type")).grid(row=row, column=0, sticky="w")
        self.cmb_picto = ttk.Combobox(frm, width=15, state="readonly")
        self.cmb_picto["values"] = [
            L.get("lbl_pictogram_normal"), L.get("lbl_pictogram_gold"), L.get("lbl_pictogram_fever")
        ]
        self.cmb_picto.current(0)
        self.cmb_picto.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)

        # Предпросмотр
        row += 1
        self.preview_label = ttk.Label(frm, text="")
        self.preview_label.grid(row=row, column=0, columnspan=3, pady=5)

        row += 1
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=5)
        ttk.Button(btn_frame, text=L.get("btn_preview"), command=self._preview).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_apply"), command=self._apply).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_close"), command=self.destroy).pack(side="left", padx=5)

    def _browse_input(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.tga *.png *.jpg *.jpeg *.bmp *.gif *.tiff"), ("All", "*.*")]
        )
        if path:
            self.ent_input.delete(0, "end")
            self.ent_input.insert(0, path)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("TGA", "*.tga"), ("JPEG", "*.jpg *.jpeg"), ("BMP", "*.bmp")]
        )
        if path:
            self.ent_output.delete(0, "end")
            self.ent_output.insert(0, path)

    def _pick_bg_color(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.bg_color = tuple(int(x) for x in c[0])

    def _pick_outline_color(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.outline_color = tuple(int(x) for x in c[0])

    def _process(self) -> Optional[object]:
        path = self.ent_input.get()
        if not path or not os.path.exists(path):
            return None
        img = load_image(path)
        if img is None:
            return None

        w = int(self.ent_width.get() or 256)
        h = int(self.ent_height.get() or 256)
        rot = float(self.ent_rotate.get() or 0)
        flip_map = {"none": None, 0: None, 1: "horizontal", 2: "vertical", 3: "both"}
        flip_idx = self.cmb_flip.current()
        flip_mode = ["none", "horizontal", "vertical", "both"][flip_idx]
        tolerance = int(self.ent_tolerance.get() or 30)
        smooth = self.chk_smooth.get()

        if rot != 0:
            img = rotate_image(img, rot)
        if flip_mode != "none":
            img = flip_image(img, flip_mode)
        if self.chk_remove_bg.get():
            img = remove_background(img, self.bg_color, tolerance, smooth)
        if self.chk_chroma.get():
            img = chroma_key(img, (0, 255, 0), tolerance, smooth)
        if self.chk_outline.get():
            ow = int(self.ent_outline_w.get() or 3)
            img = add_outline(img, self.outline_color, ow)
        if self.chk_grid.get():
            img = add_grid(img)
        filt_idx = self.cmb_filter.current()
        filt_map = {0: None, 1: "grayscale", 2: "blur", 3: "sharpen", 4: "edges", 5: "invert"}
        filt = filt_map.get(filt_idx)
        if filt:
            img = apply_filter(img, filt)
        picto_idx = self.cmb_picto.current()
        picto_map = {0: "normal", 1: "gold", 2: "fever"}
        pstyle = picto_map.get(picto_idx, "normal")
        if pstyle != "normal":
            ow = int(self.ent_outline_w.get() or 3)
            img = apply_pictogram_style(img, pstyle, outline_width=ow)
        opacity = int(self.ent_opacity.get() or 255)
        if opacity < 255:
            img = set_transparency(img, opacity)
        img = resize_image(img, w, h, "fit")
        return img

    def _preview(self):
        img = self._process()
        if img is None:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        tmp = tempfile.mktemp(suffix=".png")
        save_image(img, tmp)
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(file=tmp)
        self.preview_label.config(image=photo, text="")
        self.preview_label.image = photo
        os.unlink(tmp)

    def _apply(self):
        img = self._process()
        if img is None:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        outp = self.ent_output.get()
        if not outp:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if save_image(img, outp):
            messagebox.showinfo("", self.loc.get("msg_saved"))
        else:
            messagebox.showerror(self.loc.get("msg_error"), "Save failed")


class CoachCreatorDialog(tk.Toplevel):
    """Диалог создания коуча / Coach creator dialog."""

    def __init__(self, parent, loc: Localization):
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("menu_coach_creator"))
        self.geometry("500x600")
        self.resizable(True, True)
        self.preview_label = None
        self._build_ui()

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        row = 0
        ttk.Label(frm, text=L.get("lbl_coach_source")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_source = ttk.Entry(frm, width=45)
        self.ent_source.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_source).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Label(frm, text=L.get("lbl_coach_name")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_name = ttk.Entry(frm, width=30)
        self.ent_name.grid(row=row, column=0, columnspan=2, pady=2)
        self.ent_name.insert(0, "coach_01")

        row += 1
        ttk.Label(frm, text=L.get("lbl_coach_pose")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_pose_time = ttk.Entry(frm, width=15)
        self.ent_pose_time.grid(row=row, column=0, sticky="w")
        self.ent_pose_time.insert(0, "0.0")

        row += 1
        ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)

        row += 1
        ttk.Label(frm, text=L.get("lbl_chroma_key")).grid(row=row, column=0, sticky="w")
        self.chk_chroma = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, variable=self.chk_chroma).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_tolerance")).grid(row=row, column=0, sticky="w")
        self.ent_tolerance = ttk.Entry(frm, width=10)
        self.ent_tolerance.grid(row=row, column=1, sticky="w")
        self.ent_tolerance.insert(0, "40")

        row += 1
        ttk.Label(frm, text=L.get("lbl_smooth_edges")).grid(row=row, column=0, sticky="w")
        self.chk_smooth = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, variable=self.chk_smooth).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_outline_color")).grid(row=row, column=0, sticky="w")
        self.outline_btn = tk.Button(frm, text="...", command=self._pick_outline, width=3)
        self.outline_btn.grid(row=row, column=1, sticky="w")
        self.outline_color = (255, 255, 255)

        row += 1
        ttk.Label(frm, text=L.get("lbl_outline_width")).grid(row=row, column=0, sticky="w")
        self.ent_outline_w = ttk.Entry(frm, width=10)
        self.ent_outline_w.grid(row=row, column=1, sticky="w")
        self.ent_outline_w.insert(0, "3")

        row += 1
        ttk.Label(frm, text=L.get("lbl_coach_color")).grid(row=row, column=0, sticky="w")
        self.color_btn = tk.Button(frm, text="...", command=self._pick_coach_color, width=3)
        self.color_btn.grid(row=row, column=1, sticky="w")
        self.coach_color = None

        row += 1
        ttk.Label(frm, text=L.get("lbl_fit") + " / " + L.get("lbl_resize")).grid(row=row, column=0, sticky="w")
        self.cmb_size = ttk.Combobox(frm, width=20, state="readonly")
        self.cmb_size["values"] = [COACH_SIZES_NAMES[k] for k in COACH_SIZES]
        self.cmb_size.current(1)
        self.cmb_size.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_coach_output")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_output = ttk.Entry(frm, width=45)
        self.ent_output.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_output).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)

        row += 1
        self.preview_label = ttk.Label(frm, text="")
        self.preview_label.grid(row=row, column=0, columnspan=3, pady=5)

        row += 1
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=5)
        ttk.Button(btn_frame, text=L.get("btn_preview"), command=self._preview).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_create"), command=self._create).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_close"), command=self.destroy).pack(side="left", padx=5)

    def _browse_source(self):
        path = filedialog.askopenfilename(
            filetypes=[("Video", "*.webm *.mp4 *.avi *.mov *.mkv"),
                       ("Images", "*.tga *.png *.jpg *.jpeg *.bmp"), ("All", "*.*")]
        )
        if path:
            self.ent_source.delete(0, "end")
            self.ent_source.insert(0, path)

    def _browse_output(self):
        d = filedialog.askdirectory()
        if d:
            self.ent_output.delete(0, "end")
            self.ent_output.insert(0, d)

    def _pick_outline(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.outline_color = tuple(int(x) for x in c[0])

    def _pick_coach_color(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.coach_color = tuple(int(x) for x in c[0])

    def _get_size_key(self):
        idx = self.cmb_size.current()
        keys = list(COACH_SIZES.keys())
        return keys[idx] if idx < len(keys) else "standard"

    def _preview(self):
        path = self.ent_source.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        img = load_image(path)
        if img is None:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        tolerance = int(self.ent_tolerance.get() or 40)
        smooth = self.chk_smooth.get()
        if self.chk_chroma.get():
            img = chroma_key(img, (0, 255, 0), tolerance, smooth)
        else:
            img = remove_background(img, None, tolerance, smooth)
        if self.coach_color:
            from PIL import Image as PILImage
            r, g, b, a = img.split()
            filled = PILImage.new("RGBA", img.size, (*self.coach_color, 255))
            filled.putalpha(a)
            img = filled
        ow = int(self.ent_outline_w.get() or 3)
        img = add_outline(img, self.outline_color, ow)
        size_key = self._get_size_key()
        ts = COACH_SIZES[size_key]
        img = resize_image(img, ts[0], ts[1], "fit")
        tmp = tempfile.mktemp(suffix=".png")
        save_image(img, tmp)
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(file=tmp)
        self.preview_label.config(image=photo, text="")
        self.preview_label.image = photo
        os.unlink(tmp)

    def _create(self):
        path = self.ent_source.get()
        out_dir = self.ent_output.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if not out_dir:
            out_dir = os.path.dirname(path) or "."
        os.makedirs(out_dir, exist_ok=True)

        name = self.ent_name.get() or "coach_01"
        pose_time = float(self.ent_pose_time.get() or 0.0)
        tolerance = int(self.ent_tolerance.get() or 40)
        smooth = self.chk_smooth.get()
        ow = int(self.ent_outline_w.get() or 3)
        size_key = self._get_size_key()

        is_video = path.lower().endswith((".webm", ".mp4", ".avi", ".mov", ".mkv"))

        self.config(cursor="watch")
        self.update()

        if is_video:
            if not check_ffmpeg():
                self.config(cursor="")
                messagebox.showerror(self.loc.get("msg_error"), self.loc.get("msg_ffmpeg_not_found"))
                return
            result = extract_coach_from_video(
                path, out_dir, pose_time, None, tolerance, smooth,
                self.outline_color, ow, self.coach_color, size_key, name
            )
        else:
            img = extract_coach_from_frame(
                path, None, tolerance, smooth,
                self.outline_color, ow, self.coach_color
            )
            if img:
                ts = COACH_SIZES[size_key]
                img = resize_image(img, ts[0], ts[1], "fit")
                result = os.path.join(out_dir, f"{name}.png")
                save_image(img, result)
            else:
                result = None

        self.config(cursor="")
        if result:
            messagebox.showinfo("", self.loc.get("msg_coach_created") + f":\\n{result}")
        else:
            messagebox.showerror(self.loc.get("msg_error"), "Failed")


class CoverCreatorDialog(tk.Toplevel):
    """Диалог создания обложки / Cover creator dialog."""

    def __init__(self, parent, loc: Localization):
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("menu_cover_creator"))
        self.geometry("520x700")
        self.resizable(True, True)
        self.preview_label = None
        self._build_ui()

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        row = 0
        ttk.Label(frm, text=L.get("lbl_cover_type")).grid(row=row, column=0, sticky="w")
        row += 1
        self.cmb_type = ttk.Combobox(frm, width=25, state="readonly")
        self.cmb_type["values"] = [
            L.get("lbl_cover_song"), L.get("lbl_cover_album"), L.get("lbl_cover_mashup")
        ]
        self.cmb_type.current(0)
        self.cmb_type.grid(row=row, column=0, columnspan=2, pady=2)

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_title")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_title = ttk.Entry(frm, width=40)
        self.ent_title.grid(row=row, column=0, columnspan=2, pady=2)
        self.ent_title.insert(0, "Song Title")

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_subtitle")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_subtitle = ttk.Entry(frm, width=40)
        self.ent_subtitle.grid(row=row, column=0, columnspan=2, pady=2)

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_background")).grid(row=row, column=0, sticky="w")
        row += 1
        self.cmb_bg = ttk.Combobox(frm, width=25, state="readonly")
        bg_keys = list(BG_TEMPLATES.keys())
        self.cmb_bg["values"] = [BG_TEMPLATES[k]["name_en"] for k in bg_keys]
        self.cmb_bg.current(0)
        self.cmb_bg.grid(row=row, column=0, columnspan=2, pady=2)

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_image") + " (bg)").grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_bg_img = ttk.Entry(frm, width=40)
        self.ent_bg_img.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_bg_img).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Label(frm, text="Coach image").grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_coach_img = ttk.Entry(frm, width=40)
        self.ent_coach_img.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_coach_img).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_logo")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_logo = ttk.Entry(frm, width=40)
        self.ent_logo.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_logo).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_font_size")).grid(row=row, column=0, sticky="w")
        self.ent_font_size = ttk.Entry(frm, width=10)
        self.ent_font_size.grid(row=row, column=1, sticky="w")
        self.ent_font_size.insert(0, "24")

        row += 1
        ttk.Label(frm, text=L.get("lbl_cover_font_color")).grid(row=row, column=0, sticky="w")
        self.font_color_btn = tk.Button(frm, text="...", command=self._pick_font_color, width=3)
        self.font_color_btn.grid(row=row, column=1, sticky="w")
        self.font_color = (255, 255, 255)

        row += 1
        ttk.Label(frm, text="Title position").grid(row=row, column=0, sticky="w")
        self.cmb_pos = ttk.Combobox(frm, width=15, state="readonly")
        self.cmb_pos["values"] = ["Top", "Center", "Bottom"]
        self.cmb_pos.current(2)
        self.cmb_pos.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frm, text=L.get("lbl_output_file")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_output = ttk.Entry(frm, width=40)
        self.ent_output.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_output).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=8)

        row += 1
        self.preview_label = ttk.Label(frm, text="")
        self.preview_label.grid(row=row, column=0, columnspan=3, pady=5)

        row += 1
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=5)
        ttk.Button(btn_frame, text=L.get("btn_preview"), command=self._preview).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_create"), command=self._create).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_close"), command=self.destroy).pack(side="left", padx=5)

    def _browse_bg_img(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.tga *.bmp"), ("All", "*.*")])
        if p: self.ent_bg_img.delete(0,"end"); self.ent_bg_img.insert(0, p)

    def _browse_coach_img(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.tga *.bmp"), ("All", "*.*")])
        if p: self.ent_coach_img.delete(0,"end"); self.ent_coach_img.insert(0, p)

    def _browse_logo(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.tga *.bmp"), ("All", "*.*")])
        if p: self.ent_logo.delete(0,"end"); self.ent_logo.insert(0, p)

    def _browse_output(self):
        p = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if p: self.ent_output.delete(0,"end"); self.ent_output.insert(0, p)

    def _pick_font_color(self):
        c = colorchooser.askcolor()
        if c[0]: self.font_color = tuple(int(x) for x in c[0])

    def _get_type(self):
        idx = self.cmb_type.current()
        return ["song", "album", "mashup"][idx]

    def _get_bg_template(self):
        idx = self.cmb_bg.current()
        keys = list(BG_TEMPLATES.keys())
        return keys[idx] if idx < len(keys) else "gradient_blue"

    def _do_create(self, preview=False):
        ctype = self._get_type()
        title = self.ent_title.get()
        subtitle = self.ent_subtitle.get()
        bg_tmpl = self._get_bg_template()
        bg_img = self.ent_bg_img.get() or None
        coach_img = self.ent_coach_img.get() or None
        logo = self.ent_logo.get() or None
        fs = int(self.ent_font_size.get() or 24)
        pos_map = {"Top": "top", "Center": "center", "Bottom": "bottom"}
        tpos = pos_map.get(self.cmb_pos.get(), "bottom")

        if preview:
            outp = tempfile.mktemp(suffix=".png")
        else:
            outp = self.ent_output.get() or "cover.png"

        if ctype == "mashup":
            coach_paths = [coach_img] if coach_img else None
            ok = create_mashup_cover(
                title=title, subtitle=subtitle,
                coach_paths=coach_paths,
                bg_template=bg_tmpl,
                font_size=fs, font_color=self.font_color,
                output_path=outp
            )
        else:
            ok = create_cover(
                cover_type=ctype,
                title=title, subtitle=subtitle,
                bg_template=bg_tmpl,
                bg_image_path=bg_img,
                coach_image_path=coach_img,
                logo_image_path=logo,
                font_size=fs, font_color=self.font_color,
                title_pos=tpos,
                output_path=outp
            )
        return ok, outp

    def _preview(self):
        ok, outp = self._do_create(preview=True)
        if ok and os.path.exists(outp):
            from PIL import ImageTk
            photo = ImageTk.PhotoImage(file=outp)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
            os.unlink(outp)
        else:
            messagebox.showerror(self.loc.get("msg_error"), "Failed")

    def _create(self):
        ok, outp = self._do_create(preview=False)
        if ok:
            messagebox.showinfo("", self.loc.get("msg_cover_created") + f":\\n{outp}")
        else:
            messagebox.showerror(self.loc.get("msg_error"), "Failed")


class ConverterDialog(tk.Toplevel):
    """Диалог конвертера форматов / Format converter dialog."""

    def __init__(self, parent, loc: Localization):
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("menu_converter"))
        self.geometry("450x350")
        self.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        row = 0
        ttk.Label(frm, text=L.get("lbl_input_file")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_input = ttk.Entry(frm, width=45)
        self.ent_input.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_input).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Label(frm, text=L.get("lbl_output_file")).grid(row=row, column=0, sticky="w")
        row += 1
        self.ent_output = ttk.Entry(frm, width=45)
        self.ent_output.grid(row=row, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text=L.get("btn_browse"), command=self._browse_output).grid(row=row, column=2, padx=5)

        row += 1
        ttk.Label(frm, text=L.get("lbl_format")).grid(row=row, column=0, sticky="w")
        row += 1
        self.cmb_format = ttk.Combobox(frm, width=30, state="readonly")
        all_fmts = []
        all_fmts += [f"{v} (video)" for v in VIDEO_FORMAT_NAMES.values()]
        all_fmts += [f"{v} (audio)" for v in AUDIO_FORMAT_NAMES.values()]
        all_fmts += [f"{IMAGE_FORMAT_NAMES[k]} (image)" for k in ["tga", "png", "jpeg", "bmp"]]
        self.cmb_format["values"] = all_fmts
        self.cmb_format.current(1)
        self.cmb_format.grid(row=row, column=0, columnspan=2, pady=2)

        row += 1
        self.lbl_status = ttk.Label(frm, text="")
        self.lbl_status.grid(row=row, column=0, columnspan=3, pady=10)

        row += 1
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text=L.get("btn_convert"), command=self._convert).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=L.get("btn_close"), command=self.destroy).pack(side="left", padx=5)

    def _browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("All", "*.*")])
        if path:
            self.ent_input.delete(0, "end")
            self.ent_input.insert(0, path)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(filetypes=[("All", "*.*")])
        if path:
            self.ent_output.delete(0, "end")
            self.ent_output.insert(0, path)

    def _convert(self):
        inp = self.ent_input.get()
        outp = self.ent_output.get()
        if not inp or not os.path.exists(inp):
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        if not outp:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return

        ext = os.path.splitext(outp)[1].lstrip(".").lower()
        is_image = ext in IMAGE_FORMATS

        if is_image:
            ok = convert_image_format(inp, outp)
        else:
            if not check_ffmpeg():
                messagebox.showerror(self.loc.get("msg_error"), self.loc.get("msg_ffmpeg_not_found"))
                return
            self.config(cursor="watch")
            self.update()
            ok = convert_media(inp, outp)
            self.config(cursor="")

        if ok:
            self.lbl_status.config(text=self.loc.get("msg_converted"))
        else:
            self.lbl_status.config(text=self.loc.get("msg_error"))


class JustDanceMashupStudio(tk.Tk):
    """Главное окно приложения / Main application window."""

    def __init__(self):
        super().__init__()
        self.loc = Localization(LANG_RU)
        self.video_tracks: List[str] = []
        self.audio_tracks: List[str] = []
        self.pictogram_tracks: List[str] = []
        self.project_file = None

        self.title(self.loc.get("lbl_title"))
        self.geometry("800x600")
        self.minsize(600, 400)

        self._build_menu()
        self._build_ui()
        self._update_texts()

    def _build_menu(self):
        L = self.loc
        menubar = tk.Menu(self)

        # Файл
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label=L.get("menu_new_project"), command=self._new_project)
        m_file.add_command(label=L.get("menu_open_project"), command=self._open_project)
        m_file.add_command(label=L.get("menu_save_project"), command=self._save_project)
        m_file.add_command(label=L.get("menu_save_as"), command=self._save_as_project)
        m_file.add_separator()
        m_file.add_command(label=L.get("menu_export"), command=self._export_mashup)
        m_file.add_separator()
        m_file.add_command(label=L.get("menu_exit"), command=self.quit)
        menubar.add_cascade(label=L.get("menu_file"), menu=m_file)

        # Правка
        m_edit = tk.Menu(menubar, tearoff=0)
        m_edit.add_command(label=L.get("menu_video_editor"), command=self._open_video_editor)
        m_edit.add_command(label=L.get("menu_audio_editor"), command=self._open_audio_editor)
        m_edit.add_command(label=L.get("menu_pictogram_editor"), command=self._open_pictogram_editor)
        m_edit.add_command(label=L.get("menu_coach_creator"), command=self._open_coach_creator)
        m_edit.add_command(label=L.get("menu_cover_creator"), command=self._open_cover_creator)
        m_edit.add_command(label=L.get("menu_converter"), command=self._open_converter)
        menubar.add_cascade(label=L.get("menu_edit"), menu=m_edit)

        # Язык
        m_lang = tk.Menu(menubar, tearoff=0)
        m_lang.add_command(label=L.get("menu_lang_ru"), command=lambda: self._set_lang(LANG_RU))
        m_lang.add_command(label=L.get("menu_lang_en"), command=lambda: self._set_lang(LANG_EN))
        menubar.add_cascade(label=L.get("menu_language"), menu=m_lang)

        # Справка
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label=L.get("menu_about"), command=self._about)
        menubar.add_cascade(label=L.get("menu_help"), menu=m_help)

        self.config(menu=menubar)
        self.menubar = menubar

    def _build_ui(self):
        L = self.loc
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        notebook = ttk.Notebook(frm)
        notebook.pack(fill="both", expand=True)

        # Вкладка таймлайна
        timeline_frame = ttk.Frame(notebook, padding=10)
        notebook.add(timeline_frame, text=L.get("menu_timeline"))

        # Видеодорожки
        video_frame = ttk.LabelFrame(timeline_frame, text=L.get("lbl_video_tracks"), padding=5)
        video_frame.pack(fill="x", pady=5)
        self.video_listbox = tk.Listbox(video_frame, height=5)
        self.video_listbox.pack(side="left", fill="x", expand=True)
        vf_btns = ttk.Frame(video_frame)
        vf_btns.pack(side="right", padx=5)
        ttk.Button(vf_btns, text=L.get("btn_add"), command=self._add_video_track).pack(pady=2)
        ttk.Button(vf_btns, text=L.get("btn_remove"), command=self._remove_video_track).pack(pady=2)

        # Аудиодорожки
        audio_frame = ttk.LabelFrame(timeline_frame, text=L.get("lbl_audio_tracks"), padding=5)
        audio_frame.pack(fill="x", pady=5)
        self.audio_listbox = tk.Listbox(audio_frame, height=5)
        self.audio_listbox.pack(side="left", fill="x", expand=True)
        af_btns = ttk.Frame(audio_frame)
        af_btns.pack(side="right", padx=5)
        ttk.Button(af_btns, text=L.get("btn_add"), command=self._add_audio_track).pack(pady=2)
        ttk.Button(af_btns, text=L.get("btn_remove"), command=self._remove_audio_track).pack(pady=2)

        # Дорожки пиктограмм
        picto_frame = ttk.LabelFrame(timeline_frame, text=L.get("lbl_pictogram_tracks"), padding=5)
        picto_frame.pack(fill="x", pady=5)
        self.picto_listbox = tk.Listbox(picto_frame, height=5)
        self.picto_listbox.pack(side="left", fill="x", expand=True)
        pf_btns = ttk.Frame(picto_frame)
        pf_btns.pack(side="right", padx=5)
        ttk.Button(pf_btns, text=L.get("btn_add"), command=self._add_picto_track).pack(pady=2)
        ttk.Button(pf_btns, text=L.get("btn_remove"), command=self._remove_picto_track).pack(pady=2)

        # Кнопки внизу
        bottom_frame = ttk.Frame(timeline_frame)
        bottom_frame.pack(fill="x", pady=10)
        ttk.Button(bottom_frame, text=L.get("menu_export"), command=self._export_mashup).pack(side="right", padx=5)

        # Вкладка информации
        info_frame = ttk.Frame(notebook, padding=15)
        notebook.add(info_frame, text="Info")
        self.info_label = ttk.Label(info_frame, text="", justify="left", wraplength=600)
        self.info_label.pack(anchor="nw")
        self._update_info()

    def _update_info(self):
        ffmpeg_status = "OK" if check_ffmpeg() else "NOT FOUND"
        text = (
            f"{self.loc.get('lbl_title')}\\n\\n"
            f"FFmpeg: {ffmpeg_status}\\n"
            f"\\n"
            f"Video: WEBM, MP4, AVI, MOV, MKV\\n"
            f"Audio: WAV, MP3, OGG\\n"
            f"Images: TGA, PNG, JPEG, BMP\\n"
            f"\\n"
            f"Tools: Video Editor, Audio Editor, Pictogram Editor,\\n"
            f"       Coach Creator, Cover Creator, Converter\\n"
            f"\\n"
            f"Language: {self.loc.lang.upper()}"
        )
        self.info_label.config(text=text)

    def _update_texts(self):
        L = self.loc
        self.title(L.get("lbl_title"))
        self._build_menu()
        # Обновляем вкладки и фреймы
        for child in self.winfo_children():
            child.destroy()
        self._build_menu()
        self._build_ui()

    def _set_lang(self, lang):
        self.loc.set_lang(lang)
        self._update_texts()
        self._update_info()

    # --- Проект ---
    def _new_project(self):
        self.video_tracks.clear()
        self.audio_tracks.clear()
        self.pictogram_tracks.clear()
        self.project_file = None
        self.video_listbox.delete(0, "end")
        self.audio_listbox.delete(0, "end")
        self.picto_listbox.delete(0, "end")

    def _save_project(self):
        if not self.project_file:
            self._save_as_project()
            return
        self._do_save(self.project_file)

    def _save_as_project(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All", "*.*")]
        )
        if path:
            self.project_file = path
            self._do_save(path)

    def _do_save(self, path):
        data = {
            "version": "2.0",
            "language": self.loc.lang,
            "video_tracks": self.video_tracks,
            "audio_tracks": self.audio_tracks,
            "pictogram_tracks": self.pictogram_tracks,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("", self.loc.get("msg_saved"))
        except Exception as e:
            messagebox.showerror(self.loc.get("msg_error"), str(e))

    def _open_project(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.video_tracks = data.get("video_tracks", [])
            self.audio_tracks = data.get("audio_tracks", [])
            self.pictogram_tracks = data.get("pictogram_tracks", [])
            self.project_file = path
            lang = data.get("language", self.loc.lang)
            self._set_lang(lang)
            self._refresh_lists()
        except Exception as e:
            messagebox.showerror(self.loc.get("msg_error"), str(e))

    def _refresh_lists(self):
        self.video_listbox.delete(0, "end")
        for t in self.video_tracks:
            self.video_listbox.insert("end", os.path.basename(t))
        self.audio_listbox.delete(0, "end")
        for t in self.audio_tracks:
            self.audio_listbox.insert("end", os.path.basename(t))
        self.picto_listbox.delete(0, "end")
        for t in self.pictogram_tracks:
            self.picto_listbox.insert("end", os.path.basename(t))

    # --- Таймлайн ---
    def _add_video_track(self):
        p = filedialog.askopenfilename(
            filetypes=[("Video", "*.webm *.mp4 *.avi *.mov *.mkv"), ("All", "*.*")]
        )
        if p:
            self.video_tracks.append(p)
            self.video_listbox.insert("end", os.path.basename(p))

    def _remove_video_track(self):
        sel = self.video_listbox.curselection()
        if sel:
            idx = sel[0]
            self.video_listbox.delete(idx)
            if idx < len(self.video_tracks):
                self.video_tracks.pop(idx)

    def _add_audio_track(self):
        p = filedialog.askopenfilename(
            filetypes=[("Audio", "*.wav *.mp3 *.ogg"), ("All", "*.*")]
        )
        if p:
            self.audio_tracks.append(p)
            self.audio_listbox.insert("end", os.path.basename(p))

    def _remove_audio_track(self):
        sel = self.audio_listbox.curselection()
        if sel:
            idx = sel[0]
            self.audio_listbox.delete(idx)
            if idx < len(self.audio_tracks):
                self.audio_tracks.pop(idx)

    def _add_picto_track(self):
        p = filedialog.askopenfilename(
            filetypes=[("Images", "*.tga *.png *.jpg *.jpeg *.bmp"), ("All", "*.*")]
        )
        if p:
            self.pictogram_tracks.append(p)
            self.picto_listbox.insert("end", os.path.basename(p))

    def _remove_picto_track(self):
        sel = self.picto_listbox.curselection()
        if sel:
            idx = sel[0]
            self.picto_listbox.delete(idx)
            if idx < len(self.pictogram_tracks):
                self.pictogram_tracks.pop(idx)

    # --- Экспорт ---
    def _export_mashup(self):
        if not self.video_tracks and not self.audio_tracks:
            messagebox.showwarning("", self.loc.get("msg_no_file"))
            return
        outp = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4"), ("WebM", "*.webm"), ("All", "*.*")]
        )
        if not outp:
            return
        if not check_ffmpeg():
            messagebox.showerror(self.loc.get("msg_error"), self.loc.get("msg_ffmpeg_not_found"))
            return

        self.config(cursor="watch")
        self.update()

        ok = True
        # Объединяем видео
        if len(self.video_tracks) > 1:
            video_out = tempfile.mktemp(suffix=".mp4")
            ok = merge_videos(self.video_tracks, video_out)
        elif len(self.video_tracks) == 1:
            video_out = self.video_tracks[0]
        else:
            video_out = None

        # Объединяем аудио
        if len(self.audio_tracks) > 1:
            audio_out = tempfile.mktemp(suffix=".wav")
            ok = ok and merge_audio(self.audio_tracks, audio_out)
        elif len(self.audio_tracks) == 1:
            audio_out = self.audio_tracks[0]
        else:
            audio_out = None

        # Композит
        if video_out and audio_out:
            cmd = [FFMPEG, "-y", "-i", video_out, "-i", audio_out,
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                   "-shortest", outp]
            import subprocess
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
                ok = proc.returncode == 0
            except Exception:
                ok = False
        elif video_out:
            import shutil as sh
            sh.copy(video_out, outp)
        elif audio_out:
            import shutil as sh
            sh.copy(audio_out, outp)

        self.config(cursor="")
        if ok:
            messagebox.showinfo("", self.loc.get("msg_export_done") + f":\\n{outp}")
        else:
            messagebox.showerror(self.loc.get("msg_error"), "Export failed")

    # --- Диалоги ---
    def _open_video_editor(self):
        VideoEditorDialog(self, self.loc)

    def _open_audio_editor(self):
        AudioEditorDialog(self, self.loc)

    def _open_pictogram_editor(self):
        PictogramEditorDialog(self, self.loc)

    def _open_coach_creator(self):
        CoachCreatorDialog(self, self.loc)

    def _open_cover_creator(self):
        CoverCreatorDialog(self, self.loc)

    def _open_converter(self):
        ConverterDialog(self, self.loc)

    def _about(self):
        messagebox.showinfo(self.loc.get("menu_about"), self.loc.get("about_text"))


def main():
    app = JustDanceMashupStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
