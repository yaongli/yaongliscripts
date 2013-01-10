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

#avoid Encoding Problem
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
    url = ""
    filepath = ""
    if len(sys.argv) == 2:
        url = sys.argv[1]
        filepath = url[url.rfind("/"):]
    elif len(sys.argv) == 3:
        url = sys.argv[1]
        filepath = sys.argv[2]
    else:
        print sys.argv[0] + " url <path>"
        sys.exit(1)
    
    try:
        def reporthook(block_count, block_size, file_size):
            print ".",
        urllib.urlretrieve(url, filepath, reporthook)
        print "\t\t[OK]"
    except:
        print "[ERROR]Failed to download ", url
        sys.exit(1)
    
    sys.exit(0)

    