# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

admin.site.register(Tag)
# admin.site.register(User)
admin.site.register(TokenStat)
admin.site.register(Image)

# admin.site.register()