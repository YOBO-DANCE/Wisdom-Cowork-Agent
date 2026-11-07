import win32process
import win32gui
import win32con

def enum_windows(hwnd, extra_list):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            extra_list.append((hwnd, title))

    window_list = []
    win32gui.EnumWindows(enum_windows, window_list)

    print(window_list)

print(enum_windows(input("Enter App name: ")))