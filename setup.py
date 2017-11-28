# -*- coding: utf-8 -*-
from setuptools import setup

# builder for macOS
setup(name="ytdl",
      description="YouTube Downloader",
      version="0.1",
      setup_requires=["py2app"],
      app=["__main__.py"],
      options={
          "py2app": {
              "includes": ["wx",
                           "youtube_dl"]
          }
      },
      data_files=["images/addButtonIcon.png",
                  "images/changeDirButtonIcon.png",
                  "images/changePrefIcon.png",
                  "images/infoButtonIcon.png",
                  "images/removeButtonIcon.png",
                  "images/skipButtonIcon.png",
                  "images/startButtonIcon.png",
                  "images/stopButtonIcon.png"]
      )