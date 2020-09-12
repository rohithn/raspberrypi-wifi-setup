# Using multistage Docker build to build the frontent first
FROM node:12.18.0-alpine as build

WORKDIR /webapp

COPY ./webapp/package.json ./
COPY ./webapp/package-lock.json ./

# Install dependencies - similar to npm install
RUN npm ci

COPY ./webapp ./

# We will get the 'build' folder after this..
RUN npm run build

# Set up the Flask app
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

# Set up the base config files - override this on run if required
COPY ./server/configs/wpa_supplicant.conf /cfg/wpa_supplicant.conf
COPY ./server/configs/wificfg.json /cfg/wificfg.json

WORKDIR /app

COPY ./server/app ./
COPY ./server/requirements.txt ./

RUN pip install -U pip
RUN pip install -r requirements.txt

# Get the static webpage files from the build stage
COPY --from=build /webapp/build/index.html ./templates/
COPY --from=build /webapp/build/static ./static

CMD ["python3", "app.py"]
