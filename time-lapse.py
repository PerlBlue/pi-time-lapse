from picamera import PiCamera
from config import config
from pathMaker import PathMaker
from datetime import datetime

import os
import time
import glob

class Capture:
    def __init__(self, config, path_maker):
        self.camera = PiCamera()
        self.camera.resolution = (int(config["width"]), int(config["height"]))
        self.camera.meter_mode = "backlit"
        self.config = config
        self.path_maker = path_maker

    def take(self):
        names = []
        start = time.time()
#        self.camera.start_preview()

        now = datetime.now()
        folder = self.path_maker.prepare_dir("/var/image", now)

        base_name = str(time.time()).replace(".", "_")
#        evs = [-25, -10, 0, 10, 25]
        evs = [0, 0, 0, 0, 0]
        i = 0
        for ev in evs:
            print("EV: " + str(ev))
            name = "slice_"+base_name + "_" + str(i)+ ".jpg"
            print("IMAGE: "+name)
            self.camera.capture(name)
#            time.sleep(0.5)
            names.append(name)
            i = i + 1
#        self.camera.stop_preview()

        end = time.time()
        return (names, (end-start))

if __name__ == "__main__":
    capture = Capture(config, PathMaker())
    files = capture.take()
    print("Duration: " + str(files[1]) + "s")
    time.sleep(1)
        


        
