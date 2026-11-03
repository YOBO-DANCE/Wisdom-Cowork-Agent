import shutil
import os
import subprocess
import platform
import shlex
import re
import difflib
from pathlib import Path
from configparser import ConfigParser

# Had to keep them here else my posix fellows will have trouble
if platform.system() == "Windows": # I remember people on unix based operating system having problem with this module so I added a if statement for it
    import win32com.client
    from AppOpener import open # Why don't more people make such modules :[


class OpenApps:
    def __init__(self, target_app):
        # Don't really know OOPS hehe
        print(f"Trying to open {target_app}")
        self.target_app = target_app
        self.current_os = platform.system()

    # Windows block starting
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

            print("Tier 1: could not open with basic module's built-in func(s)")
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
            print(f"Tier 2 failed: {e}")
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

                print(f"Opening(tier 3) {self.target_app}")
                subprocess.Popen(f"explorer.exe shell:AppsFolder\\{chosen_id}")
                return True

            else:
                print(f"Tier 3: No UWP matches found for {self.target_app}")
                return False

        except Exception as e:
            print(f"Tier 3 failed {e}")
            return False

    def final_pass(self):
        # The last pass if something is not found here then, the app doesn't exists 
        self.target_app = self.target_app.lower()

        try:
            start_menu_paths = [os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"), os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs")]

            for start_menu_path in start_menu_paths:
                for root, dirs, files in os.walk(start_menu_path):
                    for file in files:
                        if file.endswith(".lnk") and self.target_app in file.lower():
                            full_path = os.path.join(root, file)

                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortcut(full_path)
                            real_target = shortcut.TargetPath

                            subprocess.Popen([real_target])
                            return True

            print(f"Tier 4: No matching shortcuts found for {self.target_app}")
            return False

        except Exception as e:
            print(f"Tier 4 failed: {e}")
            return False

    def windows_open_app(self):
        try:
            try:
                tier_1_success = self.first_pass()

                if tier_1_success:
                    return

                tier_2_success = self.second_pass()

                if tier_2_success:
                    return

                tier_3_success = self.third_pass()

                if tier_3_success:
                    return

                tier_4_success = self.final_pass()

                if tier_4_success:
                    return

            finally:
                pass

        except Exception as e:
            print(f"No app named {self.target_app} is found! \n Error: {e}")
    # Windows Block Ends

    # Linux Block Starts
    def linux_tier_1(self): # the lighting fast shutil.which comes in PLAYYYYY!!!!!!
        exec_path = shutil.which(self.target_app)
        path = os.environ.get("PATH", "")

        if exec_path:
            try:
                subprocess.Popen([exec_path], shell=False)
                return f"Opened {self.target_app}", 1

            except Exception as e:
                print(f"Direct launch failed: {e}")

        # Added this check here because if added at the top, it would fail LOL
        if not path:
            return False

        try:
            executable = {}

            # Splitting TIME!!
            for directory in path.split(os.pathsep):
                if not os.path.isdir(directory):
                    continue

                try:
                    for entry in os.scandir(directory):
                        if entry.is_file() and os.access(entry.path, os.X_OK):
                            # Now lets store it
                            executable[entry.name] = entry.path

                # Tested it once, and I got obliterated with Permission Errors
                except PermissionError:
                    continue

        # Now lets fuzzy strin' em!

            matches = difflib.get_close_matches(self.target_app, executable.keys(), n=1)

            if matches:
                best_match_name = matches[0]
                exec_path = executable[best_match_name]

                subprocess.Popen([exec_path], shell=False)
                return f"Opened {best_match_name}. Please write the app names correctly man, like you wrote {self.target_app} and I fuzzy matched it to {best_match_name})", 1
            
        except Exception as e:
            print(f"Tier 1 failed(Linux Edition)\n Error: {e}")

        return False

    def linux_tier_2(self):
        Xdg_files_paths = [Path("/usr/share/applications"), Path("~/.local/share/applications").expanduser()]
        imp_data = {}

        for path in Xdg_files_paths:
            if path.exists():
                # Here I am trying a new way(for me) of fuzzy stringing!
                for file_path in path.rglob("*.desktop"):
                    try:
                        Config_Read = ConfigParser()
                        Config_Read.read(file_path)

                        if "Desktop Entry" in Config_Read:
                            config_data = Config_Read["Desktop Entry"]

                            app_name = config_data.get("Name", file_path.stem).lower()
                            app_exec_command = config_data.get("Exec", "")

                            imp_data[app_name] = app_exec_command

                    # Skipping all the bullshit
                    except:
                        continue

        # Main function starts here
        try:
            self.target_app = self.target_app.lower()
            matches = difflib.get_close_matches(self.target_app, imp_data.keys(), n=1, cutoff=0.6)

            if matches:
                best_match_name = matches[0]
                exec_path = imp_data[best_match_name]

                exec_path = os.path.expandvars(exec_path)

                pattern = r"\s+%[a-zA-Z]"

                exec_command = re.sub(pattern, "", exec_path)
                split_exec_command = shlex.split(exec_command)

                if split_exec_command:
                    subprocess.Popen(split_exec_command, shell=False)
                    return True

        except Exception as e:
            print(f"The App does not exist \n {e}")
            return False


    def open_app(self):
        try:
            if self.current_os == "Windows":
                return self.windows_open_app()

            elif self.current_os == "Darwin":
                print(f"not implemented yet! \n Current OS: {self.current_os}")
                return False

            elif self.current_os == "Linux":
                print(f"not implemented yet! \n Current OS: {self.current_os}")
                return False

            else:
                print(f"Unsupported OS! \n Current OS: {self.current_os}")
                return False

        except Exception as e:
            print(f"Some Error occured: {e}")

# Quick Test Block
if __name__ == "__main__":
    app_to_open = OpenApps(input("Write the app name: "))

    app_to_open.linux_tier_2()