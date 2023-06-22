FROM ubuntu:latest

RUN apt update
RUN apt install python3 python3-pip curl -y

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

RUN mkdir /backend

COPY ./backend /backend

RUN pip3 install -r ./backend/requirements.txt