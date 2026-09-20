import os
from pathlib import Path

# print(os.getcwd())
# print(Path.cwd())

# for f in os.listdir():
#     print(f)

# for p in Path().iterdir():
#     print(p)

# my_file_os = os.path.abspath("main.py")
# my_file_pathlib = Path("main.py")
# my_dir = Path("Learning")

# print(my_file_os)
# print(my_file_pathlib)


# new_file = my_dir / __file__ / "Hello World.txt"

# print(new_file.parent.resolve())
# print(new_file.parent.absolute())

# user_dic = Path("~").expanduser()
# print(user_dic)

# for files in user_dic.rglob("*vscode*", case_sensitive=False):
#     print(files)

p = Path("tempfile.txt")
p.unlink()

# with p.open("w") as p:
#     p.write("Hello World")