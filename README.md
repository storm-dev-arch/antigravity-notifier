# 🔔 Antigravity Glassmorphism Toast Notifier

<p align="center">
  <img src="antigravity_logo.png" alt="Google Antigravity Logo" width="128" height="128" />
</p>

<p align="center">
  <b>Sleek, Linear/Raycast-style Glassmorphism Desktop Toasts with Authentic Steam Audio Chimes</b>
</p>

<p align="center">
  <a href="https://github.com/storm-dev-arch/antigravity-notifier/releases"><img src="https://img.shields.io/github/v/release/storm-dev-arch/antigravity-notifier?color=blue&style=for-the-badge" alt="Release"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## ✨ Features

- **💎 Linear / Raycast Aesthetic**:
  - Dark glassmorphism card with deep translucency (`rgba(18, 18, 24, 215)`).
  - Subtle frosted border (`rgba(255, 255, 255, 0.12)`) and soft ambient glow.
  - Pixel-perfect typography and brand icon rendering.

- **🎬 60 FPS Cubic Animation**:
  - Smooth 320ms slide-in from the bottom-right corner of the primary screen.
  - Easing curve: `QEasingCurve.Type.OutCubic` for natural momentum.
  - Auto-fade after 4.5 seconds.

- **🔊 Authentic Steam Toast Audio**:
  - Plays the official, satisfying Steam Deck toast chime (`chime.wav` / `steam_toast.wav`).
  - Zero latency asynchronous audio playback via `winsound.SND_ASYNC`.

- **🤖 Antigravity & Generic App Support**:
  - Includes `notifier_service.py` to watch Antigravity database tasks (`conversation_summaries.db`).
  - Can be triggered as a standalone CLI for ANY script or workflow:
    ```bash
    python toast.py "Title" "Your message here"
    ```

---

## 🛠️ Project Structure

```
antigravity-notifier/
├── toast.py               # Standalone PyQt6 toast notification widget
├── notifier_service.py    # Background SQLite db watcher for turn completions
├── chime.wav              # Crisp notification sound
├── antigravity_logo.png   # Brand asset
├── run_silent.vbs         # Silent background launcher
├── test.bat               # One-click test script
├── start.bat / stop.bat   # Windows control scripts
└── requirements.txt       # Dependencies
```

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/storm-dev-arch/antigravity-notifier.git
cd antigravity-notifier
pip install -r requirements.txt
```

### 2. Standalone Toast Usage
You can call `toast.py` directly from any program, PowerShell script, or batch file:
```bash
python toast.py "Build Complete" "Your project compiled successfully in 1.4s"
```

### 3. Background Service
To run the automated background watcher for Google Antigravity:
- Double-click `run_silent.vbs` (runs invisibly in the background).
- To test the toast appearance: double-click `test.bat`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
