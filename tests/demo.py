import os

target_app = str(input("Write the app name: "))
target_app = target_app.lower()

start_menu_paths = [os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"), os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs")]

for start_menu_path in start_menu_paths:
    for root, dirs, files in os.walk(start_menu_path):
        for file in files:
            if file.endswith(".lnk") and target_app in file.lower():
                full_path = os.path.join(root, file)

                print(full_path)