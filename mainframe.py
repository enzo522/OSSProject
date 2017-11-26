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
        self.addButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/addButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickAddButton, self.addButton)

        # labelGridSizer includes attributes that place on the top
        labelGridSizer = wx.GridSizer(cols=3)
        labelGridSizer.Add(sourceLabel, 0, wx.ALIGN_LEFT)
        labelGridSizer.Add(wx.StaticText(panel, size=(wx.GetDisplaySize().Width, -1)), 0, wx.EXPAND)
        labelGridSizer.Add(self.addButton, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        hBoxes[0].Add(labelGridSizer, flag=wx.EXPAND)
        vBox.Add(hBoxes[0], flag=wx.ALL, border=10)

        # text field to input urls
        self.sourceText = wx.TextCtrl(panel, size=(-1, wx.GetDisplaySize().Height), style=wx.TE_MULTILINE)
        hBoxes[1].Add(self.sourceText, proportion=1)
        vBox.Add(hBoxes[1], proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # a button to change download directory
        dirBox = wx.BoxSizer(wx.HORIZONTAL)
        self.changeDirButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/changeDirButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickChangeDirButton, self.changeDirButton)
        dirBox.Add(self.changeDirButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        # this text shows currently selected download directory
        self.dirText = wx.TextCtrl(panel, value="/Users/KimSungsoo/Downloads/", size=(300, -1), style=wx.TE_READONLY)
        dirBox.Add(self.dirText)

        # a meaningless icon
        optBox = wx.BoxSizer(wx.HORIZONTAL)
        prefIcon = wx.StaticBitmap(panel, -1, wx.Bitmap("images/changePrefIcon.png"))
        optBox.Add(prefIcon, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        # a combobox which includes all available stream options that are available on selected video
        self.prefCombobox = wx.ComboBox(panel, size=(200, -1), style=wx.CB_DROPDOWN | wx.TE_READONLY)
        self.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.OnDropDownRefreshItems, self.prefCombobox)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectType, self.prefCombobox)
        optBox.Add(self.prefCombobox)

        # optionGridSizer includes attributes which place on the center
        optionGridSizer = wx.GridSizer(cols=3)
        optionGridSizer.Add(dirBox, 0, wx.ALIGN_LEFT)
        optionGridSizer.Add(wx.StaticText(panel, size=(wx.GetDisplaySize().Width, -1)), 0, wx.EXPAND)
        optionGridSizer.Add(optBox, 0, wx.ALIGN_RIGHT)
        hBoxes[2].Add(optionGridSizer, flag=wx.EXPAND)
        vBox.Add(hBoxes[2], flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # a tabled list which includes download list
        self.addedList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_DOUBLE)
        cols = [ "제목", "저자", "길이", "옵션", "크기", "속도", "진행률", "남은 시간", "" ] # an empty column not to spoil UI when resizing
        columnWidths = [ 230, 80, 70, 180, 70, 85, 60, 70, wx.GetDisplaySize().Width ]

        for i in range(len(cols)):
            self.addedList.InsertColumn(i, cols[i], wx.TEXT_ALIGNMENT_CENTER)
            self.addedList.SetColumnWidth(i, columnWidths[i])

        hBoxes[3].Add(self.addedList, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        vBox.Add(hBoxes[3], flag=wx.LEFT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))

        self.startButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/startButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickStartButton, self.startButton)
        hBoxes[4].Add(self.startButton, flag=wx.RIGHT, border=12)

        self.skipButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/skipButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickSkipButton, self.skipButton)
        hBoxes[4].Add(self.skipButton, flag=wx.RIGHT, border=12)

        self.stopButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/stopButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickStopButton, self.stopButton)
        hBoxes[4].Add(self.stopButton, flag=wx.RIGHT, border=12)

        self.infoButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/infoButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickInfoButton, self.infoButton)
        hBoxes[4].Add(self.infoButton, flag=wx.RIGHT, border=12)

        self.removeButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/removeButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.OnClickRemoveButton, self.removeButton)
        hBoxes[4].Add(self.removeButton)

        vBox.Add(hBoxes[4], flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))
        panel.SetSizer(vBox)

        self.CreateStatusBar()
        self.GetStatusBar().SetBackgroundColour("white")
        self.SetStatusText("")

        self.downloadList = []
        self.downloading = False

        self.am = None # AddManager for adding urls
        self.dm = None # DownloadManager for downloading videos

        self.Bind(wx.EVT_UPDATE_UI, self.UIUpdater)
        self.Center()
        self.Show()

        # stop all downloads before force close
    def onClose(self, event):
        if self.am and self.am.isAlive():
            self.am.stop()
            self.am.join()

        if self.dm and self.dm.isAlive():
            self.dm.stop()
            self.dm.join()

        self.Destroy()

        # UI updater to enable / disable button properly
    def UIUpdater(self, event):
        self.addButton.Enable(not self.downloading and self.sourceText.GetValue() != "" and True if self.am is None else not self.am.isAlive())
        self.changeDirButton.Enable(not self.downloading)
        self.prefCombobox.Enable(not self.downloading and self.addedList.SelectedItemCount == 1)

        self.startButton.Enable(not self.downloading and len(self.downloadList) > 0 and self.am is not None and not self.am.isAlive())
        self.skipButton.Enable(self.downloading)
        self.stopButton.Enable(self.downloading)

        self.infoButton.Enable(self.addedList.SelectedItemCount == 1)
        self.removeButton.Enable(not self.downloading and self.addedList.SelectedItemCount == 1 and self.am is not None and not self.am.isAlive())

        # event handler for AddButton
    def OnClickAddButton(self, event):
        if self.sourceText.GetValue():
            urlList = []

            for i in range(self.sourceText.GetNumberOfLines()):
                if self.sourceText.GetLineText(i) != "": # blank is useless
                    urlList.append(self.sourceText.GetLineText(i))

            self.am = AddManager(urlList)
            self.am.start()
            self.sourceText.Clear()

        # event handler for StartButton
    def OnClickStartButton(self, event):
        self.dm = DownloadManager(self.downloadList, self.dirText.GetValue())
        self.dm.start()
        self.downloading = True
        self.SetStatusText("Downloading...")

        # event handler for SkipButton
    def OnClickSkipButton(self, event):
        if self.dm and self.dm.isAlive():
            self.dm.skip()

        # event handler for StopButton
    def OnClickStopButton(self, event):
        if self.dm and self.dm.isAlive():
            self.dm.stop()

        self.downloading = False

        # event handler for InfoButton
    def OnClickInfoButton(self, event):
        infoDialog = VideoInfoDialog(self.downloadList[self.addedList.GetFocusedItem()].video)
        infoDialog.Show()

        # event handler for RemoveButton
    def OnClickRemoveButton(self, event):
        with self._lock:
            toRemove = self.downloadList.pop(self.addedList.GetFocusedItem())

        self.addedList.DeleteItem(self.addedList.GetFocusedItem())
        self.SetStatusText(toRemove.video.title + " has been removed.")

        # event handler for ChangeDirButton
    def OnClickChangeDirButton(self, event):
        dialog = wx.DirDialog(None, message="test", defaultPath=self.dirText.GetValue())

        if dialog.ShowModal() == wx.ID_OK:
            self.dirText.SetValue(dialog.GetPath() + "/")

        dialog.Destroy()

        # event handler for dropdowned PrefCombobox
    def OnDropDownRefreshItems(self, event):
        selectedItem = self.downloadList[self.addedList.GetFocusedItem()]
        optList = []
        self.prefCombobox.Clear()

        for s in selectedItem.video.allstreams: # get all the available options about selected video
            optList.append(s.mediatype + " / " + s.extension + " / " + s.quality)

        self.prefCombobox.AppendItems(optList)

        # event handler for selecting PrefCombobox
    def OnSelectType(self, event):
        self.downloadList[self.addedList.GetFocusedItem()].selectedExt = self.prefCombobox.GetStringSelection()
        self.addedList.SetItem(self.addedList.GetFocusedItem(), 3, self.prefCombobox.GetStringSelection())

        # add item to list
    def AddToList(self, item):
        with self._lock:
            self.downloadList.append(item)

        num_items = self.addedList.GetItemCount()
        self.addedList.InsertItem(num_items, item.video.title)
        self.addedList.SetItem(num_items, 1, item.video.author)
        self.addedList.SetItem(num_items, 2, item.video.duration)
        self.addedList.SetItem(num_items, 3, item.selectedExt)

        self.SetStatusText(item.video.title + " has been added.")

        # update status of downloading item
    def UpdateStatus(self, tuple):
        index = tuple[0]

        if tuple[1] > 1000000: # about file size
            self.addedList.SetItem(self.downloadList.index(index), 4, round(tuple[1] / 1000000, 1).__str__() + "MB")
        else:
            self.addedList.SetItem(self.downloadList.index(index), 4, round(tuple[1] / 1000, 1).__str__() + "KB")

        if tuple[2][1] > 1000: # about download speed
            self.addedList.SetItem(self.downloadList.index(index), 5, round(tuple[2][1] / 1000, 1).__str__() + "MB/s")
        else:
            self.addedList.SetItem(self.downloadList.index(index), 5, round(tuple[2][1], 1).__str__() + "KB/s")

        # about progress rate and estimated time of arrival
        self.addedList.SetItem(self.downloadList.index(index), 6, round(tuple[2][0] * 100, 1).__str__() + "%")
        self.addedList.SetItem(self.downloadList.index(index), 7, round(tuple[2][2], 1).__str__() + "초")

        # remove item from list when downloaded
    def RemoveFinishedItem(self, item):
        with self._lock:
            self.addedList.DeleteItem(self.downloadList.index(item))
            self.downloadList.remove(item)

        # set finished when all videos are downloaded
    def SetFinished(self):
        self.SetStatusText("Finished")
        self.downloading = False


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
        self.urlList = urlList
        self.isRunning = True
        self._lock = threading.RLock()

    def run(self):
        for url in self.urlList:
            if self.isRunning:
                video = pafy.new(url)

                if video._have_basic: # check current url is available
                    default = video.getbest() # default selected options are the best ones that current video has

                    with self._lock:
                        frame.AddToList(Item(video, default.mediatype + " / " + default.extension + " / " + default.resolution))

                    sleep(WAIT_TIME)

    def stop(self):
        self.isRunning = False

    def join(self, timeout=None):
        super(AddManager, self).join(timeout)


