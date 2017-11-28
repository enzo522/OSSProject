# Item class to encapsulate video and selected options (media type, extension, resolution)
class Item():
    def __init__(self, video, selectedExt):
        self.video = video
        self.selectedExt = selectedExt
        self.filesize = None
        self.__sizes = []
        self.options = []

        for s in self.video.allstreams:
            self.options.append(s.mediatype + " / " + s.extension + " / " + s.quality)
            self.__sizes.append(s.get_filesize())

        self.__calcFilesize()

    def __calcFilesize(self):
        orgFilesize = None

        for i in range(len(self.options)):
            if self.selectedExt == self.options[i]:
                orgFilesize = self.__sizes[i]

        self.filesize = round(orgFilesize / 1024 ** 2, 1).__str__() + "MB" if orgFilesize > 1024 ** 2 else \
            round(orgFilesize / 1024, 1).__str__() + "KB" \
            if orgFilesize is not None else ""

    def setSelectedExt(self, newExt):
        self.selectedExt = newExt
        self.__calcFilesize()
