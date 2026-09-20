# This file is for basic functions of a OS such as closing or opening
import os
import shutil
from pathlib import Path
import platform
import pyautogui
import subprocess


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


print(file_finder_by_name("Solution4.py", "."))