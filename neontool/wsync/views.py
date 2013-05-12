# Create your views here.

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.shortcuts import render

def home(request):
    return render(request, 'wsync_index.html')
