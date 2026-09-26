import sqlite3
import os
import platform

if platform.system == "Windows":
    import winreg


DB_FILE = "tests/apps.db"

def init_db():
    """Creates the apps.db file and 'apps' table if it doesn't already exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create table with app_alias as primary key (no duplicates allowed)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            app_alias TEXT PRIMARY KEY,
            exe_path TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_apps_from_db(app_name: str) -> str | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT exe_path FROM apps WHERE app_alias = ?", (app_name,)),
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return row[0]
    return None

def save_apps_to_db(app_dict: dict[str, str]):
    """Wipes old entries and inserts a fresh dictionary of {alias: path} into SQLite."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Clear old entries so deleted/uninstalled apps don't linger
    cursor.execute("DELETE FROM apps")

    # Insert all app entries in a loop
    for alias, path in app_dict.items():
        cursor.execute(
            "INSERT OR REPLACE INTO apps (app_alias, exe_path) VALUES (?, ?)",
            (alias.lower().strip(), path.lower().strip()),
        )

    conn.commit()
    conn.close()

def populate_db() -> dict[str, str]:
    if platform.system != "Windows":
        return {}

    discovered = {}

    targets = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        ),
    ]

    for hive, subkey_path in targets:
        try:
            access_mask = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            parent_key = winreg.OpenKey(hive, subkey_path, 0, access_mask)
            num_subkeys, _, _ = winreg.QueryInfoKey(parent_key)


            for i in range(num_subkeys):
                try:
                    app_exe_name = winreg.EnumKey(parent_key, i)
                    app_key = winreg.OpenKey(parent_key, app_exe_name, 0, access_mask)
                    raw_path, _ = winreg.QueryValueEx(app_key, "")
                    winreg.CloseKey(app_key)

                    if not raw_path:
                        continue

                    clean_path = raw_path.replace('"', '').strip()

                    if " " in clean_path and not clean_path.lower().endswith(
                        ".exe"
                    ):
                        exe_idx = clean_path.lower().find(".exe")
                        if exe_idx != -1:
                            clean_path = clean_path [: exe_idx + 4]

                    if os.path.exists(clean_path):
                        alias = app_exe_name.lower().replace(".exe", "")
                        discovered[alias] = clean_path.lower()

                except OSError:
                    continue

            winreg.CloseKey(parent_key)
        except OSError:
            continue

        return discovered

def add_apps_to_db():
    init_db()

    print("Scanning Windows Registry for Apps...")
    real_apps = populate_db()

    save_apps_to_db(real_apps)
    print(f"Success! Added {len(real_apps)} into the Database.")



if __name__ == "__main__":
    add_apps_to_db()

    # Test reading back a real application from your database
    chrome_path = get_apps_from_db("chrome")
    print(f"Queried Chrome path from DB: {chrome_path}")