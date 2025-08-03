# BulutYönetici SaaS Platform

BulutYönetici is a Turkish SaaS company website built with Python Flask that provides cloud hosting and server management services.

## Features

- User authentication (registration and login)
- Customer management panel
- Server ordering system with customizable CPU, RAM, and storage
- Hosting ordering system with customizable features:
  - Disk space (10GB, 50GB, 100GB, 200GB, 500GB)
  - Bandwidth (100GB, 500GB, 1TB, 5TB)
  - Email accounts
  - Subdomains
  - Databases
- Support ticket system
- Admin panel for managing users, orders, and support tickets
- Upgrade/downgrade functionality for both server and hosting orders

## Recent Changes

### Customizable Hosting Features

We've replaced the fixed hosting packages (Basic, Standard, Premium) with a customizable feature selection system. Users can now individually select:

- Disk space
- Bandwidth
- Number of email accounts
- Number of subdomains
- Number of databases

Each feature has its own pricing:

- Base hosting price: ₺20
- Disk space pricing:
  - 10GB: ₺0
  - 50GB: ₺10
  - 100GB: ₺20
  - 200GB: ₺40
  - 500GB: ₺100
- Bandwidth pricing:
  - 100GB: ₺0
  - 500GB: ₺10
  - 1TB: ₺20
  - 5TB: ₺50
- Per-unit pricing:
  - Email accounts: ₺2 each
  - Subdomains: ₺1 each
  - Databases: ₺5 each

### Database Migration

The database schema was updated to support the new customizable hosting features. The migration included:

1. Adding new columns to the hosting_order table:
   - disk_space
   - bandwidth
   - email_accounts
   - subdomains
   - databases
2. Removing the old package column
3. Migrating existing hosting orders from package-based to feature-based structure

## Tech Stack

- Python 3.x
- Flask web framework
- Flask-SQLAlchemy for database ORM
- SQLite database
- Jinja2 templating engine
- Bootstrap 5 for responsive UI
- Font Awesome for icons

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Access the application at http://127.0.0.1:5000

## Usage

1. Register for a new account or login with existing credentials
2. Navigate to the dashboard to view your orders and support tickets
3. Order new servers or hosting services using the "Yeni Sunucu Siparişi" or "Yeni Hosting Siparişi" buttons
4. Customize your hosting features according to your needs
5. Manage your existing orders through the upgrade/downgrade functionality
6. Create support tickets for any issues or questions

## Admin Panel

Administrators can access the admin panel by logging in with an account that has admin privileges. The admin panel allows for:

- Managing users
- Managing orders
- Managing support tickets
- Granting/revoking admin privileges to other users

## License

This project is licensed under the MIT License.
