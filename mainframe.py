#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
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
        self.__addButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/addButtonIcon.png"), style=wx.NO_BORDER)
        self.__addButton.SetBackgroundColour(BACKGROUND_COLOR)
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
        self.__changeDirButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickChangeDirButton, self.__changeDirButton)
        dirBox.Add(self.__changeDirButton, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        defaultDir = ""

        if os.path.exists(DEFAULT_DIR):
            dirFile = open(DEFAULT_DIR, "r")
            defaultDir = dirFile.readline()
        else:
            dialog = wx.DirDialog(None)

            if dialog.ShowModal() == wx.ID_OK:
                dirFile = open(DEFAULT_DIR, "w")
                defaultDir = dialog.GetPath() + "/"
                dirFile.write(defaultDir)

            dialog.Destroy()

        # this text shows currently selected download directory
        self.__dirText = wx.TextCtrl(panel, value=defaultDir, size=(300, -1), style=wx.TE_READONLY)
        dirBox.Add(self.__dirText)

        # a meaningless icon
        optBox = wx.BoxSizer(wx.HORIZONTAL)
        prefIcon = wx.StaticBitmap(panel, -1, wx.Bitmap("images/changePrefIcon.png"))
        prefIcon.SetBackgroundColour(BACKGROUND_COLOR)
        optBox.Add(prefIcon, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)

        # a combobox which includes all available stream options that are available on selected video
        self.__prefCombobox = wx.ComboBox(panel, size=(200, -1), style=wx.CB_DROPDOWN | wx.TE_READONLY)
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

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__onSelectItem, self.__addedList)
        hBoxes[3].Add(self.__addedList, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        vBox.Add(hBoxes[3], flag=wx.LEFT | wx.RIGHT, border=10)
        vBox.Add((-1, 10))

        # add 5 buttons (start, skip, stop, info, remove)
        self.__startButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/startButtonIcon.png"), style=wx.NO_BORDER)
        self.__startButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickStartButton, self.__startButton)
        hBoxes[4].Add(self.__startButton, flag=wx.RIGHT, border=12)

        self.__skipButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/skipButtonIcon.png"), style=wx.NO_BORDER)
        self.__skipButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickSkipButton, self.__skipButton)
        hBoxes[4].Add(self.__skipButton, flag=wx.RIGHT, border=12)

        self.__stopButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/stopButtonIcon.png"), style=wx.NO_BORDER)
        self.__stopButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickStopButton, self.__stopButton)
        hBoxes[4].Add(self.__stopButton, flag=wx.RIGHT, border=12)

        self.__infoButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/infoButtonIcon.png"), style=wx.NO_BORDER)
        self.__infoButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickInfoButton, self.__infoButton)
        hBoxes[4].Add(self.__infoButton, flag=wx.RIGHT, border=12)

        self.__removeButton = wx.BitmapButton(panel, -1, wx.Bitmap("images/removeButtonIcon.png"), style=wx.NO_BORDER)
        self.__removeButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickRemoveButton, self.__removeButton)
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

        if self.__addedList.SelectedItemCount != 1:
            self.__prefCombobox.Clear()

        self.__startButton.Enable(not self.__downloading and len(self.__downloadList) > 0 and \
                                  self.__am is not None and not self.__am.isAlive())
        self.__skipButton.Enable(self.__downloading)
        self.__stopButton.Enable(self.__downloading)

        self.__infoButton.Enable(self.__addedList.SelectedItemCount > 0)
        self.__removeButton.Enable(not self.__downloading and self.__addedList.SelectedItemCount > 0 \
                                   and self.__am is not None and not self.__am.isAlive())

        # event handler for AddButton
    def __onClickAddButton(self, event):
        if self.__sourceText.GetValue():
            urls = []

            for i in range(self.__sourceText.GetNumberOfLines()):
                if self.__sourceText.GetLineText(i) != "": # skip blank and duplicated url
                    urls.append(self.__sourceText.GetLineText(i))

            self.__am = AddManager(self, urls)
            self.__am.start()
            self.__sourceText.Clear()

        # event handler for StartButton
    def __onClickStartButton(self, event):
        self.__dm = DownloadManager(self, self.__downloadList, self.__dirText.GetValue())
        self.__dm.start()
        self.__downloading = True
        self.__urlList = []
        self.__prefCombobox.Clear()
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
            dirFile = open(DEFAULT_DIR, "w")
            self.__dirText.SetValue(dialog.GetPath() + "/")
            dirFile.write(self.__dirText.GetValue())

        dialog.Destroy()

        # event handler for selecting an item -> update PrefCombobox list
    def __onSelectItem(self, event):
        selectedItem = self.__downloadList[self.__addedList.GetFocusedItem()]
        self.__prefCombobox.Clear()
        self.__prefCombobox.AppendItems(selectedItem.options)
        self.__prefCombobox.SetValue(selectedItem.selectedExt)

        # event handler for selecting an option in PrefCombobox -> update selected item's selected extension
    def __onSelectOption(self, event):
        selectedItem = self.__addedList.GetFocusedItem()
        self.__downloadList[selectedItem].setSelectedExt(self.__prefCombobox.GetStringSelection())
        self.__addedList.SetItem(selectedItem, 3, self.__downloadList[selectedItem].selectedExt)
        self.__addedList.SetItem(selectedItem, 4, self.__downloadList[selectedItem].filesize)

        # add item to list
    def addToDownloadList(self, item):
        if item.video.title not in [ d.video.title for d in self.__downloadList ]:
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
