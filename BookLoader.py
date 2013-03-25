# -*- coding:utf-8 -*-

import bs4
import urllib2
import threading
import logging
import sys
import Queue
import os
import re

#avoid Encoding Problem
#print sys.getdefaultencoding()
reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger("BookLoader")
logger.setLevel(logging.DEBUG)

#print sys.getdefaultencoding()

class BookInfo(object):
    def __init__(self, bookurl, bookname=None, authorname=None):
        self.bookname = bookname
        self.bookurl = bookurl
        self.authorname = authorname

    def __repr__(self):
        return ("%(bookname)s  %(bookurl)s  %(authorname)s  " % self.__dict__).encode("gbk")

class ChapterInfo(object):
    def __init__(self, bookInfo, chapterUrl, chapterName, content=None):
        self.bookInfo = bookInfo
        self.chapterUrl = chapterUrl
        self.chapterName = chapterName
        self.content = content

    def __repr__(self):
        return "%(chapterUrl)s  %(chapterName)s " % self.__dict__

class PageDownloader(threading.Thread):
    def __init__(self, pageUrl):
        threading.Thread.__init__(self)
        self.pageUrl = pageUrl

    def run(self):
        logger.debug("Begin to retrieve and parse %s" % self.pageUrl)
        trytimes = 0
        while True:
            try:
                webResponse = urllib2.urlopen(self.pageUrl)
                pageContent = webResponse.read()
            except Exception, e:
                print e
                trytimes += 1
                print "Try to read %s for %s time." % (self.pageUrl, trytimes)
                if trytimes > 3:
                    break
            else:
                print "Read %s successfully." % self.pageUrl
                break
        bs = bs4.BeautifulSoup(pageContent)
        self.handlePageBS(bs)

    def handlePageBS(self, bs):
        pass

class BookDownloader(PageDownloader):
    def __init__(self, bookInfo):
        PageDownloader.__init__(self, bookInfo.bookurl)
        self.bookInfo = bookInfo

    def handlePageBS(self, bs):
        self.parseBookInfo(bs)
        self.chapterInfoList = self.parseChapterInfoList(bs)

    def parseBookInfo(self, bs):
        pass

    def parseChapterInfoList(self, bs):
        return []

    def getBookInfo(self):
        return self.bookInfo

    def getChapterInfoList(self):
        return self.chapterInfoList

class ChapterDownloader(PageDownloader):
    def __init__(self, chapterInfo):
        PageDownloader.__init__(self, chapterInfo.chapterUrl)
        self.chapterInfo = chapterInfo

    def handlePageBS(self, bs):
        self.content = self.parseContent(bs)

    def parseContent(self, bs):
        return content


class ShuzijiaBookDownloader(BookDownloader):
    def parseChapterInfoList(self, bs):
        chapterInfos = []
        contentTable = bs.find("table", {"class" : "acss"})
        ctdlist = contentTable.findAll("td")
        for ctd in ctdlist:
            classes = ctd.attrs.get('class')
            if None == classes:
                classes = []

            if 'vcss' in classes:
                volumn = ctd.text
                #print volumn
            elif 'ccss' in classes:
                clink = ctd.find("a")
                if clink:
                    clink_href = clink.attrs.get("href")
                    clink_value = clink.text
                    #print clink_value + "\t\t" + clink_href
                    chapterInfo = ChapterInfo(self.bookInfo, clink_href, clink_value)
                    chapterInfos.append(chapterInfo)
            else:
                pass

        return chapterInfos

class ShuzijiaChapterDownloader(ChapterDownloader):
    def parseContent(self, bs):
        cbs = bs.find("div", {"id": "content"})
        if cbs:
            content = cbs.text
            #print content
        return content

