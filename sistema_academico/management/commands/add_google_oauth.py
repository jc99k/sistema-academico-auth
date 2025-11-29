from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Interactive command to add Google OAuth credentials'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('Google OAuth Setup Wizard'))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))

        # Check if Google app already exists
        if SocialApp.objects.filter(provider='google').exists():
            self.stdout.write(self.style.WARNING('⚠️  Google OAuth is already configured!'))
            existing = SocialApp.objects.get(provider='google')
            self.stdout.write(f'\n   Current Client ID: {existing.client_id[:30]}...')

            overwrite = input('\n   Do you want to update it? (yes/no): ').lower()
            if overwrite != 'yes':
                self.stdout.write('\nExiting without changes.\n')
                return
            else:
                existing.delete()
                self.stdout.write(self.style.SUCCESS('   Deleted existing configuration.\n'))

        # Get or create site
        self.stdout.write(self.style.HTTP_INFO('Step 1: Setting up Site...'))
        site, created = Site.objects.get_or_create(
            domain='localhost:8000',
            defaults={'name': 'Sistema Academico'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'   ✓ Created site: {site.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ Using existing site: {site.domain}'))

        # Get credentials from user
        self.stdout.write('\n' + self.style.HTTP_INFO('Step 2: Enter Google OAuth Credentials'))
        self.stdout.write('\nIf you don\'t have credentials yet, follow these steps:')
        self.stdout.write('1. Go to: https://console.cloud.google.com/')
        self.stdout.write('2. Create a project (or select existing)')
        self.stdout.write('3. Go to: APIs & Services → Credentials')
        self.stdout.write('4. Create OAuth client ID (Web application)')
        self.stdout.write('5. Add redirect URI: http://localhost:8000/accounts/google/login/callback/')
        self.stdout.write('6. Copy the Client ID and Secret\n')

        client_id = input('Enter Google Client ID (or "cancel" to exit): ').strip()
        if client_id.lower() == 'cancel':
            self.stdout.write('\nExiting without changes.\n')
            return

        if not client_id:
            self.stdout.write(self.style.ERROR('\n✗ Client ID cannot be empty!'))
            self.stdout.write('Exiting without changes.\n')
            return

        client_secret = input('Enter Google Client Secret (or "cancel" to exit): ').strip()
        if client_secret.lower() == 'cancel':
            self.stdout.write('\nExiting without changes.\n')
            return

        if not client_secret:
            self.stdout.write(self.style.ERROR('\n✗ Client Secret cannot be empty!'))
            self.stdout.write('Exiting without changes.\n')
            return

        # Create social app
        self.stdout.write('\n' + self.style.HTTP_INFO('Step 3: Creating Social Application...'))
        try:
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=client_id,
                secret=client_secret,
            )
            google_app.sites.add(site)

            self.stdout.write(self.style.SUCCESS('\n✓ Google OAuth configured successfully!\n'))
            self.stdout.write('Configuration details:')
            self.stdout.write(f'  Provider: Google')
            self.stdout.write(f'  Client ID: {client_id[:30]}...')
            self.stdout.write(f'  Linked to site: {site.domain}')
            self.stdout.write('\nYou can now test Google login at: http://localhost:8000/login/')
            self.stdout.write('\n')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error creating Social Application: {e}'))
            self.stdout.write('\nPlease check your credentials and try again.\n')
