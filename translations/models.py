from django.db import models
from django.utils.translation import  ugettext as _

class Languages(models.Model):
    """
    Language codes, code is based on django.conf.global_settings.LANGUAGES
    """
    code = models.CharField(max_length=5)
    locale = models.CharField(max_length=5)
    label = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s ( %s / %s )" % (self.label,self.code,self.locale)

    class Meta:
        verbose_name = _(u"Languages")
        verbose_name_plural = _(u"Languages")
