import win32gui
import win32con


def callback(hwnd, extra_list):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            print(f"HWND: {hwnd} | Title: {title}")

    return True

if __name__ == "__main__":
    results = win32gui.EnumWindows(callback, None)
    print(results)