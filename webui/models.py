from django.db import models
from django.contrib.auth.models import User
from translations.models import TranslationModel
from django.utils.translation import  ugettext as _

#class BObjectType(models.Model):
#    """
#    object types and data types, ex:
#    post, page, title, date, etc
#    """
#    name = models.CharField(max_length=20)
#    slug = models.SlugField()
#
#    def __unicode__(self):
#        return u"%s" % self.name
#
#    class Meta:
#        verbose_name = _(u"Blog Object types")
#        verbose_name_plural = _(u"Blog Object types")
#
#class BObject(models.Model):
#    """
#    this is generic object model.
#    """
#    objid = models.IntegerField()
#    type = models.ForeignKey(BObjectType,related_name='object_type')
#    lang = models.ForeignKey(Languages)
#    property = models.ForeignKey(BObjectType,related_name='property_type')
#    char = models.CharField(max_length=255,default=None,null=True)
#    text = models.TextField(default=None,null=True)
#    date = models.DateField(default=None,null=True)
#    datetime = models.DateTimeField(default=None,null=True)
#
#    def __unicode__(self):
#        return "%s %s %s" % (self.type,self.lang)



class Post(TranslationModel):
    title = models.CharField(max_length=250)
    slug = models.CharField(max_length=250,blank=True)
    author = models.ForeignKey(User)
    resume = models.TextField(blank=True)
    content = models.TextField()

    def save(self,force_insert=False,force_update=False):

        import ipdb
        ipdb.set_trace()


        super(Post,self).save(force_insert=force_insert,force_update=force_update)


