#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pafy
import wx

FRAME_WIDTH = 870
FRAME_HEIGHT = 480
WAIT_TIME = 0.5


# MainFrame class to handle UI
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, title="YouTube Downloader", size=(FRAME_WIDTH, FRAME_HEIGHT), style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((FRAME_WIDTH, FRAME_HEIGHT))
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self._lock = threading.RLock()

        panel = wx.Panel(self)
        vBox = wx.BoxSizer(wx.VERTICAL)
        hBoxes = []

        for i in range(5): # 5 boxsizer to place attributes properly
            hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))

        sourceLabel = wx.StaticText(panel, label="URLs:")
        self.__addButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/addButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickAddButton, self.__addButton)

        # labelGridSizer includes attributes that place on the top
        labelGridSizer = wx.GridSizer(cols=3)
        labelGridSizer.Add(sourceLabel, 0, wx.ALIGN_LEFT)
        labelGridSizer.Add(wx.StaticText(panel, size=(wx.GetDisplaySize().Width, -1)), 0, wx.EXPAND)
        labelGridSizer.Add(self.__addButton, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        hBoxes[0].Add(labelGridSizer, flag=wx.EXPAND)
        vBox.Add(hBoxes[0], flag=wx.ALL, border=10)

        # text field to input urls
        self.__sourceText = wx.TextCtrl(panel, size=(-1, wx.GetDisplaySize().Height), style=wx.TE_MULTILINE)
        hBoxes[1].Add(self.__sourceText, proportion=1)
        vBox.Add(hBoxes[1], proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # a button to change download directory
        dirBox = wx.BoxSizer(wx.HORIZONTAL)
        self.__changeDirButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/changeDirButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickChangeDirButton, self.__changeDirButton)
        dirBox.Add(self.__changeDirButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        # this text shows currently selected download directory
        self.__dirText = wx.TextCtrl(panel, value="/Users/KimSungsoo/Downloads/", size=(300, -1), style=wx.TE_READONLY)
        dirBox.Add(self.__dirText)

        # a meaningless icon
        optBox = wx.BoxSizer(wx.HORIZONTAL)
        prefIcon = wx.StaticBitmap(panel, -1, wx.Bitmap("images/changePrefIcon.png"))
        optBox.Add(prefIcon, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        # a combobox which includes all available stream options that are available on selected video
        self.__prefCombobox = wx.ComboBox(panel, size=(200, -1), style=wx.CB_DROPDOWN | wx.TE_READONLY)
        self.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.OnDropDownRefreshItems, self.__prefCombobox)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectType, self.__prefCombobox)
        optBox.Add(self.__prefCombobox)

        # optionGridSizer includes attributes which place on the center
        optionGridSizer = wx.GridSizer(cols=3)
        optionGridSizer.Add(dirBox, 0, wx.ALIGN_LEFT)
        optionGridSizer.Add(wx.StaticText(panel, size=(wx.GetDisplaySize().Width, -1)), 0, wx.EXPAND)
        optionGridSizer.Add(optBox, 0, wx.ALIGN_RIGHT)
        hBoxes[2].Add(optionGridSizer, flag=wx.EXPAND)
        vBox.Add(hBoxes[2], flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # a tabled list which includes download list
        self.__addedList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_DOUBLE)
        cols = [ "제목", "저자", "길이", "옵션", "크기", "속도", "진행률", "남은 시간", "" ] # an empty column not to spoil UI when resizing
        columnWidths = [ 230, 80, 70, 180, 70, 85, 60, 70, wx.GetDisplaySize().Width ]

        for i in range(len(cols)):
            self.__addedList.InsertColumn(i, cols[i], wx.TEXT_ALIGNMENT_CENTER)
            self.__addedList.SetColumnWidth(i, columnWidths[i])

        hBoxes[3].Add(self.__addedList, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        vBox.Add(hBoxes[3], flag=wx.LEFT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))

        self.__startButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/startButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickStartButton, self.__startButton)
        hBoxes[4].Add(self.__startButton, flag=wx.RIGHT, border=12)

        self.__skipButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/skipButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickSkipButton, self.__skipButton)
        hBoxes[4].Add(self.__skipButton, flag=wx.RIGHT, border=12)

        self.__stopButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/stopButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickStopButton, self.__stopButton)
        hBoxes[4].Add(self.__stopButton, flag=wx.RIGHT, border=12)

        self.__infoButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/infoButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickInfoButton, self.__infoButton)
        hBoxes[4].Add(self.__infoButton, flag=wx.RIGHT, border=12)

        self.__removeButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/removeButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickRemoveButton, self.__removeButton)
        hBoxes[4].Add(self.__removeButton)

        vBox.Add(hBoxes[4], flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))
        panel.SetSizer(vBox)

        self.CreateStatusBar()
        self.GetStatusBar().SetBackgroundColour("white")
        self.SetStatusText("")

        self.__downloadList = []
        self.__downloading = False

        self.__am = None # AddManager for adding urls
        self.__dm = None # DownloadManager for downloading videos

        self.Bind(wx.EVT_UPDATE_UI, self.UIUpdater)
        self.Center()
        self.Show()

        # stop all downloads before force close
    def onClose(self, event):
        if self.__am and self.__am.isAlive():
            self.__am.stop()
            self.__am.join()

        if self.__dm and self.__dm.isAlive():
            self.__dm.stop()
            self.__dm.join()

        self.Destroy()

        # UI updater to enable / disable button properly
    def UIUpdater(self, event):
        self.__addButton.Enable(not self.__downloading and self.__sourceText.GetValue() != "" and True if self.__am is None else not self.__am.isAlive())
        self.__changeDirButton.Enable(not self.__downloading)
        self.__prefCombobox.Enable(not self.__downloading and self.__addedList.SelectedItemCount == 1)

        self.__startButton.Enable(not self.__downloading and len(self.__downloadList) > 0 and self.__am is not None and not self.__am.isAlive())
        self.__skipButton.Enable(self.__downloading)
        self.__stopButton.Enable(self.__downloading)

        self.__infoButton.Enable(self.__addedList.SelectedItemCount == 1)
        self.__removeButton.Enable(not self.__downloading and self.__addedList.SelectedItemCount == 1 and self.__am is not None and not self.__am.isAlive())

        # event handler for AddButton
    def OnClickAddButton(self, event):
        if self.__sourceText.GetValue():
            urlList = []

            for i in range(self.__sourceText.GetNumberOfLines()):
                if self.__sourceText.GetLineText(i) != "": # blank is useless
                    urlList.append(self.__sourceText.GetLineText(i))

            self.__am = AddManager(urlList)
            self.__am.start()
            self.__sourceText.Clear()

        # event handler for StartButton
    def OnClickStartButton(self, event):
        self.__dm = DownloadManager(self.__downloadList, self.__dirText.GetValue())
        self.__dm.start()
        self.__downloading = True
        self.SetStatusText("Downloading...")

        # event handler for SkipButton
    def OnClickSkipButton(self, event):
        if self.__dm and self.__dm.isAlive():
            self.__dm.skip()

        # event handler for StopButton
    def OnClickStopButton(self, event):
        if self.__dm and self.__dm.isAlive():
            self.__dm.stop()

        self.__downloading = False

        # event handler for InfoButton
    def OnClickInfoButton(self, event):
        infoDialog = VideoInfoDialog(self.__downloadList[self.__addedList.GetFocusedItem()].video)
        infoDialog.Show()

        # event handler for RemoveButton
    def OnClickRemoveButton(self, event):
        with self._lock:
            toRemove = self.__downloadList.pop(self.__addedList.GetFocusedItem())

        self.__addedList.DeleteItem(self.__addedList.GetFocusedItem())
        self.SetStatusText(toRemove.video.title + " has been removed.")

        # event handler for ChangeDirButton
    def OnClickChangeDirButton(self, event):
        dialog = wx.DirDialog(None, message="test", defaultPath=self.__dirText.GetValue())

        if dialog.ShowModal() == wx.ID_OK:
            self.__dirText.SetValue(dialog.GetPath() + "/")

        dialog.Destroy()

        # event handler for dropdowned PrefCombobox
    def OnDropDownRefreshItems(self, event):
        selectedItem = self.__downloadList[self.__addedList.GetFocusedItem()]
        optList = []
        self.__prefCombobox.Clear()

        for s in selectedItem.video.allstreams: # get all the available options about selected video
            optList.append(s.mediatype + " / " + s.extension + " / " + s.quality)

        self.__prefCombobox.AppendItems(optList)

        # event handler for selecting PrefCombobox
    def OnSelectType(self, event):
        self.__downloadList[self.__addedList.GetFocusedItem()].selectedExt = self.__prefCombobox.GetStringSelection()
        self.__addedList.SetItem(self.__addedList.GetFocusedItem(), 3, self.__prefCombobox.GetStringSelection())

        # add item to list
    def AddToList(self, item):
        with self._lock:
            self.__downloadList.append(item)

        num_items = self.__addedList.GetItemCount()
        self.__addedList.InsertItem(num_items, item.video.title)
        self.__addedList.SetItem(num_items, 1, item.video.author)
        self.__addedList.SetItem(num_items, 2, item.video.duration)
        self.__addedList.SetItem(num_items, 3, item.selectedExt)

        self.SetStatusText(item.video.title + " has been added.")

        # update status of downloading item
    def UpdateStatus(self, tuple):
        selectedItem = self.__downloadList.index(tuple[0])

        if tuple[1] > 1024 ** 2: # about file size
            self.__addedList.SetItem(selectedItem, 4, round(tuple[1] / 1024 ** 2, 1).__str__() + "MB")
        else:
            self.__addedList.SetItem(selectedItem, 4, round(tuple[1] / 1024, 1).__str__() + "KB")

        if tuple[2][1] > 1024: # about download speed
            self.__addedList.SetItem(selectedItem, 5, round(tuple[2][1] / 1024, 1).__str__() + "MB/s")
        else:
            self.__addedList.SetItem(selectedItem, 5, round(tuple[2][1], 1).__str__() + "KB/s")

        # about progress rate and estimated time of arrival
        self.__addedList.SetItem(selectedItem, 6, round(tuple[2][0] * 100, 1).__str__() + "%")
        self.__addedList.SetItem(selectedItem, 7, round(tuple[2][2], 1).__str__() + "초")

        # remove item from list when downloaded
    def RemoveFinishedItem(self, item):
        with self._lock:
            self.__addedList.DeleteItem(self.__downloadList.index(item))
            self.__downloadList.remove(item)

        # set finished when all videos are downloaded
    def SetFinished(self):
        self.SetStatusText("Finished")
        self.__downloading = False


