# OTU Found - Campus Lost & Found
A modern, comprehensive lost and found management platform built specifically for Ostim Teknik University (OTU) using Python and Django. The system enables students and staff to report lost items, register found items, make claims, and efficiently reunite people with their belongings securely on campus.

## Description
OTU Found is a full-stack web application designed to streamline the process of reporting, tracking, and claiming lost items within the university campus. Users can report lost belongings, register found items, and make claims through an intuitive interface. The platform features university-exclusive access control, a secure claims verification system, convenient pick-up point management, and comprehensive admin tools.

This project demonstrates a complete implementation of a university community service platform with email-restricted user authentication, item management, claim processing, and administrative oversight capabilities.


## Features
- University-exclusive authentication (restricted to `@ostimteknik.edu.tr` emails)
- Secure Email Verification system for new accounts
- Lost item reporting with detailed descriptions and images
- Found item registration with location and date tracking
- Pick-up Points integration (Campus Security, Student Affairs, Library)
- Claim system for matching lost and found items with proof of ownership
- Admin dashboard with comprehensive analytics and user management
- Category management for item organization
- Responsive design for mobile and desktop
- Secure password reset flows
- Soft delete/suspend functionality for user accounts

## Tech Stack
**Frontend:**
- HTML5
- CSS3 (Custom Styling)
- Bootstrap 5
- Bootstrap Icons

**Backend:**
- Python 3
- Django Web Framework
- Pillow (for image processing)

**Database:**
- SQLite (Default)

**Authentication & Security:**
- Django Sessions & CSRF Protection
- Custom Email-based Verification
- PBKDF2 (Django default password hashing)

**Development Tools:**
- Git
- pip

## User Roles
**User (Student/Staff):** Can register, verify email, login, post lost or found items, submit claims for found items, manage their posted items, and drop off found items at campus locations.
**Admin (Staff/Superuser):** Can access the dedicated Admin Dashboard, view platform statistics, moderate and delete items, suspend or activate user accounts, and resolve claims.

## Installation & Usage (Local)

```bash
# Clone the repository
git clone https://github.com/OTUfound/Campus-Lost-And-Found-Platform

# Navigate to the project directory
cd Campus-Lost-And-Found-Platform

# Set up a virtual environment (Recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install requirements directly
pip install Django>=4.2.0 Pillow>=10.0.0

# Run database migrations
python manage.py migrate

# Create a Superuser (Admin) account
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```
Open http://localhost:8000 in your browser.

## Project Structure
```text
Campus-Lost-And-Found-Platform/
├── items/                   # Main Django App (Core Features)
│   ├── migrations/          # Database migrations
│   ├── models.py            # Database schemas
│   ├── views.py             # Business logic & controllers
│   ├── forms.py             # Form validation logic
│   ├── backends.py          # Custom authentication backend
│   └── urls.py              # App routing
├── otufound/                # Django Project Settings
│   ├── settings.py          # Configuration
│   ├── urls.py              # Root routing
│   ├── views.py             # Homepage and static page views
│   ├── asgi.py              # ASGI entry point
│   └── wsgi.py              # WSGI entry point
├── templates/               # HTML Templates
│   ├── account/             # Auth pages (login, register, forgot password)
│   ├── admin_dashboard/     # Admin interface templates
│   ├── includes/            # Navbar, footer, and messages
│   └── items/               # Core item pages (post, detail, claims)
├── media/                   # User-uploaded files (Item images)
└── manage.py                # Django CLI tool
```

## Environment Variables
While you can run the app out of the box with defaults, you can configure the following environment variables in your deployment environment (or via `os.environ`):

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `True` or `False`
- `ALLOWED_HOSTS`: Comma-separated list of domains
- `EMAIL_HOST`: SMTP host for email verification
- `EMAIL_PORT`: SMTP port
- `EMAIL_HOST_USER`: Your SMTP email address
- `EMAIL_HOST_PASSWORD`: Your SMTP app password

## Main Routes
**Authentication**
- `GET/POST /login/` - Login user
- `GET/POST /register/` - Register user
- `GET/POST /forgot-password/` - Password recovery

**Items & Claims**
- `GET /` - Home landing page
- `GET /items/` - Browse Items
- `GET/POST /items/post/` - Create a new item
- `GET /items/<id>/` - View item details
- `GET/POST /items/<id>/claim/` - Submit a claim
- `GET/POST /claims/<id>/approve/` - Approve a claim (Owner only)

**Admin Dashboard**
- `GET /admin-dashboard/` - Overview statistics
- `GET /admin-dashboard/users/` - User management
- `GET /admin-dashboard/items/` - Item moderation

## Database Schema
The application uses SQLite natively via Django ORM. Key models include:

- **CustomUser**: Extended user model restricted to OTU emails.
- **EmailVerificationToken / PasswordResetToken**: Secure, time-sensitive tokens for auth flows.
- **LostFoundItem**: Stores item details, images, status, and drop-off locations.
- **Claim**: Stores proof of ownership and tracks claim status (pending, approved, rejected).

## Key Features Detail
**University-Exclusive Authentication**
- Users can only register using `@ostimteknik.edu.tr` email addresses, ensuring a safe, trusted community.

**Item Management & Drop-off Points**
- Users can post items they lost or found. If they find an item, they have the option to leave it at a designated Drop-off Location (Security, Library, Student Affairs), streamlining the return process without requiring face-to-face meetups.

**Claims System**
- If an item is kept by the finder, the owner must submit a claim with specific proof of ownership. The finder reviews the proof and can approve or reject the claim.

**Admin Dashboard**
- A dedicated, custom-built dashboard for university staff to oversee the platform, moderate content, and manage user access without needing backend server access.

## Security Features
- Built-in Django CSRF Protection
- Session-based authentication
- Password hashing with PBKDF2
- Strict email domain validation
- Route-level permissions (Staff-only access for dashboards)
- Soft delete functionality for user accounts

## Responsive Design
The application is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile devices (Smartphones)

## Deployment
The application is ready to be deployed on platforms like:
- **Hosting**: Render, Heroku, or DigitalOcean App Platform
- **Static/Media Files**: AWS S3 or Cloudinary
- **Database**: PostgreSQL (can easily swap out SQLite via settings)

