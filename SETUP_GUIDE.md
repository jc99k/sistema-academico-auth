# Sistema Academico - Setup Guide

Complete Django academic management system with 2FA and social authentication.

## Features

- Custom User model with email authentication
- Role-based access control (RBAC)
- Two-Factor Authentication (2FA) with TOTP
- Backup codes for 2FA recovery
- Social login (Google, Facebook, GitHub)
- Clean Bootstrap 5 UI
- Django admin integration

## Quick Start

### 1. Install Dependencies

First, install the required packages:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install Django>=5.2.8
pip install pyotp qrcode[pil]
pip install django-allauth
```

### 2. Run Migrations

Create the database tables:

```bash
python manage.py migrate
```

### 3. Create Superuser

Create an admin account:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Email address
- First name
- Last name
- Password

### 4. Run Development Server

Start the server:

```bash
python manage.py runserver
```

### 5. Access the Application

- **Login Page**: http://localhost:8000/login/
- **Admin Panel**: http://localhost:8000/admin/
- **Dashboard**: http://localhost:8000/ (after login)

## Setting Up 2FA

### For Users

1. Login to your account
2. Go to Dashboard
3. Click "Enable 2FA" in the Security Settings card
4. Scan the QR code with your authenticator app:
   - Google Authenticator
   - Authy
   - Microsoft Authenticator
   - Any TOTP-compatible app
5. Enter the 6-digit code to verify
6. **Save your backup codes** in a safe place
7. Next time you login, you'll need to enter the 2FA code

### Testing 2FA

1. Logout from your account
2. Login with email and password
3. You'll be redirected to 2FA verification page
4. Enter the 6-digit code from your authenticator app
5. You'll be logged in successfully

## Setting Up Social Authentication

Social login requires OAuth credentials from each provider. See **SOCIAL_AUTH_SETUP.md** for detailed instructions.

### Quick Steps

1. Get OAuth credentials from:
   - [Google Cloud Console](https://console.cloud.google.com/)
   - [Facebook Developers](https://developers.facebook.com/)
   - [GitHub Settings](https://github.com/settings/developers)

2. Add credentials in Django Admin:
   - Go to http://localhost:8000/admin/
   - Navigate to **Social Applications**
   - Add each provider with Client ID and Secret

3. Test social login:
   - Go to login page
   - Click on a social login button
   - Authorize the application
   - You'll be logged in

## Working with Roles and Permissions

### Creating Roles

1. Go to Django Admin: http://localhost:8000/admin/
2. Navigate to **Roles**
3. Click **Add Role**
4. Enter role details:
   - Name: e.g., "Student", "Teacher", "Administrator"
   - Description: Brief description
   - Is Active: Check
5. Click **Save**

### Creating Permissions

1. In Django Admin, go to **Permissions**
2. Click **Add Permission**
3. Enter:
   - Name: e.g., "View Grades"
   - Codename: e.g., "view_grades" (no spaces)
   - Description: What this permission allows
4. Click **Save**

### Assigning Permissions to Roles

1. Edit a Role in Django Admin
2. In the **Permissions** section, select permissions
3. Use the arrow buttons to move permissions to "Chosen permissions"
4. Click **Save**

### Assigning Roles to Users

1. Edit a User in Django Admin
2. Select a **Role** from the dropdown
3. Optionally set student_id or employee_id
4. Click **Save**

## Project Structure

```
sistema-academico-auth/
├── my_site/                    # Django project settings
│   ├── settings.py            # Main settings
│   └── urls.py                # Root URL configuration
├── sistema_academico/          # Main app
│   ├── models.py              # User, Role, Permission models
│   ├── views.py               # Authentication views
│   ├── forms.py               # Login and 2FA forms
│   ├── adapters.py            # Social auth adapters
│   ├── admin.py               # Admin configuration
│   ├── urls.py                # App URL routes
│   └── templates/             # HTML templates
│       └── sistema_academico/
│           ├── base.html
│           ├── login.html
│           ├── dashboard.html
│           ├── setup_2fa.html
│           └── ...
├── requirements.txt           # Python dependencies
├── SOCIAL_AUTH_SETUP.md      # OAuth setup guide
└── SETUP_GUIDE.md            # This file
```

## User Model Fields

### Basic Information
- `email` - Primary authentication field
- `first_name` - User's first name
- `last_name` - User's last name

### Academic Fields
- `student_id` - For students (optional)
- `employee_id` - For faculty/staff (optional)

### Access Control
- `role` - Linked to Role model
- `is_active` - Account status
- `is_staff` - Django admin access
- `is_superuser` - Full permissions

### 2FA Fields
- `totp_secret` - TOTP secret key
- `is_2fa_enabled` - 2FA status
- `backup_codes` - Recovery codes (JSON)

### Timestamps
- `date_joined` - Account creation date
- `last_login` - Last login timestamp
- `updated_at` - Last update

## Common Tasks

### Disable 2FA for a User (Admin)

If a user loses access to their authenticator:

```python
python manage.py shell

