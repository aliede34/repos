"""
Database migration script to update the hosting_order table schema.
This script adds new columns for customizable hosting features and removes the old package column.
"""

import sqlite3
import os

def migrate_database():
    """Migrate the database schema for hosting_order table."""
    print("Starting database migration...")
    
    # Connect to the database
    db_path = os.path.join('instance', 'bulutyonetici.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the table has the old schema
        cursor.execute("PRAGMA table_info(hosting_order)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        # Check if we need to migrate
        if 'package' in column_names and 'disk_space' not in column_names:
            print("Migrating table schema...")
            
            # Create a new table with the updated schema
            cursor.execute("""
                CREATE TABLE hosting_order_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    disk_space VARCHAR(20),
                    bandwidth VARCHAR(20),
                    email_accounts INTEGER,
                    subdomains INTEGER,
                    databases INTEGER,
                    domain VARCHAR(100),
                    price FLOAT,
                    status VARCHAR(20),
                    created_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES user (id)
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO hosting_order_new 
                (id, user_id, domain, price, status, created_at)
                SELECT 
                id, user_id, domain, price, status, created_at
                FROM hosting_order
            """)
            
            # Drop the old table
            cursor.execute("DROP TABLE hosting_order")
            
            # Rename the new table to the original name
            cursor.execute("ALTER TABLE hosting_order_new RENAME TO hosting_order")
            
            print("Database migration completed successfully.")
        else:
            print("Table schema is already up to date.")
            
        # Commit changes
        conn.commit()
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
