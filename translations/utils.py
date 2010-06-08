from django.conf import settings
from django.core.cache import cache
from translations.models import Languages

def get_lang(lang):
    return Languages.objects.get_lang(lang)

