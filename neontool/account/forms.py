# -*- coding: utf-8 -*-
import re
import random
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

class SignupForm(forms.Form):
    email = forms.EmailField(label=u'email', required=True, widget=forms.TextInput(attrs={'tabindex': '1', "class" : "span4"}))
    nickname = forms.CharField(label=u'昵称', required=False, max_length=30, widget=forms.TextInput(attrs={'tabindex': '2', "class" : "span4"}))
    password1 = forms.CharField(label=u'密码', required=True, widget=forms.PasswordInput(render_value=False, attrs={'tabindex': '3', "class" : "span4"}))
    password2 = forms.CharField(label=u'重复密码', widget=forms.PasswordInput(render_value=False, attrs={'tabindex': '4', "class" : "span4"}))
    
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname'].strip()
        if nickname and (not re.compile(ur'^[\w|\u2E80-\u9FFF]+$').search(nickname)):
            raise forms.ValidationError(u'昵称“%s”名非法，昵称目前仅允许使用中英文字数字和下划线' % nickname)
        return nickname
    
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        try:
            # 每个Member对应一个User，但是允许后台User不对应Member
            User.objects.get(username__iexact=email) 
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(u'已经有用户使用“%s”注册了用户，请您确认邮件是否拼写错误' % email)
        return email
    
    def clean_password1(self):
        password = self.cleaned_data['password1'].strip()
        if not password:
            raise forms.ValidationError(u'对不起，密码不能为空')
        return password
    
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(u'您所输入的两个密码不一致，请您重新输入')
        return self.cleaned_data
    
    def save(self, request):
        if not self.is_valid():
            return False
        email = self.cleaned_data['email']
        nickname = self.cleaned_data['nickname']
        password = self.cleaned_data['password1']
        
        user = User()
        user.username = email
        user.email = email
        user.set_password(password)
        user.is_active = True
        user.save()
        #注册后登录
        credential = { 'username': email, 'password': password}
        user = authenticate(**credential)
        login(request, user)
        return True
    
class LoginForm(forms.Form):
    email = forms.EmailField(label=u'email', required=True, widget=forms.TextInput(attrs={'tabindex': '1'}))
    password = forms.CharField(label=u'密码', required=True, widget=forms.PasswordInput(render_value=False, attrs={'tabindex': '2'}))
    remember = forms.BooleanField(label=u'记住登陆信息', help_text=u'如果选择记住登陆信息，会保留登陆信息2周', required = False, widget=forms.CheckboxInput(attrs={'tabindex': '3'}))
    
    user = None
    
    def clean_email(self):
        email=self.cleaned_data.get('email','')
        return email
    
    def clean(self):
        super(LoginForm,self).clean()
        credential = { 'username': self.cleaned_data.get('email',''), 'password': self.cleaned_data.get('password','')}
        user = authenticate(**credential)
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(u'您还没有通过邮件激活帐号，请您登陆邮箱打开链接激活')
        else:
            raise forms.ValidationError(u'您输入的邮件地址与密码不匹配或者帐号还不存在，请您重试或者注册帐号')
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            if "remember" in self.cleaned_data and self.cleaned_data["remember"]:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
            return True
        return False

class ChangePasswdForm(forms.Form):
    oldpassword = forms.CharField(label=u'原密码', required=True, widget=forms.PasswordInput(render_value=False, attrs={'tabindex': '1'}))
    password1 = forms.CharField(label=u'新密码', required=True, widget=forms.PasswordInput(render_value=False, attrs={'tabindex': '2'}))
    password2 = forms.CharField(label=u'重复新密码', required=True, widget=forms.PasswordInput(render_value=False, attrs={'tabindex': '3'}))
   
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ChangePasswdForm, self).__init__(*args, **kwargs)
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(u"旧密码不正确，请重试")
        return self.cleaned_data["oldpassword"]

    def clean_password1(self):
        password = self.cleaned_data['password1'].strip()
        if not password:
            raise forms.ValidationError(u'密码不能为空')
        return password

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(u'您所输入的两个密码不一致，请您重新输入')
        return self.cleaned_data

    def save(self):
        if not self.is_valid():
            return False
        password = self.cleaned_data['password1']
        self.user.set_password(password)
        self.user.save()
        return True

