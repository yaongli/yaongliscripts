# Create your views here.
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escapejs
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from forms import SignupForm, LoginForm, ChangePasswdForm

def signin(req):
    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.login(req):
            return HttpResponseRedirect(reverse('home', args=[]))
    else:
        form = LoginForm()
    return render_to_response('login.html', {'settings' : settings, 'form': form}, context_instance=RequestContext(req))

def change_passwd(req):
    if req.method == 'POST' and req.user.is_authenticated():
        form = ChangePasswdForm(req.user, req.POST)
        if form.save():
            return render_to_response('change_passwd_success.html', {'settings' : settings}, context_instance=RequestContext(req))
    else:
        form = ChangePasswdForm(req.user)
    return render_to_response('change_passwd.html', {'settings' : settings, 'form': form}, context_instance=RequestContext(req))

def signup(req):
    if req.method == 'POST':
        form = SignupForm(req.POST)
        if form.save(req):
            ctx = {'settings' : settings, 'email': form.cleaned_data['email'], }
            return render_to_response('singup_success.html', ctx, context_instance=RequestContext(req))
    else:
        form = SignupForm()
    return render_to_response('singup.html', {'settings' : settings, 'form': form}, context_instance=RequestContext(req))

def signout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('home', args=[]))
