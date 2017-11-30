import wx


# ErrorMsg class to show error dialog
class ErrorMsg:
    def __init__(self, message):
        self.msg = wx.MessageDialog(None, message, "Error", wx.OK | wx.ICON_ERROR)
        self.msg.Bind(wx.EVT_CLOSE, self.__onClose)

        if self.msg.ShowModal() == wx.ID_OK:
            self.__onClose()

    def __onClose(self):
        self.msg.Destroy()
