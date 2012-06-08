# coding: utf-8 
"""
下载纵横小说

目录URL：
http://book.zongheng.com/showchapter/书号.html

章节URL：
<a href="http://book.zongheng.com/chapter/156621/2785994.html" title="最后更新时间:2012-02-25  字数:2047">
十五、《赤城杂摄妙用阳符经》
</a>


文本内容：
<div id="readtext" class="fontm" level="0" style="margin-bottom:25px">
	<p>正文内容</p>
	<p>正文内容</p>
</div>


内部有干扰需要去除：
<p><span class="watermark"></span></p>

"""

import urllib2
import re
import os

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
	chapterurl = r"http://book.zongheng.com/showchapter/%s.html" % bookNum
	webResponse = urllib2.urlopen(chapterurl)
	chapterPage = webResponse.read()
	chapterReg = r'<a href="(http://book.zongheng.com/chapter/%s/\d+\.html)" title=".*?(\d+\-\d+\-\d+)\s*.*?(\d+)">\s*\n*(.*?)\s*\n*\s*</a>' % bookNum
	chapterGroupList = re.findall(chapterReg, chapterPage, re.M)
	chapterList = []
	for chapterGroup in chapterGroupList:
		chapter = Chapter(chapterGroup[3], chapterGroup[0], chapterGroup[1], chapterGroup[2])
		chapterList.append(chapter)
	return chapterList

def writeChapter(bookName, chapters):
	with open(bookName + ".txt", "w") as bookindex:
		for index,chapter in enumerate(chapters):
			line = "%s\t%s\t%s" % (index, chapter.title.encode('utf-8'), chapter.href)
			print unicode(line, 'utf-8')
			#print line
			bookindex.write(line)
			bookindex.write("\n")
		bookindex.flush()

def queryContent(chapter):
	print "Download %s" % chapter.title
	webResponse = urllib2.urlopen(chapter.href)
	contentpage = webResponse.read()
	startposit = contentpage.find("<div id=\"readtext\"")
	endposit = contentpage.find("</div", startposit)
	contenttext = contentpage[startposit:endposit]
	contentReg = r'(<p>(.*?)</p>)'
	contentGroupList = re.findall(contentReg, contenttext, re.M)
	contentList = []
	for contentGroup in contentGroupList:
		line = contentGroup[0].replace("\n", "").replace("<p>", "").replace("</p>", "")
		line = re.sub("<span.*?</span>", "", line, re.M)
		if "" != line:
			contentList.append(line)
	
	content = Content(chapter, contentList)
	return content

def writeContent(content):
	chapter = content.chapter
	title = chapter.title
	with open(title + ".txt", "w") as writer:
		for line in content.lines:
			writer.write(line)
			writer.write("\n")

def downloadbook(bookName, bookNum):
	print "Download index ..."
	chapters = queryChapter(bookNum)
	writeChapter(bookName, chapters)
	print "Download content ..."
	for chapter in chapters:
		if os.path.exists(chapter.title + ".txt"):
			continue
		content = queryContent(chapter)
		writeContent(content)

if __name__ == "__main__":
	bookName = u"赤城"
	bookNum = "156621"
	downloadbook(bookName, bookNum)
	#chapter = Chapter(u"三百九十一、鲁大师", "http://book.zongheng.com/chapter/156621/3329043.html", "2012-06-08", "2000")
	#content = queryContent(chapter)
	#writeContent(content)
