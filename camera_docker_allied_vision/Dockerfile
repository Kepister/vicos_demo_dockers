FROM debian:10

LABEL maintainer "pm4824@student.uni-lj.si"

ENV DEBIAN_FRONTEND noninteractive

###########################DETECTED_PYTHONS###########
# install dependencies for vicos-demo (echolib and echocv)

ENV WD /home

WORKDIR ${WD}

#RUN apt-get update && apt-get install software-properties-common -y && add-apt-repository ppa:ubuntu-toolchain-r/ppa \
#    && apt-get update && apt-get install python3.7 -y
#RUN python3.7 -m pip install numpy

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake make git pkg-config g++ ffmpeg libtinyxml2-dev software-properties-common libopencv-dev wget python3-dev python3-numpy-dev python3-pip && \
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

COPY camera.py ${WD}

RUN mkdir /etc/udev
RUN mkdir /etc/udev/rules.d

# Install Allied Vision SDK
RUN cd ${WD} && wget https://downloads.alliedvision.com/Vimba_v5.0_Linux.tgz
#RUN tar -xzf Vimba_v5.0_Linux.tgz
RUN tar -xzf Vimba_v5.0_Linux.tgz && cd ${WD}/Vimba_5_0/VimbaUSBTL && ./Install.sh && cd ${WD}/Vimba_5_0/VimbaPython && ./Install.sh

ENV GENICAM_GENTL64_PATH=$GENICAM_GENTL64_PATH:"/home/Vimba_5_0/VimbaUSBTL/CTI/x86_64bit"

# define entry-point and default arguments
ENTRYPOINT ["/bin/bash"]
