import winreg

path = winreg.HKEY_CURRENT_USER

_SOFTWARE_ = winreg.OpenKeyEx(path, r"SOFTWARE\\HELLOWORLD")
# HelloWorld = winreg.CreateKeyEx(_SOFTWARE_, "HELLOWORLD")

# FirstValue = winreg.SetValueEx(HelloWorld, "FirstValue", 0, winreg.REG_SZ, "HELLO WORLD")

HW_value = winreg.QueryValueEx(_SOFTWARE_, "FirstValue")

if _SOFTWARE_:
    winreg.CloseKey(_SOFTWARE_)

print(HW_value[0])