# Item class to encapsulate video and selected options (media type, extension, resolution)
class Item():
    def __init__(self, video, selectedExt):
        self.video = video
        self.selectedExt = selectedExt


import wx.grid
from wx.grid import GridCellAutoWrapStringRenderer


# InfoTable class to set information of selected video.
class InfoTable(wx.grid.Grid):
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
    def __init__(self, video):
        wx.Dialog.__init__(self, None, -1, "Info")
        panel = wx.Panel(self)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_CLOSE, self.onClose)

        tagList = [ "제   목", "저   자", "길   이", "평   점", "조회수", "좋아요", "싫어요", "설   명" ]
        infoList = [ video.title, video.author, video.duration, round(video.rating, 1).__str__(), video.viewcount.__str__(),
                     video.likes.__str__(), video.dislikes.__str__(), video.description ]

        sizer = wx.BoxSizer(wx.VERTICAL)
        dataList = []

        for i in range(8):
            data = (tagList[i], infoList[i])
            dataList.append(data)

        sizer.Add(InfoTable(self, dataList), flag=wx.ALL, border=10)
        panel.SetSizerAndFit(sizer)
        self.Fit()

    def onClose(self, event):
        self.Destroy()


from time import sleep
import threading


# AddManager class to add urls to download list.
class AddManager(threading.Thread):
    def __init__(self, urlList):
        super(AddManager, self).__init__()
        self.__urlList = urlList
        self.__isRunning = True
        self._lock = threading.RLock()

    def run(self):
        for url in self.__urlList:
            if self.__isRunning:
                video = pafy.new(url)

                if video._have_basic: # check current url is available
                    default = video.getbest() # default selected options are the best ones that current video has

                    with self._lock:
                        frame.AddToList(Item(video, default.mediatype + " / " + default.extension + " / " + default.resolution))

                    sleep(WAIT_TIME)

    def stop(self):
        self.__isRunning = False

    def join(self, timeout=None):
        super(AddManager, self).join(timeout)


