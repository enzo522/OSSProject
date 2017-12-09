import threading
import pafy
from item import Item


# AddManager class to add urls to download list.
class AddManager(threading.Thread):
    def __init__(self, frame, playlistManager, urlList, lock):
        super(AddManager, self).__init__(target=self.__analyze)
        self.__frame = frame
        self.__plm = playlistManager
        self.__urlList = urlList
        self.__isRunning = True
        self._lock = lock

    def __analyze(self):
        for url in self.__urlList:
            if not self.__isRunning:
                break

            if not url in self.__plm.get_downloads_urls():
                video = pafy.new(url)

                if video.has_basic:  # check current url is available
                    default = video.getbest()  # default selected options are the best ones that current video has

                    with self._lock:
                        self.__frame.addToDownloadList(Item(video, default.mediatype + " / " + default.extension + \
                                                            " / " + default.resolution))

    def stop(self):
        self.__isRunning = False
