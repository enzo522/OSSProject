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
import wx
from infodialog import InfoTable
from playlist import get_playlist

BACKGROUND_COLOR = "white"


# PlaylistInfoDialog class to show information table which was made by InfoTable object
class _PlaylistInfoDialog(wx.Dialog):
    def __init__(self, parent, playlist, x, y):
        wx.Dialog.__init__(self, parent, -1, "Info")
        panel = wx.Panel(self)
        self.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_CLOSE, self.__onClose)
        self.__pl = playlist

        tagList = [ "I D", "제   목", "저   자", "좋아요", "싫어요", "설   명" ]
        infoList = [ self.__pl['playlist_id'], self.__pl['title'], self.__pl['author'], self.__pl['likes'].__str__(), \
                     self.__pl['dislikes'].__str__(), self.__pl['description'] ]

        sizer = wx.BoxSizer(wx.VERTICAL)
        dataList = []

        for i in range(6):
            dataList.append((tagList[i], infoList[i]))

        sizer.Add(InfoTable(self, dataList), flag=wx.ALL, border=10)

        autoCheckbox = wx.CheckBox(panel, -1, "자동으로 다운로드 목록에 추가")
        autoCheckbox.SetValue(self.Parent.getAutoAdd(self.__pl['playlist_id']))
        self.Bind(wx.EVT_CHECKBOX, self.__onCheckAutoAdd, autoCheckbox)
        sizer.Add(autoCheckbox, flag=wx.LEFT | wx.BOTTOM, border=10)
        panel.SetSizerAndFit(sizer)
        self.Fit()

        if x > 0 and y > 0:
            self.Move(self.GetPosition().__iadd__((x, y)))

    def __onClose(self, event):
        self.Destroy()

    def __onCheckAutoAdd(self, event):
        self.Parent.setAutoAdd(self.__pl['playlist_id'], event.IsChecked())

    def show(self):
        self.Show()


# PlaylistDialog class to show currently subscribed playlists
class PlaylistDialog(wx.Dialog):
    def __init__(self, frame, playlistManager):
        wx.Dialog.__init__(self, None, -1, "Playlists")
        self.__frame = frame
        self.__plm = playlistManager
        self.__pls = []
        
        for p in self.__plm.get_playlists_urls():
            self.__pls.append(get_playlist(p))

    def __onClose(self, event):
        self.Destroy()

    def __onCheckCanStart(self, event):
        event.Enable(len(self.__pls) > 0 and self.__frame.isAddable())

    def __onCheckCanShowInfo(self, event):
        event.Enable(self.__plList.GetSelectedItemCount() > 0)

    def __onCheckCanAdd(self, event):
        pass

    def __onCheckCanRemove(self, event):
        event.Enable(self.__plList.GetSelectedItemCount() > 0)

    def __onClickAddButton(self, event):
        dialog = wx.TextEntryDialog(self, "Playlist URL", "Subscribe")

        if dialog.ShowModal() == wx.ID_OK:
            pl = get_playlist(dialog.GetValue())

            if pl is not None:
                self.__plm.subscribe(pl['playlist_id'])
                self.__plList.InsertItem(self.__plList.GetItemCount(), pl['title'])
                self.__pls.append(pl)
                
        dialog.Destroy()

    def __onClickRemoveButton(self, event):
        selectedItem = self.__plList.GetFirstSelected()
        removeList = []

        while selectedItem >= 0:  # get every index to remove
            removeList.append(selectedItem)
            selectedItem = self.__plList.GetNextSelected(selectedItem)

        removeList.sort(reverse=True)  # sort remove list reversely to remove safely by starting from latest index

        for r in removeList:
            self.__plm.unsubscribe(self.__pls[r]['playlist_id'])
            self.__plList.DeleteItem(r)
            self.__pls.pop(r)

    def __onClickInfoButton(self, event):
        selectedItem = self.__plList.GetFirstSelected()
        x = 0
        y = 0

        while selectedItem >= 0:
            _PlaylistInfoDialog(self, self.__pls[selectedItem], x, y).show()
            selectedItem = self.__plList.GetNextSelected(selectedItem)
            x += 30
            y += 30

    def onClickStartButton(self, event):
        videosInPlaylist = []

        for i in range(len(self.__pls)):
            for _, item in enumerate(self.__pls[i]['items']):
                videosInPlaylist.append(item['playlist_meta']['encrypted_id'])

        self.__frame.addPlaylist(videosInPlaylist)
        self.__onClose(None)

    def setAutoAdd(self, url, setting):
        self.__plm.set_playlist_auto_add(url, setting)

    def getAutoAdd(self, url):
        return self.__plm.get_playlist_auto_add(url)

    def autoAdd(self):
        videosInPlaylist = []

        for pl in self.__pls:
            if self.__plm.get_playlist_auto_add(pl['playlist_id']):
                for _, item in enumerate(pl['items']):
                    videosInPlaylist.append(item['playlist_meta']['encrypted_id'])

        self.__frame.addPlaylist(videosInPlaylist)
        self.__onClose(None)

    def show(self, x, y):
        panel = wx.Panel(self)
        self.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_CLOSE, self.__onClose)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.__plList = wx.ListCtrl(panel, size=(300, 390), style=wx.LC_REPORT | wx.BORDER_DOUBLE)
        self.__plList.InsertColumn(0, "플레이리스트", wx.TEXT_ALIGNMENT_CENTER)
        self.__plList.SetColumnWidth(0, 300)

        for i in range(len(self.__pls)):
            self.__plList.InsertItem(i, self.__pls[i]['title'])

        sizer.Add(self.__plList, flag=wx.ALL, border=10)

        buttonBox = wx.BoxSizer(wx.HORIZONTAL)
        self.__startButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/playlistStartButtonIcon.png")), style=wx.NO_BORDER)
        self.__startButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.onClickStartButton, self.__startButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanStart, self.__startButton)
        buttonBox.Add(self.__startButton, flag=wx.RIGHT, border=8)

        self.__infoButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/playlistInfoButtonIcon.png")), style=wx.NO_BORDER)
        self.__infoButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickInfoButton, self.__infoButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanShowInfo, self.__infoButton)
        buttonBox.Add(self.__infoButton, flag=wx.RIGHT, border=8)

        self.__addButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/playlistAddButtonIcon.png")), style=wx.NO_BORDER)
        self.__addButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickAddButton, self.__addButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanAdd, self.__addButton)
        buttonBox.Add(self.__addButton, flag=wx.RIGHT, border=8)

        self.__removeButton = wx.BitmapButton(panel, -1, wx.Bitmap(resource_path("images/playlistRemoveButtonIcon.png")), style=wx.NO_BORDER)
        self.__removeButton.SetBackgroundColour(BACKGROUND_COLOR)
        self.Bind(wx.EVT_BUTTON, self.__onClickRemoveButton, self.__removeButton)
        self.Bind(wx.EVT_UPDATE_UI, self.__onCheckCanRemove, self.__removeButton)
        buttonBox.Add(self.__removeButton, flag=wx.BOTTOM, border=10)

        sizer.Add(buttonBox, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
        panel.SetSizerAndFit(sizer)
        self.Fit()

        if x > 0 and y > 0:
            self.Move((x, y))

        self.Show()
