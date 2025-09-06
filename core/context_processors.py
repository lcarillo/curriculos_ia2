from .models import SiteSettings

def theme(request):
    """Context processor para configurações de tema"""
    return {
        'site_settings': SiteSettings.objects.first() or SiteSettings(),
    }