FROM ubuntu:18.04

LABEL maintainer "pm4824@student.uni-lj.si"

ENV DEBIAN_FRONTEND noninteractive

######################################
# install dependencies for vicos-demo (echolib and echocv)

ENV WD /home

WORKDIR ${WD}

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git python3-dev python3-numpy-dev python3-pip libopencv-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

##################################
# install dependency pybind11
RUN git clone https://github.com/wjakob/pybind11.git && cd pybind11 && mkdir build && cd build && cmake -DPYBIND11_TEST=OFF -DPYBIND11_INSTALL=ON .. && make -j install
# install echolib
RUN git clone --depth 1 https://github.com/MysteriousMan231/echolib.git
RUN cd ${WD}//echolib && mkdir build && cd build && \
    cmake -DBUILD_DAEMON=OFF .. && make -j && make install && cd ../.. && rm -r echolib

# install echocv
RUN git clone --depth 1 https://github.com/MysteriousMan231/echocv.git
RUN cd ${WD}//echocv && mkdir build && cd build && \
    cmake -DBUILD_APPS=OFF .. && make -j && make install && cd ../.. && rm -r echocv

##################################
RUN python3 -m pip install --upgrade pip && python3 -m pip install setuptools
RUN python3 -m pip install opencv-python>=3 cython

COPY flycapture ${WD}/flycapture
COPY pyCapture  ${WD}/pyCapture
COPY camera.py  ${WD}

# Install FlyCapture dependecies and install FlyCapture
RUN apt-get update && apt-get install -y libraw1394-11 libavcodec57 libavformat57 libswscale4 libswresample2 libavutil55 libgtkmm-2.4-1v5 libglademm-2.4-1v5 libgtkglextmm-x11-1.2-0v5 libgtkmm-2.4-dev libglademm-2.4-dev libgtkglextmm-x11-1.2-dev libusb-1.0-0

RUN cd ${WD}/flycapture && /bin/bash install_flycapture.sh

RUN python3 ${WD}/pyCapture/setup.py install

# Install Allied Vision SDK
RUN cd ${WD} && wget https://download.alliedvision.com/Vimba_v5.0_Linux.tgz
RUN tar -xzf Vimba_v5.0_Linux.tgz
RUN cd ${WD}/Vimba_v5.0_Linux/Vimba_5_0/VimbaGigETL/Install.sh
RUN cd ${WD}/Vimba_v5.0_Linux/Vimba_5_0/VimbaUSBTL/Install.sh
RUN cd ${WD}/Vimba_v5.0_Linux/Vimba_5_0/VimbaPython/Install.sh

# define entry-point and default arguments
ENTRYPOINT ["/bin/bash"]