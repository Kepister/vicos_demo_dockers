import numpy as np
from echolib import pyecho
import echocv
import cv2
import sys, getopt

from vimba import *

import time

import queue
import copy

def VimbaCameraLoop(echlLoop, cameraOut):
    frame_dummy = np.zeros((4000,3000,3),dtype=np.uint8)
    n_frames = 0
    frame_times = []
    frame_latest = queue.Queue(maxsize=2)
    def frame_handler(cam, frame):
        #print('{} acquired {}'.format(cam, frame), flush=True)

        if frame.get_status() == FrameStatus.Complete:
            frame_copy = copy.deepcopy(frame)
            frame_copy.convert_pixel_format(PixelFormat.Rgb8)
            frame_copy = frame_copy.as_numpy_ndarray()
            try:
               frame_latest.put_nowait(frame_copy)
            except queue.Full:
                pass

        cam.queue_frame(frame)

    with Vimba.get_instance() as vimba:

        cams = vimba.get_all_cameras()

        with cams[0] as cam:
            print("start streaming")
            cam.start_streaming(frame_handler,buffer_count=10)
            try:
                start = time.time()
                while echlLoop.wait(1):
                    start = time.time()
                    while True:
                        try:
                            frame = frame_latest.get_nowait()
                            break
                        except queue.Empty:
                            time.sleep(0.001)

                    #print(frame_latest.qsize())

                    # slower if converting here than if doing in callback
                    #frame.convert_pixel_format(PixelFormat.Rgb8)
                    #frame = frame.as_numpy_ndarray()

                    #frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2RGB)
                    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    writer = pyecho.MessageWriter()
                    echocv.writeMat(writer, frame)
                    cameraOut.send(writer)

                    end = time.time()
                    print("FPS: %.1f" % (1/(end-start)))
            finally:
                print("stoping streaming")
                cam.stop_streaming()
                print("end")

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
