import PyCapture2
import numpy as np
from echolib import pyecho
import echocv
import cv2
import sys, getopt

def PyCaptureCameraLoop(pycBus, echlLoop, cameraOut):
    pycCamera = PyCapture2.Camera()
    pycUid    = pycBus.getCameraFromIndex(0)
    pycCamera.connect(pycUid)

    pycCamera.startCapture()

    while echlLoop.wait(1):
        try:
            image = pycCamera.retrieveBuffer()
        except PyCapture2.Fc2error as fc2Err:
            print('Error retrieving buffer : %s' % fc2Err)
            continue
            
        image     = image.convert(PyCapture2.PIXEL_FORMAT.RGB)
        imageData = image.getData()

        imageNummpy = np.array(imageData, dtype="uint8").reshape((image.getRows(), image.getCols(), 3))

        writer = pyecho.MessageWriter()
        echocv.writeMat(writer, imageNummpy)
        cameraOut.send(writer)

        
    pycCamera.stopCamera()

def CVCameraLoop(pycBus, echlLoop, cameraOut):
    
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
            CVCAMERA = True if arg == '1' else False

    # Echolib publisher
    echlLoop = pyecho.IOLoop()
    echlClient = pyecho.Client()
    echlLoop.add_handler(echlClient)

    cameraOut = pyecho.Publisher(echlClient, "cameraStream", "numpy.ndarray")

    # PyCapture camera check
    pycBus   = PyCapture2.BusManager()
    pycNCams = pycBus.getNumOfCameras()

    if pycNCams and not CVCAMERA:
        PyCaptureCameraLoop(pycBus, echlLoop, cameraOut)
    else:
        CVCameraLoop(pycBus, echlLoop, cameraOut)


if __name__=='__main__':
    main()