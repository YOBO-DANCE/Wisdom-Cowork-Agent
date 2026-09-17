import time
import os

Folder_name = "Clean Desktop"
File_name = "Hello-World.txt"

os.chdir("C:/Users/rhhat/OneDrive/Desktop")

if not os.path.exists(Folder_name):
    os.mkdir(Folder_name)

file_path = os.path.join(Folder_name, File_name)

with open(file_path, "w") as file:
    file.write("Hello World!")

print(f"The file was created at {file_path}")

time.sleep(5)

if os.path.exists(file_path):
    os.chdir("C:/Users/rhhat/OneDrive/Desktop/Clean Desktop")
    os.remove(File_name)

time.sleep(3)

os.chdir("C:/Users/rhhat/OneDrive/Desktop")
os.rmdir(Folder_name)