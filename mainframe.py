#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pafy
import wx

FRAME_WIDTH = 870
FRAME_HEIGHT = 480
WAIT_TIME = 0.2


# MainFrame class to handle UI
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, title="YouTube Downloader", size=(FRAME_WIDTH, FRAME_HEIGHT), \
                          style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((FRAME_WIDTH, FRAME_HEIGHT))
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_CLOSE, self.__onClose)

        panel = wx.Panel(self)
        vBox = wx.BoxSizer(wx.VERTICAL)
        hBoxes = []

        for i in range(5): # 5 boxsizer to place attributes properly
            hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))

        sourceLabel = wx.StaticText(panel, label="URLs:")
        self.__addButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/addButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__onClickAddButton, self.__addButton)

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
        self.Bind(wx.EVT_BUTTON, self.__onClickChangeDirButton, self.__changeDirButton)
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
        self.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.__onDropdownPrefCombobox, self.__prefCombobox)
        self.Bind(wx.EVT_COMBOBOX, self.__onSelectOption, self.__prefCombobox)
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

        # add 5 buttons (start, skip, stop, info, remove)
        self.__startButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/startButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__onClickStartButton, self.__startButton)
        hBoxes[4].Add(self.__startButton, flag=wx.RIGHT, border=12)

        self.__skipButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/skipButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__onClickSkipButton, self.__skipButton)
        hBoxes[4].Add(self.__skipButton, flag=wx.RIGHT, border=12)

        self.__stopButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/stopButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__onClickStopButton, self.__stopButton)
        hBoxes[4].Add(self.__stopButton, flag=wx.RIGHT, border=12)

        self.__infoButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/infoButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__onClickInfoButton, self.__infoButton)
        hBoxes[4].Add(self.__infoButton, flag=wx.RIGHT, border=12)

        self.__removeButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/removeButtonIcon.png"), style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self.__onClickRemoveButton, self.__removeButton)
        hBoxes[4].Add(self.__removeButton)

        vBox.Add(hBoxes[4], flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))
        panel.SetSizer(vBox)

        # status bar to show events
        self.CreateStatusBar()
        self.GetStatusBar().SetBackgroundColour("white")
        self.SetStatusText("")

        self.__downloadList = []
        self.__downloading = False

        self.__am = None # AddManager for adding urls
        self.__dm = None # DownloadManager for downloading videos

        self.Bind(wx.EVT_UPDATE_UI, self.__UIUpdater)
        self.Center()
        self.Show()

        # stop all threads before force close
    def __onClose(self, event):
        if self.__am and self.__am.isAlive():
            self.__am.stop()
            self.__am.join()

        if self.__dm and self.__dm.isAlive():
            self.__dm.stop()
            self.__dm.join()

        self.Destroy()

        # UI updater to enable / disable buttons properly
    def __UIUpdater(self, event):
        self.__addButton.Enable(not self.__downloading and self.__sourceText.GetValue() != "" and \
                                True if self.__am is None else not self.__am.isAlive())
        self.__changeDirButton.Enable(not self.__downloading)
        self.__prefCombobox.Enable(not self.__downloading and self.__addedList.SelectedItemCount == 1)

        self.__startButton.Enable(not self.__downloading and len(self.__downloadList) > 0 and \
                                  self.__am is not None and not self.__am.isAlive())
        self.__skipButton.Enable(self.__downloading)
        self.__stopButton.Enable(self.__downloading)

        self.__infoButton.Enable(self.__addedList.SelectedItemCount == 1)
        self.__removeButton.Enable(not self.__downloading and self.__addedList.SelectedItemCount == 1 \
                                   and self.__am is not None and not self.__am.isAlive())

        # event handler for AddButton
    def __onClickAddButton(self, event):
        if self.__sourceText.GetValue():
            urlList = []

            for i in range(self.__sourceText.GetNumberOfLines()):
                if self.__sourceText.GetLineText(i) != "": # blank is useless
                    urlList.append(self.__sourceText.GetLineText(i))

            self.__am = AddManager(urlList)
            self.__am.start()
            self.__sourceText.Clear()

        # event handler for StartButton
    def __onClickStartButton(self, event):
        self.__dm = DownloadManager(self.__downloadList, self.__dirText.GetValue())
        self.__dm.start()
        self.__downloading = True
        self.SetStatusText("Downloading...")

        # event handler for SkipButton
    def __onClickSkipButton(self, event):
        if self.__dm and self.__dm.isAlive():
            self.__dm.skip()

        # event handler for StopButton
    def __onClickStopButton(self, event):
        if self.__dm and self.__dm.isAlive():
            self.__dm.stop()

        self.__downloading = False

        # event handler for InfoButton
    def __onClickInfoButton(self, event):
        infoDialog = VideoInfoDialog(self.__downloadList[self.__addedList.GetFocusedItem()].video)
        infoDialog.Show()

        # event handler for RemoveButton
    def __onClickRemoveButton(self, event):
        toRemove = self.__downloadList.pop(self.__addedList.GetFocusedItem())

        self.__addedList.DeleteItem(self.__addedList.GetFocusedItem())
        self.SetStatusText(toRemove.video.title + " has been removed.")

        # event handler for ChangeDirButton
    def __onClickChangeDirButton(self, event):
        dialog = wx.DirDialog(None, message="test", defaultPath=self.__dirText.GetValue())

        if dialog.ShowModal() == wx.ID_OK:
            self.__dirText.SetValue(dialog.GetPath() + "/")

        dialog.Destroy()

        # event handler for dropdowned PrefCombobox
    def __onDropdownPrefCombobox(self, event):
        selectedItem = self.__downloadList[self.__addedList.GetFocusedItem()]
        self.__prefCombobox.Clear()
        self.__prefCombobox.AppendItems(selectedItem.options)

        # event handler for selecting PrefCombobox
    def __onSelectOption(self, event):
        selectedItem = self.__addedList.GetFocusedItem()
        self.__downloadList[selectedItem].setSelectedExt(self.__prefCombobox.GetStringSelection())
        self.__addedList.SetItem(selectedItem, 3, self.__downloadList[selectedItem].selectedExt)
        self.__addedList.SetItem(selectedItem, 4, self.__downloadList[selectedItem].filesize)

        # add item to list
    def addToDownloadList(self, item):
        self.__downloadList.append(item)
        num_items = self.__addedList.GetItemCount()

        self.__addedList.InsertItem(num_items, item.video.title)
        self.__addedList.SetItem(num_items, 1, item.video.author)
        self.__addedList.SetItem(num_items, 2, item.video.duration)
        self.__addedList.SetItem(num_items, 3, item.selectedExt)
        self.__addedList.SetItem(num_items, 4, item.filesize)

        self.SetStatusText(item.video.title + " has been added.")

        # update status of downloading item
    def updateStatus(self, item, rate, progress, eta):
        selectedItem = self.__downloadList.index(item)
        self.__addedList.SetItem(selectedItem, 5, rate)
        self.__addedList.SetItem(selectedItem, 6, progress)
        self.__addedList.SetItem(selectedItem, 7, eta)

        # remove item from list when downloaded
    def removeFinishedItem(self, item):
        self.__addedList.DeleteItem(self.__downloadList.index(item))
        self.__downloadList.remove(item)

        # set finished when all videos are downloaded
    def setFinished(self):
        self.SetStatusText("Finished")
        self.__downloading = False


