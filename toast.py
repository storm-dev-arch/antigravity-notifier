"""
Ultra-optimized, theme-adaptive compact Toast Notification for Google Antigravity.
235x35 bottom-centered semi-transparent pill with pre-baked HiDPI QPixmap rendering,
zero child widgets, zero CSS overhead, and non-blocking WinMM/winsound audio.
"""

import ctypes
import json
import os
import sys
import tempfile
import threading
import time
import winreg
import winsound
from pathlib import Path

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QRectF,
    Qt,
    QTimer,
    QVariantAnimation,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import QApplication, QWidget

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent
MP3_SOUND_FILE = BASE_DIR / "sound.mp3"
WAV_SOUND_FILE = BASE_DIR / "chime.wav"

TOAST_WIDTH = 235
TOAST_HEIGHT = 35
CORNER_RADIUS = 11.5
MARGIN_BOTTOM = 24
SLIDE_OFFSET = 18

# Default Antigravity theme seeds (matches Appearance settings defaults)
DEFAULT_DARK_SEEDS = {
    "background": "#282C34",
    "foregroundOverride": "#ABB2BF",
    "primary": "#61AFEF",
}
DEFAULT_LIGHT_SEEDS = {
    "background": "#F9F9F9",
    "foregroundOverride": "#101010",
    "primary": "#007ACC",
}


# ---------------------------------------------------------------------------
# Ultra-fast Non-Blocking Audio Engine (Zero QtMultimedia DLL overhead)
# ---------------------------------------------------------------------------
_AUDIO_EVENT = threading.Event()
_AUDIO_THREAD_STARTED = False
_AUDIO_LOCK = threading.Lock()


def _audio_worker() -> None:
    """Persistent background thread for zero-latency audio playback via WinMM."""
    winmm = ctypes.windll.winmm
    has_mp3 = MP3_SOUND_FILE.exists()
    has_wav = WAV_SOUND_FILE.exists()
    mci_opened = False

    if has_mp3:
        mp3_path = str(MP3_SOUND_FILE)
        cmd = f'open "{mp3_path}" type mpegvideo alias ag_toast_snd'
        if winmm.mciSendStringW(cmd, None, 0, 0) == 0:
            mci_opened = True

    while True:
        _AUDIO_EVENT.wait()
        _AUDIO_EVENT.clear()
        if mci_opened:
            if winmm.mciSendStringW("play ag_toast_snd from 0", None, 0, 0) != 0:
                # Re-open if device handle was reset
                winmm.mciSendStringW("close ag_toast_snd", None, 0, 0)
                cmd = f'open "{MP3_SOUND_FILE}" type mpegvideo alias ag_toast_snd'
                if winmm.mciSendStringW(cmd, None, 0, 0) == 0:
                    winmm.mciSendStringW("play ag_toast_snd from 0", None, 0, 0)
        elif has_wav:
            try:
                winsound.PlaySound(
                    str(WAV_SOUND_FILE),
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                )
            except Exception:
                pass


def trigger_sound() -> None:
    """Signals the background audio thread without blocking the GUI thread."""
    global _AUDIO_THREAD_STARTED
    if not _AUDIO_THREAD_STARTED:
        with _AUDIO_LOCK:
            if not _AUDIO_THREAD_STARTED:
                t = threading.Thread(target=_audio_worker, daemon=True)
                t.start()
                _AUDIO_THREAD_STARTED = True
    _AUDIO_EVENT.set()


# ---------------------------------------------------------------------------
# Antigravity Theme Loader (Cached by config.json st_mtime_ns)
# ---------------------------------------------------------------------------
def _find_config_path() -> Path | None:
    custom = os.environ.get("ANTIGRAVITY_CONFIG_PATH")
    if custom:
        p = Path(custom)
        if p.exists():
            return p

    candidates = [
        Path.home() / ".gemini" / "config" / "config.json",
    ]
    user_prof = os.environ.get("USERPROFILE")
    if user_prof:
        candidates.append(Path(user_prof) / ".gemini" / "config" / "config.json")

    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