from Queue import Queue


# DownloadManager class to download selected videos.
class DownloadManager(threading.Thread):
    def __init__(self, itemList, dir):
        super(DownloadManager, self).__init__()
        self.__dir = dir
        self.__queue = Queue(len(itemList)) # a queue to download in order
        self.__threadList = []
        self.__isRunning = True
        self.__abort = False
        self._lock = threading.RLock()

        for item in itemList:
            self.__queue.put(item)

    def run(self):
        while self.__isRunning:
            if len(self.__threadList) < 3: # download 3 videos simultaneously
                if not self.__queue.empty():
                    dl = Downloader(self.__queue.get(), self.__dir, self.__abort)
                    self.__threadList.append(dl)
                    dl.start()
                    sleep(WAIT_TIME)

            for t in self.__threadList:
                if not t.isAlive():
                    self.__threadList.remove(t)
                else: # update download progress
                    frame.UpdateStatus(t.status())
                    sleep(WAIT_TIME)

            if len(self.__threadList) <= 0 and self.__queue.empty(): # when every video is completed
                self.__isRunning = False

        with self._lock:
            frame.SetFinished()

    def skip(self): # cancel current downloads
        with self._lock:
            for t in self.__threadList:
                if t.isAlive():
                    t.stop()

    def stop(self): # cancel current downloads and abort further ones
        self.skip()
        self.__abort = True

    def join(self, timeout=None):
        super(DownloadManager, self).join(timeout)


# Downloader class to download a video.
class Downloader(threading.Thread):
    def __init__(self, item, downloadPath, abort):
        super(Downloader, self).__init__()
        self.__item = item
        self.__stream = None
        self.__abort = abort
        self.__filename = downloadPath + self.__item.video.title + "."
        self._lock = threading.RLock()

        for s in self.__item.video.allstreams: # find a stream which satisfies selected options
            if self.__item.selectedExt == s.mediatype + " / " + s.extension + " / " + s.quality:
                self.__stream = s
                break

    def status(self): # current download progress about this video
        return self.__item, self.__stream.get_filesize(), self.__stream.progress_stats

    def run(self): # if the user clicked stop button, the downloader shouldn't start download
        if not self.__abort: # otherwise, check whether the user has already downloaded this video
            if not os.path.exists(self.__filename + self.__stream.extension):
                self.__stream.download(filepath=self.__filename + self.__stream.extension)

        with self._lock:
            frame.RemoveFinishedItem(self.__item)

    def stop(self): # when the user clicked skip / stop button, current download should be canceled
        if self.__stream:
            self.__stream.cancel()

    def join(self, timeout=None):
        super(Downloader, self).join(timeout)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
