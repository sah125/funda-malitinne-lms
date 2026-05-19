# Funda Malitinne LMS

A comprehensive Learning Management System built with Django for managing courses, students, instructors, and learning progress.

## 🚀 Features

- **Multi-role System**: Student, Instructor, and Admin roles with distinct features
- **Course Management**: Create, organize, and manage courses with lessons
- **Interactive Learning**: Video lessons, documents, quizzes, and assignments
- **Assessment**: Automated and manual grading with detailed feedback
- **Progress Tracking**: Real-time progress monitoring and completion percentages
- **Certificates**: Automatic certificate generation upon course completion
- **Gamification**: Badge system and daily streak tracking
- **AI Features**: AI-powered course recommendations and admin assistant
- **Real-time Notifications**: User notifications for important events
- **Bulk Operations**: CSV import for course setup and enrollment
- **PDF Generation**: Generate certificates and reports as PDFs
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

## 🔧 Installation

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/funda_malitinne_system.git
   cd funda_malitinne_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create demo data**
   ```bash
   python manage.py create_demo_data
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

Access the application at `http://localhost:8000`

## 🐳 Docker Deployment

### Using Docker Compose

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

2. **Build and start services**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate --settings=lms.settings_production
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser --settings=lms.settings_production
   ```

5. **Collect static files**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput --settings=lms.settings_production
   ```

Access the application at `https://yourdomain.com`

## 📚 Project Structure

```
funda_malitinne_system/
├── core/                          # Main application
│   ├── models.py                 # Database models
│   ├── views.py                  # View functions
│   ├── forms.py                  # Django forms
│   ├── serializers.py            # DRF serializers
│   ├── permissions.py            # Custom permissions
│   ├── admin.py                  # Admin configuration
│   ├── ai_assistant.py           # AI features
│   ├── management/               # Management commands
│   │   └── commands/
│   │       └── create_demo_data.py
│   ├── migrations/               # Database migrations
│   └── tests.py                  # Unit tests
├── lms/                          # Project configuration
│   ├── settings.py              # Development settings
│   ├── settings_production.py   # Production settings
│   ├── celery.py                # Celery configuration
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
├── templates/                    # HTML templates
│   ├── base.html
│   ├── student_dashboard.html
│   ├── instructor_dashboard.html
│   ├── admin_dashboard.html
│   └── email/                   # Email templates
├── static/                       # Static files (CSS, JS, images)
├── media/                        # User-uploaded files
├── Dockerfile                    # Docker image configuration
├── docker-compose.yml            # Docker Compose configuration
├── nginx.conf                    # Nginx configuration
├── gunicorn_config.py           # Gunicorn configuration
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management script
└── README.md                     # This file
```

## 🔐 Security

- **Environment Variables**: Sensitive data stored in `.env` file
- **HTTPS**: SSL/TLS encryption enabled in production
- **CSRF Protection**: Django CSRF tokens on all forms
- **SQL Injection**: Parameterized queries via Django ORM
- **XSS Protection**: Template auto-escaping and security headers
- **Rate Limiting**: API rate limiting via nginx
- **Password Hashing**: PBKDF2 with SHA256 hashing
- **Security Headers**: HSTS, X-Frame-Options, CSP configured

## 📝 API Documentation

### Authentication Endpoints
- `POST /login/` - User login
- `POST /register/` - User registration
- `POST /logout/` - User logout
- `POST /forgot-password/` - Request password reset
- `POST /reset-password/<token>/` - Reset password

### Course Endpoints
- `GET /api/courses/` - List all courses
- `GET /api/courses/<id>/` - Get course details
- `POST /api/courses/` - Create course (Instructor)
- `PUT /api/courses/<id>/` - Update course
- `DELETE /api/courses/<id>/` - Delete course

### Student Endpoints
- `GET /student/` - Student dashboard
- `GET /course/<id>/` - View course
- `POST /enroll/<course_id>/` - Enroll in course
- `GET /certificates/` - View certificates

### Instructor Endpoints
- `GET /instructor/` - Instructor dashboard
- `POST /course/create/` - Create course
- `GET /course/<id>/manage/` - Manage course
- `POST /course/<id>/lesson/add/` - Add lesson

### Admin Endpoints
- `GET /admin/` - Admin dashboard
- `POST /admin/bulk-upload/` - Bulk user upload
- `GET /admin/users/` - Manage users

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run tests with coverage:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📧 Email Configuration

Update `.env` with your email settings:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🔄 Celery Tasks

Async tasks are handled by Celery:
- Send registration emails
- Send course enrollment notifications
- Send grade notifications
- Send announcement emails
- Update daily streaks
- Send assignment deadline reminders

Start Celery worker:
```bash
celery -A lms worker -l info
```

Start Celery beat scheduler:
```bash
celery -A lms beat -l info
```

## 📊 Database

The application uses PostgreSQL in production. Initial schema is created via Django migrations:

```bash
python manage.py migrate
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- AWS EC2
- Heroku
- DigitalOcean
- VPS with Nginx

## 📞 Support

For issues and questions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Contact: support@fundamalitinne.com

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Contributors

- Funda Malitinne Team

---

**Last Updated**: May 2026
