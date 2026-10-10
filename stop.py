import os
import psutil

cur_pid = os.getpid()
for p in psutil.process_iter(['pid', 'cmdline']):
    try:
        cmd = " ".join(p.info['cmdline'] or [])
        if "notifier_service.py" in cmd and p.pid != cur_pid:
            p.kill()
            print(f"Остановлен процесс: {p.pid}")
    except Exception:
        pass
