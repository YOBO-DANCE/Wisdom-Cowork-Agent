import sqlite3 as db

# Define connection and cursor

connection = db.connect(r"Learning\SQLITE3\test.db")

cursor = connection.cursor()