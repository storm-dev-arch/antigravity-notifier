"""
Ultra-lightweight Background Service that monitors Antigravity task completions
and displays 235x35 bottom-centered theme-adaptive glass notifications.
Optimized with:
- Win32 Kernel Named Mutex (zero psutil scan overhead)
- SQLite st_mtime_ns stat-gating (zero DB queries when idle)
- Persistent read-only SQLite connection
- Single reusable ToastNotification instance with live theme sync
- System Tray integration with clean exit, test toast, and autorun toggle
"""

import ctypes
import io
import logging
import os
import sqlite3
import sys
import winreg
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

# Redirect stdout and stderr if running under pythonw
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
    APP_DIR = BASE_DIR

LOG_FILE = APP_DIR / "notifier_service.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

from toast import ToastNotification, _CONFIG_PATH, show_notification

# Single-instance check via fast Win32 Kernel Mutex (~5 microseconds)
_MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(
    None, False, "Local\\AntigravityNotifierService_Mutex"
)
if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    show_notification("Google Antigravity", "Уведомления уже активны в трее", duration=2800)
    sys.exit(0)

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_KEY = "AntigravityNotifier"


def is_autorun_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, REG_KEY)
            return True
    except WindowsError:
        return False


def set_autorun(enabled: bool) -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE) as key:
            if enabled:
                if getattr(sys, "frozen", False):
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
        return True
    except Exception as exc:
        logging.error("Failed to update autorun: %s", exc)
        return False


def find_antigravity_db() -> Path | None:
    """Finds the Antigravity conversation database once across environments."""
    custom_env = os.environ.get("ANTIGRAVITY_DB_PATH")
    if custom_env:
        p = Path(custom_env)
        if p.exists():
            return p

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


