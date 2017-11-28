#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import wx.grid
from wx.grid import GridCellAutoWrapStringRenderer


# InfoTable class to set information of selected video.
class _InfoTable(wx.grid.Grid):
    def __init__(self, parent, dataList):
        wx.grid.Grid.__init__(self, parent, -1)

        self.CreateGrid(8, 1)
        self.SetColLabelSize(1)
        self.SetLabelBackgroundColour("white")
        self.EnableEditing(False)

        for i in range(8):
            self.SetRowLabelValue(i, dataList[i][0])
            self.SetCellValue(i, 0, dataList[i][1])
            self.SetCellRenderer(i, 0, GridCellAutoWrapStringRenderer())

        self.AutoSize()


# VideoInfoDialog class to show information table which was made by InfoTable object.
class VideoInfoDialog(wx.Dialog):
    def __init__(self, video, x, y):
        wx.Dialog.__init__(self, None, -1, "Info")
        panel = wx.Panel(self)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_CLOSE, self.__onClose)

        tagList = [ "제   목", "저   자", "길   이", "평   점", "조회수", "좋아요", "싫어요", "설   명" ]
        infoList = [ video.title, video.author, video.duration, round(video.rating, 1).__str__(), \
                     video.viewcount.__str__(), video.likes.__str__(), video.dislikes.__str__(), video.description ]

        sizer = wx.BoxSizer(wx.VERTICAL)
        dataList = []

        for i in range(8):
            data = (tagList[i], infoList[i])
            dataList.append(data)

        sizer.Add(_InfoTable(self, dataList), flag=wx.ALL, border=10)
        panel.SetSizerAndFit(sizer)
        self.Fit()

        if x > 0 and y > 0:
            self.Move(self.GetPosition().__iadd__((x, y)))

    def __onClose(self, event):
        self.Destroy()

    def show(self):
        self.Show()
