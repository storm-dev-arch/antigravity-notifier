"""
Background Service that monitors Antigravity task completions
and displays smooth glassmorphism toast notifications.
"""

import os
import sys
import time
import sqlite3
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import io

# Redirect stdout and stderr if running under pythonw
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "notifier_service.log"

class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = FlushFileHandler(str(LOG_FILE), encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)

from toast import ToastNotification

import psutil

# Ensure single instance
_cur_pid = os.getpid()
for _p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        pname = (_p.info['name'] or '').lower()
        if _p.info['pid'] != _cur_pid and pname in ('python.exe', 'pythonw.exe'):
            _cmd = " ".join(_p.info['cmdline'] or [])
            if "notifier_service.py" in _cmd:
                logging.info(f"Another notifier instance already running (PID: {_p.info['pid']}). Exiting.")
                sys.exit(0)
    except Exception:
        pass

def find_antigravity_db() -> Path | None:
    """Finds the Antigravity conversation database dynamically across environments."""
    custom_env = os.environ.get("ANTIGRAVITY_DB_PATH")
    if custom_env and Path(custom_env).exists():
        return Path(custom_env)

    std_home = Path.home() / ".gemini" / "antigravity" / "conversation_summaries.db"
    if std_home.exists():
        return std_home

    user_prof = os.environ.get("USERPROFILE")
    if user_prof:
        up_path = Path(user_prof) / ".gemini" / "antigravity" / "conversation_summaries.db"
        if up_path.exists():
            return up_path

    local_app = os.environ.get("LOCALAPPDATA")
    if local_app:
        app_path = Path(local_app) / "Google" / "Antigravity" / "conversation_summaries.db"
        if app_path.exists():
            return app_path

    return None

def get_latest_conversation():
    db_path = find_antigravity_db()
    if not db_path or not db_path.exists():
        return None
    uri = f"file:{db_path.as_posix()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=1.0)
        cur = conn.cursor()
        cur.execute(
            "SELECT conversation_id, title, status, step_count, last_modified_time "
            "FROM conversation_summaries ORDER BY last_modified_time DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        return row
    except Exception as e:
        return None

class NotifierApp:
    def __init__(self):
        self.last_status = None
        self.last_convo_id = None
        self.active_toast = None

        # Check DB every 800ms
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_status)
        self.poll_timer.start(800)

        # Initial seed
        initial = get_latest_conversation()
        if initial:
            self.last_convo_id = initial[0]
            self.last_status = initial[2]
            logging.info(f"Initialized with convo {self.last_convo_id}, status: {self.last_status}")

        # Show welcome toast on startup so user sees it is active on their screen
        QTimer.singleShot(500, self.show_welcome)

    def show_welcome(self):
        self.welcome_toast = ToastNotification(
            title="Google Antigravity",
            message="Уведомления активированы на твоем экране! 🚀",
            duration=3500
        )
        self.welcome_toast.show_smooth()

    def check_status(self):
        row = get_latest_conversation()
        if not row:
            return

        convo_id, title, status, step_count, last_mod = row

        # Trigger notification when transitioning from RUNNING -> IDLE
        is_finish_transition = (
            self.last_status == "CASCADE_RUN_STATUS_RUNNING" and
            status == "CASCADE_RUN_STATUS_IDLE"
        )

        if is_finish_transition:
            logging.info(f"Turn finished for '{title}'! Triggering smooth notification.")
            self.trigger_toast(title or "Antigravity Task")

        self.last_status = status
        self.last_convo_id = convo_id

    def trigger_toast(self, title):
        msg = f"Ответ готов: {title}"
        if len(msg) > 75:
            msg = msg[:72] + "..."

        self.active_toast = ToastNotification(
            title="Google Antigravity",
            message=msg,
            duration=4500
        )
        self.active_toast.show_smooth()

def main():
    logging.info("Antigravity Notifier service started.")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    notifier = NotifierApp()
    try:
        sys.exit(app.exec())
    except BaseException as exc:
        logging.critical(f"Notifier exiting with {type(exc).__name__}: {exc}", exc_info=True)

if __name__ == "__main__":
    main()
