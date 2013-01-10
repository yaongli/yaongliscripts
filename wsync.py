#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import re
import shutil
import sys
from  pprint import pprint
import urlparse
from Queue import Queue
import os
import glob

import signal
from contextlib import contextmanager

#avoid Encoding Problem
reload(sys)
sys.setdefaultencoding('utf-8')

WORKDIR = os.path.abspath(os.curdir)

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

import socket
socket.setdefaulttimeout(30)


class UrlDownload(object):
    def __init__(self, targetUrl):
        if not targetUrl.startswith("http"):
            targetUrl = "http://" + targetUrl
        self.targetUrl = targetUrl
        self.domainUrl = targetUrl[0: targetUrl.find("/", 10)] #https://mail.google.com/mail/#inbox  excludes // after http
        self.targetDir = targetUrl[0: targetUrl.rfind("/")]
        self.folder = "UrlDownload"
        self.orginFolder = self.folder + "/download"
        self.resultFolder =self.folder + "/result"
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        self.mkdir(self.folder)
        self.mkdir(self.orginFolder)
        self.mkdir(self.resultFolder)
        self.mainpage = "template.html"
        self.resdir = "resources"

    def execute(self):
        self.download(self.targetUrl, self.mainpage)
        mainContent = self.readFile(os.path.join(self.orginFolder, self.mainpage))
        mainContent = self.handleBaseHref(mainContent)
        mainContent = self.down4js(mainContent)
        mainContent = self.down4css(mainContent)
        mainContent = self.down4img(mainContent)
        mainContent = self.replaceHref(mainContent)
        mainContent = self.replaceSpecialChar(mainContent)
        mainContent = self.addNeonCssfile(mainContent)
        #todo favicon: <link rel="shortcut icon" href="/np/clients/test/resources/favicon.ico" />
        #todo form action url :<form action="search.html?L=0" 
        self.writeFile(os.path.join(self.resultFolder, self.mainpage), mainContent)

    def handleBaseHref(self, content):
        #<base href="http://www.anthroposophy.org/" />
        basehrefs = re.findall(r"<base\s+href=\"(.*?)\"", content, flags=re.I)
        if basehrefs:
            self.targetDir = basehrefs[0]
        
        content = re.sub(r"<base\s+href=\"(.*?)\"\s*/>", "", content, flags=re.I)
        return content
        
    def replaceSpecialChar(self, content):
        specialCharMap = {"©": "&copy;"}
        for key,value in specialCharMap.items():
            content = content.replace(key, value)
        return content
    
    def addNeonCssfile(self, content):
        shutil.copy(os.path.abspath(os.path.dirname(__file__)) + "/neon/" + "neon.css", self.resultFolder + "/" + self.resdir + "/" + "neon.css")
        neoncss = """\n<link rel="stylesheet" href="resources/neon.css" type="text/css"/>\n"""
        content = content.replace("</head>", neoncss + "</head>")
        return content
    
    def replace(self, content, replacelist):
        pprint(replacelist)
        for (old, new) in replacelist:
            if old != None and new != None:
                content = content.replace(old, new)
        return content

    def copyrestree(self, resfolder):
        if os.path.exists(self.orginFolder + "/" + self.resdir + "/" +  resfolder):
            shutil.copytree(self.orginFolder + "/" + self.resdir + "/" +  resfolder, self.resultFolder + "/" + self.resdir + "/" +  resfolder)

    def replaceHref(self, content):
        print "Replace link href to absolute url"
        reg = re.compile(r"""(<a\s+[^>]*?href=[\"\'])(.*?)([\"\'].*?>)""", flags=re.I|re.M)
        def href_replace(m):
            href = m.group(2)
            if not (href == "" or href == "#" or href.startswith("mailto:") or href.startswith("http")): 
                href = urlparse.urljoin(self.targetDir, href)
            return m.group(1) + href + m.group(3)
            
        content = reg.sub(href_replace, content)
        return content
        
    def down4js(self, content):
        urllist = re.findall(r"""<script.*?src=[\"\'](.*?)[\"\'].*?>""", content, flags=re.I|re.M)
        if len(urllist) == 0:
            print "No javascript file need to be download"
            return content
        
        reslist = []
        for url in urllist:
            (url, localfilename) = self.downtofolder(url, self.resdir + "/js")
            if url != None:
                reslist.append((url, localfilename))
        
        content = self.replace(content, reslist)
        self.copyrestree("js")
        return content

    def down4css(self, content):
        urllist = self.parseCssUrl(content)
        if len(urllist) == 0:
            print "No css file need to be download"
            return content
        
        reslist = []
        for url in urllist:
            (url, localfilename) = self.downtofolder(url, self.resdir + "/css")
            if url != None:
                reslist.append((url, localfilename))
        
        content = self.replace(content, reslist)
        for (cssurl, cssfile) in reslist:
            self.handle4css(cssurl, cssfile)

        self.copyrestree("font")
        self.copyrestree("others")
        return content

    def parseCssUrl(self, content):
        reglist = [r"""<link.*?rel=[\"\']stylesheet[\"\'].*?href=[\"\'](.*?)[\"\'].*>""", r"""<link.*?href=[\"\'](.*?)[\"\'].*?rel=[\"\']stylesheet[\"\'].*?>"""]
        urllist = []
        for regstr in reglist:
            urllist += re.findall(regstr, content, flags=re.I|re.M)
        return urllist

    def handle4css(self, cssurl, cssfile):
        print "handle4css: cssurl=", cssurl, " \t cssfile= ", cssfile
        content = self.readFile(self.orginFolder + "/" + cssfile)
        cssurl = urlparse.urljoin(self.targetUrl, cssurl)
        self.down4cssurl(cssurl, content, cssfile)
        

    def down4cssurl(self, cssurl, content, cssfile):
        regstr = r"url\([\'\"]?(.*?)[\'\"]?\)"
        urllist = re.findall(regstr, content, flags=re.I|re.M)
        if not urllist:
            self.writeFile(self.resultFolder + "/" + cssfile, content)
            return
        
        reslist = []
        for url in urllist:
            orignalurl = url
            fullurl = urlparse.urljoin(cssurl, url)
            if url.endswith(".css"):
                (url, localfilename) = self.downtofolder(fullurl, self.resdir + "/css")
                if localfilename:
                    self.handle4css(fullurl, localfilename)
            elif url.endswith(".gif") or url.endswith(".jpg") or url.endswith(".png") or url.endswith(".jpeg"):
                (url, localfilename) = self.downtofolder(fullurl, self.resdir + "/images")
            elif url.endswith(".eot") or url.endswith(".woff") or url.endswith(".ttf") or url.endswith(".svg"):
                (url, localfilename) = self.downtofolder(fullurl, self.resdir + "/font")
            else:
                (url, localfilename) = self.downtofolder(fullurl, self.resdir + "/others")
            if url != None:
                localfilename = ".." + localfilename[localfilename.find("/"):]
                reslist.append((orignalurl, localfilename))
        
        content = self.replace(content, reslist)
        self.writeFile(self.resultFolder + "/" + cssfile, content)

    def down4img(self, content):
        urllist = self.parseImagesUrl(content)
        if len(urllist) == 0:
            print "No image file need to be download"
            return content
        
        reslist = []
        for url in urllist:
            (url, localfilename) = self.downtofolder(url, self.resdir + "/images")
            if url != None:
                reslist.append((url, localfilename))
        
        content = self.replace(content, reslist)
        self.copyrestree("images")
        return content

    def parseImagesUrl(self, content):
        #<img src="http://ecsonline.org/wp-content/uploads/2012/08/logo-ecs.png" alt="Environmental Charter Schools" />
        #<link rel="apple-touch-icon" sizes="72x72" href="http://ecsonline.org/wp-content/themes/ecs/images/devices/ecs-ipad.png" />
        #<li class="royalSlide" data-src="http://ecsonline.org/wp-content/uploads/2012/09/partners-1.jpg"></li>
        reglist = [r"""<img.*?src=[\'\"](.*?)[\'\"]""", 
                   r"""<link rel="[^\"]*icon".*?href=[\'\"](.*?)[\'\"]""",
                   r"""data-src=[\'\"](.*?\.jpg)[\'\"]""", r"""data-src=[\'\"](.*?\.png)[\'\"]""", r"""data-src=[\'\"](.*?\.gif)[\'\"]""",
                   #r"\"([^\"]*?\.jpg)\"", r"\"([^\"]*?\.gif)\"",r"\"([^\"]*?\.png)\"",
                   #r"\'([^\']*?\.jpg)\'", r"\'([^\']*?\.gif)\'",r"\'([^\']*?\.png)\'",
                   ]
        urllist = []
        for regstr in reglist:
            urllist += re.findall(regstr, content, flags=re.I|re.M)
        return urllist

    def download(self, url, filename):
        print "download from ", url
        print "save as ",filename,"        ",
        if not os.path.exists(os.path.dirname(self.orginFolder + "/" + filename)):
            self.mkdir(os.path.dirname(self.orginFolder + "/" + filename))
        if os.path.exists(self.orginFolder + "/" + filename):
            print ""
            print "[ERROR] file %s already exist." % filename
            return False
        
        try:
            def reporthook(block_count, block_size, file_size):
                print ".",
            urllib.urlretrieve(url, self.orginFolder + "/" + filename, reporthook)
            print "\t\t[OK]"
        except:
            print "[ERROR]Failed to download ", url
            return False
        return True

    def downtofolder(self, url, folder):
        (original_url, url, filename, param) = self.tidyurl(url)
        filepath = folder + "/" + filename
        if os.path.exists(self.orginFolder + "/" + filepath) and param != None:
            param = param.replace("?","_").replace("#","_").replace("&","_")
            filename = filename[0: filename.rfind(".")] + param + filename[filename.rfind("."): ]
        filepath = folder + "/" + filename
        isOK = self.download(url, filepath)
        if not isOK:
            return (None, None)
        return (original_url, filepath)

    def mkdir(self, dirpath):
        os.makedirs(dirpath)
        print "Create dir: ", dirpath

    def readFile(self, filepath):
        content = ""
        with open(filepath, 'rb') as afile:
            content = afile.read()
        return content

    def writeFile(self, filepath, content):
        if not os.path.exists(os.path.dirname(filepath)):
            self.mkdir(os.path.dirname(filepath))
        with open(filepath, 'wb') as afile:
            afile.write(content)

    def tidyurl(self, url):
        original_url = url = url.strip().strip("'").strip('"').strip()
        filename = ""
        param = ""
        if url.rfind("?") > url.rfind("/"):
            filename = url[url.rfind("/") + 1 : url.rfind("?")]
            param = url[url.rfind("?")]
        elif url.rfind("#") > url.rfind("/"):
            filename = url[url.rfind("/") + 1 : url.rfind("#")]
            param = url[url.rfind("#")]
        else:
            filename = url[url.rfind("/") + 1 :]
        
        if not url.startswith("http"):
            url = urlparse.urljoin(self.targetDir, url)
        return (original_url, url, filename, param)

def main():
    """
    """
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " url"
        return 1
    
    targetUrl = sys.argv[1]
    dl = UrlDownload(targetUrl)
    dl.execute()
    


if __name__ == "__main__":
    main()