# -*- coding:utf-8 -*-
from django.db import models
from django.db.models import F
from django.contrib.auth.models import User


class Wsync(models.Model):
    instance = models.CharField(max_length=50, verbose_name=u'Instance Name')
    site_url = models.CharField(max_length=200, verbose_name=u'Site Url')
    user = models.ForeignKey(User, verbose_name=u'User')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'Create Time', editable=False, db_index=True)

    def __unicode__(self):
        return self.instance


