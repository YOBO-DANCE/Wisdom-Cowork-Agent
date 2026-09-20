import os
import platform
from pathlib import Path

# winreg is only available on Windows operating systems
if platform.system() == "Windows":
    import winreg


def discover_windows_apps() -> dict[str, str]:
    """
    Scans the Windows Registry ('App Paths') across HKLM and HKCU to build a clean
    dictionary mapping lowercased application names to their absolute .exe paths.
    
    Returns:
        dict[str, str]: e.g., {"chrome": "c:\\program files\\google\\chrome\\application\\chrome.exe"}
    """
    if platform.system() != "Windows":
        return {}

    discovered_apps = {}
    
    # Registry targets to scan (both system-wide and current-user installations)
    registry_targets = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
    ]

    for hive, subkey_path in registry_targets:
        try:
            parent_key = winreg.OpenKey(hive, subkey_path, 0, winreg.KEY_READ)
            num_subkeys, _, _ = winreg.QueryInfoKey(parent_key)

            for i in range(num_subkeys):
                try:
                    # Step 1: Read the subkey name (e.g., "chrome.exe", "vlc.exe")
                    app_exe_name = winreg.EnumKey(parent_key, i)
                    
                    # Step 2: Open individual app subkey and read its default value (absolute path)
                    app_key = winreg.OpenKey(parent_key, app_exe_name)
                    raw_path, _ = winreg.QueryValueEx(app_key, "")
                    winreg.CloseKey(app_key)

                    if not raw_path:
                        continue

                    # Step 3: Clean path string (strip surrounding quotes and CLI flags like %1 or /fast)
                    clean_path = raw_path.replace('"', '').strip()
                    if " " in clean_path and not clean_path.lower().endswith(".exe"):
                        # Truncate at the .exe extension if arguments are attached
                        exe_index = clean_path.lower().find(".exe")
                        if exe_index != -1:
                            clean_path = clean_path[:exe_index + 4]

                    # Step 4: Validate that the file actually exists on disk
                    if os.path.exists(clean_path):
                        app_alias = app_exe_name.lower().replace(".exe", "")
                        discovered_apps[app_alias] = clean_path.lower()

                except OSError:
                    # Skip restricted or unreadable registry subkeys cleanly
                    continue

            winreg.CloseKey(parent_key)

        except OSError:
            # Skip hive if the 'App Paths' key doesn't exist under current user
            continue

    return discovered_apps


# Test run
if __name__ == "__main__":
    apps = discover_windows_apps()
    print(f"discovered {len(apps)} installed applications via windows registry:\n")
    for app_name, exe_path in list(apps.items()):  # Show first 10
        print(f"  {app_name:<20} -> {exe_path}")