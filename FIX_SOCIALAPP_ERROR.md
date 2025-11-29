# Fix: SocialApp.DoesNotExist Error

## What This Error Means

The error `allauth.socialaccount.models.SocialApp.DoesNotExist` means that:
- Django-allauth is installed correctly ✓
- But Google OAuth credentials haven't been added to the database yet ✗

## Solution: Add OAuth Credentials via Django Admin

### Option 1: Use Django Admin (Recommended - Easiest)

#### Step 1: Access Django Admin

1. Make sure your server is running:
   ```bash
   python manage.py runserver
   ```

2. Open your browser and go to:
   ```
   http://localhost:8000/admin/
   ```

3. Login with your superuser credentials

#### Step 2: Add Google Credentials

1. In the admin panel, find the **"SOCIAL ACCOUNTS"** section (scroll down)

2. Click on **"Social applications"**

3. Click the **"ADD SOCIAL APPLICATION"** button (top right)

4. Fill in the form:
   - **Provider**: Select `Google` from dropdown
   - **Name**: Type `Google` (or any name you want)
   - **Client id**: `PASTE_YOUR_GOOGLE_CLIENT_ID_HERE`
   - **Secret key**: `PASTE_YOUR_GOOGLE_CLIENT_SECRET_HERE`
   - **Key**: Leave empty
   - **Sites**:
     - Find "example.com" or "localhost:8000" in "Available sites"
     - Select it and click the **→** arrow to move it to "Chosen sites"

5. Click **"SAVE"** at the bottom

#### Step 3: Test

1. Go to: http://localhost:8000/login/
2. Click "Continue with Google"
3. Should work now!

---

## Don't Have Google OAuth Credentials Yet?

### Quick Google OAuth Setup (5 minutes)

#### 1. Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

#### 2. Create a New Project
- Click the project dropdown (top left, next to "Google Cloud")
- Click **"NEW PROJECT"**
- Project name: `Sistema Academico`
- Click **"CREATE"**
- Wait for project creation, then select it

#### 3. Configure OAuth Consent Screen
- From the left menu: **APIs & Services** → **OAuth consent screen**
- User Type: Select **"External"**
- Click **"CREATE"**
- Fill in:
  - **App name**: `Sistema Academico`
  - **User support email**: Select your email from dropdown
  - **Developer contact information**: Enter your email
- Click **"SAVE AND CONTINUE"**
- **Scopes**: Click **"SAVE AND CONTINUE"** (skip this step)
- **Test users**:
  - Click **"+ ADD USERS"**
  - Enter: `duenas01@gmail.com`
  - Click **"ADD"**
  - Click **"SAVE AND CONTINUE"**
- **Summary**: Click **"BACK TO DASHBOARD"**

#### 4. Create OAuth Client ID
- From the left menu: **APIs & Services** → **Credentials**
- Click **"+ CREATE CREDENTIALS"** (top)
- Select **"OAuth client ID"**
- Application type: **"Web application"**
- Name: `Sistema Academico Web`
- **Authorized JavaScript origins**:
  - Click **"+ ADD URI"**
  - Add: `http://localhost:8000`
- **Authorized redirect URIs**:
  - Click **"+ ADD URI"**
  - Add: `http://localhost:8000/accounts/google/login/callback/`
  - ⚠️ **IMPORTANT**: Include the trailing slash!
- Click **"CREATE"**

#### 5. Copy Your Credentials
A popup will appear with your credentials:
- **Client ID**: Something like `123456789.apps.googleusercontent.com`
- **Client Secret**: Something like `GOCSPX-abc123xyz...`

**Copy both** and keep them handy!

---

### Option 2: Add via Django Shell (Advanced)

If you prefer using the command line:

```bash
python manage.py shell
```

Then paste this code (replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET):

```python
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Get or create the site
site = Site.objects.get_or_create(
    domain='localhost:8000',
    defaults={'name': 'Sistema Academico'}
)[0]

# Create Google social app
google_app = SocialApp.objects.create(
    provider='google',
    name='Google',
    client_id='YOUR_CLIENT_ID_HERE',  # Replace this
    secret='YOUR_CLIENT_SECRET_HERE',  # Replace this
)

# Link to site
google_app.sites.add(site)

print("✓ Google OAuth configured successfully!")
print(f"  Client ID: {google_app.client_id}")
print(f"  Linked to site: {site.domain}")
```

---

## Verify Everything is Set Up

Run this command to check your configuration:

```bash
python manage.py check_oauth
```

You should see:
- ✓ Site found
- ✓ Provider: google
- ✓ Has Secret: Yes
- ✓ Sites: localhost:8000

---

## Common Issues

### Issue: "Site matching query does not exist"

**Fix**: Create a site first

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
Site.objects.create(domain='localhost:8000', name='Sistema Academico')
```

### Issue: Still getting SocialApp.DoesNotExist after adding in admin

**Fix**: Restart your Django server

```bash
# Press Ctrl+C to stop the server
# Then start it again:
python manage.py runserver
```

### Issue: Can't find "Social applications" in admin

**Fix**: Make sure allauth is in INSTALLED_APPS and migrations are run

```bash
python manage.py migrate
python manage.py runserver
```

---

## Complete Checklist

Before testing Google login:

- [ ] Created Google Cloud project
- [ ] Configured OAuth consent screen
- [ ] Added yourself as test user (duenas01@gmail.com)
- [ ] Created OAuth client ID
- [ ] Added redirect URI: `http://localhost:8000/accounts/google/login/callback/`
- [ ] Copied Client ID and Secret
- [ ] Logged into Django admin at http://localhost:8000/admin/
- [ ] Added Social Application for Google
- [ ] Pasted Client ID and Secret
- [ ] Linked the site in "Chosen sites"
- [ ] Saved the Social Application
- [ ] Ran `python manage.py check_oauth` successfully
- [ ] Restarted Django server

---

## Test Your Setup

1. **Check configuration**:
   ```bash
   python manage.py check_oauth
   ```

2. **Visit login page**:
   ```
   http://localhost:8000/login/
   ```

3. **Click "Continue with Google"**

4. **You should see**:
   - Google login page
   - App name: "Sistema Academico"
   - Request to access your email and profile

5. **Authorize the app**

6. **You should be**:
   - Redirected back to your app
   - Logged in automatically
   - See your dashboard

---

## Still Having Issues?

Run the diagnostic command and share the output:

```bash
python manage.py check_oauth
```

This will tell you exactly what's missing!
