#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import os


# Downloader class to download a video.
class Downloader(threading.Thread):
    def __init__(self, frame, item, downloadPath, abort):
        super(Downloader, self).__init__()
        self.__frame = frame
        self.__item = item
        self.__stream = None
        self.__abort = abort
        self.__filename = downloadPath + self.__item.video.title + "."
        self._lock = threading.RLock()

        for s in self.__item.video.allstreams:  # find a stream which satisfies selected options
            if self.__item.selectedExt == s.mediatype + " / " + s.extension + " / " + s.quality:
                self.__stream = s
                break

    def updateStatus(self):  # current download progress about this video
        if self.__stream.has_stats:
            stats = self.__stream.progress_stats
            rate = round(stats[0] * 100, 1).__str__() + "%"
            progress = round(stats[1] / 1024, 1).__str__() + "MB/s" if stats[1] > 1024 else \
                round(stats[1], 1).__str__() + "KB/s"
            eta = round(stats[2], 1).__str__() + "초"

            self.__frame.updateStatus(self.__item, progress, rate, eta)

    def run(self):  # if the user clicked stop button, the downloader shouldn't start download
        if not self.__abort:  # otherwise, check whether the user has already downloaded this video
            if not os.path.exists(self.__filename + self.__stream.extension):
                self.__stream.download(filepath=self.__filename + self.__stream.extension, quiet=True)

        with self._lock:
            self.__frame.removeFinishedItem(self.__item)

    def stop(self):  # when the user clicked skip / stop button, current download should be canceled
        if self.__stream:
            self.__stream.cancel()
