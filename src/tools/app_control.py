# Found some modules so I thought why not use them
import shutil
import os
import subprocess
from sys import platform
from AppOpener import open # Why don't more people make such modules :[
if platform == "win32": # I remember people on unix based operating system having problem with this module so I added a if statement for it
    import win32com.client


class OpenApps:
    def __init__(self, target_app):
        # Don't really know OOPS hehe
        print(f"Trying to open {target_app}")
        self.target_app = target_app

    def first_pass(self):
        try:
            exec_path = shutil.which(self.target_app)

            if exec_path:
                # This is for those .cmd and .bat app especially developer programs
                if platform == "win32" and exec_path.lower().endswith((".bat", ".cmd")):
                    subprocess.Popen(["cmd.exe", "/c", exec_path])
                    return True

                else:
                    subprocess.Popen([exec_path])
                    return True

            return False

        except Exception as e:
            print(f"Tier 1 failed {e}")

    def second_pass(self):
        self.target_app = self.target_app.lower()

        try:
            open(self.target_app, match_closest=True, throw_error=True)

        except Exception as e:
            print(f"Tier 2 failed {e}")

    def open_app(self):
        try:
            tier1_success = self.first_pass()

            if not tier1_success:
                self.second_pass()

        except Exception as e:
            print(f"Some error occured {e}")

# Quick Test Block
if __name__ == "__main__":
    app_to_open = OpenApps(input("Write the app name: "))

    app_to_open.open_app()