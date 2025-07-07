"""
Background tasks for the Tiffin Service application
"""
from datetime import datetime, date
from app import app, db
from models import MenuItem
import logging

def disable_expired_menu_items():
    """
    Disable menu items that have passed their date
    This function should be called periodically (e.g., daily)
    """
    with app.app_context():
        try:
            today = date.today()
            
            # Find all active menu items with dates before today
            expired_items = MenuItem.query.filter(
                MenuItem.date < today,
                MenuItem.is_available == True
            ).all()
            
            count = 0
            for item in expired_items:
                item.is_available = False
                item.updated_at = datetime.utcnow()
                count += 1
            
            if count > 0:
                db.session.commit()
                logging.info(f"Disabled {count} expired menu items")
            
            return count
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error disabling expired menu items: {e}")
            return 0

def get_expired_items_count():
    """Get count of items that should be disabled"""
    with app.app_context():
        today = date.today()
        return MenuItem.query.filter(
            MenuItem.date < today,
            MenuItem.is_available == True
        ).count()

if __name__ == "__main__":
    # Run the task manually
    count = disable_expired_menu_items()
    print(f"Disabled {count} expired menu items")