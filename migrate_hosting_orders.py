"""
Migration script to update HostingOrder table from package-based to feature-based structure.
This script will migrate existing hosting orders to the new customizable feature structure.
"""

import sqlite3
import sys
import os

# Add the website directory to the path so we can import app
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import app, db, HostingOrder

def migrate_hosting_orders():
    """Migrate existing hosting orders from package-based to feature-based structure."""
    print("Starting migration of hosting orders...")
    
    # Get all existing hosting orders
    orders = HostingOrder.query.all()
    print(f"Found {len(orders)} hosting orders to migrate.")
    
    migrated_count = 0
    
    for order in orders:
        print(f"Migrating order {order.id}...")
        
        # Map old packages to new feature values
        if order.package == 'basic':
            order.disk_space = '10GB'
            order.bandwidth = '100GB'
            order.email_accounts = 1
            order.subdomains = 1
            order.databases = 1
        elif order.package == 'standard':
            order.disk_space = '50GB'
            order.bandwidth = '500GB'
            order.email_accounts = 5
            order.subdomains = 5
            order.databases = 2
        elif order.package == 'premium':
            order.disk_space = '200GB'
            order.bandwidth = '5TB'
            order.email_accounts = 20
            order.subdomains = 20
            order.databases = 10
        else:
            # Default values if package is unknown
            order.disk_space = '10GB'
            order.bandwidth = '100GB'
            order.email_accounts = 1
            order.subdomains = 1
            order.databases = 1
        
        # Recalculate price based on new features
        from app import calculate_hosting_price
        new_price = calculate_hosting_price({
            'disk_space': order.disk_space,
            'bandwidth': order.bandwidth,
            'email_accounts': order.email_accounts,
            'subdomains': order.subdomains,
            'databases': order.databases
        })
        order.price = new_price
        
        migrated_count += 1
        print(f"  Migrated order {order.id} - New price: ₺{new_price}")
    
    # Commit all changes
    db.session.commit()
    print(f"Successfully migrated {migrated_count} hosting orders.")

if __name__ == "__main__":
    with app.app_context():
        migrate_hosting_orders()
