# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

zipfile = r"sharedlib.zip"
includes = ["encodings", "encodings.*"]
options = {"py2exe":{
                     "compressed": 1,
                     "optimize": 2,
                     "ascii": 0,
                     "includes":includes,
                     "bundle_files": 2
                    }
           }
setup(
    options = options,
    zipfile = None,
    name = "Download Template",
    description = "Neon Tool",
    windows=[
            {
             "script": "NeonTool.py",
             "icon_resources": [(2, "neon.ico"),(1, "import.ico")]
            },
        ]
    )
    