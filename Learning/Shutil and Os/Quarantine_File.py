import shutil
import os

os.chdir("E:\\Practice folder")

Quarantine_Folder = r"E:\Practice folder\Quarantine"

if not os.path.exists(Quarantine_Folder):
    os.mkdir(Quarantine_Folder)
# os.rmdir("Quarantine")

def remove_empty_folders(root_dir, skip_folder="Quarantine"):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if not dirnames and not filenames:
            if os.path.basename(dirpath).lower() == skip_folder.lower():
                continue
            try:
                shutil.move(dirpath, Quarantine_Folder)
                print(f"Moved: {dirpath} to {Quarantine_Folder}")

            except (PermissionError, OSError):
                print(f"Skipped Folder: {dirpath}")


remove_empty_folders(r"E:\Practice folder")