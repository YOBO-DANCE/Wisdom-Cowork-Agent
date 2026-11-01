import os
from time import sleep
from pathlib import Path
import random
import glob

base_dir = Path.cwd()
matches = list(base_dir.glob("**/Os module"))

if matches:
    folder_path = matches[0]
    print(folder_path)
    os.chdir(folder_path)

test_folder = "test_workspace"
os.makedirs(test_folder, exist_ok=True)

extensions = [".txt", ".ini", ".dat", ".log"]
dummy_files_no_ext = [
    # Documents & Text
    "test_document_v1",
    "sample_notes_2026",
    "meeting_minutes_draft",
    "user_agreement_final_final",
    "readme_backup",
    
    # Data & Sheets
    "sales_data_q3_clean",
    "user_metrics_export_2026-11-01",
    "config_prod_backup",
    "settings_local_dev",
    "inventory_audit_raw"
    ]


subfolders = ["logs", "config", "docs", "treasure", "stuff", "test"]


for folder_name in subfolders:
    file_name = f"{random.choice(dummy_files_no_ext)}{random.choice(extensions)}"
    new_folder_path = os.path.join(test_folder, folder_name)

    os.makedirs(new_folder_path, exist_ok=True)
    print(f"Created folder: {new_folder_path}")

    full_file_path = os.path.join(new_folder_path, file_name)
    with open(full_file_path, "w") as f:
        f.write("Hello World")

try:
    searches = glob.glob(os.path.abspath(os.path.join(test_folder, "**", "*.txt")), recursive=True)
    print(searches)

except OSError as e:
    print(f"Access not available: {e}")

# sleep(2)
# print("\n")

# for folder_names in subfolders:
#     new_folder_path = os.path.join(test_folder, folder_names)

#     os.removedirs(new_folder_path)
#     print(f"Deleted {new_folder_path}")