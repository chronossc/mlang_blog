# -*- coding: utf-8 -*-

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

    def get_flag(self,size=None):
        """
        Return flag using self.language.split('-')[1:], but this was WRONG!
        The right way is use a dict that links codes from ISO-3366-1
        (http://en.wikipedia.org/wiki/ISO_3166-1) to self.language (language
        lang code), so we need to provide methods that do the job on model too.
        """
        from translations.utils import get_flag
        if size:
            return get_flag(self,size)
        else:
            return get_flag(self)
    get_flag.allow_tags = True

    class Meta:
        verbose_name = _(u"Languages")
        verbose_name_plural = _(u"Languages")

# These Translation* classes are slightly based on Rafal Jońca code
# (http://1l.to/be9) and django-pluggable-model-i18n (http://1l.to/c11)
#
# The idea is to provide a extensible Model to use in translatable models.
class TranslationQuerySet(QuerySet):
    pass

class TranslationModelManager(models.Manager):

    def get_query_set(self):
        """
        Just use TranslationQuerySet for some future customization, just
        self.get_query_set().select_related('self') works here :)
        """
        return TranslationQuerySet(self.model,using=self._db).select_related('self')

    def get_lang(self,langs=None):
        """
        Filter translated objects in given language(s)
        """
        # transform in one list with current language to use as default language
        # note that if is same language of your object, it don't return
        # anything (in instance.translations.get_lang() if both are same lang)
        if not langs:
            langs = translation.get_language()

        if not getattr(langs,'__iter__',False):
            langs = [langs]

        # we set real langs because if not have 'en-us' in db, we return 'en',
        # if user search for 'en-us'
        real_langs = set()
        try:
            # setup de languages cache
            if not hasattr(self,'_languages_cache',):
                self._languages_cache = Languages.objects.all()

            for lang in langs:
                # if not exists let DoesNotExist error follow your way
                lang = self._languages_cache.get_lang(lang)
                real_langs.add(lang.language)

        except Languages.DoesNotExist:
            raise self.model.DoesNotExist,u"This language aren't found in database."

        # if any problem occurred, filter by lang ids 
        return self.get_query_set().filter(lang__in=real_langs)

    def dummy(self):
        pass


import django.db.models.options as modelbaseoptions
modelbaseoptions.DEFAULT_NAMES = modelbaseoptions.DEFAULT_NAMES + ('cloneable_fields',)

class TranslationModel(models.Model):

    source = models.ForeignKey('self',related_name='translations',null=True,blank=True)
    lang = models.ForeignKey('Languages',to_field='language',default=lambda:Languages.objects.get_lang(settings.LANGUAGE_CODE))
    tree = models.CharField(max_length=11,editable=False)

    objects = TranslationModelManager()

    __UNCLONEABLE_FIELDS = ('lang','id','tree')

    class Meta:
        abstract = True
        cloneable_fields = tuple()

    def __unicode__(self):
        raise NotImplementedError,u"You need to implement __unicode__ in %s.models.%s." % ( self._meta.app_label,self._meta.object_name )

    def _getCloneableFields(self):
        """
        Check if cloneable fields are in UNCLONEABLE_FIELDS, raise ValueError
        if in, return cloneable fields or False if no cloneable fields are set
        """

        _in = lambda k: k in self.__UNCLONEABLE_FIELDS

        if any(map(_in,self._meta.cloneable_fields)):
            raise ValueError,"Meta cloneable_fields doesn't accept %s fields. "\
                "Fix this to continue." % (
                    ' and '.join([
                        ', '.join(self.__UNCLONEABLE_FIELDS[:-1]),
                        self.__UNCLONEABLE_FIELDS[-1]
                    ]))

        return self._meta.cloneable_fields or False # [f1,f2,...] or False

    def clean(self):

        # clone fields ...
        if self.source:
            for f in self._getCloneableFields():
                setattr(self,f,getattr(self.source,f))

    def get_translations(self,langs=None):
        """
        Return translations of this object to given lang(s) or all of them
        """
        if langs and self.source:
            return self.source.translations.get_lang(langs)
        elif langs and not self.source:
            return self.translations.get_lang(langs)
        elif not langs and self.source:
            return self.source.translations.all()
        elif not langs and not self.source:
            return self.translations.all()
        else:
            raise ValueError,"Something that can't happen happened :P"

    def add_translation(self,lang,**kwargs):
        """
        Return a instance of this model with sent lang and fill fields in
        cloneable_fields meta option.
        """
        # args
        lang = Languages.objects.get_lang(lang)

        # we create a new instance of this object with kwargs to update
        # 'cloned' fields after and than save.
        newinstance = self.__class__(lang=lang,**kwargs)

        # the save calls newinstance.full_clean(), that calls self.clean() that
        # clone fields from source
        # We let raise any ValidationError
        newinstance.save()
        return newinstance

    def get_flag(self,size=None):
        return self.lang.get_flag(size)
    get_flag.allow_tags = True

    def save(self,*args,**kwargs):
        self.full_clean()
        super(TranslationModel,self).save(*args,**kwargs)
        # fix self.tree
        self.tree = "%s.%s" % (self.source_id or self.id,1 if self.source_id else 0)
        super(TranslationModel,self).save(*args,**kwargs)
        
