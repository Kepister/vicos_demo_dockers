#!/usr/bin/python

import echolib
from echolib.camera import Frame, FramePublisher, FrameSubscriber
from time import time, sleep

import numpy as np

SEND_FRAME = False

channel_in  = "out"
channel_out = "in"

counter = 0

def __callback_image(message):
    
    global counter
    counter += 1

    image = message.image

    print("Msg {}: {}".format(counter, image.shape))

def __callback_string(message):

    global counter
    counter += 1

    print("Msg {}: {}".format(counter, echolib.MessageReader(message).readString()))

loop   = echolib.IOLoop()
client = echolib.Client()
loop.add_handler(client)

if SEND_FRAME:
    subscriber = FrameSubscriber(client, channel_in, __callback_image)
    publisher  = FramePublisher(client, channel_out)
else:
    subscriber = echolib.Subscriber(client, channel_in, "string", __callback_string)
    publisher  = echolib.Publisher(client, channel_out, "string")

print("Writing to: {}\nListening on: {}".format(channel_out, channel_in))

t = time()

while loop.wait(1):
    
    if (time() - t) >= 1:

        if SEND_FRAME:
            publisher.send(Frame(image = np.zeros((300, 300, 3), dtype = np.float32)))
        else:
            writer = echolib.MessageWriter()
            writer.writeString("Hello there")
            publisher.send(writer)

        t = time()

    sleep(0.1)