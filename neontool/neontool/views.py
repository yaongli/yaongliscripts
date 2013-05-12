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

from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def index(request):
    return render_to_response('index.html', 
        {'settings' : settings}, 
        context_instance=RequestContext(request)
    )


    