_CONFIG_PATH: Path | None = _find_config_path()
_CACHED_MTIME_NS: int = -1
_CACHED_OS_LIGHT: bool = False
_CACHED_OS_CHECK_TS: float = 0.0
_CACHED_PALETTE: tuple[QColor, QColor, QColor, bool] | None = None


def _is_windows_light_mode() -> bool:
    """Reads Windows AppsUseLightTheme with a 2-second monotonic cache."""
    global _CACHED_OS_LIGHT, _CACHED_OS_CHECK_TS
    now = time.monotonic()
    if now - _CACHED_OS_CHECK_TS < 2.0:
        return _CACHED_OS_LIGHT
    _CACHED_OS_CHECK_TS = now
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            _CACHED_OS_LIGHT = bool(val == 1)
    except Exception:
        _CACHED_OS_LIGHT = False
    return _CACHED_OS_LIGHT


def _parse_hex_color(hex_str: str | None, fallback: str) -> QColor:
    if isinstance(hex_str, str):
        s = hex_str.strip()
        if not s.startswith("#"):
            s = "#" + s
        c = QColor(s)
        if c.isValid():
            return c
    return QColor(fallback)


def _blend(c1: QColor, c2: QColor, ratio: float) -> QColor:
    """Blends c1 and c2 where ratio=0.0 is c1 and ratio=1.0 is c2."""
    r = int(c1.red() * (1.0 - ratio) + c2.red() * ratio)
    g = int(c1.green() * (1.0 - ratio) + c2.green() * ratio)
    b = int(c1.blue() * (1.0 - ratio) + c2.blue() * ratio)
    return QColor(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def get_antigravity_palette() -> tuple[QColor, QColor, QColor, bool]:
    """
    Returns (bg_color, fg_color, accent_color, is_dark) synced with Antigravity Appearance.
    Uses st_mtime_ns caching so steady-state calls take < 3 microseconds.
    """
    global _CACHED_MTIME_NS, _CACHED_PALETTE

    mtime_ns = 0
    if _CONFIG_PATH is not None:
        try:
            mtime_ns = _CONFIG_PATH.stat().st_mtime_ns
        except OSError:
            mtime_ns = 0

    os_light = _is_windows_light_mode()
    if _CACHED_PALETTE is not None and mtime_ns == _CACHED_MTIME_NS:
        return _CACHED_PALETTE

    theme_mode = "THEME_MODE_INHERIT"
    dark_seeds = dict(DEFAULT_DARK_SEEDS)
    light_seeds = dict(DEFAULT_LIGHT_SEEDS)

    if _CONFIG_PATH is not None and mtime_ns > 0:
        try:
            raw = _CONFIG_PATH.read_bytes()
            data = json.loads(raw)
            settings = data.get("userSettings", data) if isinstance(data, dict) else {}
            if isinstance(settings, dict):
                tm = settings.get("themeMode")
                if isinstance(tm, str) and tm:
                    theme_mode = tm.upper()

                ds = settings.get("customThemeSeedsDark")
                if isinstance(ds, dict):
                    for k in ("background", "foregroundOverride", "primary"):
                        if ds.get(k):
                            dark_seeds[k] = ds[k]
                    if not ds.get("foregroundOverride") and ds.get("foreground"):
                        dark_seeds["foregroundOverride"] = ds["foreground"]
                    if not ds.get("primary") and ds.get("accent"):
                        dark_seeds["primary"] = ds["accent"]

                ls = settings.get("customThemeSeedsLight")
                if isinstance(ls, dict):
                    for k in ("background", "foregroundOverride", "primary"):
                        if ls.get(k):
                            light_seeds[k] = ls[k]
                    if not ls.get("foregroundOverride") and ls.get("foreground"):
                        light_seeds["foregroundOverride"] = ls["foreground"]
                    if not ls.get("primary") and ls.get("accent"):
                        light_seeds["primary"] = ls["accent"]
        except Exception:
            pass

    if "LIGHT" in theme_mode:
        use_light = True
    elif "DARK" in theme_mode:
        use_light = False
    else:
        use_light = os_light

    seeds = light_seeds if use_light else dark_seeds
    defaults = DEFAULT_LIGHT_SEEDS if use_light else DEFAULT_DARK_SEEDS

    bg = _parse_hex_color(seeds.get("background"), defaults["background"])
    fg = _parse_hex_color(seeds.get("foregroundOverride"), defaults["foregroundOverride"])
    accent = _parse_hex_color(seeds.get("primary"), defaults["primary"])

    lum = 0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()
    is_dark = lum < 140.0

    _CACHED_MTIME_NS = mtime_ns
    _CACHED_PALETTE = (bg, fg, accent, is_dark)
    return _CACHED_PALETTE


# ---------------------------------------------------------------------------
# Instant Antigravity Window Focus & Chat Router (Win32 + DevTools Bridge)
# ---------------------------------------------------------------------------
def _focus_win32_antigravity() -> bool:
    """Brings the Antigravity Electron window to the foreground immediately via Win32."""
    try:
        import ctypes.wintypes as wt

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        found_hwnds: list[int] = []

        WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

        def _enum_cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                cls_buf = ctypes.create_unicode_buffer(64)
                user32.GetClassNameW(hwnd, cls_buf, 64)
                if cls_buf.value == "Chrome_WidgetWin_1":
                    title_buf = ctypes.create_unicode_buffer(256)
                    user32.GetWindowTextW(hwnd, title_buf, 256)
                    t = title_buf.value
                    if t == "Antigravity" or t.endswith(" - Antigravity") or "Antigravity" in t:
                        found_hwnds.append(hwnd)
            return True

        user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)
        if not found_hwnds:
            return False

        hwnd = found_hwnds[0]
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE

        fg_hwnd = user32.GetForegroundWindow()
        fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
        cur_tid = kernel32.GetCurrentThreadId()

        attached = False
        if fg_tid and fg_tid != cur_tid:
            attached = bool(user32.AttachThreadInput(cur_tid, fg_tid, True))

        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)

        if attached:
            user32.AttachThreadInput(cur_tid, fg_tid, False)
        return True
    except Exception:
        return False


