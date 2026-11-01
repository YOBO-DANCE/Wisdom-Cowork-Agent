import os
from time import sleep
from pathlib import Path

base_dir = Path.cwd()
matches = list(base_dir.glob("**/Os module"))

if matches:
    folder_path = matches[0]
    print(folder_path)
    os.chdir(folder_path)

test_folder = "test_workspace"
os.makedirs(test_folder, exist_ok=True)

subfolders = ["logs", "config", "docs", "treasure", "stuff", "test"]

for folder_names in subfolders:
    new_folder_path = os.path.join(test_folder, folder_names)

    os.makedirs(new_folder_path, exist_ok=True)
    print(f"Created {new_folder_path}")
    continue



# sleep(2)
# print("\n")

# for folder_names in subfolders:
#     new_folder_path = os.path.join(test_folder, folder_names)

#     os.removedirs(new_folder_path)
#     print(f"Deleted {new_folder_path}")