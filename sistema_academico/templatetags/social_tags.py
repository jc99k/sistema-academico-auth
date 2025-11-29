from django import template
from allauth.socialaccount.models import SocialApp

register = template.Library()


@register.simple_tag(takes_context=True)
def provider_available(context, provider_id):
    """
    Check if a social provider is configured and available.
    Returns True if the provider has a SocialApp configured, False otherwise.
    """
    request = context.get('request')
    if not request:
        return False

    try:
        from django.contrib.sites.models import Site
        from django.conf import settings

        site_id = getattr(settings, 'SITE_ID', None)
        if not site_id:
            return False

        # Check if the provider app exists for current site
        SocialApp.objects.get(
            provider=provider_id,
            sites__id=site_id
        )
        return True
    except SocialApp.DoesNotExist:
        return False
    except Exception:
        return False
