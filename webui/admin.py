from django.contrib import admin
from django.utils.safestring import mark_safe
from models import *

class AdminArticle(admin.ModelAdmin):
    list_display = ('getid','get_flag','gettitle','get_absolute_url','author',
        'is_active','is_draft','publish_date','updated_date',
        'expiration_date',)
    list_display_links=('gettitle',)
    select_related = True
    prepopulated_fields = {"slug":("title",)}
    raw_id_fields = ('source',)

    def getid(self,obj):
        return obj.id
    getid.short_description = 'ID'
    getid.admin_order_field = 'id'

    class Media:
        js = ['/media/admin/tinymce/jscripts/tiny_mce/jquery.tiny_mce.js',
              '/media/admin/tinymce_setup/tinymce_setup.js']

admin.site.register(Article,AdminArticle)