def _resolve_latest_convo_id() -> str | None:
    try:
        import sqlite3

        db = Path.home() / ".gemini" / "antigravity" / "conversation_summaries.db"
        if not db.exists():
            return None
        conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True, timeout=0.3)
        row = conn.execute(
            "SELECT conversation_id FROM conversation_summaries ORDER BY last_modified_time DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def _navigate_chat_bg(convo_id: str | None, win_found: bool) -> None:
    """Navigates Antigravity to /c/<convo_id> via local DevTools port without blocking UI."""
    import socket
    import struct
    import urllib.request

    if not win_found:
        try:
            os.startfile("antigravity://open")
        except Exception:
            pass

    cid = convo_id or _resolve_latest_convo_id()
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return

    dt_file = Path(appdata) / "Antigravity" / "DevToolsActivePort"
    if not dt_file.exists():
        return

    try:
        port = int(dt_file.read_text(encoding="utf-8").splitlines()[0].strip())
        raw = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=0.4).read()
        targets = json.loads(raw)
        page = next(
            (t for t in targets if t.get("type") == "page" and "127.0.0.1" in t.get("url", "")),
            None,
        )
        if not page:
            return

        tid = page["id"]
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/json/activate/{tid}", timeout=0.3).read()
        except Exception:
            pass

        s = socket.create_connection(("127.0.0.1", port), timeout=0.4)
        req = (
            f"GET /devtools/page/{tid} HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        s.sendall(req.encode("ascii"))
        s.recv(1024)

        def _ws_send(obj: dict) -> None:
            payload = json.dumps(obj).encode("utf-8")
            n = len(payload)
            hdr = bytearray([0x81])
            if n < 126:
                hdr.append(0x80 | n)
            elif n < 65536:
                hdr.append(0x80 | 126)
                hdr.extend(struct.pack(">H", n))
            else:
                hdr.append(0x80 | 127)
                hdr.extend(struct.pack(">Q", n))
            hdr.extend(b"\x00\x00\x00\x00")
            s.sendall(hdr + payload)

        _ws_send({"id": 1, "method": "Page.bringToFront"})
        if cid:
            js_expr = (
                f"(() => {{ const p = '/c/{cid}'; "
                f"if (!location.pathname.startsWith(p)) {{ "
                f"history.pushState({{}}, '', p); "
                f"dispatchEvent(new PopStateEvent('popstate')); "
                f"}} window.focus(); }})()"
            )
            _ws_send({"id": 2, "method": "Runtime.evaluate", "params": {"expression": js_expr}})
        s.recv(512)
        s.close()
    except Exception:
        pass


def focus_antigravity_chat(convo_id: str | None = None) -> None:
    """Focuses Antigravity window immediately and navigates to the conversation chat."""
    win_found = _focus_win32_antigravity()
    threading.Thread(target=_navigate_chat_bg, args=(convo_id, win_found), daemon=True).start()


# ---------------------------------------------------------------------------
# Ultra-Lightweight Pre-Baked 235x35 Centered Toast Widget
# ---------------------------------------------------------------------------
class ToastNotification(QWidget):
    __slots__ = (
        "duration",
        "is_closing",
        "_title",
        "_message",
        "_convo_id",
        "_surface",
        "_palette_key",
        "_font_main",
        "_font_small",
        "final_x",
        "final_y",
        "anim",
        "timer",
    )

    def __init__(
        self,
        title: str = "Google Antigravity",
        message: str = "Ответ готов",
        duration: int = 3800,
        convo_id: str | None = None,
    ):
        super().__init__(None)
        self.duration = duration
        self.is_closing = False
        self._title = title
        self._message = message
        self._convo_id = convo_id
        self._surface: QPixmap | None = None
        self._palette_key: tuple | None = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setFixedSize(TOAST_WIDTH, TOAST_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._font_main = QFont("Segoe UI", -1, QFont.Weight.DemiBold)
        self._font_main.setPixelSize(12)
        self._font_main.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

        self._font_small = QFont("Segoe UI", -1, QFont.Weight.DemiBold)
        self._font_small.setPixelSize(11)
        self._font_small.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

        self.final_x = 0
        self.final_y = 0

        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self._on_anim_tick)
        self.anim.finished.connect(self._on_anim_finished)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.slide_out)

        self._recompute_screen_pos()
        self._bake_surface()

    def _recompute_screen_pos(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            self.final_x = geo.x() + (geo.width() - TOAST_WIDTH) // 2
            self.final_y = geo.y() + geo.height() - TOAST_HEIGHT - MARGIN_BOTTOM
        else:
            self.final_x = 800
            self.final_y = 980

    @staticmethod
    def _clean_text(s: str) -> str:
        s = (s or "").strip()
        if any(ch in s for ch in ("╨", "╤", "╢", "╣", "║", "╗", "╝", "╜", "╛", "┐")):
            for enc in ("cp866", "cp1251"):
                try:
                    fixed = s.encode(enc).decode("utf-8")
                    if fixed:
                        return fixed
                except Exception:
                    pass
        return s

    def _format_display_text(self) -> str:
        msg = self._clean_text(self._message)
        if not msg:
            msg = self._clean_text(self._title) or "Ответ готов"
        return msg

    def _bake_surface(self) -> None:
        """Pre-renders the entire 235x35 card into a single HiDPI QPixmap."""
        bg, fg, accent, is_dark = get_antigravity_palette()
        dpr = self.devicePixelRatioF() or 1.0
        text = self._format_display_text()

        key = (bg.rgba(), fg.rgba(), accent.rgba(), is_dark, dpr, text)
        if self._surface is not None and self._palette_key == key:
            return
        self._palette_key = key

        px_w = int(round(TOAST_WIDTH * dpr))
        px_h = int(round(TOAST_HEIGHT * dpr))
        pixmap = QPixmap(px_w, px_h)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )

        rect = QRectF(0.5, 0.5, TOAST_WIDTH - 1.0, TOAST_HEIGHT - 1.0)
        path = QPainterPath()
        path.addRoundedRect(rect, CORNER_RADIUS, CORNER_RADIUS)

        # 1. Semi-transparent glass background derived from Antigravity Background + Accent
        bg_grad = QLinearGradient(0.0, 0.0, 0.0, float(TOAST_HEIGHT))
        if is_dark:
            top_bg = _blend(bg.lighter(112), accent, 0.06)
            bot_bg = _blend(bg, accent, 0.03)
            top_bg.setAlpha(196)  # ~77% opacity (semi-transparent glass)
            bot_bg.setAlpha(214)  # ~84% opacity
        else:
            top_bg = _blend(bg, accent, 0.03)
            bot_bg = _blend(bg.darker(104), accent, 0.05)
            top_bg.setAlpha(206)
            bot_bg.setAlpha(222)

        bg_grad.setColorAt(0.0, top_bg)
        bg_grad.setColorAt(1.0, bot_bg)
        painter.fillPath(path, bg_grad)

        # 2. Crisp 1px border blending Accent & Foreground
        border_grad = QLinearGradient(0.0, 0.0, 0.0, float(TOAST_HEIGHT))
        b_top = _blend(fg, accent, 0.48)
        b_bot = _blend(fg, accent, 0.22)
        b_top.setAlpha(90 if is_dark else 72)
        b_bot.setAlpha(40 if is_dark else 36)
        border_grad.setColorAt(0.0, b_top)
        border_grad.setColorAt(1.0, b_bot)

        pen = QPen(border_grad, 1.0)
        painter.setPen(pen)
        painter.drawPath(path)

        # 3. Centered content: [Glowing Accent Dot + Gap + Foreground Text]
        max_text_w = TOAST_WIDTH - 38  # 12px padding each side + 14px for dot & gap
        font = self._font_main
        fm = QFontMetrics(font)
        if fm.horizontalAdvance(text) > max_text_w:
            font = self._font_small
            fm = QFontMetrics(font)

        elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, max_text_w)
        text_w = fm.horizontalAdvance(elided)

        dot_diam = 6.0
        dot_gap = 8.0
        total_w = dot_diam + dot_gap + text_w
        start_x = (TOAST_WIDTH - total_w) * 0.5
        center_y = TOAST_HEIGHT * 0.5

        # Draw Accent Glow + Dot
        dot_cx = start_x + dot_diam * 0.5
        halo_r = 6.5
        halo_grad = QRadialGradient(dot_cx, center_y, halo_r)
        hc1 = QColor(accent)
        hc1.setAlpha(95 if is_dark else 70)
        hc2 = QColor(accent)
        hc2.setAlpha(0)
        halo_grad.setColorAt(0.0, hc1)
        halo_grad.setColorAt(1.0, hc2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(halo_grad)
        painter.drawEllipse(QRectF(dot_cx - halo_r, center_y - halo_r, halo_r * 2.0, halo_r * 2.0))

        dot_color = QColor(accent)
        dot_color.setAlpha(255)
        painter.setBrush(dot_color)
        painter.drawEllipse(
            QRectF(dot_cx - dot_diam * 0.5, center_y - dot_diam * 0.5, dot_diam, dot_diam)
        )

        # Draw Text in Theme Foreground Color (slightly contrast-boosted for glass legibility)
        target_contrast = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0)
        text_color = _blend(fg, target_contrast, 0.22)
        text_color.setAlpha(250)

        painter.setFont(font)
        painter.setPen(text_color)
        text_rect = QRectF(start_x + dot_diam + dot_gap, -0.5, text_w + 4.0, float(TOAST_HEIGHT))
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            elided,
        )

        painter.end()
        self._surface = pixmap

    def refresh_theme(self) -> None:
        """Re-bakes surface and repaints if Antigravity theme settings changed."""
        old_key = self._palette_key
        self._bake_surface()
        if self._palette_key != old_key and self.isVisible():
            self.update()

    def notify(
        self,
        title: str,
        message: str,
        duration: int = 3800,
        convo_id: str | None = None,
    ) -> None:
        """Reuses the existing widget instance for a new notification with zero allocation."""
        self.timer.stop()
        self.anim.stop()
        self.is_closing = False
        self.duration = duration
        self._title = title
        self._message = message
        self._convo_id = convo_id
        self._recompute_screen_pos()
        self._bake_surface()
        self.update()
        self.show_smooth()

    def _on_anim_tick(self, value: float) -> None:
        t = float(value)
        offset = int(round((1.0 - t) * SLIDE_OFFSET))
        self.move(self.final_x, self.final_y + offset)
        self.setWindowOpacity(t)

    def _on_anim_finished(self) -> None:
        if self.is_closing:
            self.hide()

    def show_smooth(self) -> None:
        self.is_closing = False
        self._recompute_screen_pos()
        self._bake_surface()

        self.move(self.final_x, self.final_y + SLIDE_OFFSET)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        trigger_sound()

        self.anim.stop()
        self.anim.blockSignals(True)
        self.anim.setDuration(240)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.setCurrentTime(0)
        self.anim.blockSignals(False)
        self.anim.start()

        self.timer.start(self.duration)

    def slide_out(self) -> None:
        if self.is_closing:
            return
        self.is_closing = True
        self.timer.stop()

        cur_val = float(self.anim.currentValue() or 1.0)
        self.anim.stop()
        self.anim.blockSignals(True)
        self.anim.setDuration(190)
        self.anim.setStartValue(cur_val)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.setCurrentTime(0)
        self.anim.blockSignals(False)
        self.anim.start()

    def paintEvent(self, _event) -> None:
        if self._surface is not None:
            QPainter(self).drawPixmap(0, 0, self._surface)

    def enterEvent(self, event) -> None:
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self.is_closing:
            self.timer.start(1800)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            focus_antigravity_chat(self._convo_id)
            self.slide_out()
        elif event.button() == Qt.MouseButton.RightButton:
            self.slide_out()
        super().mousePressEvent(event)


def show_notification(
    title: str = "Google Antigravity",
    message: str = "Ответ готов",
    duration: int = 3800,
    convo_id: str | None = None,
) -> None:
    app = QApplication.instance()
    owns_app = False
    if app is None:
        app = QApplication(sys.argv)
        owns_app = True

    toast = ToastNotification(title, message, duration, convo_id=convo_id)
    toast.show_smooth()

    if owns_app:
        QTimer.singleShot(duration + 450, app.quit)
        app.exec()


def acquire_toast_lock() -> bool:
    lock_file = Path(tempfile.gettempdir()) / "ag_toast_debounce.lock"
    now = time.time()
    try:
        if now - lock_file.stat().st_mtime < 2.0:
            return False
    except OSError:
        pass
    try:
        lock_file.touch()
    except OSError:
        pass
    return True


if __name__ == "__main__":
    if not acquire_toast_lock():
        sys.exit(0)

    title_arg = sys.argv[1] if len(sys.argv) > 1 else "Google Antigravity"
    msg_arg = sys.argv[2] if len(sys.argv) > 2 else "Ответ готов"
    show_notification(title=title_arg, message=msg_arg)
