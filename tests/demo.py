import os

user_start_menu = os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs")
common_start_menu = os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs")

both_start_menu = (user_start_menu, common_start_menu)

print(both_start_menu)