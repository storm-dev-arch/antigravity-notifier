"""
Antigravity Notifier v1.2.0 — Update by cm1s
Staff-level Glassmorphism Desktop Notifications & System Tray Application for Google Antigravity.
"""

import os
import sys
import time
import sqlite3
import winreg
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QUrl, QThread, pyqtSignal, QSharedMemory
from PyQt6.QtGui import QColor, QFont, QPixmap, QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Резолвер путей (поддерживает запуск в виде скрипта и в виде скомпилированного .exe через PyInstaller)
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

ICON_PNG = get_resource_path("antigravity_logo.png")
ICON_ICO = get_resource_path("antigravity_icon.ico")
SOUND_MP3 = get_resource_path("sound.mp3")
SOUND_WAV = get_resource_path("chime.wav")

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_KEY = "AntigravityNotifier"

def is_autorun_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, REG_KEY)
        winreg.CloseKey(key)
        return True
    except WindowsError:
        return False

def set_autorun(enabled):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        if enabled:
            if getattr(sys, 'frozen', False):
                app_path = f'"{sys.executable}"'
            else:
                pyw = sys.executable.replace("python.exe", "pythonw.exe")
                app_path = f'"{pyw}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, REG_KEY, 0, winreg.REG_SZ, app_path)
        else:
            try:
                winreg.DeleteValue(key, REG_KEY)
            except WindowsError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting autorun: {e}")
        return False

