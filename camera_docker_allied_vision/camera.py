#!/usr/bin/env python3

from math import floor
import numpy as np
from json import load

import echolib

from vimba import Vimba, PixelFormat, FrameStatus, Camera

from echolib.camera import FramePublisher, Frame

def setup_software_triggering(cam: Camera):
    # Always set the selector first so that folling features are applied correctly!
    cam.TriggerSelector.set('FrameStart')

    # optional in this example but good practice as it might be needed for hadware triggering
    cam.TriggerActivation.set('RisingEdge')

    # Make camera listen to Software trigger
    cam.TriggerSource.set('Software')
    cam.TriggerMode.set('On')

class VimbaCameraHandler():

    def __init__(self):

        self.frame = None
        self.n_frames = 0

        self.camera: Camera = None

        self.command_chain = []

        self.commands = \
        {
            "ExposureAuto":     lambda camera, v: camera.ExposureAuto.set(v),
            "BalanceWhiteAuto": lambda camera, v: camera.BalanceWhiteAuto.set(v),
            "BalanceRatio":     lambda camera, v: camera.BalanceRatio.set(v),
            "ExposureTime":     lambda camera, v: camera.ExposureTime.set(v)
        }

    def frame_handler(self, camera, frame):

        print("Got possible frame...")

        if frame.get_status() == FrameStatus.Complete:

            print("Got complete frame...")

            frame.convert_pixel_format(PixelFormat.Rgb8)
            frame_copy = frame.as_numpy_ndarray()

            self.frame = np.array(frame_copy)

            self.n_frames += 1

        camera.queue_frame(frame)

    def callback_camera_input(self, message):

        command = echolib.MessageReader(message).readString().split(" ")

        value   = command[1]
        command = command[0]

        try:
            print(f"Got command: {command} -> {value}")

            if command == "ExposureAuto":
                self.commands[command](self.camera, value)
            elif command == "BalanceWhiteAuto":
                self.commands[command](self.camera, value)
            elif command == "BalanceRatio":
                value = float(value)

                self.commands[command](self.camera, value)
            elif command == "ExposureTime":
                value = float(value)

                self.commands[command](self.camera, value)

        except Exception as e:
            print(f"[ERROR] Error while setting {command} = {value} | error print -> {e}")
            
        
def main():

    ###########################
    # Load camera parameters  #
    ###########################

    config = load(open("/opt/config/camera0.json"))
    config_set_functions = \
    {
        "ExposureAuto": lambda camera, v: camera.ExposureAuto.set(v),
        "DeviceLinkThroughputLimit":  lambda camera, v: camera.DeviceLinkThroughputLimit.set(int(v)),
        "AcquisitionFrameRateEnable": lambda camera, v: camera.AcquisitionFrameRateEnable.set(bool(int(v)))
    }

    ###########################

    handler = VimbaCameraHandler()

    loop   = echolib.IOLoop()
    client = echolib.Client()
    loop.add_handler(client)

    output = FramePublisher(client, "camera_stream_0")
    command_input  = echolib.Subscriber(client, "camera_stream_0_input", "string", handler.callback_camera_input)
    command_output = echolib.Publisher(client, "camera_stream_0_output", "string")

    loop.wait(100)
    
    ###########################

    with Vimba.get_instance() as vimba_instance:

        vimba_cameras = vimba_instance.get_all_cameras()

        with vimba_cameras[0] as vimba_camera:

            handler.camera = vimba_camera
    
            ###########################
            # Grab relevant ranges
            ###########################

            output_ranges = None
            for f in ["BalanceRatio", "ExposureTime"]:
                range = vimba_camera.get_feature_by_name(f).get_range()

                output_ranges = f"{f} {range[0]} {range[1]}" if output_ranges is None else f"{output_ranges} {f} {range[0]} {range[1]}" 

            writer = echolib.MessageWriter()
            writer.writeString(output_ranges)

            command_output.send(writer)

            ###########################
            # Set default camera values
            ###########################

            for feature in config_set_functions:
                try:
                    print(f"Setting default feature {feature} with {config[feature]}")

                    config_set_functions[feature](vimba_camera, config[feature])
                except Exception as e:
                    print(f"[ERROR] Setting camera feature {feature} failer: {e}")

            ###########################
            # Get and set max frame rate
            ###########################

            range = vimba_camera.get_feature_by_name("AcquisitionFrameRate").get_range()
            fr = floor(range[1])

            print(f"Frame rate range: [{range[0]}, {range[1]}]: setting {fr}")

            try:
                vimba_camera.AcquisitionFrameRate.set(fr)
            except Exception as e:
                    print(f"[ERROR] Setting camera frame rate failed: {e}")  
            
            ###########################
            # Send compleated frames  #
            ###########################

            vimba_camera.start_streaming(handler.frame_handler, buffer_count = 1)

            while loop.wait(1):

                if handler.frame is not None:

                    print(f"Sending frame {handler.frame.shape}")

                    output.send(Frame(image = handler.frame))

                    handler.frame = None


            ###########################
        
            vimba_camera.stop_streaming()
        
        print("Stoped streming?")

if __name__=='__main__':
    main()
