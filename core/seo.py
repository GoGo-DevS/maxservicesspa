from django.conf import settings
from django.templatetags.static import static


def absolute_static_url(path):
    return f"{settings.SITE_URL}{static(path)}"
