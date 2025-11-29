from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Check OAuth configuration status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('OAuth Configuration Check'))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))

        # Check Site configuration
        self.stdout.write(self.style.HTTP_INFO('1. Checking Sites Configuration...'))
        sites = Site.objects.all()
        if sites.exists():
            for site in sites:
                self.stdout.write(self.style.SUCCESS(f'   ✓ Site found: {site.domain} (ID: {site.id}, Name: {site.name})'))

            # Check SITE_ID
            site_id = getattr(settings, 'SITE_ID', None)
            if site_id:
                self.stdout.write(self.style.SUCCESS(f'   ✓ SITE_ID in settings: {site_id}'))
                try:
                    current_site = Site.objects.get(id=site_id)
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Current site: {current_site.domain}'))
                except Site.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'   ✗ SITE_ID {site_id} does not exist!'))
                    self.stdout.write(self.style.WARNING('   → Create a site or update SITE_ID in settings.py'))
            else:
                self.stdout.write(self.style.ERROR('   ✗ SITE_ID not found in settings'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ No sites found!'))
            self.stdout.write(self.style.WARNING('   → Run: python manage.py shell'))
            self.stdout.write(self.style.WARNING('   → Then: from django.contrib.sites.models import Site'))
            self.stdout.write(self.style.WARNING('   → Then: Site.objects.create(domain="localhost:8000", name="Sistema Academico")'))

        # Check Social Applications
        self.stdout.write(self.style.HTTP_INFO('\n2. Checking Social Applications...'))
        try:
            from allauth.socialaccount.models import SocialApp

            apps = SocialApp.objects.all()
            if apps.exists():
                for app in apps:
                    self.stdout.write(self.style.SUCCESS(f'\n   ✓ Provider: {app.provider}'))
                    self.stdout.write(f'     Name: {app.name}')
                    self.stdout.write(f'     Client ID: {app.client_id[:30]}...' if len(app.client_id) > 30 else f'     Client ID: {app.client_id}')
                    self.stdout.write(f'     Has Secret: {"Yes" if app.secret else "No"}')

                    # Check linked sites
                    app_sites = app.sites.all()
                    if app_sites.exists():
                        self.stdout.write(self.style.SUCCESS(f'     Sites: {", ".join([s.domain for s in app_sites])}'))
                    else:
                        self.stdout.write(self.style.ERROR('     ✗ No sites linked!'))
                        self.stdout.write(self.style.WARNING('     → Go to admin and link a site to this app'))
            else:
                self.stdout.write(self.style.ERROR('   ✗ No social applications configured!'))
                self.stdout.write(self.style.WARNING('   → Go to: http://localhost:8000/admin/socialaccount/socialapp/'))
                self.stdout.write(self.style.WARNING('   → Click "Add social application"'))
                self.stdout.write(self.style.WARNING('   → Configure Google, Facebook, or GitHub'))
        except ImportError:
            self.stdout.write(self.style.ERROR('   ✗ django-allauth not installed!'))
            self.stdout.write(self.style.WARNING('   → Run: pip install django-allauth'))

        # Check Authentication Backends
        self.stdout.write(self.style.HTTP_INFO('\n3. Checking Authentication Backends...'))
        backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        if backends:
            for backend in backends:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {backend}'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ No authentication backends configured'))

        # Check Installed Apps
        self.stdout.write(self.style.HTTP_INFO('\n4. Checking Installed Apps...'))
        required_apps = [
            'django.contrib.sites',
            'allauth',
            'allauth.account',
            'allauth.socialaccount',
        ]
        installed_apps = settings.INSTALLED_APPS

        for app in required_apps:
            if app in installed_apps:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {app}'))
            else:
                self.stdout.write(self.style.ERROR(f'   ✗ {app} not installed'))

        # Check provider apps
        providers_to_check = ['google', 'facebook', 'github']
        self.stdout.write(self.style.HTTP_INFO('\n5. Checking Provider Apps...'))
        for provider in providers_to_check:
            provider_app = f'allauth.socialaccount.providers.{provider}'
            if provider_app in installed_apps:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {provider.title()} provider'))
            else:
                self.stdout.write(self.style.WARNING(f'   - {provider.title()} provider not enabled'))

        # Summary and next steps
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('Summary'))
        self.stdout.write('='*60)

        all_good = True

        if not sites.exists():
            all_good = False
            self.stdout.write(self.style.ERROR('\n✗ Missing Site configuration'))
            self.stdout.write('  Fix: Create a Site in Django admin or via shell')

        try:
            from allauth.socialaccount.models import SocialApp
            if not SocialApp.objects.exists():
                all_good = False
                self.stdout.write(self.style.ERROR('\n✗ No Social Applications configured'))
                self.stdout.write('  Fix: Add OAuth credentials in Django admin')
                self.stdout.write('  See: QUICK_OAUTH_SETUP.md for instructions')
        except:
            pass

        if all_good:
            self.stdout.write(self.style.SUCCESS('\n✓ Configuration looks good!'))
            self.stdout.write('\nYou can now test social login at: http://localhost:8000/login/')
        else:
            self.stdout.write(self.style.WARNING('\nPlease fix the issues above before testing social login'))
            self.stdout.write('\nFor detailed setup instructions, see:')
            self.stdout.write('  - QUICK_OAUTH_SETUP.md (Quick Google setup)')
            self.stdout.write('  - SOCIAL_AUTH_SETUP.md (All providers)')

        self.stdout.write('\n')
