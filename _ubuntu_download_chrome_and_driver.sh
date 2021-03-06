#!/bin/bash

apt-get install sudo

sudo apt-get update \
    && apt-get install -y wget unzip \
    && rm -rf /var/lib/apt/lists/*

wget -N http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_92.0.4515.159-1_amd64.deb
wget -N https://chromedriver.storage.googleapis.com/92.0.4515.107/chromedriver_linux64.zip
unzip -o chromedriver_linux64.zip
