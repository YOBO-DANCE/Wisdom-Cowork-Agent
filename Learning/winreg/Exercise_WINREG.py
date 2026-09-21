import winreg

path = winreg.HKEY_CURRENT_USER

APP_PATHS = winreg.OpenKey(path, r"Software\\Microsoft\\Windows\\CurrentVersion\\App Paths", 0, winreg.KEY_READ)

# subkeys, values, _ = winreg.QueryInfoKey(APP_PATHS)

for i in range(5):
    i = i+1
    subkeys = winreg.EnumKey(APP_PATHS, i)
    print(f"{i:<20} --> {subkeys}")

if APP_PATHS:
    winreg.CloseKey(APP_PATHS)