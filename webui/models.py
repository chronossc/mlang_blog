# -*- coding: utf-8 -*-

import datetime
import re
import grappelli

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import ValidationError,slug_re,validate_slug
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.utils.translation import ugettext as _
from translations.models import TranslationModel
from translations.utils import get_lang
from externals.autoslug.fields import AutoSlugField

# The code here are partially based on django-articles models.
# Django articles are writed by Josh VanderLinden under a BSD license (until
# now (25/Jun/2010)) and this great work can be found at
# http://code.google.com/p/django-articles/

# markup options
MARKUP_HTML = 'h'
MARKUP_MARKDOWN = 'm'
MARKUP_REST = 'r'
MARKUP_TEXTILE = 't'
MARKUP_OPTIONS = getattr(settings, 'ARTICLE_MARKUP_OPTIONS', (
        (MARKUP_HTML, _('HTML/Plain Text')),
        (MARKUP_MARKDOWN, _('Markdown')),
        (MARKUP_REST, _('ReStructured Text')),
        (MARKUP_TEXTILE, _('Textile'))
    ))
MARKUP_DEFAULT = getattr(settings, 'ARTICLE_MARKUP_DEFAULT', MARKUP_HTML)
MARKUP_HELP = _("""Select the type of markup you are using in this article.
<ul>
<li><a href="http://daringfireball.net/projects/markdown/basics" target="_blank">Markdown Guide</a></li>
<li><a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">ReStructured Text Guide</a></li>
<li><a href="http://thresholdstate.com/articles/4312/the-textile-reference-manual" target="_blank">Textile Guide</a></li>
</ul>
""")
# regex used to find links in an article
LINK_RE = re.compile('<a.*?href="(.*?)".*?>(.*?)</a>', re.I|re.M)
TITLE_RE = re.compile('<title>(.*?)</title>', re.I|re.M)
TAG_RE = re.compile('[^a-z0-9\-_\+\:\.]?', re.I)

class Article(TranslationModel):

    title = models.CharField(max_length=250)

    slug = models.SlugField(max_length=250,help_text=_("If is one translation, slug automatically are forced to slug of base article."))

    author = models.ForeignKey(User)
    
    publish_date = models.DateTimeField(_("Publish(ed) at"),default=datetime.datetime.now,
        help_text=_('The date and time this article shall appear online.'))

    updated_date = models.DateTimeField(_("Last updated at"),auto_now=True,editable=False)

    expiration_date = models.DateTimeField(_("Expires(ed) at"),blank=True, null=True,
        help_text=_('Leave blank if the article does not expire.'))

    is_draft = models.BooleanField(mark_safe(_("This article<br /> is a draft?")),default=True,
        help_text=_("Mark it if this article still as draft."))

    is_active = models.BooleanField(mark_safe(_("This article<br /> is active?")),default=True)
    
    keywords = models.TextField(blank=True,
        help_text=_("If omitted, the keywords will be the same as the "\
            "article tags."))

    description = models.TextField(blank=True,
        help_text=_("If omitted, the description will be determined by the "\
            "first bit of the article's content."))

    markup = models.CharField(max_length=1, choices=MARKUP_OPTIONS,
        default=MARKUP_DEFAULT, help_text=MARKUP_HELP)

    content = models.TextField()

    rendered_content = models.TextField(editable=False)

    class Meta:
        cloneable_fields = ('slug',)
        unique_together = ('title','slug','source')
        ordering = ('tree',)

    def __unicode__(self):
        return u"<%s> %s" % (self.lang_id,truncate_words(self.title,8))

    def __init__(self, *args, **kwargs):
        """
        Make sure that we have some rendered content to use.
        """

        super(Article, self).__init__(*args, **kwargs)

        self._next = None
        self._previous = None
        self._teaser = None

        if self.id:
            # mark the article as inactive if it's expired and still active
            if self.expiration_date and\
                    self.expiration_date <= datetime.datetime.now() and\
                    self.is_active:
                self.is_active = False
                self.save()

            if not self.rendered_content or not len(self.rendered_content.strip()):
                self.save()

    def clean(self):
        super(Article,self).clean()

        # SLUG CHECKS
        # if is translation, get slug from source, not our own..
        # more than one url for same content (and Article url are composed by
        # slug) are very bad idea for SEO
        if self.source:
            # just do a validation on source slug and set it to self.slug
            if not re.search(slug_re,self.source.slug):
                raise ValidationError,_(u"The translation source doesn't "\
                    "have a valid slug. Edit translation source and fix "\
                    "the problem, than back to save this translation.")
            self.slug = self.source.slug
        else:
            # if isn't a source check if slug field is filed
            if not self.slug: self.slug = slugify(self.title)

            # invalid slug ... we get valid slug from forms, but and about from
            # models in tests, shell, views, etc... so we 'auto slugify' here
            if not re.search(slug_re,self.slug):
                self.slug = slugify(self.slug)

    def get_next_article(self):
        """Determines the next active article"""

        if not self._next:
            try:
                qs = Article.objects.active().exclude(id__exact=self.id)
                article = qs.filter(publish_date__gte=self.publish_date).order_by('publish_date')[0]
            except (Article.DoesNotExist, IndexError):
                article = None
            self._next = article

        return self._next

    def get_previous_article(self):
        """Determines the previous active article"""

        if not self._previous:
            try:
                qs = Article.objects.active().exclude(id__exact=self.id)
                article = qs.filter(publish_date__lte=self.publish_date).order_by('-publish_date')[0]
            except (Article.DoesNotExist, IndexError):
                article = None
            self._previous = article

        return self._previous

    @property
    def teaser(self):
        """
        Retrieve some part of the article or the article's description.
        """
        if not self._teaser:
            if len(self.description.strip()):
                text = self.description
            else:
                text = self.rendered_content

            words = text.split(' ')
            if len(words) > WORD_LIMIT:
                text = '%s...' % ' '.join(words[:WORD_LIMIT])
            self._teaser = text

        return self._teaser

    def gettitle(self):
        """
        returns idented article title, this method live in model because if live
        in admin class for this model we can't set links in admin ui
        """
        if self.source:
            return u"&nbsp;&nbsp;&nbsp;&nbsp;|- %s" % self.title
        else:
            return self.title
    gettitle.short_description = u"Title"
    gettitle.allow_tags = True
    gettitle.admin_order_field = 'title'
    
    #@models.permalink
    def get_absolute_url(self):
        return '/%s/' % self.slug
    get_absolute_url.short_description = u"URL"
    get_absolute_url.admin_order_field = 'slug'
