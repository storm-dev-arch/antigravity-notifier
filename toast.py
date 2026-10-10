"""
Staff-level Raycast / Linear aesthetic Toast Notification for Google Antigravity.
Zero emojis, zero AI slop. Clean typography, precision spacing, custom luxury audio chime.
"""

import sys
import winsound
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame
)

BASE_DIR = Path(__file__).resolve().parent
ICON_FILE = BASE_DIR / "antigravity_logo.png"
SOUND_FILE = BASE_DIR / "chime.wav"

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

        # Main Card: Raycast/Linear inspired obsidian dark mode
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
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(13)

        # App Icon
        self.icon_label = QLabel(self.card)
        self.icon_label.setFixedSize(40, 40)
        if ICON_FILE.exists():
            pix = QPixmap(str(ICON_FILE)).scaled(
                40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.icon_label.setPixmap(pix)
        else:
            self.icon_label.setText("AG")
            self.icon_label.setStyleSheet("color: #6366f1; font-weight: 800; font-size: 16px;")
        card_layout.addWidget(self.icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        text_layout.setContentsMargins(0, 0, 0, 0)

        # Header row: Title + Clean Status Pill (No emojis)
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        title_lbl = QLabel(title, self.card)
        title_lbl.setStyleSheet("""
            color: #f1f5f9;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.2px;
            font-family: "Segoe UI", -apple-system, sans-serif;
        """)
        top_row.addWidget(title_lbl)

        # Modern minimalist pill badge
        status_pill = QLabel("ГОТОВО", self.card)
        status_pill.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.28);
            font-size: 9px;
            font-weight: 700;
            padding: 1px 6px;
            border-radius: 4px;
            letter-spacing: 0.5px;
            font-family: "Segoe UI", -apple-system, sans-serif;
        """)
        top_row.addWidget(status_pill)
        top_row.addStretch()

        text_layout.addLayout(top_row)

        # Message body: clean high-contrast subtitle
        msg_lbl = QLabel(message, self.card)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            font-weight: 400;
            line-height: 14px;
            font-family: "Segoe UI", -apple-system, sans-serif;
        """)
        text_layout.addWidget(msg_lbl)

        card_layout.addLayout(text_layout)

        # Minimalist dismiss button
        close_btn = QPushButton("×", self.card)
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                font-size: 14px;
                font-weight: 400;
                border-radius: 10px;
                margin-top: -2px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
                color: #cbd5e1;
            }
        """)
        close_btn.clicked.connect(self.slide_out)
        card_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addWidget(self.card)

    def _setup_animation(self):
        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()

        margin_right = 24
        margin_bottom = 24

        self.final_x = geo.width() - self.width() - margin_right
        self.final_y = geo.height() - self.height() - margin_bottom

        self.start_pos = QPoint(self.final_x, self.final_y + 36)
        self.final_pos = QPoint(self.final_x, self.final_y)

        self.move(self.start_pos)
        self.setWindowOpacity(1.0)

        # Snappy cubic slide-in
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(320)
        self.pos_anim.setStartValue(self.start_pos)
        self.pos_anim.setEndValue(self.final_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def show_smooth(self):
        self.show()
        self.raise_()
        self.activateWindow()

        # Play custom luxury audio chime
        if SOUND_FILE.exists():
            try:
                winsound.PlaySound(str(SOUND_FILE), winsound.SND_FILENAME | winsound.SND_ASYNC)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.slide_out()
        super().mousePressEvent(event)

def show_notification(title="Google Antigravity", message="Генерация завершена", duration=4500):
    app = QApplication.instance()
    owns_app = False
    if app is None:
        app = QApplication(sys.argv)
        owns_app = True

    toast = ToastNotification(title, message, duration)
    toast.show_smooth()

    if owns_app:
        QTimer.singleShot(duration + 1000, app.quit)
        app.exec()

if __name__ == "__main__":
    title_arg = sys.argv[1] if len(sys.argv) > 1 else "Google Antigravity"
    msg_arg = sys.argv[2] if len(sys.argv) > 2 else "Ответ готов, шеф! Вайбкодим дальше"
    show_notification(
        title=title_arg,
        message=msg_arg
    )
