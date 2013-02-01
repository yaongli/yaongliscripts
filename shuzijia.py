# -*- coding:utf-8 -*-

import bs4
import urllib2

def getIndexPage(linkurl):
    content = urllib2.urlopen(linkurl).read()
    bs = bs4.BeautifulSoup(content)

    title = bs.find("h1").text
    print title
    authorbs = bs.find("meta", {"name" : "author"})
    if authorbs:
        author = authorbs.attrs.get("content")
        print author
    contentTable = bs.find("table", {"class" : "acss"})
    ctdlist = contentTable.findAll("td")
    for ctd in ctdlist:
        classes = ctd.attrs.get('class')
        if None == classes:
            classes = []

        if 'vcss' in classes:
            volumn = ctd.text
            print volumn
        elif 'ccss' in classes:
            clink = ctd.find("a")
            if clink:
                clink_href = clink.attrs.get("href")
                clink_value = clink.text
                print clink_value + "\t\t" + clink_href
        else:
            pass

def getChapterPage(linkurl):
    content = urllib2.urlopen(linkurl).read()
    bs = bs4.BeautifulSoup(content)
    cbs = bs.find("div", {"id": "content"})
    if cbs:
        cc = cbs.text
        with open("text.txt", "wb") as f:
            f.write(cc)
            f.flush()
    


if __name__ == "__main__":
    linkurl = "http://www.shuzhijia.com/html/18/18061/index.html"
    #getIndexPage(linkurl)

    chapterlink = "http://www.shuzhijia.com/html/18/18061/6888795.html"
    getChapterPage(chapterlink)

