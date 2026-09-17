import os
import shutil

Desktop = r"C:\Users\rhhat\OneDrive\Desktop"
File_name = "practice-.txt"

os.chdir(Desktop)
if not os.path.exists("Practice Folder"):
    os.mkdir("Practice Folder")

Folder = os.path.join(Desktop, "Practice Folder")
os.chdir(Folder)

for i in range(1000):
    base_name, extension = os.path.splitext(File_name)
    file_path = os.path.join(Folder, f"{base_name}{i + 1}{extension}")
    with open(file_path, "w") as file:
        file.write(f"This is file {i + 1}\n")

# if not os.path.exists("Backup"):
#     # os.chdir(Desktop)
#     os.mkdir("Backup")

shutil.copytree(Folder, "Backup")