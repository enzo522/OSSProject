#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def resource_path(relative_path): # a global method to return relative path
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)

import os
import threading
import wx
from addmanager import AddManager
from downloadmanager import DownloadManager
from info import VideoInfoDialog

FRAME_WIDTH = 870
FRAME_HEIGHT = 480
BACKGROUND_COLOR = "white"
DEFAULT_DIR = "default.dir"


# MainFrame class to handle UI
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, title="YouTube Downloader", size=(FRAME_WIDTH, FRAME_HEIGHT), \
                          style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((FRAME_WIDTH, FRAME_HEIGHT))
        self.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_CLOSE, self.__onClose)

        panel = wx.Panel(self)
        vBox = wx.BoxSizer(wx.VERTICAL)
        hBoxes = []

        for i in range(5): # 5 boxsizer to place attributes properly
            hBoxes.append(wx.BoxSizer(wx.HORIZONTAL))

        sourceLabel = wx.StaticText(panel, label="URLs:")
        self.__addButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/addButtonIcon.png")), style=wx.NO_BORDER)
        self.__addButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickAddButton, self.__addButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanAdd, self.__addButton)

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
        self.__changeDirButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/changeDirButtonIcon.png")), style=wx.NO_BORDER)
        self.__changeDirButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickChangeDirButton, self.__changeDirButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanChangeDir, self.__changeDirButton)
        dirBox.Add(self.__changeDirButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        defaultDir = ""
        # set default download directory
        if os.path.exists(DEFAULT_DIR): # if the user has already set default directory, read it
            dirFile = open(DEFAULT_DIR, "r")
            defaultDir = dirFile.readline()
            dirFile.close()

            if not os.path.exists(defaultDir): # if saved default directory is corrupt, remove it and let user reset it
                os.remove(DEFAULT_DIR)
                os.execl(sys.executable, sys.executable, *sys.argv) # restart this program
        else: # otherwise, make the user set default directory
            dialog = wx.DirDialog(None)

            if dialog.ShowModal() == wx.ID_OK:
                defaultDir = dialog.GetPath()

                if os.name == "nt": # setting directory for Windows
                    if not defaultDir.endswith("\\"):
                        defaultDir += "\\"
                else: # for Linux or macOS
                    if not defaultDir.endswith("/"):
                        defaultDir += "/"

                dirFile = open(DEFAULT_DIR, "w")
                dirFile.write(defaultDir)
                dirFile.close()
            else: # if the user click cancel, program should be exited
                self.Destroy()

            dialog.Destroy()

        # this text shows currently selected download directory
        self.__dirText = wx.TextCtrl(panel, value=defaultDir, size=(300, -1), style=wx.TE_READONLY)
        dirBox.Add(self.__dirText)

        # a meaningless icon
        optBox = wx.BoxSizer(wx.HORIZONTAL)
        prefIcon = wx.StaticBitmap(panel, -1, wx.Bitmap(resource_path("images/changePrefIcon.png")))
        prefIcon.SetBackgroundColour(BACKGROUND_COLOR)
        optBox.Add(prefIcon, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        # a combobox which includes all available stream options that are available on selected video
        self.__prefCombobox = wx.ComboBox(panel, size=(200, -1), style=wx.CB_DROPDOWN | wx.TE_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.__onSelectOption, self.__prefCombobox)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanChangeOption, self.__prefCombobox)
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
            self.__addedList.InsertColumn(i, cols[i], wx.TEXT_ALIGNMENT_RIGHT if i == 0 else wx.TEXT_ALIGNMENT_CENTER)
            self.__addedList.SetColumnWidth(i, columnWidths[i])

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__onSelectItem, self.__addedList)
        hBoxes[3].Add(self.__addedList, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        vBox.Add(hBoxes[3], flag=wx.LEFT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))

        # add 6 buttons (start, pause, skip, stop, info, remove)
        self.__startButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/startButtonIcon.png")), style=wx.NO_BORDER)
        self.__startButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickStartButton, self.__startButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanStart, self.__startButton)
        hBoxes[4].Add(self.__startButton, flag=wx.RIGHT, border=12)

        self.__pauseButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/pauseButtonIcon.png")), style=wx.NO_BORDER)
        self.__pauseButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickPauseButton, self.__pauseButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanPause, self.__pauseButton)
        hBoxes[4].Add(self.__pauseButton, flag=wx.RIGHT, border=12)

        self.__skipButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/skipButtonIcon.png")), style=wx.NO_BORDER)
        self.__skipButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickSkipButton, self.__skipButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanSkip, self.__skipButton)
        hBoxes[4].Add(self.__skipButton, flag=wx.RIGHT, border=12)

        self.__stopButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/stopButtonIcon.png")), style=wx.NO_BORDER)
        self.__stopButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickStopButton, self.__stopButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanStop, self.__stopButton)
        hBoxes[4].Add(self.__stopButton, flag=wx.RIGHT, border=12)

        self.__infoButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/infoButtonIcon.png")), style=wx.NO_BORDER)
        self.__infoButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickInfoButton, self.__infoButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanShowInfo, self.__infoButton)
        hBoxes[4].Add(self.__infoButton, flag=wx.RIGHT, border=12)

        self.__removeButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/removeButtonIcon.png")), style=wx.NO_BORDER)
        self.__removeButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickRemoveButton, self.__removeButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanRemove, self.__removeButton)
        hBoxes[4].Add(self.__removeButton)

        vBox.Add(hBoxes[4], flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))
        panel.SetSizer(vBox)

        # status bar to show events
        self.CreateStatusBar()
        self.GetStatusBar().SetBackgroundColour(BACKGROUND_COLOR)
        self.SetStatusText("")

        self.__downloadList = []
        self.__downloading = False

        self.__am = None # AddManager for adding urls
        self.__dm = None # DownloadManager for downloading videos
        self._lock = threading.Lock()

        self.Center()
        self.Show()

        # stop all threads before force close
    def __onClose(self, event):
        if self.__am and self.__am.isAlive():
            self.__am.stop()

        if self.__dm and self.__dm.isAlive():
            self.__dm.pause()

        self.Destroy()

        # UI updater for AddButton
    def __onCheckCanAdd(self, event):
        event.Enable(not self.__downloading and self.__sourceText.GetValue() != "" and \
                     (True if self.__am is None else not self.__am.isAlive()))

        # UI updater for ChangeDirButton
    def __onCheckCanChangeDir(self, event):
        event.Enable(not self.__downloading)

        # UI updater for PrefCombobox
    def __onCheckCanChangeOption(self, event):
        event.Enable(not self.__downloading and self.__addedList.GetSelectedItemCount() == 1)

        # UI updater for StartButton
    def __onCheckCanStart(self, event):
        event.Enable(not self.__downloading and len(self.__downloadList) > 0 and \
                     self.__am is not None and not self.__am.isAlive())

        # UI updater for PauseButton
    def __onCheckCanPause(self, event):
        event.Enable(self.__downloading)

        # UI updater for SkipButton
    def __onCheckCanSkip(self, event):
        event.Enable(self.__downloading)

        # UI updater for StopButton
    def __onCheckCanStop(self, event):
        event.Enable(self.__downloading and self.__addedList.GetSelectedItemCount() == 1 and \
                     self.__dm is not None and self.__dm.isAlive() and \
                     self.__dm.isDownloading(self.__addedList.GetFocusedItem()))

        # UI updater for InfoButton
    def __onCheckCanShowInfo(self, event):
        event.Enable(self.__addedList.GetSelectedItemCount() > 0)

        # UI updater for RemoveButton
    def __onCheckCanRemove(self, event):
        event.Enable(not self.__downloading and self.__addedList.GetSelectedItemCount() > 0 and \
                     self.__am is not None and not self.__am.isAlive())

        # event handler for AddButton
    def __onClickAddButton(self, event):
        urls = []

        for i in range(self.__sourceText.GetNumberOfLines()):
            if self.__sourceText.GetLineText(i) != "": # skip blank
                urls.append(self.__sourceText.GetLineText(i))

        self.__am = AddManager(self, urls, self._lock)
        self.__am.start()
        self.__sourceText.Clear()

        # event handler for StartButton
    def __onClickStartButton(self, event):
        self.__dm = DownloadManager(self, self.__downloadList, self.__dirText.GetValue(), self._lock)
        self.__dm.start()
        self.__downloading = True
        self.__prefCombobox.Clear()
        self.SetStatusText("Downloading...")

        # event handler for PauseButton
    def __onClickPauseButton(self, event):
        self.__dm.pause()
        self.SetStatusText("Paused.")
        self.__downloading = False

        # event handler for SkipButton
    def __onClickSkipButton(self, event):
        self.__dm.skip()

        # event handler for StopButton
    def __onClickStopButton(self, event):
        self.__dm.stop(self.__addedList.GetFirstSelected())

        # event handler for InfoButton
    def __onClickInfoButton(self, event):
        selectedItem = self.__addedList.GetFirstSelected()
        x = 0 # x-coordinate to move info dialog if multiple items are selected
        y = 0 # y-coordinate to move info dialog if multiple items are selected

        while True: # do-while loop to show information dialogs for multiple selected items
            VideoInfoDialog(self.__downloadList[selectedItem].video, x, y).show()
            selectedItem = self.__addedList.GetNextSelected(selectedItem)
            x += 30
            y += 30

            if selectedItem < 0:
                break

        # event handler for RemoveButton
    def __onClickRemoveButton(self, event):
        selectedItem = self.__addedList.GetFirstSelected()
        removeList = []

        while selectedItem >= 0: # get every index to remove
            removeList.append((selectedItem, self.__downloadList[selectedItem]))
            selectedItem = self.__addedList.GetNextSelected(selectedItem)

        removeList.sort(reverse=True) # sort remove list reversely to remove safely by starting from latest index

        for itemTuple in removeList:
            self.SetStatusText(itemTuple[1].video.title + " has been removed.")
            self.__downloadList.remove(itemTuple[1])
            self.__addedList.DeleteItem(itemTuple[0])

        # event handler for ChangeDirButton
    def __onClickChangeDirButton(self, event):
        dialog = wx.DirDialog(None, defaultPath=self.__dirText.GetValue())

        if dialog.ShowModal() == wx.ID_OK:
            defaultDir = dialog.GetPath()

            if os.name == "nt": # setting directory for Windows
                self.__dirText.SetValue(defaultDir + "\\" \
                                        if not defaultDir.endswith("\\") else defaultDir)
            else: # for Linux or macOS
                self.__dirText.SetValue(defaultDir + "/" \
                                        if not defaultDir.endswith("/") else defaultDir)

            dirFile = open(DEFAULT_DIR, "w")
            dirFile.write(self.__dirText.GetValue())
            dirFile.close()

        dialog.Destroy()

        # event handler for selecting an item -> update PrefCombobox list
    def __onSelectItem(self, event):
        self.__prefCombobox.Clear()

        if not self.__downloading and self.__addedList.GetSelectedItemCount() == 1:
            selectedItem = self.__downloadList[self.__addedList.GetFocusedItem()]
            self.__prefCombobox.AppendItems(selectedItem.options)
            self.__prefCombobox.SetValue(selectedItem.selectedExt)

        # event handler for selecting an option in PrefCombobox -> update selected item's selected extension
    def __onSelectOption(self, event):
        selectedItem = self.__addedList.GetFocusedItem()
        self.__downloadList[selectedItem].setSelectedExt(self.__prefCombobox.GetStringSelection())
        self.__addedList.SetItem(selectedItem, 3, self.__downloadList[selectedItem].selectedExt)
        self.__addedList.SetItem(selectedItem, 4, self.__downloadList[selectedItem].filesize)

        # add item to list
    def addToDownloadList(self, item): # if video is already in download list, skip it
        if item.video.title not in [ d.video.title for d in self.__downloadList ]:
            self.__downloadList.append(item)
            num_items = self.__addedList.GetItemCount()

            self.__addedList.InsertItem(num_items, item.video.title)
            self.__addedList.SetItem(num_items, 1, item.video.author)
            self.__addedList.SetItem(num_items, 2, item.video.duration)
            self.__addedList.SetItem(num_items, 3, item.selectedExt)
            self.__addedList.SetItem(num_items, 4, item.filesize)

            self.SetStatusText(item.video.title + " has been added.")
        else:
            self.SetStatusText(item.video.title + " is already in download list.")

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
