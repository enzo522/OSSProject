#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        self.__abort = False
        self._lock = threading.RLock()

        for item in itemList:
            self.__queue.put(item)

    def run(self):
        while self.__isRunning:
            if len(self.__threadList) < 3:  # download 3 videos simultaneously
                if not self.__queue.empty():
                    dl = Downloader(self.__frame, self.__queue.get(), self.__dir, self.__abort)
                    self.__threadList.append(dl)
                    dl.start()
                    sleep(WAIT_TIME)

            for t in self.__threadList:
                if not t.isAlive():
                    self.__threadList.remove(t)
                    break
                else:  # update download progress
                    t.updateStatus()
                    sleep(WAIT_TIME)

            if len(self.__threadList) <= 0 and self.__queue.empty():  # when every video is completed
                self.__isRunning = False

        with self._lock:
            self.__frame.setFinished()

    def skip(self):  # cancel current downloads
        for t in self.__threadList:
            if t.isAlive():
                t.stop()
                t.join()

    def stop(self):  # cancel current downloads and abort further ones
        self.skip()
        self.__abort = True

    def join(self, timeout=None):
        super(DownloadManager, self).join(timeout)
