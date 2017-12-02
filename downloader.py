#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import threading


# Downloader class to download a video.
class Downloader(threading.Thread):
    def __init__(self, frame, playlistManager, item, downloadPath, lock):
        super(Downloader, self).__init__()
        self.__frame = frame
        self.__plm = playlistManager
        self.__item = item
        self.__stream = None
        self.__downloadPath = downloadPath
        self._lock = lock

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

            with self._lock:
                self.__frame.updateStatus(self.__item, progress, rate, eta)

    def run(self):
        flag = self.__stream.download(filepath=self.__downloadPath, quiet=True) # 1: completed/ 0: paused/ -1: stopped

        if flag == 1: # only if successfully downloaded, video is added to downloaded list
            self.__plm.add_downloads(self.__item.video.videoid)

        if flag != 0: # except paused, remove video from download list
            with self._lock:
                self.__frame.removeFinishedItem(self.__item)

    def stop(self, delete):  # when the user clicked skip / stop button, current download should be canceled
        if self.__stream:
            self.__stream.cancel(delete=delete)
