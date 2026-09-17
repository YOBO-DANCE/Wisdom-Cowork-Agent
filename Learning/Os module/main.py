import os

if not os.path.exists("Files"):
    os.mkdir("Files")

os.rmdir("Files")