from Queue import Queue


# DownloadManager class to download selected videos.
class DownloadManager(threading.Thread):
    def __init__(self, itemList, dir):
        super(DownloadManager, self).__init__()
        self.dir = dir
        self.queue = Queue(len(itemList)) # a queue to make it download in order
        self.threadList = []
        self.isRunning = True
        self.abort = False
        self._lock = threading.RLock()

        for item in itemList:
            self.queue.put(item)

    def run(self):
        while self.isRunning:
            if len(self.threadList) < 3: # download 3 videos simultaneously
                if not self.queue.empty():
                    dl = Downloader(self.queue.get(), self.dir, self.abort)
                    self.threadList.append(dl)
                    dl.start()
                    sleep(WAIT_TIME)

            for t in self.threadList:
                if not t.isAlive():
                    self.threadList.remove(t)
                else:
                    with self._lock: # update download progress
                        frame.UpdateStatus(t.status())

                    sleep(WAIT_TIME)

            if len(self.threadList) <= 0 and self.queue.empty(): # when every video is completed
                self.isRunning = False

        with self._lock:
            frame.SetFinished()

    def skip(self): # cancel current download
        for t in self.threadList:
            if t.isAlive():
                t.stop()

    def stop(self): # cancel current download and abort further videos
        self.skip()
        self.abort = True

    def join(self, timeout=None):
        super(DownloadManager, self).join(timeout)


# Downloader class to download a video.
class Downloader(threading.Thread):
    def __init__(self, item, downloadPath, abort):
        super(Downloader, self).__init__()
        self.item = item
        self.stream = None
        self.abort = abort
        self.downloadPath = downloadPath
        self._lock = threading.RLock()

        for s in self.item.video.allstreams: # find a stream which satisfy selected options
            if self.item.selectedExt == s.mediatype + " / " + s.extension + " / " + s.quality:
                self.stream = s
                break

    def status(self): # current download progress about this video
        return self.item, self.stream.get_filesize(), self.stream.progress_stats

    def run(self): # if the user clicked stop button, the downloader shouldn't start download
        if not self.abort: # otherwise, check whether the user has already downloaded this video
            if not os.path.exists(self.downloadPath + self.stream.title + "." + self.stream.extension):
                self.stream.download(filepath=self.downloadPath + self.stream.title + "." + self.stream.extension)

        with self._lock:
            frame.RemoveFinishedItem(self.item)

    def stop(self): # when the user clicked skip / stop button, current download should be canceled
        if self.stream:
            self.stream.cancel()

    def join(self, timeout=None):
        super(Downloader, self).join(timeout)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
