#!/bin/bash

# Sample scripts to start up the docker container when there is no internet.

wget -q --spider http://google.com

wpa_status=$(wpa_cli  status | grep wpa_state | cut -d"=" -f2)

if test  "$wpa_status" = "COMPLETED"
then
    echo "$wpa_status, not starting ap container"
    # wpa_passphrase "$1" "$2" >> /etc/wpa_supplicant.conf
else
    echo " $wpa_status : starting ap container"
    sudo wpa_cli -i wlan0 terminate
    sudo systemctl stop wpa_supplicant
    sudo killall wpa_supplicant
    docker build -t wifi-configure .
    docker run --rm --name kyle-ap --privileged --net host --device /dev/vchiq -v /etc/wpa_supplicant:/etc/wpa_supplicant wifi-configure
fi
