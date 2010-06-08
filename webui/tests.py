import sys,os

from django.test import TestCase
from webui.models import Post
from django.contrib.webdesign import lorem_ipsum
from django.contrib.auth.models import User
from random import choice

class SimpleTest(TestCase):

    def test_new_post(self):

        dct = dict(
            author = choice(User.objects.filter(is_active=True)),
            content = '\n'.join(lorem_ipsum.paragraphs(randint(10,20))),
            title = 'teste 1'
        )

        p = Post(**dct)

        p.save()