# Item class to encapsulate video and selected options (media type, extension, resolution)
class Item():
    def __init__(self, video, selectedExt):
        self.video = video
        self.selectedExt = selectedExt
        self.filesize = None
        self.__sizes = []
        self.options = []

        for s in self.video.allstreams:
            self.options.append(s.mediatype + " / " + s.extension + " / " + s.quality)
            self.__sizes.append(s.get_filesize())

        self.__calcFilesize()

    def __calcFilesize(self):
        orgFilesize = None

        for i in range(len(self.options)):
            if self.selectedExt == self.options[i]:
                orgFilesize = self.__sizes[i]

        self.filesize = round(orgFilesize / 1024 ** 2, 1).__str__() + "MB" if orgFilesize > 1024 ** 2 else \
                round(orgFilesize / 1024, 1).__str__() + "KB" \
            if orgFilesize is not None \
            else "-"

    def setSelectedExt(self, newExt):
        self.selectedExt = newExt
        self.__calcFilesize()


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
        self.Bind(wx.EVT_CLOSE, self.__onClose)

        tagList = [ "제   목", "저   자", "길   이", "평   점", "조회수", "좋아요", "싫어요", "설   명" ]
        infoList = [ video.title, video.author, video.duration, round(video.rating, 1).__str__(), \
                     video.viewcount.__str__(), video.likes.__str__(), video.dislikes.__str__(), video.description ]

        sizer = wx.BoxSizer(wx.VERTICAL)
        dataList = []

        for i in range(8):
            data = (tagList[i], infoList[i])
            dataList.append(data)

        sizer.Add(InfoTable(self, dataList), flag=wx.ALL, border=10)
        panel.SetSizerAndFit(sizer)
        self.Fit()

    def __onClose(self, event):
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
                        frame.addToDownloadList(Item(video, default.mediatype + " / " + default.extension + " / " + \
                                             default.resolution))

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
                    break
                else: # update download progress
                    t.updateStatus()
                    sleep(WAIT_TIME)

            if len(self.__threadList) <= 0 and self.__queue.empty(): # when every video is completed
                self.__isRunning = False

        with self._lock:
            frame.setFinished()

    def skip(self): # cancel current downloads
        for t in self.__threadList:
            if t.isAlive():
                t.stop()
                t.join()

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

    def updateStatus(self): # current download progress about this video
        if self.__stream.has_stats:
            stats = self.__stream.progress_stats
            rate = round(stats[0] * 100, 1).__str__() + "%"
            progress = round(stats[1] / 1024, 1).__str__() + "MB/s" if stats[1] > 1024 else \
                round(stats[1], 1).__str__() + "KB/s"
            eta = round(stats[2], 1).__str__() + "초"
            
            frame.updateStatus(self.__item, progress, rate, eta)

    def run(self): # if the user clicked stop button, the downloader shouldn't start download
        if not self.__abort: # otherwise, check whether the user has already downloaded this video
            if not os.path.exists(self.__filename + self.__stream.extension):
                self.__stream.download(filepath=self.__filename + self.__stream.extension, quiet=True)

        with self._lock:
            frame.removeFinishedItem(self.__item)

    def stop(self): # when the user clicked skip / stop button, current download should be canceled
        if self.__stream:
            self.__stream.cancel()

    def join(self, timeout=None):
        super(Downloader, self).join(timeout)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
