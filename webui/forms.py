# -*- coding: utf-8 -*-
from django import forms
from models import *

class modelform(forms.ModelForm):
    class Meta:
        model = Post
    class Media:
        js = ('/js/url/here.js')

class normalform(forms.Form):
    field_one = forms.CharField(max_length=10)
    class Media:
        js = ('/js/url/here.js')
