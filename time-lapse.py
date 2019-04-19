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
        self.base_name          = config['file_dir']+'img_'+time.strftime("%y%m%d-%H%M_")

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


    def take_one_picture(self, postfix):
        filename = self.base_name + postfix + '.jpg'

        cmd = 'raspistill -vf -hf -ag 1 -dg 1 -o '+filename
        print("CMD: "+cmd)
        os.system(cmd)
        print("XXX: "+filename)
        return filename


    def take_one_picture_with_settings(self, postfix, exp, gain_r, gain_b, mult):

        ss = str(int(exp) * mult)
        awbg = str(gain_r)+','+str(gain_b)
        filename = self.base_name + postfix + '.jpg'
        cmd = 'raspistill -vf -hf -ag 1 -dg 1 -t 30 -awb off -awbg '+awbg+' -ss '+ss+' -o '+filename
        
        print("CMD: "+cmd)
        os.system(cmd)
        

    def take_sequence(self):

        # Reference image to get correct exposure
        reference_image_file = self.take_one_picture('x')

        # I have not found a way yet to get the exposure settings
        # so we need to read the data from the file
        (exp, gain_r, gain_b) = self.get_settings(reference_image_file)
        print("got reference data")

        self.take_one_picture_with_settings('0', exp, gain_r, gain_b, 0.25)
        self.take_one_picture_with_settings('1', exp, gain_r, gain_b, 0.5)
        self.take_one_picture_with_settings('2', exp, gain_r, gain_b, 1)
        self.take_one_picture_with_settings('3', exp, gain_r, gain_b, 2)
        self.take_one_picture_with_settings('4', exp, gain_r, gain_b, 4)
        

    def transfer(self):
        files = self.base_name+"*"
        print("Transfer files "+files)
        print("scp "+ files + " " + config['scp_dir'])

        for f in glob.glob(files):
            cmd = 'scp '+f+' '+config['scp_dir']
            os.system(cmd)
            
            print("REMOVE: "+f)
            os.remove(f)

if __name__ == "__main__":
    start = time.time()

    try:
        capture = Capture(config)
        capture.take_sequence()
        capture.transfer()
        pass
    finally:
        print("All Done")
        
    end = time.time()
    print("Duration: " + str(end - start) + "s")


        


        
