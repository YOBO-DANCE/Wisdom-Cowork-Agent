import sqlite3

connection_name = "tut.db"
# connection = sqlite3.connect(":memory:") # For cache type Database
connection = sqlite3.connect(connection_name)

# This is the command handler
cursor = connection.cursor()

cursor.execute("""
        CREATE TABLE sports (
        aadhar_no integer,
        pan_no text not null unique,
        player_id integer not null unique,
    )""")

cursor.execute("""

""")