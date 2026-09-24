import winreg
from difflib import get_close_matches
import subprocess
import shutil
import os

# Only imports when you are in Windows
if platform.system == "Windows":
    import platform

def open_application(app_name: str):
    # Spoken Voice Aliases mapped to real Executable Names
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

    # Takes input from the user for the name of the app and lowercases it
    app_name = input("Enter the name of your app: ").lower()

    exe_path = shutil.which(app_name)

    try:
        if not exe_path:
            # Match input against dictionary keys (e.g., "google chrome")
            matches = get_close_matches(app_name, APP_ALIASES.keys(), n=1, cutoff=0.6)
            
            if matches:
                best_match_key = matches[0]
                exe_name = APP_ALIASES[best_match_key] # Retrieve the .exe string
                exe_path = shutil.which(exe_name)     # Look up full system path

        # 3. Launch if a valid executable path was found
        if exe_path and os.access(exe_path, os.X_OK):
            try:
                subprocess.Popen(exe_path)
            except:
                pass
    except:
        pass

    winreg_path = winreg.HKEY_CURRENT_USER
    apps_path = winreg.OpenKey(winreg_path, r"Software\\Microsoft\\Windows\\CurrentVersion\\App Paths", 0, winreg.KEY_READ)

    subkeys = winreg.EnumKey(apps_path)

    if get_close_matches(subkeys)