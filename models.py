from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner
    price_full = db.Column(db.Float, nullable=False)  # Full tiffin price
    price_roti_only = db.Column(db.Float, nullable=False)  # Roti only price
    is_available = db.Column(db.Boolean, default=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_roti_only = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_lat = db.Column(db.Float, nullable=True)
    delivery_lng = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, denied, delivered
    notes = db.Column(db.Text, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    order_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu_item = db.relationship('MenuItem', backref='orders', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='feedback', lazy=True)
    order = db.relationship('Order', backref='feedback', lazy=True)


class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<Settings {self.key}: {self.value}>'
    
    @staticmethod
    def get_value(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_value(key, value, description=None, user_id=None):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_by = user_id
            if description:
                setting.description = description
        else:
            setting = Settings(
                key=key,
                value=value,
                description=description,
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @staticmethod
    def get_central_coordinates():
        lat = float(Settings.get_value('CENTRAL_LAT', '20.457316'))
        lng = float(Settings.get_value('CENTRAL_LNG', '75.016754'))
        return lat, lng
    
    @staticmethod
    def get_service_radius():
        return float(Settings.get_value('SERVICE_RADIUS_KM', '5'))
