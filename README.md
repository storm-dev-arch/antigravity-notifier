# 🔔 Antigravity Glassmorphism Toast Notifier

<p align="center">
  <img src="antigravity_logo.png" alt="Google Antigravity Logo" width="128" height="128" />
</p>

<p align="center">
  <b>Sleek, Linear/Raycast-style Glassmorphism Desktop Toasts with Custom Luxury Audio Chimes</b><br>
  <i>Элегантные всплывающие стеклянные уведомления для Windows с кастомным звуком</i>
</p>

<p align="center">
  <a href="#russian">🇷🇺 Читать на русском</a> • <a href="#english">🇬🇧 English Readme</a> • <a href="#changelog">📜 Changelog</a>
</p>

<p align="center">
  <a href="https://github.com/storm-dev-arch/antigravity-notifier/releases/tag/v1.1.0"><img src="https://img.shields.io/badge/Release-v1.1.0-blue?style=for-the-badge" alt="Release"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Update%20by-cm1s-orange?style=for-the-badge" alt="Update by cm1s">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

<a name="changelog"></a>
## 🚀 Версия 1.1.0 (v1.1.0) — Update by cm1s

### 🇷🇺 Что нового:
- **🎵 Обновленный звуковой движок**: переход на `PyQt6.QtMultimedia` с поддержкой `sound.mp3` и `chime.wav` с кристально чистым воспроизведением без задержек.
- **🛡️ Аппаратный Debounce-лок (2.5 сек)**: защита от двойных уведомлений. Исключает ложные дублирования при одновременных триггерах.
- **💎 Доработанная геометрия Glassmorphism**: оптимизированная плавная кубическая кривая скольжения `OutCubic` и улучшенный отклик на клик и ховер.
- **🇷🇺 Полная русскоязычная документация**: добавлены подробные инструкции и описание архитектуры на русском языке.
- *Credit: Update by cm1s.*

### 🇬🇧 What's New:
- **🎵 Modern Audio Engine**: Powered by `PyQt6.QtMultimedia`, playing `sound.mp3` and `chime.wav` with zero audio latency.
- **🛡️ 2.5s Mutex Debounce Lock**: Completely eliminates double toasts across concurrent callers.
- **💎 Refined Glassmorphism Aesthetics**: Polished cubic slide-in physics, hover states, and dismiss mechanics.
- **🌐 Full Bilingual Support**: Comprehensive documentation in Russian and English.
- *Credit: Update by cm1s.*

---

<a name="russian"></a>
## 🇷🇺 Документация на русском

### ✨ Возможности
- **💎 Glassmorphism UI (Raycast / Linear)**:
  - Глубокий темный стеклянный фон с эффектом прозрачности (`rgba(15, 20, 28, 0.95)`).
  - Тонкая рамка с градиентом и мягким свечением.
  - Никаких лишних смайликов и AI-слопа — чистая типографика и оригинальный логотип.
- **🎬 Плавная анимация на 60 FPS**:
  - Кубическая кривая скольжения (`OutCubic`) длительностью 320ms из правого нижнего угла экрана.
  - Автоматическое плавное скрытие через 4.5 секунды (или кликом по карточке).
- **🔊 Кастомный звук уведомления**:
  - Воспроизведение через встроенный `PyQt6.QtMultimedia` (поддержка `sound.mp3` и `chime.wav`).
  - Мгновенный отклик без задержек.
- **🛡️ Защита от дублей (Debounce Lock)**:
  - Встроенный 2.5-секундный мьютекс предотвращает повторные всплытия, если несколько процессов вызывают тост одновременно.
- **🛠️ Автономный CLI**:
  - Можно использовать в любых своих скриптах, играх или задачах автоматизации.

### 🚀 Быстрый старт

#### 1. Установка
```bash
git clone https://github.com/storm-dev-arch/antigravity-notifier.git
cd antigravity-notifier
pip install -r requirements.txt
```

#### 2. Проверка работы
```bash
# Запустить тестовое уведомление:
test.bat
# или через Python:
python toast.py "Заголовок" "Генерация ответа завершена!"
```

#### 3. Фоновый наблюдатель за Antigravity
- **Запуск в фоне (без окон):** запусти `run_silent.vbs` или `start.bat`.
- **Остановка сервиса:** запусти `stop.bat`.
Скрипты полностью автономны и автоматически находят установленный Python и базу данных Antigravity на любом компьютере.

---

<a name="english"></a>
## 🇬🇧 English Documentation

### ✨ Features
- **💎 Linear / Raycast Aesthetic**:
  - Dark obsidian glassmorphism card with precision borders and subtle ambient glow.
  - Zero emojis or AI-slop graphics — staff-grade typography and branding.
- **🎬 60 FPS Cubic Animation**:
  - Snappy 320ms slide-in from bottom-right corner using `QEasingCurve.Type.OutCubic`.
  - Auto-fade after 4.5 seconds with pause-on-hover capability.
- **🔊 Custom Audio Playback**:
  - Native playback of `sound.mp3` or `chime.wav` via `PyQt6.QtMultimedia`.
- **🛡️ Hardware Debounce Lock**:
  - Built-in 2.5-second mutex lock preventing duplicate toasts across multiple callers.
- **🛠️ Standalone CLI & Auto-Detection**:
  - Automatically resolves Python runtime (`pythonw`, `py`, `python`) and dynamic Antigravity paths on any machine.

### 🚀 Quick Start
```bash
git clone https://github.com/storm-dev-arch/antigravity-notifier.git
cd antigravity-notifier
pip install -r requirements.txt

# Test notification:
test.bat

# Run background watcher:
run_silent.vbs
# (or start.bat)

# Stop background watcher:
stop.bat
```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
