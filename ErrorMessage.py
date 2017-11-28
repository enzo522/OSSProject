#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import threading
import wx


class ErrorMsg(threading.Thread):
    def __init__(self, message):
        super(ErrorMsg, self).__init__()
        self.msg = wx.MessageDialog(None, message, "Error", wx.OK | wx.ICON_ERROR)

    def run(self):
        self.msg.ShowModal()
