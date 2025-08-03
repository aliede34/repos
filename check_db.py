import sqlite3

def check_database():
    # Connect to the database
    conn = sqlite3.connect('instance/bulutyonetici.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables in database:')
    for table in tables:
        print(table[0])
    
    # Check if hosting_order table exists and its schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hosting_order'")
    result = cursor.fetchone()
    
    if result:
        print('\nhosting_order table exists')
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='hosting_order'")
        schema = cursor.fetchone()[0]
        print('Schema:')
        print(schema)
    else:
        print('\nhosting_order table does not exist')
    
    conn.close()

if __name__ == '__main__':
    check_database()
