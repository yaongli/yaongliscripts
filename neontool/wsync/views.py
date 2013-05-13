# Create your views here.

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.shortcuts import render

from forms import WsyncForm
import posixpath
import zipfile
import os
import shutil

def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
        
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()
    
def home(request):
    if request.method == 'POST':
        form = WsyncForm(request.POST)
        if form.save(request):
            instance = form.cleaned_data['instance']
            filename = instance + ".zip"
            filepath = os.path.join(settings.MEDIA_ROOT, "wsync", filename)
            fileurl = settings.MEDIA_URL + "wsync/" + filename
            if os.path.exists(filepath):
                os.remove(filepath)
                
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
                
            zip_dir(os.path.join(settings.WSYNC_RESULT_DIR, "result"), filepath)
            return render(request, 'wsync_success.html', {'fileurl' : fileurl, 'filename':filename})
    else:
        form = WsyncForm()
    
    return render(request, 'wsync_index.html', {'form' : form})
