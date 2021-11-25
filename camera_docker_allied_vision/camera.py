import numpy as np
from echolib import pyecho
import echocv
import cv2
import sys, getopt

from vimba import *

def VimbaCameraLoop(echlLoop, cameraOut):

    with Vimba.get_instance() as vimba:

        cams = vimba.get_all_cameras()

        with cams[0] as cam:

            while echlLoop.wait(1):

                frame = cam.get_frame()
                frame.convert_pixel_format(PixelFormat.Bgr8)
                frame = cv2.resize(frame.as_opencv_image(), (1920, 1080), interpolation = cv2.INTER_AREA)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                print(f"Reading camera ... {frame[0:5, 0:5, :]}")

                writer = pyecho.MessageWriter()
                echocv.writeMat(writer, frame)
                cameraOut.send(writer)

def CVCameraLoop(echlLoop, cameraOut):
    
    camera = cv2.VideoCapture(0)

    while echlLoop.wait(1):

        _, frame = camera.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        writer = pyecho.MessageWriter()
        echocv.writeMat(writer, frame)
        cameraOut.send(writer)

    camera.release()

def main():

    CVCAMERA = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError:
        print("dockerCameraScript -c <1/0>")
        return

    for opt, arg in opts:
        if opt == '-c':
            CVCAMERA = arg == '1'

    # Echolib publisher
    echlLoop = pyecho.IOLoop()
    echlClient = pyecho.Client()
    echlLoop.add_handler(echlClient)

    cameraOut = pyecho.Publisher(echlClient, "cameraStream", "numpy.ndarray")

    if CVCAMERA:
        CVCameraLoop(echlLoop, cameraOut)
    else:
        VimbaCameraLoop(echlLoop, cameraOut)
    


if __name__=='__main__':
    main()