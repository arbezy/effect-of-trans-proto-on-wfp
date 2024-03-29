# syntax=docker/dockerfile:1

FROM ubuntu:latest

WORKDIR /

COPY . .

RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y unzip xvfb libxi6 libgconf-2-4
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN apt-get -y update



EXPOSE 3000