# Поиск базы данных Antigravity
def get_antigravity_db_path():
    appdata = os.environ.get("APPDATA", "")
    userprofile = os.environ.get("USERPROFILE", "")
    candidates = [
        Path(appdata) / "Antigravity" / "User" / "globalStorage" / "conversation_summaries.db",
        Path(appdata) / "Google" / "Antigravity" / "User" / "globalStorage" / "conversation_summaries.db",
        Path(userprofile) / ".antigravity" / "conversation_summaries.db",
        Path(userprofile) / ".gemini" / "antigravity" / "conversation_summaries.db"
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

# Фоновый поток для отслеживания событий Antigravity
class AntigravityWatcherThread(QThread):
    turn_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.last_status = None

    def run(self):
        while self.running:
            try:
                db_path = get_antigravity_db_path()
                if db_path.exists():
                    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=2.0)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT summary, status FROM conversations 
                        WHERE status IS NOT NULL 
                        ORDER BY last_modified_time DESC LIMIT 1
                    """)
                    row = cursor.fetchone()
                    conn.close()

                    if row:
                        title, status = row
                        if self.last_status == "CASCADE_RUN_STATUS_RUNNING" and status == "CASCADE_RUN_STATUS_IDLE":
                            self.turn_finished.emit(title or "Генерация ответа завершена!")
                        self.last_status = status
            except Exception:
                pass
            time.sleep(1.8)

    def stop(self):
        self.running = False
        self.wait(1500)

# Виджет всплывающего уведомления (Glassmorphism)
class ToastNotification(QWidget):
    def __init__(self, title="Google Antigravity", message="Генерация завершена", duration=4500):
        super().__init__()
        self.duration = duration
        self.is_closing = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFixedSize(390, 88)

        self._init_ui(title, message)
        self._setup_animation()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.slide_out)

    def _init_ui(self, title, message):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)

        self.card = QFrame(self)
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f141c,
                    stop:1 #090d14);
                border: 1px solid rgba(255, 255, 255, 0.09);
                border-top: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 12px;
            }
        """)

        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(12)

        # Логотип
        self.icon_label = QLabel(self.card)
        self.icon_label.setFixedSize(38, 38)
        self.icon_label.setStyleSheet("background: transparent;")
        if os.path.exists(ICON_PNG):
            pixmap = QPixmap(ICON_PNG)
            self.icon_label.setPixmap(pixmap.scaled(38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # Текст
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title, self.card)
        self.title_label.setFont(QFont("Segoe UI Variable Display", 10, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: #ffffff; background: transparent;")

        self.msg_label = QLabel(message, self.card)
        self.msg_label.setFont(QFont("Segoe UI Variable Text", 9, QFont.Weight.Normal))
        self.msg_label.setStyleSheet("color: #94a3b8; background: transparent;")
        self.msg_label.setWordWrap(True)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.msg_label)

        # Кнопка закрытия
        self.close_btn = QPushButton("✕", self.card)
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                font-size: 11px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
        """)
        self.close_btn.clicked.connect(self.slide_out)

        card_layout.addWidget(self.icon_label)
        card_layout.addLayout(text_layout, 1)
        card_layout.addWidget(self.close_btn)

        main_layout.addWidget(self.card)

    def _setup_animation(self):
        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()

        margin_right = 20
        margin_bottom = 20

        self.final_x = geo.width() - self.width() - margin_right
        self.final_y = geo.height() - self.height() - margin_bottom

        self.start_pos = QPoint(self.final_x, self.final_y + 36)
        self.final_pos = QPoint(self.final_x, self.final_y)

        self.move(self.start_pos)
        self.setWindowOpacity(1.0)

        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(320)
        self.pos_anim.setStartValue(self.start_pos)
        self.pos_anim.setEndValue(self.final_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def show_smooth(self):
        self.show()
        self.raise_()
        self.activateWindow()

        # Воспроизведение звука
        sound_path = SOUND_MP3 if os.path.exists(SOUND_MP3) else SOUND_WAV
        if os.path.exists(sound_path):
            try:
                self.player = QMediaPlayer(self)
                self.audio_output = QAudioOutput(self)
                self.player.setAudioOutput(self.audio_output)
                self.audio_output.setVolume(1.0)
                self.player.setSource(QUrl.fromLocalFile(sound_path))
                self.player.play()
            except Exception:
                pass

        self.pos_anim.start()
        self.timer.start(self.duration)

    def slide_out(self):
        if self.is_closing:
            return
        self.is_closing = True
        self.timer.stop()

        self.pos_anim.stop()
        self.pos_anim.setDuration(220)
        self.pos_anim.setStartValue(self.pos())
        self.pos_anim.setEndValue(self.start_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.pos_anim.finished.connect(self.close)
        self.pos_anim.start()

    def enterEvent(self, event):
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_closing:
            self.timer.start(2500)
        super().leaveEvent(event)

# Главный класс приложения с системным треем
class AntigravityNotifierApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Установка иконки приложения
        icon_path = ICON_ICO if os.path.exists(ICON_ICO) else ICON_PNG
        self.app_icon = QIcon(icon_path)
        self.app.setWindowIcon(self.app_icon)

        self.active_toast = None
        self._init_tray()

        # Запуск фонового потока
        self.watcher = AntigravityWatcherThread()
        self.watcher.turn_finished.connect(self.show_toast_notification)
        self.watcher.start()

        # Приветственное уведомление при старте программы
        QTimer.singleShot(600, lambda: self.show_toast_notification("Программа запущена и активна в трее"))

    def _init_tray(self):
        self.tray = QSystemTrayIcon(self.app_icon, self.app)
        self.tray.setToolTip("Antigravity Notifier v1.2.0 (Update by cm1s)")

        # Меню трея
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #0f141c;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1e293b;
            }
        """)

        # Пункты меню
        self.action_test = QAction("🔔 Тестовое уведомление", self.menu)
        self.action_test.triggered.connect(lambda: self.show_toast_notification("Тестовое уведомление: всё работает отлично!"))
        self.menu.addAction(self.action_test)

        self.action_autorun = QAction("⚡ Автозагрузка с Windows", self.menu)
        self.action_autorun.setCheckable(True)
        self.action_autorun.setChecked(is_autorun_enabled())
        self.action_autorun.triggered.connect(self.toggle_autorun)
        self.menu.addAction(self.action_autorun)

        self.menu.addSeparator()

        self.action_about = QAction("ℹ️ О программе", self.menu)
        self.action_about.triggered.connect(self.show_about)
        self.menu.addAction(self.action_about)

        self.menu.addSeparator()

        self.action_exit = QAction("❌ Выход", self.menu)
        self.action_exit.triggered.connect(self.exit_app)
        self.menu.addAction(self.action_exit)

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_toast_notification("Программа активна в системном трее")

    def toggle_autorun(self):
        new_state = self.action_autorun.isChecked()
        set_autorun(new_state)
        status_text = "включена" if new_state else "выключена"
        self.show_toast_notification(f"Автозагрузка с Windows {status_text}")

    def show_about(self):
        msg = QMessageBox()
        msg.setWindowTitle("О программе — Antigravity Notifier")
        msg.setText("<b>Antigravity Notifier v1.2.0</b><br><br>"
                    "Элегантные Glassmorphism-уведомления с кастомным звуком для Google Antigravity.<br><br>"
                    "<i>Update by cm1s</i><br>"
                    "GitHub: <a href='https://github.com/storm-dev-arch/antigravity-notifier'>storm-dev-arch/antigravity-notifier</a>")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def show_toast_notification(self, text="Генерация ответа завершена!"):
        if self.active_toast:
            try:
                self.active_toast.close()
            except Exception:
                pass
        self.active_toast = ToastNotification("Google Antigravity", text[:75], duration=4500)
        self.active_toast.show_smooth()

    def exit_app(self):
        self.watcher.stop()
        self.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    # Защита от повторного запуска (Single Instance Lock)
    shared_memory = QSharedMemory("AntigravityNotifier_SingleInstance_Mutex")
    if not shared_memory.create(1):
        # Экземпляр уже запущен
        sys.exit(0)

    app_instance = AntigravityNotifierApp()
    sys.exit(app_instance.run())
