from app import app, db, User, ServerOrder, HostingOrder, SupportTicket
import json

def migrate_database():
    with app.app_context():
        # Get all existing data
        users = User.query.all()
        server_orders = ServerOrder.query.all()
        hosting_orders = HostingOrder.query.all()
        support_tickets = SupportTicket.query.all()
        
        # Store data in memory
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'company': user.company,
                'is_admin': getattr(user, 'is_admin', False),  # Default to False if column doesn't exist
                'created_at': user.created_at
            })
        
        server_order_data = []
        for order in server_orders:
            server_order_data.append({
                'id': order.id,
                'user_id': order.user_id,
                'server_type': order.server_type,
                'cpu': order.cpu,
                'ram': order.ram,
                'storage': order.storage,
                'price': order.price,
                'status': order.status,
                'created_at': order.created_at
            })
        
        hosting_order_data = []
        for order in hosting_orders:
            hosting_order_data.append({
                'id': order.id,
                'user_id': order.user_id,
                'package': order.package,
                'domain': order.domain,
                'price': order.price,
                'status': order.status,
                'created_at': order.created_at
            })
        
        support_ticket_data = []
        for ticket in support_tickets:
            support_ticket_data.append({
                'id': ticket.id,
                'user_id': ticket.user_id,
                'subject': ticket.subject,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at,
                'updated_at': ticket.updated_at
            })
        
        # Drop all tables
        db.drop_all()
        
        # Recreate tables with new schema
        db.create_all()
        
        # Reinsert data
        for data in user_data:
            user = User(
                id=data['id'],
                username=data['username'],
                email=data['email'],
                password=data['password'],
                company=data['company'],
                is_admin=data['is_admin'],
                created_at=data['created_at']
            )
            db.session.add(user)
        
        for data in server_order_data:
            order = ServerOrder(
                id=data['id'],
                user_id=data['user_id'],
                server_type=data['server_type'],
                cpu=data['cpu'],
                ram=data['ram'],
                storage=data['storage'],
                price=data['price'],
                status=data['status'],
                created_at=data['created_at']
            )
            db.session.add(order)
        
        for data in hosting_order_data:
            order = HostingOrder(
                id=data['id'],
                user_id=data['user_id'],
                package=data['package'],
                domain=data['domain'],
                price=data['price'],
                status=data['status'],
                created_at=data['created_at']
            )
            db.session.add(order)
        
        for data in support_ticket_data:
            ticket = SupportTicket(
                id=data['id'],
                user_id=data['user_id'],
                subject=data['subject'],
                description=data['description'],
                status=data['status'],
                priority=data['priority'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            db.session.add(ticket)
        
        # Commit changes
        db.session.commit()
        print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
