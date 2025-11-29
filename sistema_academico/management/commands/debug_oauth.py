from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Debug OAuth configuration in detail'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n' + '='*70))
        self.stdout.write(self.style.WARNING('DETAILED OAuth Debug Information'))
        self.stdout.write(self.style.WARNING('='*70 + '\n'))

        # Check SITE_ID from settings
        self.stdout.write(self.style.HTTP_INFO('1. Settings Configuration:'))
        site_id = getattr(settings, 'SITE_ID', None)
        self.stdout.write(f'   SITE_ID in settings.py: {site_id}')

        # Check all sites
        self.stdout.write('\n' + self.style.HTTP_INFO('2. All Sites in Database:'))
        sites = Site.objects.all()
        if sites.exists():
            for site in sites:
                marker = ' ← CURRENT' if site.id == site_id else ''
                self.stdout.write(f'   • ID: {site.id}, Domain: {site.domain}, Name: {site.name}{marker}')
        else:
            self.stdout.write(self.style.ERROR('   ✗ NO SITES FOUND!'))
            self.stdout.write(self.style.WARNING('   → This is the problem! Creating one now...'))
            site = Site.objects.create(domain='localhost:8000', name='Sistema Academico')
            self.stdout.write(self.style.SUCCESS(f'   ✓ Created site: {site.domain} (ID: {site.id})'))

        # Check Social Apps
        self.stdout.write('\n' + self.style.HTTP_INFO('3. Social Applications:'))
        try:
            from allauth.socialaccount.models import SocialApp

            apps = SocialApp.objects.all()
            if apps.exists():
                for app in apps:
                    self.stdout.write(f'\n   Provider: {app.provider}')
                    self.stdout.write(f'   Name: {app.name}')
                    self.stdout.write(f'   Client ID: {app.client_id}')
                    self.stdout.write(f'   Has Secret: {"Yes" if app.secret else "No"}')

                    # Check sites for this app
                    app_sites = app.sites.all()
                    self.stdout.write(f'   Linked Sites ({app_sites.count()}):')
                    if app_sites.exists():
                        for s in app_sites:
                            self.stdout.write(self.style.SUCCESS(f'      ✓ {s.domain} (ID: {s.id})'))
                    else:
                        self.stdout.write(self.style.ERROR('      ✗ NO SITES LINKED!'))
                        self.stdout.write(self.style.WARNING('      → THIS IS THE PROBLEM!'))

                        # Auto-fix
                        current_site = Site.objects.get(id=site_id) if site_id else Site.objects.first()
                        if current_site:
                            app.sites.add(current_site)
                            self.stdout.write(self.style.SUCCESS(f'      ✓ AUTO-FIXED: Linked to {current_site.domain}'))
            else:
                self.stdout.write(self.style.ERROR('   ✗ NO SOCIAL APPLICATIONS FOUND!'))
                self.stdout.write(self.style.WARNING('   → You need to add OAuth credentials'))

        except ImportError:
            self.stdout.write(self.style.ERROR('   ✗ django-allauth not installed'))

        # Check how allauth will look up the app
        self.stdout.write('\n' + self.style.HTTP_INFO('4. How Allauth Looks Up Apps:'))
        try:
            from allauth.socialaccount.models import SocialApp

            current_site = Site.objects.get(id=site_id) if site_id else None
            if current_site:
                self.stdout.write(f'   Current site: {current_site.domain} (ID: {current_site.id})')

                # Try to get Google app for current site
                try:
                    google_app = SocialApp.objects.get(
                        provider='google',
                        sites__id=site_id
                    )
                    self.stdout.write(self.style.SUCCESS(f'   ✓ Google app found for site {site_id}'))
                    self.stdout.write(f'     Client ID: {google_app.client_id}')
                except SocialApp.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'   ✗ Google app NOT found for site {site_id}'))

                    # Check if Google app exists but not linked to this site
                    google_apps = SocialApp.objects.filter(provider='google')
                    if google_apps.exists():
                        self.stdout.write(self.style.WARNING('   → Google app exists but not linked to current site!'))
                        for app in google_apps:
                            self.stdout.write(f'     App "{app.name}" is linked to sites: {[s.domain for s in app.sites.all()]}')

                            # Auto-fix
                            if current_site not in app.sites.all():
                                app.sites.add(current_site)
                                self.stdout.write(self.style.SUCCESS(f'     ✓ AUTO-FIXED: Linked to {current_site.domain}'))
                    else:
                        self.stdout.write(self.style.ERROR('   → No Google app exists at all'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   Error: {e}'))

        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.HTTP_INFO('SUMMARY & RECOMMENDED ACTIONS:'))
        self.stdout.write('='*70)

        try:
            from allauth.socialaccount.models import SocialApp

            # Final check
            current_site = Site.objects.get(id=site_id) if site_id else Site.objects.first()
            try:
                google_app = SocialApp.objects.get(provider='google', sites__id=current_site.id)
                self.stdout.write(self.style.SUCCESS('\n✓ Everything looks good now!'))
                self.stdout.write(f'  Google OAuth is configured for: {current_site.domain}')
                self.stdout.write(f'  Client ID: {google_app.client_id}')
                self.stdout.write('\nYou can now test at: http://localhost:8000/login/')

            except SocialApp.DoesNotExist:
                self.stdout.write(self.style.ERROR('\n✗ Configuration still has issues!'))
                self.stdout.write('\nPlease do ONE of the following:')
                self.stdout.write('\n1. Use Django Admin (RECOMMENDED):')
                self.stdout.write('   • Go to: http://localhost:8000/admin/socialaccount/socialapp/')
                self.stdout.write('   • Edit the Google app')
                self.stdout.write('   • In "Sites" section, move your site to "Chosen sites"')
                self.stdout.write('   • Click SAVE')

                self.stdout.write('\n2. Delete and recreate:')
                self.stdout.write('   • python manage.py shell')
                self.stdout.write('   • Then run:')
                self.stdout.write('     from allauth.socialaccount.models import SocialApp')
                self.stdout.write('     SocialApp.objects.all().delete()')
                self.stdout.write('   • Then use: python manage.py add_google_oauth')

                self.stdout.write('\n3. Manual fix in shell:')
                self.stdout.write('   • python manage.py shell')
                self.stdout.write('   • Then run:')
                self.stdout.write('     from allauth.socialaccount.models import SocialApp')
                self.stdout.write('     from django.contrib.sites.models import Site')
                self.stdout.write(f'     app = SocialApp.objects.get(provider="google")')
                self.stdout.write(f'     site = Site.objects.get(id={current_site.id})')
                self.stdout.write('     app.sites.add(site)')
                self.stdout.write('     print("Fixed!")')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError during final check: {e}'))

        self.stdout.write('\n')
