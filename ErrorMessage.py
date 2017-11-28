import threading
import wx


# ErrorMsg class to show error dialog
class ErrorMsg(threading.Thread):
    def __init__(self, message):
        super(ErrorMsg, self).__init__()
        self.msg = wx.MessageDialog(None, message, "Error", wx.OK | wx.ICON_ERROR)

    def run(self):
        self.msg.ShowModal()
