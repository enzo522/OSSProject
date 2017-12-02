# -*- coding: utf-8 -*-
import copy
import re
import os

from playlist import get_playlist
from json_util import get_playlist_json_util, get_playlist_download_json_util


def get_playlist_manager():
    return PlaylistManager()


class PlaylistManager:
    """ This class manages the subscription, unsubscription, downloading of youtube playlist """

    def __init__(self):
        """ Init variables and modules """

        ''' Init playlist related things '''
        self.__pl_json = get_playlist_json_util()
        self.__default_playlist_data = {
            'autoEnabled': False,
            'interval': 3600,
            'lastTriedAt': 0,
            'lastDownloadedAt': 0
        }
        self.__playlists = {}
        self.__load_playlist_file()

        ''' Init playlist download history things '''
        self.__pld_json = get_playlist_download_json_util()
        self.__default_playlist_download_data = {
            'status': 'downloading',
            'last_status_date': 0,
            'size': 0
        }
        self.__downloads = {}
        self.__load_playlist_downloads_file()

    def subscribe(self, url):
        """ Subscribe using playlist url """
        pl_code = self.__parse_playlist_id(url)
        print('subscribe "' + pl_code + '"')
        self.__playlists[pl_code] = copy.deepcopy(self.__default_playlist_data)
        self.__pl_json.write(self.__playlists)

    def unsubscribe(self, url):
        """ Unsubscribe using playlist url """
        pl_code = self.__parse_playlist_id(url)
        print('unsubscribe "' + pl_code + '"')
        try:
            del self.__playlists[pl_code]
        except KeyError:
            print('cannot found "' + pl_code + '" in the playlist')
        self.__pl_json.write(self.__playlists)

    def download(self):
        """ Download streams, including not yet finished, of subscribed playlists """

        print('start downloading')

        ''' reload config files '''
        self.__load_config_files()

        # For every subscribed playlist
        for pl_url, _ in self.__playlists.items():
            pl = get_playlist(pl_url)
            print('(' + str(len(pl['items'])) + ') ' + pl['title'])

            # For every stream on the playlist
            for _, item in enumerate(pl['items']):
                vid = item['pafy']
                best = vid.getbest()
                print(vid.title + ': ' + str(best))

                try:
                    self.__downloads[pl_url]
                except KeyError:
                    self.__downloads[pl_url] = {}

                # Do downloading if current stream is not in download history or not marked as finished
                dl_pl = self.__downloads[pl_url]
                if vid.videoid not in dl_pl or dl_pl[vid.videoid]['status'] != 'finished':

                    # Write current stream to download history
                    dl_pl[vid.videoid] = copy.deepcopy(self.__default_playlist_download_data)
                    self.__pld_json.write(self.__downloads)

                    # Start downloading, making directory if not already exists
                    down_dir = './downloads'
                    if not os.path.exists(down_dir):
                        os.makedirs(down_dir)

                    def cb(total, recvd, ratio, rate, eta):
                        # Mark status when download finished
                        if ratio >= 1.0:
                            dl_pl[vid.videoid]['status'] = 'finished'
                            self.__pld_json.write(self.__downloads)

                    best.download(quiet=False, filepath=down_dir, callback=cb)

            print('download completed for the playlist "' + pl_url + '"')

        print('All downloads have been completed')

    def __load_config_files(self):
        """ Load json config files """
        self.__load_playlist_file()
        self.__load_playlist_downloads_file()

    def __load_playlist_file(self):
        """ Load playlists from json file """
        try:
            print('load playlist from the file')
            self.__playlists = self.__pl_json.read()
        except:
            print('playlist file does not exist or is corrupted')
            self.__pl_json.write(self.__playlists)
        print(self.__playlists)

    def __load_playlist_downloads_file(self):
        """ Load playlist download history from json file """
        try:
            print('load playlist downloads from the file')
            self.__downloads = self.__pld_json.read()
        except:
            print('playlist download file does not exist or is corrupted')
            self.__pld_json.write(self.__downloads)
        print(self.__downloads)

    @staticmethod
    def __parse_playlist_id(url):
        """ Parse playlist id from url """
        m = re.search('list=([\w\-_]+)', url)
        if m is None:
            return url
        else:
            return m.group(1)

    def get_playlists_urls(self):
        return self.__playlists.keys()


    def set_playlist_auto_add(self, url, setting):
        if url in self.__playlists.keys():
            self.__playlists[url]['autoEnabled'] = setting
            self.__pl_json.write(self.__playlists)

    def get_playlist_auto_add(self, url):
        return (url in self.__playlists.keys()) and self.__playlists[url]['autoEnabled']
