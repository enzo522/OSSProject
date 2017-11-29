# -*- coding: utf-8 -*-
from setuptools import setup
import os

    # builder for Windows
if os.name == "nt":
    import py2exe

    platform_options = {
        "windows": [ {
            "script": "__main__.py"
        } ],
        "zipfile": None,
        "setup_requires": ["py2exe"],
        "options": {
            "py2exe": {
                "includes": ["wx",
                             "youtube_dl"],
                "dll_excludes": ["w9xpopen.exe",
                                 "msvcr71.dll",
                                 "MSVCP90.dll"],
                "compressed": True
            }
        }
    }
else:
    # builder for macOS
    platform_options = {
        "setup_requires": ["py2app"],
        "app": ["__main__.py"],
        "options": {
            "py2app": {
                "argv_emulation": True,
                "includes": ["wx",
                             "youtube_dl"]
            }
        }
    }
setup(name="ytdl",
      description="YouTube Downloader",
      version="0.1",
      data_files=["images/addButtonIcon.png",
                  "images/changeDirButtonIcon.png",
                  "images/changePrefIcon.png",
                  "images/infoButtonIcon.png",
                  "images/removeButtonIcon.png",
                  "images/skipButtonIcon.png",
                  "images/startButtonIcon.png",
                  "images/stopButtonIcon.png"],
      **platform_options
      )
