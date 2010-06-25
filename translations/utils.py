from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe
from models import Languages

if hasattr(settings,'FLAGS_SIZE'):
    if settings.FLAG_SIZE not in (16,24,32,48):
        raise ValueError,"The settings.FLAGS_SIZE isn't one of valid sizes or"\
            " isn't a integer"
else:
    settings.FLAG_SIZE=16

if not hasattr(settings,'FLAGS_URL'):
    settings.FLAGS_URL=settings.MEDIA_URL+u'img/flags_iso'

def get_lang(lang):
    return Languages.objects.get_lang(lang)

def get_flag(lang,size=None):
    if size is None:
        size = settings.FLAG_SIZE
    if not hasattr(lang,'id'): # isn't a model instance
        # leave error happen if not exist
        lang = Languages.objects.get(language=lang)

    path = "%s/%s/%s.png" % (
        settings.FLAGS_URL,
        settings.FLAG_SIZE,
        lang.language.split('-',1)[-1]
    )

    country = lang.get_language_display()

    return u"""<img src="%s" alt="%s" /> &lt;%s&gt;""" % (path,country,lang.language)
