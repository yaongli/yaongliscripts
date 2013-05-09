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
import threading
from threading import Thread
import time
import signal
from contextlib import contextmanager

#avoid Encoding Problem
#reload(sys)
#sys.setdefaultencoding('utf-8')

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
        self.folder = "temp"
        self.orginFolder = self.folder + "/download"
        self.resultFolder =self.folder + "/result"
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        self.mkdir(self.folder)
        self.mkdir(self.orginFolder)
        self.mkdir(self.resultFolder)
        self.mainpage = "template.html"
        self.resdir = "resources"
        self.local2urlmap = {}

    def execute(self):
        self.download(self.targetUrl, self.mainpage)
        print "The main html file has been download to %s, before download refrence resources, you handle this file." % os.path.join(self.orginFolder, self.mainpage)
        #raw_input("Press ENTER to continue to download refrence resources:[Enter]")
        
        mainContent = self.readFile(os.path.join(self.orginFolder, self.mainpage))
        mainContent = self.handleBaseHref(mainContent)
        mainContent = self.removeCanonical(mainContent)
        mainContent = self.down4js(mainContent)
        mainContent = self.down4css(mainContent)
        mainContent = self.down4img(mainContent)
        mainContent = self.replaceHref(mainContent)
        mainContent = self.replaceSpecialChar(mainContent)
        mainContent = self.addNeonCssfile(mainContent)
        #todo favicon: <link rel="shortcut icon" href="/np/clients/test/resources/favicon.ico" />
        #todo form action url :<form action="search.html?L=0" 
        self.writeFile(os.path.join(self.resultFolder, self.mainpage), mainContent)

    def removeCanonical(self, content):
        #<link rel="canonical" href="http://www.example.com/product.php?item=swedish-fish"/>
        content = re.sub(r"<link rel=[\"\']?canonical[\"\']?.*?>", "", content, flags=re.I)
        return content 

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
        shutil.copy("neon/neon.css", self.resultFolder + "/" + self.resdir + "/" + "neon.css")
        neoncss = """\n<link rel="stylesheet" href="resources/neon.css" type="text/css"/>\n"""
        content = content.replace("</head>", neoncss + "</head>")
        return content
    
    def replace(self, content, replacelist):
        pprint(replacelist)
        #clear the duplicated
        replaceMap = {}
        for (old, new) in replacelist:
            if old != None and new != None and old.strip() != "":
                replaceMap[old] = new

        for (old, new) in replaceMap.items():
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
        
        if not os.path.exists(self.orginFolder + "/" +self.resdir + "/js"):
            os.makedirs(self.orginFolder + "/" +self.resdir + "/js")
        reslist = self.batchDownload(urllist, self.resdir + "/js")
        
        content = self.replace(content, reslist)
        self.copyrestree("js")
        return content

    def down4css(self, content):
        urllist = self.parseCssUrl(content)
        if len(urllist) == 0:
            print "No css file need to be download"
            return content
        if not os.path.exists(self.orginFolder + "/" +self.resdir + "/css"):
            os.makedirs(self.orginFolder + "/" +self.resdir + "/css")
        reslist = self.batchDownload(urllist, self.resdir + "/css")
        
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
        
        if not os.path.exists(self.orginFolder + "/" +self.resdir + "/images"):
            os.makedirs(self.orginFolder + "/" +self.resdir + "/images")
        reslist = self.batchDownload(urllist, self.resdir + "/images")
        
        content = self.replace(content, reslist)
        self.copyrestree("images")
        return content
    
    def singleDownload(self, url, destFolder, resultList):
        (url, localfilename) = self.downtofolder(url, destFolder)
        if url != None:
            resultList.append((url, localfilename))
    
    def batchDownload(self, urllist, destFolder):
        resultList = []
        threads = []
        for url in urllist:
            t = Thread(None,self.singleDownload,None,(url, destFolder, resultList))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
        
        return resultList

    def parseImagesUrl(self, content):
        #<img src="http://ecsonline.org/wp-content/uploads/2012/08/logo-ecs.png" alt="Environmental Charter Schools" />
        #<link rel="apple-touch-icon" sizes="72x72" href="http://ecsonline.org/wp-content/themes/ecs/images/devices/ecs-ipad.png" />
        #<li class="royalSlide" data-src="http://ecsonline.org/wp-content/uploads/2012/09/partners-1.jpg"></li>
        reglist = [r"""<img.*?src=[\'\"](.*?)[\'\"]""", 
                   r"""<link rel="[^\"]*icon".*?href=[\'\"](.*?)[\'\"]""",
                   r"""data-src=[\'\"](.*?\.jpg)[\'\"]""",
                   r"""data-src=[\'\"](.*?\.jpeg)[\'\"]""",  
                   r"""data-src=[\'\"](.*?\.png)[\'\"]""", 
                   r"""data-src=[\'\"](.*?\.gif)[\'\"]""",
                   r"""rel=[\'\"](.*?\.jpg)[\'\"]""",
                   r"""rel=[\'\"](.*?\.jpeg)[\'\"]""",  
                   r"""rel=[\'\"](.*?\.png)[\'\"]""", 
                   r"""rel=[\'\"](.*?\.gif)[\'\"]""",
                   r"""background=[\'\"](.*?\.jpg)[\'\"]""",
                   r"""background=[\'\"](.*?\.jpeg)[\'\"]""",  
                   r"""background=[\'\"](.*?\.png)[\'\"]""", 
                   r"""background=[\'\"](.*?\.gif)[\'\"]""",
                   r"""url\([\'\"]?(.*?)[\'\"]?\)""",
                   r"""<input\stype=[\'\"]?image[\'\"]?\ssrc=[\'\"]?(.*?)[\'\"]?\s?.*?>""",
                   #r"\"([^\"]*?\.jpg)\"", r"\"([^\"]*?\.gif)\"",r"\"([^\"]*?\.png)\"",
                   #r"\'([^\']*?\.jpg)\'", r"\'([^\']*?\.gif)\'",r"\'([^\']*?\.png)\'",
                   ]
        urllist = []
        for regstr in reglist:
            urllist += re.findall(regstr, content, flags=re.I|re.M)
        return urllist

    def download(self, url, filename, original_url=None):
        if original_url == None:
            original_url = url
        print "download from ", url
        dlfilepath = self.orginFolder + "/" + filename
        print "save as ",dlfilepath,"        ",
        if not os.path.exists(os.path.dirname(dlfilepath)):
            self.mkdir(os.path.dirname(dlfilepath))
        (dlfilepathname, dlfilepathext) = os.path.splitext(dlfilepath)
        (filenamebase, filenameext) = os.path.splitext(filename)
        extCount = 1
        while os.path.exists(dlfilepath):
            oldurl = self.local2urlmap.get(dlfilepath)
            if oldurl and oldurl == url:
                print "File %s already exist with same url. " % dlfilepath
                return (original_url, filename)
            else:
                print "File %s already exist but with different url. " % dlfilepath
                dlfilepath = dlfilepathname + "_" + str(extCount) + dlfilepathext
                filename = filenamebase + "_" + str(extCount) + filenameext
                print "Change name to %s and try again." % dlfilepath
                extCount += 1

        tryCount = 0
        while True:
            try:
                def reporthook(block_count, block_size, file_size):
                    print ".",
                urllib.urlretrieve(url, dlfilepath, reporthook)
                self.local2urlmap[dlfilepath] = url
                print "\t\t[OK]"
                return (original_url, filename)
            except:
                tryCount += 1
                print "[WARNING]Failed to download %s for the %s try." % (url, tryCount)
                if tryCount > 3:
                    print "[ERROR] Failed to download %s after the %s times try." % (url, tryCount)
                    return (None, None)

    def downtofolder(self, url, folder):
        (original_url, url, filename, param) = self.tidyurl(url)
        filepath = folder + "/" + filename
        if os.path.exists(self.orginFolder + "/" + filepath) and param != None:
            param = param.replace("?","_").replace("#","_").replace("&","_")
            filename = filename[0: filename.rfind(".")] + param + filename[filename.rfind("."): ]
        filepath = folder + "/" + filename
        return self.download(url, filepath, original_url)

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
    starttime = time.time()
    main()
    endtime = time.time()
    usedtime = endtime - starttime
    print "Total used time %s seconds." % usedtime
    