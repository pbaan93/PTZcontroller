
from pathlib import Path
import os, math
class presetImageWatcher:
    def __init__(self, positionNr, camNr):
        self.camNr = camNr
        self._cached_stamp = 0
        self.nr = positionNr
        self.filename = "previews"+str(self.camNr)+"/"+str(positionNr)+".jpg"

    def changed(self):
        my_file = Path("previews"+str(self.camNr)+"/"+str(self.nr)+".jpg")
        if my_file.is_file():
            stamp = os.stat(self.filename).st_mtime
            if stamp != self._cached_stamp:
                self._cached_stamp = stamp
                return True
            else:
                return False
        else:
            if self._cached_stamp != 0:
                self._cached_stamp = 0
                return True
            else:
                return False