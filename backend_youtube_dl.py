#!/usr/bin/python
# -*- coding: utf-8 -*-

'''모듈 불러오기'''
import sys #파이썬 인터프리터 제어
import time
import logging

'''설치된 파이썬의 버전에 따른 인코딩'''
if sys.version_info[:2] >= (3, 0):
    # pylint: disable=E0611,F0401,I0011
    uni = str
else:
    uni = unicode

import youtube_dl
import wx
import threading

'''선언한 모듈(from)에서 필요한 것(import)만 가져온다.'''
import g
from backend_shared import BasePafy, BaseStream

dbg = logging.debug #디버깅용 로그

'''sys.version_info: 버전의 다섯가지 요소인 major,minor,micro,releaselevel,serial을 포함하는 튜플.'''
early_py_version = sys.version_info[:2] < (2, 7)

'''BasePafy를 상속받는 클래스 VtdlPafy'''
class YtdlPafy(BasePafy):
    def __init__(self, *args, **kwargs): #__init__메서드를 사용하여 객체초기화
        self._ydl_info = None
        self._ydl_opts = g.def_ydl_opts
        ydl_opts = kwargs.get("ydl_opts")
        if ydl_opts:
            self._ydl_opts.update(ydl_opts)
        super(YtdlPafy, self).__init__(*args, **kwargs) #BasePafy 클래스의 __init__메서드 호출

    def _fetch_basic(self):
        """ 일반적인 데이터와 스트림 불러옴 """
        if self._have_basic:
            return True

        with youtube_dl.YoutubeDL(self._ydl_opts) as ydl:
            try: #에러가 발생할 가능성이 있는 코드
                self._ydl_info = ydl.extract_info(self.videoid, download=False)
            # Turn into an IOError since that is what pafy previously raised
            except youtube_dl.utils.DownloadError as e: #에러 종류
                ErrorMsg(self.videoid).start()
                return False

        if self.callback:
            self.callback("Fetched video info")

        self._title = self._ydl_info['title']
        self._author = self._ydl_info['uploader']
        self._rating = self._ydl_info['average_rating']
        self._length = self._ydl_info['duration']
        self._viewcount = self._ydl_info['view_count']
        self._likes = self._ydl_info['like_count']
        self._dislikes = self._ydl_info['dislike_count']
        self._username = self._ydl_info['uploader_id']
        self._category = self._ydl_info['categories'][0] if self._ydl_info['categories'] else ''
        self._bigthumb = g.urls['bigthumb'] % self.videoid
        self._bigthumbhd = g.urls['bigthumbhd'] % self.videoid
        self.expiry = time.time() + g.lifespan

        self._have_basic = True
        return True

    def _fetch_gdata(self):
        """ gdata 값을 추출 및 필요할 경우 gdata 불러옴 """
        if self._have_gdata:
            return

        item = self._get_video_gdata(self.videoid)['items'][0]
        snippet = item['snippet']
        self._published = uni(snippet['publishedAt'])
        self._description = uni(snippet["description"])
        # 어떤 영상은 tag객체가 없음에 따라 snippet.get 메서드 사용
        self._keywords = [uni(i) for i in snippet.get('tags', ())]
        self._have_gdata = True

    def _process_streams(self):
        """ 내부 스트림 맵으로 부터 스트림 객체 생성 """

        if self._have_basic:
            allstreams = [YtdlStream(z, self) for z in self._ydl_info['formats']]
            self._streams = [i for i in allstreams if i.mediatype == 'normal']
            self._audiostreams = [i for i in allstreams if i.mediatype == 'audio']
            self._videostreams = [i for i in allstreams if i.mediatype == 'video']
            self._m4astreams = [i for i in allstreams if i.extension == 'm4a']
            self._oggstreams = [i for i in allstreams if i.extension == 'ogg']
            self._allstreams = allstreams

'''BaseStream을 상속받는 클래스'''
class YtdlStream(BaseStream):
    def __init__(self, info, parent):
        super(YtdlStream, self).__init__(parent) #BaseStream 클래스의 __init__메서드 호출
        self._itag = info['format_id']

        if (info.get('acodec') != 'none' and
                info.get('vcodec') == 'none'):
            self._mediatype = 'audio'
        elif (info.get('acodec') == 'none' and
                info.get('vcodec') != 'none'):
            self._mediatype = 'video'
        else:
            self._mediatype = 'normal'

        self._threed = info.get('format_note') == '3D'
        self._rawbitrate = info.get('abr', 0) * 1024

        height = info.get('height') or 0
        width = info.get('width') or 0
        self._resolution = str(width) + 'x' + str(height)
        self._dimensions = width, height
        self._bitrate = str(info.get('abr', 0)) + 'k'
        self._quality = self._bitrate if self._mediatype == 'audio' else self._resolution

        self._extension = info['ext']
        self._notes = info.get('format_note') or ''
        self._url = info.get('url')

        self._info = info

    def get_filesize(self):
        """ 스트림의 파일 크기를 바이트로 반환 / 멤버 변수를 설정 """

        # Faster method
        if 'filesize' in self._info and self._info['filesize'] is not None:
            return self._info['filesize']

        # Fallback
        return super(YtdlStream, self).get_filesize()

    def progress_stats(self):
        return super(YtdlStream, self).progress_stats

class ErrorMsg(threading.Thread):
    def __init__(self, videoid):
        super(ErrorMsg, self).__init__()
        self.msg = wx.MessageDialog(None, videoid + "\n에 해당하는 유튜브 영상이 존재하지 않습니다.", "Error", wx.OK | wx.ICON_ERROR)

    def run(self):
        self.msg.ShowModal()
