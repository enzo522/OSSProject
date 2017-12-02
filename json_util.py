# -*- coding: utf-8 -*-
import json


def get_playlist_json_util():
    return PlaylistJsonUtil()


def get_playlist_download_json_util():
    return PlaylistDownloadJsonUtil()


class JsonUtil:
    """ JSON 파일에 쓰거나 읽어오는 등의 상호작용을 담당하는 클래스 """

    def __init__(self, filename):
        self._filename = filename

    def test(self):
        print('JsonUtil')

    def write(self, data):
        with open(self._filename, 'w') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    def read(self):
        with open(self._filename, 'r') as json_file:
            return json.load(json_file)


class PlaylistJsonUtil(JsonUtil):
    def __init__(self, filename="playlists.json"):
        JsonUtil.__init__(self, filename)

    def test(self):
        print('PlaylistJsonUtil')
        super(PlaylistJsonUtil, self).test()


class PlaylistDownloadJsonUtil(JsonUtil):
    def __init__(self, filename="playlist_downloads.json"):
        JsonUtil.__init__(self, filename)

    def test(self):
        print('PlaylistDownloadJsonUtil')
        super(PlaylistDownloadJsonUtil, self).test()


def echo_test():
    print("echo")


def test_dumps():
    obj = ['foo', {'bar': ('baz', None, 1.0, 2)}]
    print(json.dumps(obj, ensure_ascii=False, indent=4))


def test_loads():
    obj = json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
    print(obj)
    print(obj[0])
    print(obj[1]['bar'])


def test_write():
    data = {}
    data['people'] = []
    data['people'].append({
        'name': 'Scott',
        'website': 'stackabuse.com',
        'from': 'Nebraska'
    })
    data['people'].append({
        'name': 'Larry',
        'website': 'google.com',
        'from': 'Michigan'
    })
    data['people'].append({
        'name': 'Tim',
        'website': 'apple.com',
        'from': 'Alabama'
    })

    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False)


def test_read():
    with open('data.txt') as json_file:
        data = json.load(json_file)
        for p in data['people']:
            print('Name: ' + p['name'])
            print('Website: ' + p['website'])
            print('From: ' + p['from'])
            print('')
