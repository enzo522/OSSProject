import threading
from Queue import Queue
from time import sleep
from downloader import Downloader

WAIT_TIME = 0.2


# DownloadManager class to download selected videos.
class DownloadManager(threading.Thread):
    def __init__(self, frame, itemList, dir):
        super(DownloadManager, self).__init__()
        self.__frame = frame
        self.__dir = dir
        self.__queue = Queue(len(itemList))  # a queue to download in order
        self.__threadList = []
        self.__isRunning = True
        self.__isSuspending = False
        self._lock = threading.Lock()

        for item in itemList:
            self.__queue.put(item)

    def run(self):
        while self.__isRunning:
            if not self.__isSuspending:
                if len(self.__threadList) < 3:  # download 3 videos simultaneously
                    if not self.__queue.empty():
                        dl = Downloader(self.__frame, self.__queue.get(), self.__dir)
                        self.__threadList.append(dl)
                        dl.start()
                        sleep(WAIT_TIME)

                for t in self.__threadList:
                    if t.isAlive(): # if video is still being downloaded, update status
                        t.updateStatus()
                    else: # otherwise, remove it from list for next video to be downloaded
                        self.__threadList.remove(t)

                    sleep(WAIT_TIME)

                if len(self.__threadList) <= 0 and self.__queue.empty():  # when every video is completed
                    with self._lock:
                        self.__frame.setFinished()

                    break

    def isDownloading(self, index): # return whether selected video is being downloaded or not
        return index < len(self.__threadList) and self.__threadList[index].isAlive()

    def pause(self): # pause current downloads
        self.__isSuspending = True

        for t in self.__threadList:
            t.pause()

        self.__isRunning = False

    def skip(self):  # cancel current downloads
        self.__isSuspending = True

        for t in self.__threadList:
            t.stop()
            sleep(WAIT_TIME)

        self.__isSuspending = False

    def stop(self, index):  # cancel selected download and delete it
        self.__isSuspending = True

        if index < len(self.__threadList):
            self.__threadList[index].stop()
            sleep(WAIT_TIME)

        self.__isSuspending = False
