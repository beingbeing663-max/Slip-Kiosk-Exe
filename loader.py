"""Slip Kiosk loader.
Runs the app code straight from CODE_URL (GitHub Pages). Nothing is saved on this PC.
If the link is removed, empty or marked disabled, the app will not start, and a running app shuts itself down.
"""
import sys
sys.dont_write_bytecode = True
import base64, json, os, shutil, threading, time, types, urllib.error, urllib.request, zlib

CODE_URL = 'https://homezonehomezone51-del.github.io/Slip-Kiosk/'
FILES = ['slip_bridge.py', 'slip_kiosk_app.py']
TIMEOUT = 10
CHECK_MIN = 5          # a running app re-checks the link every 5 minutes

# Libraries used by the downloaded code - imported here only so PyInstaller packs them into the exe.
try:
    import glob, html, re, socket, queue, subprocess, datetime   # noqa: F401
    import tkinter, tkinter.ttk, tkinter.filedialog, tkinter.messagebox, tkinter.scrolledtext, tkinter.simpledialog   # noqa: F401
    import pandas, openpyxl, zk   # noqa: F401
    import win32print, win32ui, win32con, pywintypes   # noqa: F401
except ImportError:
    pass

BASE = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))


def fetch():
    """-> ('ok', {file: source}) | ('gone', reason) link removed / disabled / broken | ('offline', reason) no internet."""
    try:
        req = urllib.request.Request(f"{CODE_URL.rstrip('/')}/data.txt?t={int(time.time())}",
                                     headers={'Cache-Control': 'no-cache', 'User-Agent': 'SlipKiosk'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
    except urllib.error.HTTPError as ex:
        return ('gone', f'HTTP {ex.code}') if ex.code in (404, 410) else ('offline', f'HTTP {ex.code}')
    except Exception as ex:
        return 'offline', str(ex)
    try:
        d = json.loads(zlib.decompress(base64.b64decode(raw)).decode('utf-8'))
        if '__disabled__' in d:
            return 'gone', 'disabled (' + str(d['__disabled__']) + ')'
        for f in FILES:
            compile(d[f], f, 'exec')            # KeyError = file missing
    except Exception as ex:
        return 'gone', f'invalid or incomplete code ({ex!r})'
    return 'ok', d


def fail(msg):
    import tkinter
    from tkinter import messagebox
    r = tkinter.Tk(); r.withdraw()
    messagebox.showerror('Slip Kiosk', msg)
    sys.exit(1)


def stop_app(reason):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f'Slip Kiosk has been disabled.\n{reason}', 'Slip Kiosk', 0x10)
    except Exception:
        pass
    os._exit(1)


def watchdog():
    while True:
        time.sleep(CHECK_MIN * 60)
        st, info = fetch()
        if st == 'gone':
            time.sleep(60)                      # confirm once, in case a deploy was just running
            st, info = fetch()
            if st == 'gone':
                stop_app(info)


def run(code):
    """Run both files from memory (nothing written to disk)."""
    bridge = types.ModuleType('slip_bridge')
    bridge.__file__ = os.path.join(BASE, 'slip_bridge.py')
    sys.modules['slip_bridge'] = bridge
    exec(compile(code['slip_bridge.py'], 'slip_bridge.py', 'exec'), bridge.__dict__)
    g = {'__name__': '__main__', '__file__': os.path.join(BASE, 'slip_kiosk_app.py')}
    exec(compile(code['slip_kiosk_app.py'], 'slip_kiosk_app.py', 'exec'), g)


def main():
    shutil.rmtree(os.path.join(BASE, 'code'), ignore_errors=True)    # remove any copy saved by older versions
    st, info = fetch()
    if st == 'gone':
        fail(f'Slip Kiosk is disabled.\n{info}')
    if st != 'ok':
        fail(f'Internet connection is required to start Slip Kiosk.\n{info}')
    threading.Thread(target=watchdog, daemon=True).start()
    run(info)


if __name__ == '__main__':
    main()
