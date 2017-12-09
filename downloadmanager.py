import os
import threading
from Queue import Queue
from time import sleep
from downloader import Downloader

WAIT_TIME = 0.2


# DownloadManager class to download selected videos.
class DownloadManager(threading.Thread):
    def __init__(self, frame, playlistManger, itemList, dir, lock):
        super(DownloadManager, self).__init__(target=self.__distribute)
        self.__frame = frame
        self.__plm = playlistManger
        self.__dir = dir
        self.__queue = Queue(len(itemList))  # a queue to download in order
        self.__threadList = []
        self.__isRunning = True
        self._lock = lock

        for item in itemList:
            self.__queue.put(item)

    def __distribute(self):
        while self.__isRunning:
            if len(self.__threadList) < 3:  # download 3 videos simultaneously
                if not self.__queue.empty():
                    dl = Downloader(self.__frame, self.__plm, self.__queue.get(), self.__dir, self._lock)
                    self.__threadList.append(dl)
                    dl.start()
                    sleep(WAIT_TIME)

            for t in self.__threadList:
                if t.is_alive():  # if video is still being downloaded, update status
                    t.updateStatus()
                else:  # otherwise, remove it from list for next video to be downloaded
                    self.__threadList.remove(t)

                sleep(WAIT_TIME)

            if len(self.__threadList) <= 0 and self.__queue.empty():  # when every video is completed
                with self._lock:
                    self.__frame.setFinished()

                self.__isRunning = False

    def isDownloading(self, index): # return whether selected video is being downloaded or not
        return index < len(self.__threadList) and self.__threadList[index].is_alive()

    def pause(self): # pause current downloads
        self.__isRunning = False

        for t in self.__threadList:
            t.stop(delete=False)

    def skip(self):  # cancel current downloads
        for t in self.__threadList:
            t.stop(delete=True)
            t.join()

    def stop(self, index):  # cancel selected download and delete it
        if index < len(self.__threadList):
            self.__threadList[index].stop(delete=True)
            self.__threadList[index].join()
