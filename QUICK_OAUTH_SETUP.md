# Quick OAuth Setup - Fix "Missing client_id" Error

If you're getting the **"Missing required parameter: client_id"** error, follow these steps:

## Step 1: Verify Django Site is Configured

1. Go to Django admin: `http://localhost:8000/admin/`
2. Navigate to **Sites** → **Sites**
3. Check if a site exists. If not, create one:
   - Domain name: `localhost:8000`
   - Display name: `Sistema Academico`
4. Note the **ID** (usually 1)
5. Make sure `SITE_ID = 1` in your settings.py matches this ID

## Step 2: Get Google OAuth Credentials

### Quick Google Setup (5 minutes)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Login with your Google account

2. **Create a Project**
   - Click "Select a project" → "New Project"
   - Name: `Sistema Academico`
   - Click "Create"

3. **Configure OAuth Consent Screen**
   - Go to: **APIs & Services** → **OAuth consent screen**
   - User Type: **External**
   - Click **Create**
   - Fill in:
     - App name: `Sistema Academico`
     - User support email: Your email
     - Developer contact: Your email
   - Click **Save and Continue**
   - Skip Scopes (click **Save and Continue**)
   - Add test users: Add your email (duenas01@gmail.com)
   - Click **Save and Continue**

4. **Create OAuth Credentials**
   - Go to: **APIs & Services** → **Credentials**
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Application type: **Web application**
   - Name: `Sistema Academico Web Client`
   - **Authorized JavaScript origins:**
     - Click **+ ADD URI**
     - Add: `http://localhost:8000`
     - Add: `http://127.0.0.1:8000`
   - **Authorized redirect URIs:**
     - Click **+ ADD URI**
     - Add: `http://localhost:8000/accounts/google/login/callback/`
     - Add: `http://127.0.0.1:8000/accounts/google/login/callback/`
   - Click **CREATE**
   - **COPY** both:
     - Client ID (looks like: xxxxx.apps.googleusercontent.com)
     - Client Secret

## Step 3: Add Credentials to Django Admin

1. **Go to Django Admin**
   - Visit: `http://localhost:8000/admin/`
   - Login with your superuser account

2. **Navigate to Social Applications**
   - Find: **Social accounts** → **Social applications**
   - Click **Add social application** (top right)

3. **Fill in the Form**
   - **Provider**: Select `Google` from dropdown
   - **Name**: `Google`
   - **Client id**: Paste your Google Client ID
   - **Secret key**: Paste your Google Client Secret
   - **Key**: Leave empty
   - **Sites**:
     - In the "Available sites" box, find your site (localhost:8000)
     - Click it, then click the arrow (→) to move it to "Chosen sites"
   - Click **SAVE**

## Step 4: Test Google Login

1. **Logout** from Django admin
2. Go to: `http://localhost:8000/login/`
3. Click **Continue with Google**
4. Select your Google account (duenas01@gmail.com)
5. If prompted, click **Continue** to authorize
6. You should be redirected back and logged in!

## Troubleshooting

### Error: "Access blocked: Authorization Error"
**Solution**: Make sure you added your email as a test user in the OAuth consent screen

### Error: "redirect_uri_mismatch"
**Solution**: The callback URL must match exactly:
- `http://localhost:8000/accounts/google/login/callback/`
- Check for trailing slash, http vs https, etc.

### Error: "Site matching query does not exist"
**Solution**:
```bash
python manage.py shell
```
```python
from django.contrib.sites.models import Site
Site.objects.all()  # Check existing sites
# If empty, create one:
Site.objects.create(domain='localhost:8000', name='Sistema Academico')
```

### Error: Still getting "Missing client_id"
**Solution**:
1. Check that Social Application exists in admin
2. Verify the site is linked to the Social Application
3. Restart the Django server: `python manage.py runserver`

### How to Check Current Configuration

Run this in Django shell:
```bash
python manage.py shell
```
```python
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Check sites
print("Sites:", Site.objects.all())

# Check social apps
for app in SocialApp.objects.all():
    print(f"\nProvider: {app.provider}")
    print(f"Name: {app.name}")
    print(f"Client ID: {app.client_id[:20]}...")
    print(f"Sites: {list(app.sites.all())}")
```

## Visual Guide

### Where to find things in Google Cloud Console:

1. **OAuth consent screen**:
   - Left menu → APIs & Services → OAuth consent screen

2. **Credentials**:
   - Left menu → APIs & Services → Credentials

3. **Create OAuth client ID**:
   - On Credentials page → + CREATE CREDENTIALS → OAuth client ID

### Important URLs to Remember:

- **Google OAuth Callback**: `http://localhost:8000/accounts/google/login/callback/`
- **Facebook OAuth Callback**: `http://localhost:8000/accounts/facebook/login/callback/`
- **GitHub OAuth Callback**: `http://localhost:8000/accounts/github/login/callback/`

## Common Mistakes

❌ **Wrong callback URL**: `http://localhost:8000/accounts/google/login/` (missing `/callback/`)
✅ **Correct callback URL**: `http://localhost:8000/accounts/google/login/callback/`

❌ **Using HTTPS locally**: `https://localhost:8000/...`
✅ **Use HTTP locally**: `http://localhost:8000/...`

❌ **Not adding site to Social Application** in Django admin
✅ **Always link the site** in the Social Application form

❌ **Not adding test users** in OAuth consent screen
✅ **Add your email** as a test user while app is in testing mode

## Quick Checklist

Before testing Google login, verify:

- [ ] Created Google Cloud project
- [ ] Configured OAuth consent screen
- [ ] Added your email as test user
- [ ] Created OAuth client ID with correct redirect URI
- [ ] Copied Client ID and Secret
- [ ] Created Site in Django admin (localhost:8000)
- [ ] Created Social Application in Django admin
- [ ] Selected "Google" as provider
- [ ] Pasted Client ID and Secret
- [ ] Linked the site to Social Application
- [ ] Saved the Social Application
- [ ] Restarted Django server

## Need Help?

If you're still stuck:

1. Check Django logs when clicking "Continue with Google"
2. Check browser console for errors
3. Verify all URLs have no typos
4. Make sure you're using the same domain (localhost vs 127.0.0.1)

## Once It's Working

After Google login works:

- You can add Facebook and GitHub the same way
- See `SOCIAL_AUTH_SETUP.md` for detailed instructions for all providers
- Users can connect multiple social accounts from dashboard
- Social accounts auto-link by email address
