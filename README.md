# 🔔 Antigravity Glassmorphism Toast Notifier

<p align="center">
  <img src="antigravity_logo.png" alt="Google Antigravity Logo" width="128" height="128" />
</p>

<p align="center">
  <b>Sleek, Linear/Raycast-style Glassmorphism Desktop Toasts with Custom Luxury Audio Chimes</b><br>
  <i>Элегантные всплывающие стеклянные уведомления для Windows с кастомным звуком</i><br>
  <sub><b>Version 1.2.0 • Update by cm1s</b></sub>
</p>

<p align="center">
  <a href="#russian">🇷🇺 Читать на русском</a> • <a href="#english">🇬🇧 English Readme</a> • <a href="https://github.com/storm-dev-arch/antigravity-notifier/releases">📦 Скачать готовый EXE</a>
</p>

<p align="center">
  <a href="https://github.com/storm-dev-arch/antigravity-notifier/releases"><img src="https://img.shields.io/github/v/release/storm-dev-arch/antigravity-notifier?color=blue&style=for-the-badge" alt="Release"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

<a name="russian"></a>
## 🇷🇺 Документация на русском

### ✨ Возможности (v1.2.0 • Update by cm1s)
- **💎 Ультра-компактный Glassmorphism Pill (235x35)**:
  - Минималистичная стеклянная плашка `235x35 px` по центру внизу экрана.
  - Адаптация под цветовую тему Antigravity (автоматически подхватывает темную/светлую тему из Appearance).
  - Pre-baked HiDPI QPixmap рендеринг без оверхеда CSS и лишних виджетов.
- **🖥️ Удобное управление в системном трее**:
  - Иконка в трее Windows с контекстным меню.
  - **Быстрый выход из программы** в один клик без поиска процессов в Диспетчере задач.
  - Тестовое уведомление и переключатель автозагрузки с Windows прямо из меню.
- **🚀 Уведомление при запуске**:
  - При старте программы сразу всплывает компактное уведомление с подтверждением активности.
- **🔊 Аппаратный звук без лагов**:
  - Мгновенное воспроизведение через WinMM (`sound.mp3` и `chime.wav`).
- **🎯 Быстрый переход в чат**:
  - Клик левой кнопкой мыши по уведомлению мгновенно активирует окно Antigravity и открывает нужный диалог.
- **🛡️ Нулевая нагрузка на CPU**:
  - SQLite stat-gating по `st_mtime_ns` — ноль запросов к базе в режиме простоя.

---

### 📦 Установка и запуск

#### Вариант 1. Готовый EXE-файл (для обычных пользователей)
1. Скачай архив `AntigravityNotifier-v1.2.0-Windows.zip` со страницы [**Releases**](https://github.com/storm-dev-arch/antigravity-notifier/releases).
2. Распакуй и запусти `AntigravityNotifier.exe`.
3. Установка Python **не требуется** — программа сразу появится в трее и покажет уведомление о готовности!

#### Вариант 2. Запуск из исходного кода (Python)
```bash
git clone https://github.com/storm-dev-arch/antigravity-notifier.git
cd antigravity-notifier
pip install -r requirements.txt
```

- **Тест уведомления:** запусти `test.bat` или `python toast.py`.
- **Запуск в фоне:** запусти `start.bat` или `run_silent.vbs`.
- **Остановка сервиса:** через меню трея ("Выход") или `stop.bat`.

---

<a name="english"></a>
## 🇬🇧 English Documentation

### ✨ Features (v1.2.0 • Update by cm1s)
- **💎 Ultra-compact Glassmorphism Pill (235x35)**:
  - Minimalistic bottom-centered glass card (`235x35 px`).
  - Native live sync with Antigravity dark/light Appearance theme.
  - Zero-CSS overhead with pre-baked HiDPI QPixmap rendering.
- **🖥️ Windows System Tray Integration**:
  - Persistent tray icon with context menu.
  - Clean one-click exit without needing Windows Task Manager.
  - Test notification trigger and Windows autorun toggle.
- **🚀 Startup Notification**:
  - Displays a brief confirmation toast immediately on app launch.
- **🔊 Zero-Latency Audio**:
  - Direct WinMM hardware playback (`sound.mp3` and `chime.wav`).
- **🎯 One-Click Chat Focus**:
  - Left-clicking the toast immediately focuses the Antigravity window and navigates to the active conversation.
- **🛡️ Zero CPU Overhead**:
  - Stat-gated SQLite `st_mtime_ns` polling — zero queries when idle.

---

### 📦 Installation & Usage

#### Option 1. Standalone EXE (Recommended)
1. Download `AntigravityNotifier-v1.2.0-Windows.zip` from [**Releases**](https://github.com/storm-dev-arch/antigravity-notifier/releases).
2. Unzip and run `AntigravityNotifier.exe`.
3. No Python installation required — it lives in your system tray and starts immediately!

#### Option 2. Run from Source
```bash
git clone https://github.com/storm-dev-arch/antigravity-notifier.git
cd antigravity-notifier
pip install -r requirements.txt
```

- **Test Notification:** run `test.bat` or `python toast.py`.
- **Background Watcher:** run `start.bat` or `run_silent.vbs`.
- **Exit Watcher:** right-click tray icon and select "Выход", or run `stop.bat`.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
