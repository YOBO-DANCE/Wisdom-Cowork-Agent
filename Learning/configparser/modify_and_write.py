from configparser import ConfigParser

Config = ConfigParser()

Config["DISPLAY"] = {
    "theme": "dark",
    "window_opacity": 0.9
}

# Lets write it
with open("settings.ini", "w") as f:
    Config.write(f)


# Now Reading the config File
Config_Read = ConfigParser()

Config_Read.read("settings.ini")
config_data = Config_Read["DISPLAY"]

print(config_data["theme"])

config_data["theme"] = input("Change the theme: ")

with open("settings.ini", "w") as chg_theme:
    Config_Read.write(chg_theme)