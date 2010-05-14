from django.db import models
from translations.models import Languages

class BObjectType(models.Model):
    """
    object types and data types, ex:
    post, page, title, date, etc
    """
    name = models.CharField(max_length=20)

class BObject(models.Model):
    """
    this is generic object model.
    objid list to id of main object, lang is language code of object, type is
    type of object (post, category, etc) and content is content it self
    """
    objid = models.IntegerField()
    lang = models.ForeignKey(Languages)
    type = models.ForeignKey(BObjectType)
    content = models.TextField()

