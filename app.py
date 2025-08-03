from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bulutyonetici.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Admin decorator
def admin_required(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen önce giriş yapın.', 'error')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Bu sayfaya erişim izniniz yok.', 'error')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return wrapped

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ServerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    server_type = db.Column(db.String(50), nullable=False)
    cpu = db.Column(db.String(20))
    ram = db.Column(db.String(20))
    storage = db.Column(db.String(20))
    price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('server_orders', lazy=True))

class HostingOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Replace package with individual features
    disk_space = db.Column(db.String(20))  # e.g., '10GB', '50GB', '100GB', '200GB', '500GB'
    bandwidth = db.Column(db.String(20))   # e.g., '100GB', '500GB', '1TB', '5TB'
    email_accounts = db.Column(db.Integer) # Number of email accounts
    subdomains = db.Column(db.Integer)     # Number of subdomains
    databases = db.Column(db.Integer)      # Number of databases
    domain = db.Column(db.String(100))
    price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('hosting_orders', lazy=True))

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('support_tickets', lazy=True))

class ColocationOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    server_size = db.Column(db.String(50))  # e.g., '1U', '2U', '4U'
    rack_units = db.Column(db.Integer)      # Number of rack units
    bandwidth = db.Column(db.String(20))    # e.g., '100Mbps', '1Gbps', '10Gbps'
    ip_addresses = db.Column(db.Integer)    # Number of IP addresses
    power_ports = db.Column(db.Integer)     # Number of power ports
    remote_hands = db.Column(db.Boolean, default=False)  # Remote hands service
    domain = db.Column(db.String(100))
    price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('colocation_orders', lazy=True))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # Note: In production, use proper password hashing
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        company = request.form.get('company', '')
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanımda', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanımda', 'error')
            return render_template('register.html')
        
        # Check if this is the first user (make them admin)
        is_first_user = User.query.count() == 0
        
        # Create new user
        new_user = User(username=username, email=email, company=company, password=password, is_admin=is_first_user)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Hesabınız oluşturuldu! Lütfen giriş yapın.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    server_orders = ServerOrder.query.filter_by(user_id=user.id).all()
    hosting_orders = HostingOrder.query.filter_by(user_id=user.id).all()
    colocation_orders = ColocationOrder.query.filter_by(user_id=user.id).all()
    support_tickets = SupportTicket.query.filter_by(user_id=user.id).all()
    
    # Combine all orders for display
    all_orders = server_orders + hosting_orders + colocation_orders
    
    return render_template('dashboard.html', user=user, server_orders=server_orders, 
                          hosting_orders=hosting_orders, colocation_orders=colocation_orders,
                          all_orders=all_orders, support_tickets=support_tickets)

