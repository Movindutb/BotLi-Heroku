FROM ubuntu:jammy
ENV DEBIAN_FRONTEND noninteractive
MAINTAINER activer
RUN echo activer
CMD echo activer
COPY . .


RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get upgrade -y && apt-get install -y sudo curl apt-utils libqt5gui5 python3-psutil wget python3 python3-pip p7zip-full git build-essential

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN chmod +x engines/stockfish
RUN chmod +x engines/multivariant_stockfish