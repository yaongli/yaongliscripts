# -*- coding:utf-8 -*-
import os
import sys
import re
import subprocess


BC_EXE = r"C:\Users\YangYongli\Downloads\BeyondComparePortable\BeyondComparePortable\App\BeyondCompare\BCompare.exe"
NEON_SRC = r"D:\workspace\neon\src"
NEON_BRANCH_SRC = r"D:\workspace\neon_branch\src"

if __name__ == "__main__":
    listfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), r"modify.txt")
    with open(listfile, 'rb') as f:
        filelist = f.readlines()
        for fn in filelist:
            fn = fn.replace("\n", "").replace("\r", "").strip()
            if "" == fn: 
                continue
            mainpath = os.path.join(NEON_SRC, fn)
            branchpath = os.path.join(NEON_BRANCH_SRC, fn)
            os.system(BC_EXE + " \"" + mainpath + "\" \"" + branchpath + "\"")
            