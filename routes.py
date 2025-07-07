from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json

from app import app, db
from models import User, MenuItem, Order, Feedback, Settings
from auth import admin_required
from location_utils import is_location_serviceable, get_location_from_address, calculate_distance, update_env_file

@app.route('/')
def index():
    """Home page"""
    # Auto-disable expired menu items
    from tasks import disable_expired_menu_items
    disable_expired_menu_items()
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    # Get today's menu for display
    today = date.today()
    menu_items = MenuItem.query.filter_by(date=today, is_available=True).all()
    
    return render_template('index.html', menu_items=menu_items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Validation
        if not all([name, email, phone, password, address]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html')
        
        # Check location serviceability
        if latitude and longitude:
            if not is_location_serviceable(latitude, longitude):
                flash('Sorry, no services are available at your location.', 'warning')
                return render_template('register.html')
        else:
            # Fallback: try to get coordinates from address
            location_data = get_location_from_address(address)
            latitude = location_data['latitude']
            longitude = location_data['longitude']
            
            if not is_location_serviceable(latitude, longitude):
                flash('Sorry, no services are available at your location.', 'warning')
                return render_template('register.html')
        
        # Create new user
        user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            app.logger.error(f"Registration error: {e}")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/user-dashboard')
@login_required
def user_dashboard():
    """User dashboard"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get user's recent orders
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(10).all()
    
    # Get today's menu
    today = date.today()
    menu_items = MenuItem.query.filter_by(date=today, is_available=True).all()
    
    return render_template('user_dashboard.html', 
                         recent_orders=recent_orders, 
                         menu_items=menu_items)

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get today's statistics
    today = date.today()
    
    stats = {
        'total_orders_today': Order.query.filter_by(order_date=today).count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'total_users': User.query.filter_by(is_admin=False).count(),
        'menu_items_today': MenuItem.query.filter_by(date=today, is_available=True).count()
    }
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', stats=stats, recent_orders=recent_orders)

@app.route('/menu')
def menu():
    """Display today's menu"""
    # Auto-disable expired menu items
    from tasks import disable_expired_menu_items
    disable_expired_menu_items()
    today = date.today()
    menu_items = MenuItem.query.filter_by(date=today, is_available=True).all()
    
    # Group by meal type
    menu_by_type = {}
    for item in menu_items:
        if item.meal_type not in menu_by_type:
            menu_by_type[item.meal_type] = []
        menu_by_type[item.meal_type].append(item)
    
    return render_template('menu.html', menu_by_type=menu_by_type)

@app.route('/order/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def place_order(menu_item_id):
    """Place an order"""
    if current_user.is_admin:
        flash('Admins cannot place orders.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    
    if not menu_item.is_available:
        flash('This menu item is not available.', 'warning')
        return redirect(url_for('menu'))
    
    if request.method == 'POST':
        quantity = request.form.get('quantity', type=int, default=1)
        is_roti_only = request.form.get('is_roti_only') == 'on'
        delivery_address = request.form.get('delivery_address', '').strip()
        notes = request.form.get('notes', '').strip()
        delivery_lat = request.form.get('delivery_lat', type=float)
        delivery_lng = request.form.get('delivery_lng', type=float)
        
        # Validation
        if quantity < 1:
            flash('Quantity must be at least 1.', 'danger')
            return render_template('order.html', menu_item=menu_item)
        
        if not delivery_address:
            flash('Delivery address is required.', 'danger')
            return render_template('order.html', menu_item=menu_item)
        
        # Check location serviceability
        if delivery_lat and delivery_lng:
            if not is_location_serviceable(delivery_lat, delivery_lng):
                flash('Sorry, no services are available at your delivery location.', 'warning')
                return render_template('order.html', menu_item=menu_item)
        else:
            # Use user's registered location as fallback
            delivery_lat = current_user.latitude
            delivery_lng = current_user.longitude
            
            if not is_location_serviceable(delivery_lat, delivery_lng):
                flash('Sorry, no services are available at your delivery location.', 'warning')
                return render_template('order.html', menu_item=menu_item)
        
        # Calculate total price
        unit_price = menu_item.price_roti_only if is_roti_only else menu_item.price_full
        total_price = unit_price * quantity
        
        # Create order
        order = Order(
            user_id=current_user.id,
            menu_item_id=menu_item.id,
            quantity=quantity,
            is_roti_only=is_roti_only,
            total_price=total_price,
            delivery_address=delivery_address,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            notes=notes,
            order_date=date.today()
        )
        
        try:
            db.session.add(order)
            db.session.commit()
            flash('Order placed successfully! You will be notified once it\'s approved.', 'success')
            return redirect(url_for('user_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to place order. Please try again.', 'danger')
            app.logger.error(f"Order placement error: {e}")
    
    return render_template('order.html', menu_item=menu_item)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin view for managing orders"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Order.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get current central coordinates for navigation
    central_lat, central_lng = Settings.get_central_coordinates()
    
    return render_template('admin_orders.html', 
                         orders=orders, 
                         current_status=status_filter,
                         central_lat=central_lat,
                         central_lng=central_lng)

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '').strip()
    
    if new_status not in ['pending', 'approved', 'denied', 'delivered']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin_orders'))
    
    order.status = new_status
    if admin_notes:
        order.admin_notes = admin_notes
    order.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update order status.', 'danger')
        app.logger.error(f"Order status update error: {e}")
    
    return redirect(url_for('admin_orders'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Update user profile"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([name, email, phone, address]):
            flash('Name, email, phone, and address are required.', 'danger')
            return render_template('profile.html')
        
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash('Email address is already in use.', 'danger')
            return render_template('profile.html')
        
        # Password change validation
        if new_password:
            if not current_password:
                flash('Current password is required to change password.', 'danger')
                return render_template('profile.html')
            
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('profile.html')
            
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('profile.html')
        
        # Update user information
        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        current_user.address = address
        
        # Update location if provided
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        if latitude is not None and longitude is not None:
            current_user.latitude = latitude
            current_user.longitude = longitude
        
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('update_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile. Please try again.', 'danger')
            app.logger.error(f"Profile update error: {e}")
    
    return render_template('profile.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin view for managing users"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = User.query
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_users.html', users=users, status_filter=status_filter)

@app.route('/admin/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if user.is_admin and not data.get('active', True):
        return jsonify({'success': False, 'message': 'Cannot deactivate admin users'}), 400
    
    user.is_active = data.get('active', True)
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"User status toggle error: {e}")
        return jsonify({'success': False}), 500

@app.route('/admin/user/<int:user_id>/details')
@admin_required
def user_details(user_id):
    """Get user details for admin"""
    user = User.query.get_or_404(user_id)
    order_count = Order.query.filter_by(user_id=user_id).count()
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
        'latitude': user.latitude,
        'longitude': user.longitude,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat(),
        'order_count': order_count
    })

@app.route('/admin/menu')
@admin_required
def admin_menu():
    """Admin menu management"""
    # Auto-disable expired menu items
    from tasks import disable_expired_menu_items
    disable_expired_menu_items()
    selected_date = request.args.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    menu_items = MenuItem.query.filter_by(date=selected_date).all()
    
    return render_template('admin_menu.html', menu_items=menu_items, selected_date=selected_date)

@app.route('/admin/menu/add', methods=['POST'])
@admin_required
def add_menu_item():
    """Add a new menu item"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    meal_type = request.form.get('meal_type', '').strip()
    price_full = request.form.get('price_full', type=float)
    price_roti_only = request.form.get('price_roti_only', type=float)
    menu_date = request.form.get('date')
    
    # Validation
    if not all([name, meal_type, price_full, price_roti_only, menu_date]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin_menu'))
    
    if meal_type not in ['breakfast', 'lunch', 'dinner']:
        flash('Invalid meal type.', 'danger')
        return redirect(url_for('admin_menu'))
    
    try:
        menu_date = datetime.strptime(menu_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('admin_menu'))
    
    # Create menu item
    menu_item = MenuItem(
        name=name,
        description=description,
        meal_type=meal_type,
        price_full=price_full,
        price_roti_only=price_roti_only,
        date=menu_date
    )
    
    try:
        db.session.add(menu_item)
        db.session.commit()
        flash('Menu item added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to add menu item.', 'danger')
        app.logger.error(f"Menu item add error: {e}")
    
    return redirect(url_for('admin_menu', date=menu_date.strftime('%Y-%m-%d')))

@app.route('/admin/menu/<int:item_id>/toggle', methods=['POST'])
@admin_required
def toggle_menu_item(item_id):
    """Toggle menu item availability"""
    menu_item = MenuItem.query.get_or_404(item_id)
    menu_item.is_available = not menu_item.is_available
    menu_item.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        status = "enabled" if menu_item.is_available else "disabled"
        flash(f'Menu item {status} successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update menu item.', 'danger')
        app.logger.error(f"Menu item toggle error: {e}")
    
    return redirect(url_for('admin_menu', date=menu_item.date.strftime('%Y-%m-%d')))

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Admin settings page"""
    central_lat, central_lng = Settings.get_central_coordinates()
    service_radius = Settings.get_service_radius()
    
    return render_template('admin_settings.html', 
                         central_lat=central_lat, 
                         central_lng=central_lng, 
                         service_radius=service_radius)

@app.route('/admin/settings', methods=['POST'])
@admin_required
def update_admin_settings():
    """Update admin settings"""
    try:
        central_lat = request.form.get('central_lat', type=float)
        central_lng = request.form.get('central_lng', type=float)
        service_radius = request.form.get('service_radius', type=float)
        
        if not all([central_lat, central_lng, service_radius]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin_settings'))
        
        if service_radius <= 0 or service_radius > 50:
            flash('Service radius must be between 1 and 50 km.', 'danger')
            return redirect(url_for('admin_settings'))
        
        # Update settings in database
        Settings.set_value('CENTRAL_LAT', str(central_lat), 
                          'Central service location latitude', current_user.id)
        Settings.set_value('CENTRAL_LNG', str(central_lng), 
                          'Central service location longitude', current_user.id)
        Settings.set_value('SERVICE_RADIUS_KM', str(service_radius), 
                          'Service radius in kilometers', current_user.id)
        
        # Update .env file to maintain synchronization
        update_env_file(central_lat, central_lng, service_radius)
        
        flash('Settings updated successfully! Service area configuration has been updated across all systems.', 'success')
        return redirect(url_for('admin_settings'))
        
    except Exception as e:
        app.logger.error(f"Settings update error: {e}")
        flash('Failed to update settings. Please try again.', 'danger')
        return redirect(url_for('admin_settings'))

@app.route('/api/check-location', methods=['POST'])
def check_location():
    """API endpoint to check if location is serviceable"""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    try:
        serviceable = is_location_serviceable(float(latitude), float(longitude))
        return jsonify({'serviceable': serviceable})
    except Exception as e:
        app.logger.error(f"Location check error: {e}")
        return jsonify({'error': 'Failed to check location'}), 500

@app.route('/api/service-config')
def get_service_config():
    """API endpoint to get current service configuration"""
    try:
        central_lat, central_lng = Settings.get_central_coordinates()
        service_radius = Settings.get_service_radius()
        
        return jsonify({
            'central_lat': central_lat,
            'central_lng': central_lng,
            'service_radius': service_radius
        })
    except Exception as e:
        app.logger.error(f"Service config error: {e}")
        return jsonify({
            'central_lat': 20.457316,
            'central_lng': 75.016754,
            'service_radius': 5
        })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
