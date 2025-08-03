import sqlite3

def add_admin_column():
    # Connect to the database
    conn = sqlite3.connect('instance/bulutyonetici.db')
    cursor = conn.cursor()
    
    # Add the is_admin column to the user table
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        print("Successfully added is_admin column to user table")
    except sqlite3.OperationalError as e:
        print(f"Error adding column: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_admin_column()
