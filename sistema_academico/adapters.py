from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter to customize allauth behavior
    """

    def get_login_redirect_url(self, request):
        """
        Redirect to dashboard after login
        """
        return reverse('dashboard')

    def save_user(self, request, user, form, commit=True):
        """
        Save user and set initial fields
        """
        user = super().save_user(request, user, form, commit=False)

        # Additional custom logic can go here
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for social login
    """

    def pre_social_login(self, request, sociallogin):
        """
        Called after a successful social login, before the login is actually processed.
        We use this to check if the user already exists.
        """
        # If the user already exists, connect the social account to the existing user
        if sociallogin.is_existing:
            return

        # Try to find existing user by email
        try:
            email = sociallogin.account.extra_data.get('email', '').lower()
            if email:
                from .models import User
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from social login
        """
        user = super().populate_user(request, sociallogin, data)

        # Extract additional data from the social provider
        if not user.first_name and 'first_name' in data:
            user.first_name = data.get('first_name', '')

        if not user.last_name and 'last_name' in data:
            user.last_name = data.get('last_name', '')

        # Handle 'name' field if first_name and last_name are not provided
        if not user.first_name and not user.last_name and 'name' in data:
            name_parts = data.get('name', '').split(' ', 1)
            user.first_name = name_parts[0] if len(name_parts) > 0 else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Redirect after connecting a social account
        """
        return reverse('dashboard')

    def save_user(self, request, sociallogin, form=None):
        """
        Save the user after social login
        """
        user = super().save_user(request, sociallogin, form)

        # Additional custom logic after user creation via social login
        # For example, you could assign a default role here

        return user
