import win32process
import win32gui
import win32con
import difflib

def enum_windows(hwnd, extra_list):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            extra_list.append((hwnd, title))

    window_list = []
    win32gui.EnumWindows(enum_windows, window_list)

    print(window_list)

enum_window = enum_windows()

def close_apps():
    hwnd_map = {}

    for hwnd, title in enum_window:
        hwnd_map[hwnd] = title

    print(hwnd_map)

close_apps()


# Failed :(

# Lets try in the app_control.py with some modifications