class ShumilouBookIndexer(PageDownloader):
    def handlePageBS(self, bs):
        self.links = []
        links = bs.findAll("a")
        for link in links:
            link_href = link.attrs.get("href")
            if re.match(r"http://www.shumilou.com/\w+/", link_href):
                link_txt = link.text
                self.links.append((link_href, link_txt))

    def findAllBook(self):
        return self.links


class ShumilouBookDownloader(BookDownloader):
    def parseChapterInfoList(self, bs):
        chapterInfos = []
        lilist = bs.findAll("li", {"class" : "zl"})
        for li in lilist:
            clink = li.find("a")
            if clink:
                clink_href = clink.attrs.get("href")
                clink_value = clink.text
                #print clink_value + "\t\t" + clink_href
                chapterInfo = ChapterInfo(self.bookInfo, clink_href, clink_value)
                chapterInfos.append(chapterInfo)

        return chapterInfos

class ShumilouChapterDownloader(ChapterDownloader):
    def parseContent(self, bs):
        #print "parseContent:"
        cbs = bs.findAll("p")
        plist = []
        for p in cbs:
            plist.append(p.text)
        content = "\n".join(plist)
        #print content
        return content

def testShuzijia():
    bookInfo = BookInfo("http://www.shuzhijia.com/html/18/18061/6888795.html", u"官场之风流人生", u"更俗")
    bookDownloader = ShuzijiaBookDownloader(bookInfo)
    bookDownloader.run()
    for chapterInfo in bookDownloader.chapterInfoList:
        chapterDownloader = ShuzijiaChapterDownloader(chapterInfo)
        chapterDownloader.run()

def testShumilou():
    bookInfo = BookInfo("http://www.shumilou.com/dakaituozhe/", u"大开拓者", u"剑扼虚空")
    print bookInfo
    bookDownloader = ShumilouBookDownloader(bookInfo)
    bookDownloader.run()
    for chapterInfo in bookDownloader.getChapterInfoList():
        print chapterInfo
        chapterDownloader = ShumilouChapterDownloader(chapterInfo)
        chapterDownloader.run()

def downShumilou():
    logger.debug("Begin to download shumilou")
    siteDir = r"D:\books\shumilou"
    if not os.path.exists(siteDir):
        os.makedirs(siteDir)

    indexList = ['http://www.shumilou.com/list-%s.html' % n for n in range(1,2)]
    bookLinkList = []
    for index in indexList:
        indexer = ShumilouBookIndexer(index)
        indexer.run()
        bookLinkList.extend(indexer.findAllBook())

    with open("bookindex.txt", 'wb') as f:
        for link in bookLinkList:
            #print link
            f.write("<a href='%s'>%s</a>\n" % (link[0], link[1]))
        f.flush()
    logger.debug("Read book index list complete.")
    
    for link in bookLinkList:
        bookUrl = link[0]
        bookName = link[1]
        bookDir = os.path.join(siteDir, bookName)
        if not os.path.exists(bookDir):
            os.makedirs(bookDir)

        bookInfo = BookInfo(bookUrl, bookName, None)
        bookDownloader = ShumilouBookDownloader(bookInfo)
        bookDownloader.run()
        charperNameList = []
        for chapterInfo in bookDownloader.getChapterInfoList():
            chapterName = chapterInfo.chapterName
            charperNameList.append(chapterName)
            fileName = chapterName + ".txt"
            #file name can not contain \ / : * ? < > |
            fileName = re.sub(r"[\\/\*\?<>\|:]", "", fileName)
            chapterFile = os.path.join(bookDir, fileName)
            if os.path.exists(chapterFile):
                continue
            chapterDownloader = ShumilouChapterDownloader(chapterInfo)
            chapterDownloader.run()
            content = chapterDownloader.content
            writeFile(chapterFile, content)
        #write index file
        writeFile(os.path.join(bookDir, "index.txt"), "\n".join(charperNameList))

def writeFile(fileName, content):
    with open(fileName, 'wb') as f:
        f.write(content)
        f.flush()


if __name__ == "__main__":
    downShumilou();
