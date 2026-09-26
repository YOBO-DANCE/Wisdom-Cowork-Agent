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