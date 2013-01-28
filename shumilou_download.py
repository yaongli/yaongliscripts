# -*- coding: utf-8 -*-
"""
下载shumilou小说

目录URL：
http://www.shumilou.com/guanchangzhifengliurensheng/

章节URL：
<li class="zl"><a href="http://www.shumilou.com/guanchangzhifengliurensheng/953682.html">第二章 谁会让你割舍不去</a></li> 


文本内容：
<p>xxx</p>
<p>xxx</p>

内部有干扰需要去除：


"""

import urllib2
import re
import os
import shutil

class Chapter():
    def __init__(self, title, href, update, num):
        title = unicode(title, 'utf-8')
        title = title.replace("*", "").replace("?", "").replace("!", "")
        self.title = title
        self.href = href
        self.update = update
        self.num = num
    
class Content():
    def __init__(self, chapter, lines):
        self.chapter = chapter
        self.lines = lines

def queryChapter(bookNum):
    chapterurl = r"http://www.shumilou.com/%s/" % bookNum
    webResponse = urllib2.urlopen(chapterurl)
    chapterPage = webResponse.read()
    chapterReg = r'<li class="zl"><a href="(http://www.shumilou.com/%s/\d+\.html)">(.*?)</a></li>' % bookNum
    chapterGroupList = re.findall(chapterReg, chapterPage, re.M)
    chapterList = []
    for chapterGroup in chapterGroupList:
        #print chapterGroup
        chapter = Chapter(chapterGroup[1], chapterGroup[0], None, None)
        chapterList.append(chapter)
    return chapterList

def writeChapter(bookName, chapters):
    with open(bookName + ".txt", "w") as bookindex:
        for index,chapter in enumerate(chapters):
            line = "%s\t%s\t%s" % (index, chapter.title, chapter.href)
            line = line.encode("utf-8")
            #print line
            bookindex.write(line)
            bookindex.write("\n")
        bookindex.flush()

def queryContent(chapter):
    message = "Download %s from %s" % (chapter.title, chapter.href)
    print message
    webResponse = urllib2.urlopen(chapter.href)
    contentpage = webResponse.read()
    startposit = contentpage.find('<div class="title">')
    endposit = contentpage.find('<div class="title">', startposit + 1)
    contenttext = contentpage[startposit:endposit]
    #print "contenttext= ", contenttext
    contentReg = r'(<p>(.*?)</p>)'
    contentGroupList = re.findall(contentReg, contenttext, re.M | re.I | re.DOTALL)
    contentList = []
    for contentGroup in contentGroupList:
        #print contentGroup
        line = contentGroup[0].replace("\n", "").replace("<p>", "").replace("</p>", "")
        #line = re.sub("<span.*?</span>", "", line, re.M)
        if "" != line:
            line = line.encode('utf-8')
            contentList.append(line)
    
    content = Content(chapter, contentList)
    return content

def writeContent(content):
    chapter = content.chapter
    title = chapter.title
    print title
    with open(title + ".txt", "w") as writer:
        for line in content.lines:
            writer.write(line)
            writer.write("\n")

def downloadbook(bookName, bookNum):
    print "Download index ..."
    if os.path.exists(bookName):
        shutil.rmtree(bookName)
    os.makedirs(bookName)
    os.chdir(bookName)
    chapters = queryChapter(bookNum)
    writeChapter(bookName, chapters)
    print "Download content ..."
    for chapter in chapters:
        try:
            if os.path.exists(chapter.title + ".txt"):
                continue
            content = queryContent(chapter)
            writeContent(content)
        except:
            pass

if __name__ == "__main__":
    bookName = u"官场之风流人生"
    bookNum = "guanchangzhifengliurensheng"
    downloadbook(bookName, bookNum)
    #chapter = Chapter(u"testtest", "http://www.shumilou.com/guanchangzhifengliurensheng/953681.html", None, None)
    #content = queryContent(chapter)
    #writeContent(content)
