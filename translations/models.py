from django.db import models
from django.conf import settings
from django.conf import global_settings
from django.utils.translation import  ugettext as _
from django.utils import translation
from django.db.models.query import QuerySet

class LanguagesQuerySet(QuerySet):

    def get_lang(self,lang=None):
        """ 
        Return a language given locale or language. if a complete language
        not exist try to return a more general, ex: 'en' instead of 'en-us' if
        not exists 'en-us' but 'en'.
        """
        if not lang:
            raise AttributeError,u"You need to send a valid language or locale to get_lang"
        try:
            _lang = self.get(
                language=translation.trans_real.to_language(lang)
            )
        except self.model.DoesNotExist:
            # full lang not exist, check if we can get base lang
            base_lang = lambda x: x.split('-', 1)[0].split('_',1)[0]
            try:
                _lang = self.get(
                    language=translation.trans_real.to_language(base_lang(lang))
                )
            except self.model.DoesNotExist:
                # ooops, bad, we not found full or base language ... raise
                # DoesNotExist
                raise self.model.DoesNotExist("%s matching query does not exist." %\
                    ("Language code '%s' (and '%s')" % (lang,base_lang(lang))))
        return _lang

    def get_languages_tuple(self):
        """
        Return a tuple of languages like used in settings.LANGUAGES
        """
        def get_tuple(obj):
            return obj.language,obj.get_language_display()
        return tuple(map(get_tuple,self.order_by('language')))

class LanguagesManager(models.Manager):
    def get_query_set(self):
        return LanguagesQuerySet(self.model, using=self._db)
    
    def get_lang(self,lang=None):
        return self.get_query_set().get_lang(lang)

    def get_languages_tuple(self):
        return self.get_query_set().get_languages_tuple()


class Languages(models.Model):
    """
    Language codes, code is based on django.conf.global_settings.LANGUAGES
    Some use examples of this model:

    Add and use get_lang
    >>> Languages(language='pt-br').save()
    >>> Languages.objects.all()
    [<Languages: Brazilian Portuguese ( pt-br / pt_BR )>]
    >>> Languages.objects.get_lang('pt-br')
    <Languages: Brazilian Portuguese ( pt-br / pt_BR )>
    >>> Languages.objects.get_lang('pt-bR')
    <Languages: Brazilian Portuguese ( pt-br / pt_BR )>
    >>> Languages.objects.get_lang('pt_br')
    <Languages: Brazilian Portuguese ( pt-br / pt_BR )>
    >>> Languages.objects.get_lang('pt_BR')
    <Languages: Brazilian Portuguese ( pt-br / pt_BR )>
    
    Add and use get lang returning a base lang instead 'full' lang
    >>> Languages(language='en').save()
    >>> Languages.objects.get_lang('en')
    <Languages: English ( en / en )>
    >>> Languages.objects.get_lang('en_us')
    <Languages: English ( en / en )>
    >>> Languages.objects.get_lang('en-us')
    <Languages: English ( en / en )>
    
    Add and show get_languages_tuple without and with filters that can be used
    as settings.LANGUAGES
    >>> Languages(language='de').save()
    >>> Languages(language='es').save()
    >>> Languages(language='es-ar').save()
    >>> Languages.objects.get_languages_tuple()
    ((u'de', u'German'), (u'en', u'English'), (u'es', u'Spanish'), (u'es-ar', u'Argentinean Spanish'), (u'pt-br', u'Brazilian Portuguese'))
    >>> Languages.objects.exclude(language='es-ar').get_languages_tuple()
    ((u'de', u'German'), (u'en', u'English'), (u'es', u'Spanish'), (u'pt-br', u'Brazilian Portuguese'))
    >>> Languages.objects.filter(language__startswith='e').get_languages_tuple()
    ((u'en', u'English'), (u'es', u'Spanish'), (u'es-ar', u'Argentinean Spanish'))

    """
    language = models.CharField(
        max_length=5,
        choices=global_settings.LANGUAGES,
        unique=True)

    objects = LanguagesManager()

    def __unicode__(self):
        return "%s ( %s / %s )" % (self.get_language_display(),self.language,self.locale)

    def to_locale(self):
        return translation.to_locale(self.language)
    locale = property(to_locale)

    class Meta:
        verbose_name = _(u"Languages")
        verbose_name_plural = _(u"Languages")

class TranslationModelManager(models.Manager):

    def set_lang(self,lang=None):
        if not lang:
            lang = translation.get_language()
        return self.get_query_set().filter(lang=Languages.get_lang(lang))


class TranslationModel(models.Model):

    source = models.ForeignKey('self',related_name='translations',null=True,blank=True)
    lang = models.ForeignKey(Languages,to_field='language',default=settings.LANGUAGE_CODE)

    class Meta:
        abstract = True
