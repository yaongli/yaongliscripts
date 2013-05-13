# -*- coding: utf-8 -*-
import re
import random
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from models import Wsync
from download import UrlDownload

class WsyncForm(forms.Form):
    instance = forms.CharField(label=u'Instance Name', required=True, max_length=50, widget=forms.TextInput(attrs={'tabindex': '1', "class" : "span4"}))
    
    site_url = forms.CharField(label=u'Site Url', required=True, max_length=200, widget=forms.TextInput(attrs={'tabindex': '2', "class" : "span4"}))

    def clean_instance(self):
        instance = self.cleaned_data['instance'].strip()
        if len(instance) == 0 or (instance and (not re.compile(ur'^[\w]+$').search(instance))):
            raise forms.ValidationError(u'Invalid instance name [%s], only letters and numbers.' % instance)
        return instance
    
    def clean_site_url(self):
        site_url = self.cleaned_data["site_url"].strip()
        if len(site_url) == 0 or (site_url and (not re.compile(ur'^[\w\.]+$').search(site_url))):
            raise forms.ValidationError(u'Invalid site url [%s], only letters and numbers and dot.' % site_url)
        return site_url
    
    def clean(self):
        return self.cleaned_data
    
    def save(self, request):
        if not (request.user and request.user.is_authenticated()):
            raise forms.ValidationError(u'Please signin.')
            
        if not self.is_valid():
            return False
        instance = self.cleaned_data['instance']
        site_url = self.cleaned_data['site_url']
        user = request.user;
        
        dl = UrlDownload(site_url)
        dl.execute()
        
        wsync = Wsync()
        wsync.instance = instance
        wsync.site_url = site_url
        wsync.user = user
        
        wsync.save()
        
        return True