class NotifierApp:
    __slots__ = (
        "__weakref__",
        "db_path",
        "wal_path",
        "conn",
        "last_db_mtime",
        "last_cfg_mtime",
        "convo_states",
        "latest_convo_id",
        "toast",
        "poll_timer",
        "tray",
        "tray_menu",
        "action_test",
        "action_autorun",
        "action_about",
        "action_exit",
    )

    def __init__(self) -> None:
        self.db_path: Path | None = find_antigravity_db()
        self.wal_path: Path | None = (
            self.db_path.with_name(self.db_path.name + "-wal") if self.db_path else None
        )
        self.conn: sqlite3.Connection | None = None
        self.last_db_mtime: int = -1
        self.last_cfg_mtime: int = self._get_cfg_mtime()
        self.convo_states: dict[str, dict] = {}
        self.latest_convo_id: str | None = None

        # Single reusable toast widget (zero re-allocation per notification)
        self.toast = ToastNotification(
            title="Google Antigravity",
            message="Программа запущена и активна в трее",
            duration=3200,
        )

        # Initial seed of all active conversations
        initial_rows = self._query_conversations(force=True)
        if initial_rows:
            self.latest_convo_id = initial_rows[0][0]
            for row in initial_rows:
                cid, title, status, step_count, _ = row
                self.convo_states[cid] = {
                    "status": status,
                    "steps": int(step_count or 0),
                    "title": title,
                }
            logging.info(
                "Initialized with %d conversations (latest: %s)",
                len(self.convo_states),
                self.latest_convo_id,
            )

        self._init_tray()

        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_status)
        self.poll_timer.start(200)

        QTimer.singleShot(250, self.show_welcome)

    def _init_tray(self) -> None:
        icon_path = BASE_DIR / "antigravity_icon.ico"
        if not icon_path.exists():
            icon_path = BASE_DIR / "antigravity_logo.png"

        app_icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
        QApplication.setWindowIcon(app_icon)

        self.tray = QSystemTrayIcon(app_icon)
        self.tray.setToolTip("Antigravity Notifier v1.2.0 (Update by cm1s)")

        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet("""
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

        self.action_test = QAction("🔔 Тестовое уведомление", self.tray_menu)
        self.action_test.triggered.connect(lambda: self.trigger_toast("Тестовое уведомление: всё работает отлично!", self.latest_convo_id))
        self.tray_menu.addAction(self.action_test)

        self.action_autorun = QAction("⚡ Автозагрузка с Windows", self.tray_menu)
        self.action_autorun.setCheckable(True)
        self.action_autorun.setChecked(is_autorun_enabled())
        self.action_autorun.triggered.connect(self.toggle_autorun)
        self.tray_menu.addAction(self.action_autorun)

        self.tray_menu.addSeparator()

        self.action_about = QAction("ℹ️ О программе", self.tray_menu)
        self.action_about.triggered.connect(self.show_about)
        self.tray_menu.addAction(self.action_about)

        self.tray_menu.addSeparator()

        self.action_exit = QAction("❌ Выход", self.tray_menu)
        self.action_exit.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.action_exit)

        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.trigger_toast("Программа активна в системном трее", self.latest_convo_id)

    def toggle_autorun(self) -> None:
        new_state = self.action_autorun.isChecked()
        set_autorun(new_state)
        status_text = "включена" if new_state else "выключена"
        self.trigger_toast(f"Автозагрузка с Windows {status_text}", self.latest_convo_id)

    def show_about(self) -> None:
        self.trigger_toast("Antigravity Notifier v1.2.0 • Update by cm1s", self.latest_convo_id)

    def quit_app(self) -> None:
        logging.info("Exiting Antigravity Notifier via tray menu.")
        self.poll_timer.stop()
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
        if self.toast:
            try:
                self.toast.close()
            except Exception:
                pass
        if hasattr(self, "tray"):
            self.tray.hide()
        QApplication.quit()

    @staticmethod
    def _get_cfg_mtime() -> int:
        if _CONFIG_PATH is not None:
            try:
                return _CONFIG_PATH.stat().st_mtime_ns
            except OSError:
                pass
        return 0

    def _get_db_mtime(self) -> int:
        if self.db_path is None:
            self.db_path = find_antigravity_db()
            if self.db_path is not None:
                self.wal_path = self.db_path.with_name(self.db_path.name + "-wal")
            else:
                return 0

        mtime = 0
        try:
            mtime = self.db_path.stat().st_mtime_ns
        except OSError:
            return 0

        if self.wal_path is not None:
            try:
                wal_m = self.wal_path.stat().st_mtime_ns
                if wal_m > mtime:
                    mtime = wal_m
            except OSError:
                pass
        return mtime

    def _query_conversations(self, force: bool = False) -> list[tuple]:
        cur_mtime = self._get_db_mtime()
        if cur_mtime == 0:
            return []
        if not force and cur_mtime == self.last_db_mtime:
            return []
        self.last_db_mtime = cur_mtime

        try:
            if self.conn is None and self.db_path is not None:
                uri = f"file:{self.db_path.as_posix()}?mode=ro"
                self.conn = sqlite3.connect(uri, uri=True, timeout=0.5, check_same_thread=False)

            if self.conn is not None:
                cur = self.conn.cursor()
                cur.execute(
                    "SELECT conversation_id, title, status, step_count, last_modified_time "
                    "FROM conversation_summaries ORDER BY last_modified_time DESC LIMIT 25"
                )
                return cur.fetchall()
        except Exception:
            if self.conn is not None:
                try:
                    self.conn.close()
                except Exception:
                    pass
                self.conn = None
        return []

    def show_welcome(self) -> None:
        self.toast.notify(
            title="Google Antigravity",
            message="Программа запущена и активна в трее",
            duration=3200,
            convo_id=self.latest_convo_id,
        )

    def check_status(self) -> None:
        # Check if Antigravity Appearance theme changed
        cfg_mtime = self._get_cfg_mtime()
        if cfg_mtime != self.last_cfg_mtime:
            self.last_cfg_mtime = cfg_mtime
            self.toast.refresh_theme()

        rows = self._query_conversations()
        if not rows:
            return

        self.latest_convo_id = rows[0][0]

        for row in rows:
            convo_id, title, status, step_count, _last_mod = row
            steps = int(step_count or 0)
            prev = self.convo_states.get(convo_id)

            if prev is not None:
                prev_status = prev.get("status")
                prev_steps = prev.get("steps", 0)

                is_finish_transition = status == "CASCADE_RUN_STATUS_IDLE" and (
                    prev_status == "CASCADE_RUN_STATUS_RUNNING"
                    or (
                        prev_status == "CASCADE_RUN_STATUS_IDLE"
                        and steps > prev_steps
                        and prev_steps > 0
                    )
                )

                if is_finish_transition:
                    logging.info(
                        "Turn finished for '%s' (%s). Triggering notification.",
                        title,
                        convo_id,
                    )
                    self.trigger_toast(title, convo_id)

            self.convo_states[convo_id] = {
                "status": status,
                "steps": steps,
                "title": title,
            }

    def trigger_toast(self, title: str | None, convo_id: str | None = None) -> None:
        clean_title = (title or "").strip()
        msg = f"Готово • {clean_title}" if clean_title else "Ответ готов"
        self.toast.notify(
            title="Google Antigravity",
            message=msg,
            duration=3800,
            convo_id=convo_id or self.latest_convo_id,
        )


def main() -> None:
    logging.info("Antigravity Notifier service started.")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    _notifier = NotifierApp()
    try:
        sys.exit(app.exec())
    except BaseException as exc:
        logging.critical("Notifier exiting with %s: %s", type(exc).__name__, exc)


if __name__ == "__main__":
    main()
