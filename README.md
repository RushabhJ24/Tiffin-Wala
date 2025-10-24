# Tiffin Service Platform - Setup Instructions

## Overview
This is a Flask-based Tiffin Service Platform with user authentication, admin panel, location-based delivery validation, and PostgreSQL database integration.

## Prerequisites
- Python 3.11+
- PostgreSQL database
- Git (optional)

## Installation Steps

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd tiffin-service-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Copy dependencies.txt to requirements.txt
cp dependencies.txt requirements.txt

# Install all dependencies
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Install PostgreSQL if not already installed
# Create a new database
createdb tiffin_service

# Or using PostgreSQL command line:
psql -U postgres
CREATE DATABASE tiffin_service;
\q
```

### 5. Environment Configuration
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/tiffin_service
PGDATABASE=tiffin_service
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password

# Flask Configuration
SESSION_SECRET=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Admin Configuration
ADMIN_EMAIL=admin@tiffinservice.com
ADMIN_PASSWORD=admin123

# Location Configuration (Central point for 5km radius check)
CENTRAL_LAT=28.6139
CENTRAL_LNG=77.2090
SERVICE_RADIUS_KM=5
```

### 6. Initialize Database
```bash
# Run the application to create tables automatically
python main.py
```

### 7. Run the Application
```bash
# Development server
python main.py

# Or using Gunicorn for production
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Default Admin Access
- **Email:** admin@tiffinservice.com
- **Password:** admin123

## Application Structure
```
tiffin-service-platform/
├── app.py              # Application factory and configuration
├── main.py             # Application entry point
├── routes.py           # URL routing and view logic
├── models.py           # Database models
├── auth.py             # Authentication and authorization
├── location_utils.py   # Location-based service utilities
├── templates/          # HTML templates
├── static/            # Static assets (CSS, JS, images)
├── dependencies.txt   # Python dependencies
├── .env              # Environment variables
└── setup_instructions.md
```

## Features
- **User Registration & Login** with location verification
- **Admin Dashboard** for managing menu items and orders
- **Location-based Delivery** validation (5km radius)
- **Daily Menu Management** with breakfast/lunch/dinner options
- **Order Placement** with full tiffin or roti-only options
- **PostgreSQL Database** integration
- **Responsive Bootstrap UI** with dark theme
- **Location Services** for delivery area checking

## API Endpoints
- `POST /api/check-location` - Check if location is serviceable

## Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Verify database exists

### Location Services Not Working
1. Ensure browser allows location access
2. Check network connectivity
3. Verify API endpoint is accessible

### Admin User Not Created
1. Check logs for errors
2. Verify database connection
3. Manually create admin user if needed

## Production Deployment

### Environment Variables
Set these in production:
- `DATABASE_URL` - Production database URL
- `SESSION_SECRET` - Strong random secret
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`

### Security Considerations
- Change default admin password
- Use strong session secret
- Enable HTTPS
- Configure firewall rules
- Regular security updates

## Support
For issues or questions, please check the application logs and database connectivity first.

## 🤝 Contributing
Contributions are welcome!
Feel free to open issues and pull requests.

## 👨‍💻 Developer
Rushabh Jain
Software Developer & Data Analyst
📌 India
🔗 GitHub: https://github.com/RushabhJ24

## ⭐ If you like this project, don’t forget to star the repo!