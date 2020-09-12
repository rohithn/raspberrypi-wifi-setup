FROM arm32v7/python:3.7-alpine3.11

RUN apk update
# Install dependencies for AP
RUN apk add bridge hostapd wireless-tools wpa_supplicant dnsmasq iw

# Required for vcgencmd
# This requires the device to be attached when running
# docker run --privileged --net host --device /dev/vchiq rohithn/kyle-ap
RUN apk add raspberrypi

# Copy the wpa_supplicant template
RUN mkdir -p /etc/wpa_supplicant/
COPY ./configs/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

# Set up the base config file - override this on run if required
COPY ./configs/wificfg.json /cfg/wificfg.json

WORKDIR /app

COPY ./app ./
COPY requirements.txt ./

RUN pip install -U pip
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]