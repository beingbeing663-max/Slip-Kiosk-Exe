"""Slip Kiosk loader.
Downloads the newest app code from CODE_URL (GitHub Pages of the code repo) every time it starts,
then runs it. If the internet / link is down, the last downloaded copy (folder 'code') is used.
"""
import sys
sys.dont_write_bytecode = True
import base64, json, os, runpy, time, urllib.request, zlib

CODE_URL = 'https://homezonehomezone51-del.github.io/Slip-Kiosk/'    # e.g. https://username.github.io/slipkiosk-code/
FILES = ['slip_bridge.py', 'slip_kiosk_app.py']
TIMEOUT = 8

# Libraries used by the downloaded code - imported here only so PyInstaller packs them into the exe.
try:
    import json, glob, html, re, shutil, socket, threading, queue, subprocess, datetime   # noqa: F401
    import tkinter, tkinter.ttk, tkinter.filedialog, tkinter.messagebox, tkinter.scrolledtext, tkinter.simpledialog   # noqa: F401
    import pandas, openpyxl, zk   # noqa: F401
    import win32print, win32ui, win32con, pywintypes   # noqa: F401
except ImportError:
    pass

BASE = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
CODE = os.path.join(BASE, 'code')


def fail(msg):
    import tkinter
    from tkinter import messagebox
    r = tkinter.Tk(); r.withdraw()
    messagebox.showerror('Slip Kiosk', msg)
    sys.exit(1)


def update():
    """Download data.txt (compressed + base64 code); replace the local copy only if every file is valid Python."""
    if 'PASTE_YOUR' in CODE_URL:
        return 'link not set in loader.py'
    os.makedirs(CODE, exist_ok=True)
    try:
        req = urllib.request.Request(f"{CODE_URL.rstrip('/')}/data.txt?t={int(time.time())}",
                                     headers={'Cache-Control': 'no-cache', 'User-Agent': 'SlipKiosk'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
        new = json.loads(zlib.decompress(base64.b64decode(raw)).decode('utf-8'))
        for f in FILES:
            compile(new[f], f, 'exec')          # reject error pages / broken uploads
    except Exception as ex:
        return f'update failed, using saved copy ({ex})'
    for f in FILES:
        p = os.path.join(CODE, f)
        with open(p + '.tmp', 'w', encoding='utf-8', newline='') as fh:
            fh.write(new[f])
        os.replace(p + '.tmp', p)
    return 'updated'


def main():
    status = update()
    if not all(os.path.exists(os.path.join(CODE, f)) for f in FILES):
        fail(f'Could not get the app code ({status}).\nCheck the internet and the link in loader.py:\n{CODE_URL}')
    sys.path.insert(0, CODE)
    runpy.run_path(os.path.join(CODE, 'slip_kiosk_app.py'), run_name='__main__')


if __name__ == '__main__':
    main()
