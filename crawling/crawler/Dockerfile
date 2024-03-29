FROM selenium/standalone-chrome:latest AS base

WORKDIR /usr/src/app

# copy entire project
COPY . .

WORKDIR /

USER root
RUN apt-get -y update

# python (don't think i need these lines tbh)
#RUN apt-get install -y software-properties-common
#RUN add-apt-repository ppa:deadsnakes/ppa
#RUN apt-get -y install python3.8

# killall
RUN apt-get -y install psmisc

# dumpcap to get pcap files
RUN apt -y install wireshark

# tshark to parse pcap files
RUN apt-get -y install tshark

# to solve issues with webcrawling within docker
#RUN sudo mount -t tmpfs -o rw,nosuid,nodev,noexec,relatime,size=512M tmpfs /dev/shm

# pip
#RUN apt -y install wget
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

# py packages
USER 1001
RUN python3 -m pip install selenium
RUN python3 -m pip install psutil
RUN python3 -m pip install scapy
RUN python3 -m pip install pyvirtualdisplay
RUN python3 -m pip install typing-extensions

USER root


WORKDIR /usr/src/app

EXPOSE 4444
EXPOSE 7900