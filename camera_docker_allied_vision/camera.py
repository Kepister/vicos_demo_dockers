#!/usr/bin/env python3

import numpy as np
from json import load

import copy
import echolib
from   echolib.camera import FramePublisher, Frame

from vimba import Vimba, PixelFormat, FrameStatus
from threading import Lock, get_ident

class VimbaCameraHandler():

    def __init__(self):

        self.frame = None
        self.frame_lock = Lock()

    def frame_handler(self, camera, frame):

        print(f"Frame_handler: {get_ident()}")
        
        if frame.get_status() == FrameStatus.Complete:
            
            frame_copy = copy.deepcopy(frame)
            frame_copy.convert_pixel_format(PixelFormat.Rgb8)
            frame_copy = frame_copy.as_numpy_ndarray()

            self.frame_lock.acquire()
            self.frame = frame_copy
            self.frame_lock.release()

        camera.queue_frame(frame)

def main():

    # Load camera parameters
    config = load(open("/opt/config/camera0.json"))
    config_set_functions = \
    {
        "ExposureAuto": lambda camera, v: camera.ExposureAuto.set(int(v)),
        "DeviceLinkThroughputLimit": lambda camera, v: camera.DeviceLinkThroughputLimit.set(int(v)),
        "AcquisitionFrameRateEnable": lambda camera, v: camera.AcquisitionFrameRateEnable.set(bool(int(v)))
    }

    #####################################

    loop   = echolib.IOLoop()
    client = echolib.Client()
    loop.add_handler(client)

    output = FramePublisher(client, "camera")
    
    with Vimba.get_instance() as vimba_instance:

        handler = VimbaCameraHandler()
        vimba_cameras = vimba_instance.get_all_cameras()

        with vimba_cameras[0] as vimba_camera:

            for feature in config:
                config_set_functions[feature](vimba_camera, config[feature])

            vimba_camera.start_streaming(handler.frame_handler, buffer_count = 10)

            while loop.wait(1):

                if handler.frame is not None:
                    print(f"Main loop: {get_ident()}")
                    output.send(Frame(image = handler.frame))
        
        vimba_camera.stop_streaming()


if __name__=='__main__':
    main()
