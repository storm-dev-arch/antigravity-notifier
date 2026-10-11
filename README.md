# 🔔 Antigravity Glassmorphism Toast Notifier

<p align="center">
  <img src="antigravity_logo.png" alt="Google Antigravity Logo" width="128" height="128" />
</p>

<p align="center">
  <b>Sleek, Linear/Raycast-style Glassmorphism Desktop Toasts & System Tray App for Google Antigravity</b><br>
  <i>Всплывающие стеклянные уведомления для Windows со звуком и управлением через системный трей</i>
</p>

<p align="center">
  <a href="#russian">🇷🇺 Читать на русском</a> • <a href="#english">🇬🇧 English Readme</a>
</p>

<p align="center">
  <a href="https://github.com/storm-dev-arch/antigravity-notifier/releases/tag/v1.2.0"><img src="https://img.shields.io/badge/Release-v1.2.0-blue?style=for-the-badge" alt="Release"></a>
  <img src="https://img.shields.io/badge/Windows-Standalone%20EXE-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/UI-PyQt6%20Glassmorphism-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/Tray-System%20Tray%20Menu-purple?style=for-the-badge" alt="Tray">
  <img src="https://img.shields.io/badge/Update%20by-cm1s-orange?style=for-the-badge" alt="Update by cm1s">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

<a name="russian"></a>
## 🇷🇺 Документация на русском

### 📦 Скачать готовый `.exe` (без установки Python):
👉 [**Скачать AntigravityNotifier-v1.2.0-Windows.zip**](https://github.com/storm-dev-arch/antigravity-notifier/releases/download/v1.2.0/AntigravityNotifier-v1.2.0-Windows.zip)  
*(Распакуй архив и просто запусти `AntigravityNotifier.exe`)*

---

### ✨ Возможности версии 1.2.0
- **🖥️ Управление через системный трей (System Tray)**:
  - Иконка программы аккуратно сидит в трее Windows возле часов.
  - Закрытие в один клик: правый клик по иконке в трее -> **«Выход»**. Больше не нужно искать процессы в диспетчере задач!
  - Меню трея:
    - 🔔 **Тестовое уведомление** — мгновенная проверка звука и анимации.
    - ⚡ **Автозагрузка с Windows** — включение/выключение автозапуска в один клик (через галочку).
    - ℹ️ **О программе** — информация о версии v1.2.0 (Update by cm1s).
    - ❌ **Выход** — полное завершение работы программы.
- **🚀 Приветственное уведомление при старте**:
  - При запуске программа сразу показывает всплывающий тост и воспроизводит звук: *«Google Antigravity: Программа запущена и активна в трее»*.
- **💎 Glassmorphism UI (Raycast / Linear style)**:
  - Глубокий темный стеклянный фон с эффектом прозрачности (`rgba(15, 20, 28, 0.95)`).
  - Плавная 60 FPS кубическая анимация выезда из правого нижнего угла экрана.
  - Кастомный аудио-отклик через встроенный медиа-движок.
- **🛡️ Защита от дублей и зависаний**:
  - Встроенный Single Instance Lock (QSharedMemory) предотвращает случайный запуск двух копий программы.

---

### 🛠️ Исходный код и запуск для разработчиков

Если ты хочешь запустить программу из исходников:
```bash
git clone https://github.com/storm-dev-arch/antigravity-notifier.git
cd antigravity-notifier
pip install -r requirements.txt
python app.py
```

Сборка собственного `.exe`:
```bash
pyinstaller --noconsole --onefile --icon=antigravity_icon.ico --add-data "sound.mp3;." --add-data "chime.wav;." --add-data "antigravity_logo.png;." --add-data "antigravity_icon.ico;." app.py -n AntigravityNotifier
```

---

<a name="english"></a>
## 🇬🇧 English Documentation

### 📦 Download Ready-to-Run `.exe` (No Python needed):
👉 [**Download AntigravityNotifier-v1.2.0-Windows.zip**](https://github.com/storm-dev-arch/antigravity-notifier/releases/download/v1.2.0/AntigravityNotifier-v1.2.0-Windows.zip)

---

### ✨ Features
- **🖥️ System Tray Integration**:
  - Program resides in Windows system tray.
  - Easy exit via context menu (no more Task Manager searching).
  - Tray options: Test Notification, Toggle Windows Startup, About, Exit.
- **🚀 Startup Welcome Toast**:
  - Shows an immediate notification and audio chime on launch.
- **💎 Linear / Raycast Glassmorphism**:
  - Dark translucent card with subtle borders and smooth 60 FPS cubic animation.
  - Powered by PyQt6 and QtMultimedia.
- **🛡️ Single-Instance Watchdog**:
  - Built-in mutex preventing duplicate running processes.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
