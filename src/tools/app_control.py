# Found some modules so I thought why not use them
import shutil
import os
import subprocess
import AppOpener # Why don't more people make such modules :[
if os.name == "win32": # I remember people on unix based operating system having problem with this module so I added a if statement for it
    import win32com.client


class OpenApps:
    def __init__(self, target_app):
        # Don't really know OOPS hehe
        print(f"Trying to open {target_app}")
        self.target_app = target_app

    def first_pass(self, target_app): 
        exec_path = shutil.which(target_app)

        if exec_path:
            if os.name == "win32":
                subprocess.Popen([exec_path], shell=True)

            else:
                subprocess.Popen(exec_path)

        else:
            pass