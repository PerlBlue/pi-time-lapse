from picamera import PiCamera
from config import config
from datetime import datetime

import os
import time
import glob
import subprocess


class Capture:
    def __init__(self, config):
        self.camera = PiCamera()
        self.camera.resolution = (int(config["width"]), int(config["height"]))
        self.camera.meter_mode = "backlit"                      # Set to maximum central region
        self.config = config

    def take(self):
        names = []

        now = datetime.now()
        base_name = time.strftime("%y%m%d-%H%M")

        #self.camera.start_preview()
        time.sleep(2)
        name = "/var/image/img_"+base_name+"_X.jpg"
        self.camera.capture(name)
        time.sleep(0.5)
        names.append(name)
        
        evs = [-25, -10, 0, 10, 25]
        i = 0
        for ev in evs:
            self.camera.exposure_compensation = ev
            
            print("EV: " + str(ev))
            name = "/var/image/img_"+base_name + "_" + str(i) + ".jpg"
            print("IMAGE: "+name)

            self.camera.capture(name)
            time.sleep(0.5)
            names.append(name)
            i = i + 1

        #self.camera.stop_preview()
        return names

    def transfer(self, names):
        print("Files: "+ ' '.join(names))

        for name in names:
            MyOut = subprocess.Popen(['scp', name, 'icydee@icydee.co.uk:/home/icydee/sandbox2/picamera/images'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            stdout,stderr = MyOut.communicate()
            print(stdout)
            print(stderr)

            os.remove(name)
            print("REMOVE: "+name)
            print("remove file "+name)


if __name__ == "__main__":
    start = time.time()

    capture = Capture(config)
    files = capture.take()
    capture.transfer(files)

    end = time.time()

    print("Duration: " + str(end - start) + "s")


        


        
