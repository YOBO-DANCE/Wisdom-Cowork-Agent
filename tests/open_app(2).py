import subprocess
import os
import shutil
from difflib import get_close_matches
import sqlite3
import platform

if platform.system == "Windows":
    import winreg

def open_application(app_name: str):
    app_name = app_name.replace(" ", "").lower() # Remove every whitespace and make the app_name in lowercase
    app_name = app_name.strip(".") # Splits the extension and the file name

    # A list for generic APPS and their app name
    APP_ALIASES = {
            # Web Browsers
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "browser": "chrome.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "firefox": "firefox.exe",
            "brave": "brave.exe",
            
            # Coding & Development
            "vscode": "code.exe",
            "vs code": "code.exe",
            "visual studio code": "code.exe",
            "pycharm": "pycharm64.exe",
            "git bash": "git-bash.exe",
            
            # Built-in Windows Tools
            "notepad": "notepad.exe",
            "text editor": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "terminal": "wt.exe",
            "windows terminal": "wt.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "paint": "mspaint.exe",
            
            # File Explorers
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "my computer": "explorer.exe",
            "files": "explorer.exe",
            
            # Productivity & Office
            "word": "winword.exe",
            "microsoft word": "winword.exe",
            "excel": "excel.exe",
            "microsoft excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "ppt": "powerpnt.exe",
            "onenote": "onenote.exe",
            
            # Media & Communication
            "vlc": "vlc.exe",
            "vlc player": "vlc.exe",
            "media player": "vlc.exe",
            "spotify": "spotify.exe",
            "music": "spotify.exe",
            "discord": "discord.exe",
            "slack": "slack.exe",
            "zoom": "zoom.exe"
        }

    try:
        # Finds match to app_name and lists
        if app_name:
            matches = get_close_matches(app_name, list(APP_ALIASES.keys()))

            if matches:
                best_match = matches[0]
                exe_name = APP_ALIASES[best_match]

                exe_path = shutil.which(exe_name)

                if exe_path and os.access(exe_path, os.X_OK):
                    subprocess.Popen(exe_path)

                else:
                    print("Step 1 failed...moving onto Step 2")

    except Exception as e:
        print(e)
        pass

    try:
        conn = sqlite3.connect("apps.db")
        cursor = conn.cursor()

        cursor.execute("SELECT exe_path FROM apps WHERE app_alias = ?", (app_name,)),
        row = cursor.fetchone()

        conn.close()

        if row:
            return row[0]
        return None

    except:
        print("Step 2 failed...moving onto Step 3")
        pass

    