from sistema_academico.models import User
user = User.objects.get(email='user@example.com')
user.disable_2fa()
```

### Create a Role with Permissions (Code)

```python
from sistema_academico.models import Role, Permission

# Create permissions
view_grades = Permission.objects.create(
    name='View Grades',
    codename='view_grades',
    description='Can view student grades'
)

edit_grades = Permission.objects.create(
    name='Edit Grades',
    codename='edit_grades',
    description='Can edit student grades'
)

# Create role
teacher_role = Role.objects.create(
    name='Teacher',
    description='Teaching staff with grade management access'
)

# Add permissions
teacher_role.permissions.add(view_grades, edit_grades)

# Assign to user
user = User.objects.get(email='teacher@example.com')
user.role = teacher_role
user.save()
```

### Check User Permissions (Code)

```python
from sistema_academico.models import User

user = User.objects.get(email='user@example.com')

# Check if user has permission
if user.has_role_permission('view_grades'):
    print("User can view grades")

# Get all permissions
permissions = user.get_all_permissions_codenames()
print(permissions)  # ['view_grades', 'edit_grades', ...]
```

## Security Considerations

1. **2FA Backup Codes**: Users should save backup codes securely
2. **Social Auth**: Never commit OAuth credentials to git
3. **Production**: Use environment variables for secrets
4. **HTTPS**: Always use HTTPS in production
5. **Email Verification**: Currently optional, consider making it required
6. **Password Policy**: Django's built-in validators are enabled
7. **Session Security**: Consider adding session timeout

## Development Tips

### Testing with Multiple Users

Create test users for different roles:

```bash
python manage.py shell

from sistema_academico.models import User, Role

# Create roles first in admin or shell
student_role = Role.objects.get(name='Student')
teacher_role = Role.objects.get(name='Teacher')

# Create test users
student = User.objects.create_user(
    email='student@test.com',
    password='testpass123',
    first_name='John',
    last_name='Doe',
    role=student_role,
    student_id='STU001'
)

teacher = User.objects.create_user(
    email='teacher@test.com',
    password='testpass123',
    first_name='Jane',
    last_name='Smith',
    role=teacher_role,
    employee_id='EMP001'
)
```

### Reset Database

If you need to start fresh:

```bash
# Delete database
rm db.sqlite3

# Delete migrations
rm sistema_academico/migrations/0*.py

# Create fresh migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser again
python manage.py createsuperuser
```

## Troubleshooting

### Issue: "No such table: sistema_academico_user"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Issue: "SITE_ID not found"
**Solution**: Create a site in Django admin or run:
```bash
python manage.py shell
from django.contrib.sites.models import Site
Site.objects.create(domain='localhost:8000', name='Sistema Academico')
```

### Issue: Social login not working
**Solution**:
1. Check OAuth credentials in Django admin
2. Verify callback URLs match exactly
3. See SOCIAL_AUTH_SETUP.md for detailed troubleshooting

### Issue: 2FA QR code not showing
**Solution**: Make sure qrcode and Pillow are installed:
```bash
pip install qrcode[pil] Pillow
```

## Next Steps

1. Customize the dashboard for your needs
2. Add more models (Courses, Grades, Attendance, etc.)
3. Implement email notifications
4. Add password reset functionality
5. Configure email backend for production
6. Deploy to production server

## Support

For questions or issues, refer to:
- Django Documentation: https://docs.djangoproject.com/
- Django Allauth: https://django-allauth.readthedocs.io/
- PyOTP: https://github.com/pyauth/pyotp
