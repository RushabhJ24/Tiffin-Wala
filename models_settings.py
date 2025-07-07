from app import db
from datetime import datetime

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