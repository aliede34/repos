import sqlite3
import os

def check_schema():
    # Connect to the database
    conn = sqlite3.connect('instance/bulutyonetici.db')
    cursor = conn.cursor()
    
    # Get the schema for the user table
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user'")
    result = cursor.fetchone()
    
    if result:
        print("Current user table schema:")
        print(result[0])
    else:
        print("User table not found")
    
    # Close the connection
    conn.close()

if __name__ == '__main__':
    check_schema()
