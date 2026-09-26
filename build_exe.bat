@echo off
chcp 65001 >nul 2>&1
title Just Dance Mashup Studio - Build EXE
color 0B

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║     Just Dance Mashup Studio - EXE Builder           ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Проверка Python ──────────────────────────────────────
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ОШИБКА] Python не найден в PATH.
    echo          Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

:: ── Проверка ffmpeg ──────────────────────────────────────
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ВНИМАНИЕ] ffmpeg не найден в PATH.
    echo            Видео/аудио функции не будут работать в exe.
    echo            Скачайте ffmpeg с https://ffmpeg.org и добавьте в PATH.
    echo.
    set /p CONT="Продолжить сборку без ffmpeg? (y/n): "
    if /i not "%CONT%"=="y" exit /b 1
)

:: ── Создаём виртуальное окружение ────────────────────────
echo  [1/5] Создание виртуального окружения...
if exist .venv (
    echo        Окружение уже существует, используем существующее.
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo  [ОШИБКА] Не удалось создать виртуальное окружение.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

:: ── Обновление pip ────────────────────────────────────────
echo  [2/5] Обновление pip...
python -m pip install --upgrade pip >nul 2>&1

:: ── Установка зависимостей ───────────────────────────────
echo  [3/5] Установка зависимостей...
pip install Pillow opencv-contrib-python-headless scipy numpy pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ОШИБКА] Не удалось установить зависимости.
    pause
    exit /b 1
)

:: ── Сборка через PyInstaller ─────────────────────────────
echo  [4/5] Сборка exe через PyInstaller...
echo.

:: Очищаем старую сборку
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "JustDanceMashupStudio.spec" del /q "JustDanceMashupStudio.spec"

:: Собираем
pyinstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "JustDanceMashupStudio" ^
    --add-data "localization.py;." ^
    --add-data "media_converter.py;." ^
    --add-data "pictogram_editor.py;." ^
    --add-data "coach_creator.py;." ^
    --add-data "cover_creator.py;." ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageDraw ^
    --hidden-import PIL.ImageFilter ^
    --hidden-import PIL.ImageEnhance ^
    --hidden-import PIL.ImageOps ^
    --hidden-import PIL.ImageFont ^
    --hidden-import PIL.ImageChops ^
    --hidden-import cv2 ^
    --hidden-import numpy ^
    --hidden-import scipy.io.wavfile ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import tkinter.colorchooser ^
    --hidden-import subprocess ^
    --hidden-import json ^
    --hidden-import os ^
    --hidden-import sys ^
    --collect-all PIL ^
    --collect-all cv2 ^
    --collect-all scipy ^
    --collect-all numpy ^
    main_app.py

if %errorlevel% neq 0 (
    echo.
    echo  [ОШИБКА] Сборка не удалась.
    pause
    exit /b 1
)

:: ── Финализация ──────────────────────────────────────────
echo  [5/5] Готово!
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║  Сборка завершена!                                  ║
echo  ║  EXE файл: dist\JustDanceMashupStudio.exe            ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Открываем папку dist
explorer dist

pause
