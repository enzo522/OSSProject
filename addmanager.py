import threading
import pafy
from item import Item


# AddManager class to add urls to download list.
class AddManager(threading.Thread):
    def __init__(self, frame, urlList):
        super(AddManager, self).__init__()
        self.__frame = frame
        self.__urlList = urlList
        self.__isRunning = True
        self._lock = threading.Lock()

    def run(self):
        for url in self.__urlList:
            if self.__isRunning:
                video = pafy.new(url)

                if video.has_basic:  # check current url is available
                    default = video.getbest()  # default selected options are the best ones that current video has

                    with self._lock:
                        self.__frame.addToDownloadList(Item(video, default.mediatype + " / " + default.extension + \
                                                            " / " + default.resolution))


    def stop(self):
        self.__isRunning = False