@app.route('/server-order', methods=['GET', 'POST'])
def server_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        server_type = request.form['server_type']
        cpu = request.form['cpu']
        ram = request.form['ram']
        storage = request.form['storage']
        
        # Simple pricing logic
        prices = {
            'basic': 100,
            'standard': 200,
            'premium': 400
        }
        price = prices.get(server_type, 100)
        
        new_order = ServerOrder(
            user_id=session['user_id'],
            server_type=server_type,
            cpu=cpu,
            ram=ram,
            storage=storage,
            price=price
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        flash('Sunucu siparişi oluşturuldu!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('server_order.html')

@app.route('/hosting-order', methods=['GET', 'POST'])
def hosting_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get individual features
        disk_space = request.form['disk_space']
        bandwidth = request.form['bandwidth']
        email_accounts = int(request.form['email_accounts'])
        subdomains = int(request.form['subdomains'])
        databases = int(request.form['databases'])
        domain = request.form['domain']
        
        # Calculate price based on features
        price = calculate_hosting_price({
            'disk_space': disk_space,
            'bandwidth': bandwidth,
            'email_accounts': email_accounts,
            'subdomains': subdomains,
            'databases': databases
        })
        
        new_order = HostingOrder(
            user_id=session['user_id'],
            disk_space=disk_space,
            bandwidth=bandwidth,
            email_accounts=email_accounts,
            subdomains=subdomains,
            databases=databases,
            domain=domain,
            price=price
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        flash('Hosting siparişi oluşturuldu!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('hosting_order.html')

@app.route('/support', methods=['GET', 'POST'])
def support():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject = request.form['subject']
        description = request.form['description']
        priority = request.form['priority']
        
        new_ticket = SupportTicket(
            user_id=session['user_id'],
            subject=subject,
            description=description,
            priority=priority
        )
        
        db.session.add(new_ticket)
        db.session.commit()
        
        flash('Destek talebi oluşturuldu!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('support.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı', 'info')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    # Get statistics
    total_users = User.query.count()
    total_server_orders = ServerOrder.query.count()
    total_hosting_orders = HostingOrder.query.count()
    total_support_tickets = SupportTicket.query.count()
    
    # Get recent orders
    recent_orders = ServerOrder.query.order_by(ServerOrder.created_at.desc()).limit(5).all() + \
                    HostingOrder.query.order_by(HostingOrder.created_at.desc()).limit(5).all()
    recent_orders = sorted(recent_orders, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Get recent support tickets
    recent_tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users,
                          total_server_orders=total_server_orders,
                          total_hosting_orders=total_hosting_orders,
                          total_support_tickets=total_support_tickets,
                          recent_orders=recent_orders,
                          recent_tickets=recent_tickets)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    server_orders = ServerOrder.query.all()
    hosting_orders = HostingOrder.query.all()
    colocation_orders = ColocationOrder.query.all()
    return render_template('admin/orders.html', 
                          server_orders=server_orders,
                          hosting_orders=hosting_orders,
                          colocation_orders=colocation_orders)

@app.route('/admin/tickets')
@admin_required
def admin_tickets():
    tickets = SupportTicket.query.all()
    return render_template('admin/tickets.html', tickets=tickets)

@app.route('/admin/toggle_admin/<int:user_id>')
@admin_required
def admin_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != session['user_id']:  # Prevent self demotion
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'{user.username} için admin durumu güncellendi.', 'success')
    else:
        flash('Kendi admin durumunuzu değiştiremezsiniz.', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != session['user_id']:  # Prevent self deletion
        # Delete associated orders and tickets first
        ServerOrder.query.filter_by(user_id=user.id).delete()
        HostingOrder.query.filter_by(user_id=user.id).delete()
        ColocationOrder.query.filter_by(user_id=user.id).delete()
        SupportTicket.query.filter_by(user_id=user.id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f'{user.username} kullanıcısı silindi.', 'success')
    else:
        flash('Kendinizi silemezsiniz.', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_server_order/<int:order_id>', methods=['POST'])
@admin_required
def admin_delete_server_order(order_id):
    order = ServerOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Sunucu siparişi silindi.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/delete_hosting_order/<int:order_id>', methods=['POST'])
@admin_required
def admin_delete_hosting_order(order_id):
    order = HostingOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Hosting siparişi silindi.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/delete_colocation_order/<int:order_id>', methods=['POST'])
@admin_required
def admin_delete_colocation_order(order_id):
    order = ColocationOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Colocation siparişi silindi.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/upgrade_server/<int:order_id>', methods=['GET', 'POST'])
def upgrade_server(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the server order
    order = ServerOrder.query.filter_by(id=order_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        # Get new features
        cpu = request.form.get('cpu', order.cpu)
        ram = request.form.get('ram', order.ram)
        storage = request.form.get('storage', order.storage)
        
        # Store old features for tracking
        old_features = {
            'cpu': order.cpu,
            'ram': order.ram,
            'storage': order.storage
        }
        
        # Update order with new features
        order.cpu = cpu
        order.ram = ram
        order.storage = storage
        
        # Calculate price difference (simplified pricing logic)
        old_price = calculate_server_price(order.server_type, old_features)
        new_price = calculate_server_price(order.server_type, {
            'cpu': cpu,
            'ram': ram,
            'storage': storage
        })
        
        price_difference = new_price - old_price
        order.price = new_price
        
        # Save changes to database
        db.session.commit()
        
        flash(f'Sunucu özellikleri güncellendi. Fiyat farkı: ₺{price_difference:.2f}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upgrade_server.html', order=order)

# Pricing calculation functions
def calculate_server_price(server_type, features):
    # Base prices
    base_prices = {
        'basic': 100,
        'standard': 200,
        'premium': 400
    }
    
    base_price = base_prices.get(server_type, 100)
    
    # Feature pricing adjustments
    cpu_price = 0
    ram_price = 0
    storage_price = 0
    
    # CPU pricing
    if features.get('cpu'):
        cpu_map = {
            '2 cores': 0,
            '4 cores': 50,
            '8 cores': 100,
            '16 cores': 200
        }
        cpu_price = cpu_map.get(features['cpu'], 0)
    
    # RAM pricing
    if features.get('ram'):
        ram_map = {
            '4GB': 0,
            '8GB': 30,
            '16GB': 60,
            '32GB': 120
        }
        ram_price = ram_map.get(features['ram'], 0)
    
    # Storage pricing
    if features.get('storage'):
        storage_map = {
            '50GB SSD': 0,
            '100GB SSD': 20,
            '200GB SSD': 40,
            '500GB SSD': 100,
            '1TB SSD': 200
        }
        storage_price = storage_map.get(features['storage'], 0)
    
    return base_price + cpu_price + ram_price + storage_price

@app.route('/upgrade_hosting/<int:order_id>', methods=['GET', 'POST'])
def upgrade_hosting(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the hosting order
    order = HostingOrder.query.filter_by(id=order_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        # Get new features
        disk_space = request.form.get('disk_space', order.disk_space)
        bandwidth = request.form.get('bandwidth', order.bandwidth)
        email_accounts = int(request.form.get('email_accounts', order.email_accounts))
        subdomains = int(request.form.get('subdomains', order.subdomains))
        databases = int(request.form.get('databases', order.databases))
        domain = request.form.get('domain', order.domain)
        
        # Store old features for tracking
        old_features = {
            'disk_space': order.disk_space,
            'bandwidth': order.bandwidth,
            'email_accounts': order.email_accounts,
            'subdomains': order.subdomains,
            'databases': order.databases
        }
        
        # Update order with new features
        order.disk_space = disk_space
        order.bandwidth = bandwidth
        order.email_accounts = email_accounts
        order.subdomains = subdomains
        order.databases = databases
        order.domain = domain
        
        # Calculate price difference
        old_price = calculate_hosting_price(old_features)
        new_price = calculate_hosting_price({
            'disk_space': disk_space,
            'bandwidth': bandwidth,
            'email_accounts': email_accounts,
            'subdomains': subdomains,
            'databases': databases
        })
        
        price_difference = new_price - old_price
        order.price = new_price
        
        # Save changes to database
        db.session.commit()
        
        flash(f'Hosting özellikleri güncellendi. Fiyat farkı: ₺{price_difference:.2f}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upgrade_hosting.html', order=order)

@app.route('/colocation-order', methods=['GET', 'POST'])
def colocation_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        server_size = request.form.get('server_size')
        rack_units = int(request.form.get('rack_units', 1))
        bandwidth = request.form.get('bandwidth')
        ip_addresses = int(request.form.get('ip_addresses', 1))
        power_ports = int(request.form.get('power_ports', 1))
        remote_hands = 'remote_hands' in request.form
        domain = request.form.get('domain', '')
        
        # Calculate price
        features = {
            'server_size': server_size,
            'rack_units': rack_units,
            'bandwidth': bandwidth,
            'ip_addresses': ip_addresses,
            'power_ports': power_ports,
            'remote_hands': remote_hands
        }
        price = calculate_colocation_price(features)
        
        # Create new colocation order
        new_order = ColocationOrder(
            user_id=session['user_id'],
            server_size=server_size,
            rack_units=rack_units,
            bandwidth=bandwidth,
            ip_addresses=ip_addresses,
            power_ports=power_ports,
            remote_hands=remote_hands,
            domain=domain,
            price=price,
            status='pending'
        )
        
        # Save to database
        db.session.add(new_order)
        db.session.commit()
        
        flash(f'Colocation siparişi oluşturuldu! Toplam fiyat: ₺{price:.2f}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('colocation_order.html')

def calculate_hosting_price(features):
    # Base price
    base_price = 20  # Base hosting price
    
    # Disk space pricing (per GB)
    disk_space_map = {
        '10GB': 0,
        '50GB': 10,
        '100GB': 20,
        '200GB': 40,
        '500GB': 100
    }
    disk_price = disk_space_map.get(features.get('disk_space'), 0)
    
    # Bandwidth pricing (per TB)
    bandwidth_map = {
        '100GB': 0,
        '500GB': 10,
        '1TB': 20,
        '5TB': 50
    }
    bandwidth_price = bandwidth_map.get(features.get('bandwidth'), 0)
    
    # Email accounts pricing (per account)
    email_price = features.get('email_accounts', 0) * 2
    
    # Subdomains pricing (per subdomain)
    subdomain_price = features.get('subdomains', 0) * 1
    
    # Databases pricing (per database)
    database_price = features.get('databases', 0) * 5
    
    return base_price + disk_price + bandwidth_price + email_price + subdomain_price + database_price

def calculate_colocation_price(features):
    # Base price for colocation service (monthly)
    base_price = 3500  # Base colocation price per month
    
    # Server size pricing
    server_size_map = {
        '1U': 0,
        '2U': 100,
        '4U': 200
    }
    server_size_price = server_size_map.get(features.get('server_size'), 0)
    
    # Rack units pricing (per unit)
    rack_units_price = features.get('rack_units', 1) * 200
    
    # Bandwidth pricing
    bandwidth_map = {
        '100Mbps': 0,
        '1Gbps': 500,
        '10Gbps': 2000
    }
    bandwidth_price = bandwidth_map.get(features.get('bandwidth'), 0)
    
    # IP addresses pricing (per IP)
    ip_price = features.get('ip_addresses', 1) * 10
    
    # Power ports pricing (per port)
    power_price = features.get('power_ports', 1) * 50
    
    # Remote hands service pricing
    remote_hands_price = 200 if features.get('remote_hands', False) else 0
    
    # Calculate monthly price
    monthly_price = base_price + server_size_price + rack_units_price + bandwidth_price + ip_price + power_price + remote_hands_price
    
    # Apply 10% discount for annual billing (12 months)
    annual_price = monthly_price * 12 * 0.9
    
    # For order creation, we'll use the monthly price
    # The discount information will be shown in the UI
    return monthly_price

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use the PORT environment variable for Render, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
