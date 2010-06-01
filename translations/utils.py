from django.conf import settings
from django.cache import cache
from translations.models import Languages

def get_languages(flush=False):


