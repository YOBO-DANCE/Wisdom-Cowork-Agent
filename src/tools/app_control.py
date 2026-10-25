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
        # Standard subprocess popen so, if a app can be opened from here we don't need to go so deep
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
        # Most apps can be open using AppOpener
        self.target_app = self.target_app.lower()

        try:
            open(self.target_app, match_closest=True, throw_error=True)
            return True

        except Exception as e:
            print(f"Tier 2 failed {e}")
            return False

    def third_pass(self):
        # This function is for UWP apps
        cmd_app_id = f'powershell -Command "Get-StartApps | Where-Object {{ $_.Name -like \'*{self.target_app}*\' }} | Select-Object -ExpandProperty AppID"'

        
        try:
            app_id = subprocess.run(cmd_app_id, capture_output=True, text=True)

            outputs = [output.strip() for output in app_id.stdout.splitlines() if output.strip()]

            if outputs:
                uwp_matches = [output for output in outputs if output.endswith("!App")]
                chosen_id = uwp_matches[0] if uwp_matches else outputs[0]

                subprocess.Popen(f"explorer.exe shell:AppsFolder\\{chosen_id}")
                return True

            else:
                return False

        except Exception as e:
            print("Tier 3 failed {e}")
            return False

    def open_app(self):
        try:
            tier1_success = self.first_pass()

            if not tier1_success:
                tier2_success = self.second_pass()

            elif not tier2_success:
                tier3_success = self.third_pass()

        except Exception as e:
            print(f"Some error occured {e}")

# Quick Test Block
if __name__ == "__main__":
    app_to_open = OpenApps(input("Write the app name: "))

    app_to_open.open_app()