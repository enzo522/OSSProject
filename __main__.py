#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import wx
from mainframe import MainFrame

app = wx.App()
frame = MainFrame()
app.MainLoop()
