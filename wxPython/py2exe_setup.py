# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*"]
options = {"py2exe":
                    {"compressed": 1,
                     "optimize": 2,
                     "ascii": 1,
                     "includes":includes,
                     "bundle_files": 1}
           }
setup(
    options = options,
    zipfile=None,
    name = "Download Template",
    description = "Neon Tool",
    windows=[
            {"script": "DownloadTemplate.py",
             "icon_resources": [(1, "neon.ico"),(2, "import.ico")]
            },
        ]
    )
    