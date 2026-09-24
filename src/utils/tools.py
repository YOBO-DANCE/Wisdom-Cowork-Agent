# This file is for basic functions of a OS such as closing or opening
import os
import shutil
from pathlib import Path
import platform
import pyautogui
import subprocess
import difflib
if platform.system() == "Windows":
    import winreg

# # Helper for opening apps (Works only on windows)
# def discover_windows_apps() -> dict[str, str]:
#     discovered_apps = {}
    
#     # Registry targets to scan (both system-wide and current-user installations)
#     registry_targets = [
#         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
#         (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
#     ]

#     for hive, subkey_path in registry_targets:
#         try:
#             parent_key = winreg.OpenKey(hive, subkey_path, 0, winreg.KEY_READ)
#             num_subkeys, _, _ = winreg.QueryInfoKey(parent_key)

#             for i in range(num_subkeys):
#                 try:
#                     app_exe_name = winreg.EnumKey(parent_key, i)
                    
#                     app_key = winreg.OpenKey(parent_key, app_exe_name)
#                     raw_path, _ = winreg.QueryValueEx(app_key, "")
#                     winreg.CloseKey(app_key)

#                     if not raw_path:
#                         continue

#                     # Step 3: Clean path string (strip surrounding quotes and CLI flags like %1 or /fast)
#                     clean_path = raw_path.replace('"', '').strip()
#                     if " " in clean_path and not clean_path.lower().endswith(".exe"):
#                         # Truncate at the .exe extension if arguments are attached
#                         exe_index = clean_path.lower().find(".exe")
#                         if exe_index != -1:
#                             clean_path = clean_path[:exe_index + 4]

#                     # Step 4: Validate that the file actually exists on disk
#                     if os.path.exists(clean_path):
#                         app_alias = app_exe_name.lower().replace(".exe", "")
#                         discovered_apps[app_alias] = clean_path.lower()

#                 except OSError:
#                     # Skip restricted or unreadable registry subkeys cleanly
#                     continue

#             winreg.CloseKey(parent_key)

#         except OSError:
#             # Skip hive if the 'App Paths' key doesn't exist under current user
#             continue

#     return discovered_apps

# Open Application - This will open apps using subprocess module, shutil.which() and os.startfile() methods
# def open_applications(app_name: str):
#     parent_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths", 0, winreg.KEY_READ)
#     app_path = shutil.which(app_name)

#     if app_path == "None":
#         winreg.QueryInfoKey(parent_key)

# File Finder - This will use os.walk for finding files
def file_finder_by_name(filename: str, search_directory: str = "~", exact_match: bool = False, max_results: int = 20, case_sensitive: bool = False):
    try:
        target_dir = Path(search_directory).expanduser().resolve()

        if not target_dir.exists():
            return f"Error: The {target_dir} does not exists".lower()

        matches = []
        search_query = filename.lower().strip()

        print("Scanning...")

        for root, dirs, files in os.walk(target_dir, topdown=True, onerror=lambda err: print(f"Skipped: {err.filename}")):

                for f in files:
                     potential_candidate_name = f.lower()

                     is_match = (potential_candidate_name == search_query) if exact_match else (search_query in potential_candidate_name)

                     if is_match:
                        candidate_full_path = str(Path(root) / f).lower()
                        matches.append(candidate_full_path)

                        if len(matches) >= max_results:
                            return matches

        return matches if matches else f"No file name matching '{filename}'.".lower()


    except Exception as e:
        print(f"An error occured: {e}").lower()