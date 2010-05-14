from django.db import models

class Languages(models.Model):
    """
    Language codes, code is based on django.conf.global_settings.LANGUAGES
    """
    code = models.CharField(max_length=5)
    locale = models.CharField(max_length=5)
    label = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s ( %s / %s )" % (self.label,self.code,self.locale)
