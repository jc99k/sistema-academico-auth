# Social Authentication Setup Guide

This guide will help you configure Google, Facebook, and GitHub OAuth authentication for the Sistema Academico application.

## Prerequisites

Before setting up social authentication, make sure you have:
1. Installed `django-allauth` package
2. Run migrations: `python manage.py migrate`
3. Created a superuser account

## Installation

Install the required package:
```bash
pip install django-allauth
```

## Configuration Steps

### 1. Run Migrations

After installing django-allauth, run migrations to create the necessary database tables:

```bash
python manage.py migrate
```

### 2. Configure OAuth Providers

You need to obtain OAuth credentials from each provider and add them to your Django admin panel.

---

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Click on the project name to open it

### Step 2: Enable Google+ API

1. Navigate to **APIs & Services** > **Library**
2. Search for "Google+ API" (or "Google Identity")
3. Click **Enable**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: Sistema Academico
   - User support email: Your email
   - Developer contact: Your email
4. Application type: **Web application**
5. Name: Sistema Academico
6. Authorized JavaScript origins:
   - `http://localhost:8000`
   - `http://127.0.0.1:8000`
   - Add your production domain when ready
7. Authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - Add production callback URL when ready
8. Click **Create**
9. Copy the **Client ID** and **Client Secret**

### Step 4: Add to Django Admin

1. Start your Django server: `python manage.py runserver`
2. Go to `http://localhost:8000/admin/`
3. Navigate to **Social applications**
4. Click **Add social application**
5. Fill in:
   - Provider: **Google**
   - Name: Google
   - Client id: [Your Google Client ID]
   - Secret key: [Your Google Client Secret]
   - Sites: Select your site (usually "example.com")
6. Click **Save**

---

## Facebook OAuth Setup

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** > **Create App**
3. Select **Consumer** as the app type
4. Fill in:
   - App name: Sistema Academico
   - App contact email: Your email
5. Click **Create App**

### Step 2: Add Facebook Login

1. In your app dashboard, find **Facebook Login** and click **Set Up**
2. Select **Web** platform
3. Enter Site URL: `http://localhost:8000`
4. Click **Save** and **Continue**

### Step 3: Configure OAuth Settings

1. Go to **Facebook Login** > **Settings**
2. Add Valid OAuth Redirect URIs:
   - `http://localhost:8000/accounts/facebook/login/callback/`
   - `http://127.0.0.1:8000/accounts/facebook/login/callback/`
3. Click **Save Changes**

### Step 4: Get App Credentials

1. Go to **Settings** > **Basic**
2. Copy your **App ID** and **App Secret**

### Step 5: Add to Django Admin

1. Go to `http://localhost:8000/admin/socialaccount/socialapp/`
2. Click **Add social application**
3. Fill in:
   - Provider: **Facebook**
   - Name: Facebook
   - Client id: [Your Facebook App ID]
   - Secret key: [Your Facebook App Secret]
   - Sites: Select your site
4. Click **Save**

---

## GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **OAuth Apps** > **New OAuth App**
3. Fill in:
   - Application name: Sistema Academico
   - Homepage URL: `http://localhost:8000`
   - Authorization callback URL: `http://localhost:8000/accounts/github/login/callback/`
4. Click **Register application**

### Step 2: Get Credentials

1. Copy the **Client ID**
2. Click **Generate a new client secret**
3. Copy the **Client Secret** (you won't be able to see it again)

### Step 3: Add to Django Admin

1. Go to `http://localhost:8000/admin/socialaccount/socialapp/`
2. Click **Add social application**
3. Fill in:
   - Provider: **GitHub**
   - Name: GitHub
   - Client id: [Your GitHub Client ID]
   - Secret key: [Your GitHub Client Secret]
   - Sites: Select your site
4. Click **Save**

---

## Testing Social Login

### Test the Login Flow

1. Start your server: `python manage.py runserver`
2. Go to `http://localhost:8000/login/`
3. Click on any social login button (Google, Facebook, or GitHub)
4. Authorize the application
5. You should be redirected back and logged in

### Troubleshooting

**Issue: "Redirect URI mismatch"**
- Make sure the callback URL in your OAuth provider settings exactly matches:
  - Google: `http://localhost:8000/accounts/google/login/callback/`
  - Facebook: `http://localhost:8000/accounts/facebook/login/callback/`
  - GitHub: `http://localhost:8000/accounts/github/login/callback/`

**Issue: "Site matching query does not exist"**
- Go to Django admin: `http://localhost:8000/admin/sites/site/`
- Make sure a site exists with domain `localhost:8000` or `example.com`
- The SITE_ID in settings.py should match the site's ID

**Issue: Social account not showing up**
- Make sure the social application is linked to a site in Django admin
- Check that the provider name matches exactly (case-sensitive)

---

## Production Deployment

When deploying to production:

1. Update OAuth redirect URIs in each provider:
   - Replace `localhost:8000` with your production domain
   - Use HTTPS URLs: `https://yourdomain.com/accounts/PROVIDER/login/callback/`

2. Update Django settings:
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS` with your domain
   - Use environment variables for OAuth credentials instead of hardcoding

3. Update Site in Django admin:
   - Change domain from `example.com` to your actual domain

4. Consider using environment variables for OAuth credentials:
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        }
    },
    # ... other providers
}
```

---

## Security Best Practices

1. **Never commit OAuth credentials** to version control
2. Use **environment variables** for sensitive data in production
3. Enable **HTTPS** in production
4. Regularly rotate **client secrets**
5. Implement **rate limiting** on login endpoints
6. Review OAuth permissions and only request what you need
7. Keep **django-allauth** updated to the latest version

---

## Additional Features

### Connecting Multiple Social Accounts

Users can connect multiple social accounts to their profile:
1. Login to the dashboard
2. Go to "Connected Accounts" section
3. Click "Connect" next to any provider
4. Authorize the connection

### Disconnecting Social Accounts

Users can disconnect social accounts:
1. Go to dashboard
2. Click "Disconnect" next to the connected account
3. Confirm the action

---

## Support

For issues or questions:
- Django Allauth Documentation: https://django-allauth.readthedocs.io/
- Google OAuth: https://developers.google.com/identity/protocols/oauth2
- Facebook Login: https://developers.facebook.com/docs/facebook-login
- GitHub OAuth: https://docs.github.com/en/developers/apps/building-oauth-apps
