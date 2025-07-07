# Tiffin Service Platform

## Overview

A modern, responsive web platform for a Tiffin Service business built with Flask. The platform enables seamless interaction between administrators and customers, featuring daily menu management, location-based service verification, and order processing capabilities.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with configurable database backend
- **Authentication**: Flask-Login for session management
- **Architecture Pattern**: MVC (Model-View-Controller)
- **Security**: Password hashing with Werkzeug, CSRF protection, role-based access control

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### File Structure
```
/
├── app.py              # Application factory and configuration
├── main.py             # Application entry point
├── routes.py           # URL routing and view logic
├── models.py           # Database models
├── auth.py             # Authentication and authorization
├── location_utils.py   # Location-based service utilities
├── templates/          # HTML templates
├── static/            # Static assets (CSS, JS, images)
└── attached_assets/   # Project documentation
```

## Key Components

### Database Models
- **User**: Customer and admin user management with location data
- **MenuItem**: Daily menu items with pricing for full tiffin and roti-only options
- **Order**: Order management with status tracking and location verification

### Authentication System
- Role-based access control (admin/customer)
- Secure password hashing
- Session management with Flask-Login
- Admin-required decorator for protected routes

### Location Service
- GPS coordinate validation
- Service area verification (5km radius)
- Haversine formula for distance calculation
- Address to coordinate geocoding (placeholder implementation)

### Admin Panel Features
- Daily menu management (CRUD operations)
- Order approval/denial system
- Customer order tracking
- Service area management

### Customer Features
- User registration with location verification
- Daily menu browsing
- Order placement with quantity selection
- Full tiffin vs. roti-only options
- Order history and status tracking

## Data Flow

### User Registration Flow
1. Customer provides personal details and address
2. Location coordinates are obtained (GPS or geocoding)
3. Service area eligibility is verified (5km radius check)
4. Account is created if location is serviceable

### Order Placement Flow
1. Customer selects menu item from daily offerings
2. Chooses quantity and meal type (full/roti-only)
3. Delivery address is confirmed
4. Order is submitted for admin review
5. Admin approves/denies order
6. Customer receives status updates

### Menu Management Flow
1. Admin accesses menu management interface
2. Adds/updates daily menu items by date
3. Sets pricing for different meal options
4. Manages item availability status

## External Dependencies

### Required Environment Variables
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session secret key
- `ADMIN_EMAIL`: Default admin account email
- `ADMIN_PASSWORD`: Default admin account password
- `CENTRAL_LAT`: Service center latitude coordinate
- `CENTRAL_LNG`: Service center longitude coordinate
- `SERVICE_RADIUS_KM`: Maximum service radius in kilometers

### Third-Party Services
- **Geocoding API**: Placeholder implementation for address-to-coordinate conversion
- **Future Integrations**: WhatsApp notifications, payment gateways

### Frontend Libraries
- Bootstrap 5.3.0 (CDN)
- Font Awesome 6.4.0 (CDN)
- JavaScript Geolocation API

## Deployment Strategy

### Environment Setup
- Python 3.x runtime
- Flask development server (production requires WSGI server)
- Database initialization with table creation
- Admin user auto-creation on first run

### Security Considerations
- ProxyFix middleware for deployment behind reverse proxy
- Environment variable configuration for sensitive data
- Role-based access control implementation
- Secure password hashing with Werkzeug

### Scalability Features
- SQLAlchemy ORM for database abstraction
- Connection pooling configuration
- Modular component architecture
- Responsive design for multiple device types

### Development Features
- Debug mode configuration
- Hot reloading in development
- Comprehensive logging setup
- Error handling and user feedback

## Changelog
- July 07, 2025: Successfully migrated from Replit Agent to standard Replit environment
  - Fixed PostgreSQL database configuration and environment variables
  - Added embedded map functionality to order placement and profile pages
  - Implemented dynamic central coordinate management system for admin
  - Added Settings model with admin interface for configuring service area
  - Enhanced location services with GPS coordinate capture and serviceability verification
  - Fixed JavaScript errors and improved user experience for location-based features
- July 06, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.