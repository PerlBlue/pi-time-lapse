from picamera import PiCamera
from datetime import datetime

import re
import glob, os
import time
import glob
import subprocess

config = {}
config['height'] = 1944
config['width'] = 2592
config['file_dir'] = '/var/image/'
config['scp_dir'] = 'icydee@139.162.231.197:/home/icydee/images'



class Capture:
    def __init__(self, config):
        self.camera             = PiCamera()
        self.camera.resolution  = (int(config["width"]), int(config["height"]))
        self.camera.meter_mode  = "backlit"                      # Set to maximum central region
        self.base_name          = config['file_dir']+'img_'+time.strftime("%y%m%d-%H%M_")
        self.camera.awb_mode    = 'auto'

    # Take and store a single image
    def take_one(self, postfix):
        name = self.base_name + postfix + '.jpg'
        print("Take one: "+name)
        self.camera.capture(name)
        
        time.sleep(0.5)
        return name

    # Make camera settings and take one image
    def take_one_with_settings(self, postfix, exp, gain_r, gain_b, mult):

        exp = int(int(exp) * mult )
        print("EXP: "+str(exp)+" GAIN_R: "+str(gain_r)+" GAIN_B: "+str(gain_b) + "MULT: "+str(mult))
        
        self.camera.awb_gains = (float(gain_r), float(gain_b))
        self.camera.awb_mode = 'off'
        self.camera.shutter_speed = exp
        
        return self.take_one(postfix)

    # Get the exposure and gain settings from the reference image
    def get_settings(self, reference_image):

        gain_r = 0
        gain_b = 0
        exp = 0
        
        chars = r"A-Za-z0-9/\-:.,q_$%'()[\]<>= "
        shortest_run = 50
        regexp = '[%s]{%d,}' % (chars, shortest_run)
        pattern = re.compile(regexp)

        with open(reference_image, 'r', encoding='latin1') as x: f = x.read()
        for found_str in pattern.findall(f):
            print("FOUND: "+found_str)
            match = re.search(r"exp=(\d+).*gain_r=(\d+\.\d*).*gain_b=(\d+\.\d*)", found_str)
            if match:
                exp = match.group(1)
                gain_r = match.group(2)
                gain_b = match.group(3)
            return (exp, gain_r, gain_b)

    def take_sequence(self):
        names = []

        # Reference image to get correct exposure
        reference_image_file = self.take_one('x')

        # I have not found a way yet to get the exposure settings
        # so we need to read the data from the file
        (exp, gain_r, gain_b) = self.get_settings(reference_image_file)
#        print("MATCH exp:"+exp+ "  gain_r:"+gain_r+ "  gain_b:"+gain_b)

        #(gain_r, gain_b) = self.camera.awb_gains
#        print("RED: "+str(gain_r)+" BLUE: "+str(gain_b))

        self.take_one_with_settings('0', exp, gain_r, gain_b, 0.25)
        self.take_one_with_settings('1', exp, gain_r, gain_b, 0.5)
        self.take_one_with_settings('2', exp, gain_r, gain_b, 1)
        self.take_one_with_settings('3', exp, gain_r, gain_b, 2)
        self.take_one_with_settings('4', exp, gain_r, gain_b, 4)
        
        return names       


    def transfer(self):
        files = self.base_name+"*"
        print("Transfer files "+files)
        print("scp "+ files + " " + config['scp_dir'])

        for f in glob.glob(files):
            my_out = subprocess.Popen(['scp', f, config['scp_dir']],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            stdout,stderr = my_out.communicate()
#            print("stdout: "+str(stdout))
#            print("stderr: "+str(stderr))

            print("REMOVE: "+f)
            os.remove(f)

if __name__ == "__main__":
    start = time.time()

    capture = Capture(config)
    files = capture.take_sequence()
    capture.transfer()

    end = time.time()
    print("Duration: " + str(end - start) + "s")


        


        
