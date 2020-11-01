## Raspberry Pi WiFi Setup

This is a Raspberry Pi wifi management module written in Python and intended to run in a 
Docker container on a [Raspberry Pi 3](https://amzn.to/2jfXhCA). It exposes a simple web form for 
controlling the wireless network interface. This container allows the Raspberry Pi to accept wifi connections 
as an access point (aka AP) while at the same time connecting to an existing wifi network (station mode).

This module sets up network interfaces, runs [hostapd], [wpa_supplicant] and [dnsmasq] to run simultaneously,  
allowing a user (or another service) to connect to the Raspberry Pi via [hostapd]/[dnsmasq] and issue commands 
that configure and connect [wpa_supplicant] to another [AP]. The module then exposes a small web server on the Pi 
and offers a simple web page based on REST APIs to configure Wifi. The container allows you to connect from another 
device and configure the target device.

The container runs [Alpine Linux](https://alpinelinux.org/) with small, optimized versions of [hostapd], 
[wpa_supplicant] and [dnsmasq], controlled by the container's API endpoints.

Table of Contents
=================
      
* [Getting Started](#getting-started)
    * [Disable wpa_supplicant on Raspberry Pi](#disable-wpa_supplicant-on-raspberry-pi)
    * [Install Docker on Raspberry Pi](#install-docker-on-raspberry-pi)
    * [Build the Docker Image](#build-the-docker-image)
    * [Run the Docker Container](#run-the-docker-container)
    * [Connect to the Pi over Wifi](#connect-to-the-pi-over-wifi)
    * [Connect the Pi to a Wifi Network](#connect-the-pi-to-a-wifi-network)


## Getting Started

You will need a Raspberry Pi 3, running [Raspberry Pi OS Stretch](https://www.raspberrypi.org/downloads/raspberry-pi-os/). 
You can use the [Noobs] release to install the latest version of the OS. 
This has been tested with Raspberry Pi OS (32-bit) Lite.

### Disable wpa_supplicant on Raspberry Pi

You do not want the default **[wpa_supplicant]** (the software that communicates
with the wifi driver and connects to Wifi networks,) running and competing
with the container.

```bash
# stop wpa_supplicant service
$ sudo systemctl stop wpa_supplicant.service

# kill any running processes named wpa_supplicant
$ sudo pkill wpa_supplicant
```

### Install Docker on Raspberry Pi

Ssh into the Pi or use the terminal application from the desktop on the Pi
to get a Bash shell.

```bash
# Docker install script
$ curl -sSL https://get.docker.com | sh

# add pi user to Docker user group
$ sudo usermod -aG docker pi
```

Reboot the Pi and test Docker.

```bash
$ sudo reboot
```

After reboot, ensure Docker is installed correctly by running a Hello World
Docker container.

```bash
# run the Docker Hello World container and remove the container
# when finished (the --rm flag)
$ docker run --rm hello-world
```

### Build the Docker Image

If you wish to change the default configuration of the container, edit the contents of the 
`server/configs/wificfg.json` and `server/configs/wpa_supplicant.conf` files. 

The default configuration looks like this:

```json
{
  "dnsmasq_cfg": {
    "domain": "kyle.rmot.io",
    "address": "/kyle.rmot.io/10.60.0.1",
    "dhcp_range": "10.60.0.100,10.60.0.150,12h",
    "vendor_class": "set:device,IoT"
  },
  "host_apd_cfg": {
    "ip": "10.60.0.1",
    "ssid": "kyle-ap",
    "wpa_passphrase": "hellokyle",
    "channel": "6"
  },
  "wpa_supplicant_cfg": {
    "country": "US",
    "cfg_file": "/etc/wpa_supplicant/wpa_supplicant.conf"
  }
}
```

The **ssid** and the **wpa_passphrase** can be configured while running the container, 
so it does not need to be changed now.

Next, build the image.

```bash
$ docker build -t wifi-configure .
```

This will create a docker image named wifi-configure.

### Run the Docker Container

The following `docker run` command will create a running Docker container from
the Docker image that we created in the steps above. The container needs to run in a **privileged mode** 
and have access to the **host network** (the Raspberry Pi device) to configure and manage the network interfaces on
the Raspberry Pi. You can also map a directory containing `wpa_supplicant.conf`.


```bash
$ docker run -d \
      --restart=unless-stopped \
      --name kyle-ap \
      --privileged --net host \
      -e AP_SSID=kyle-ap \
      -e AP_PASS=hellokyle \
      -v /etc/wpa_supplicant:<WPA_SUPPLICANT_CONTAINER_PATH> \
      wifi-configure
```

Where `<WPA_SUPPLICANT_CONTAINER_PATH>` is the path containing `wpa_supplicant.conf` specified in `wificfg.json`.

[Read more on the `docker run` command.](https://docs.docker.com/engine/reference/run/)


Take a look the network interfaces on the Raspberry Pi.

```bash
# use ifconfig to view the network interfaces
$ ifconfig
```

You should see a new interface called **uap0**:

```plain
uap0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.27.1  netmask 255.255.255.0  broadcast 192.168.27.255
        inet6 fe80::6e13:d169:b00b:c946  prefixlen 64  scopeid 0x20<link>
        ether b8:27:eb:fe:c8:ab  txqueuelen 1000  (Ethernet)
        RX packets 111  bytes 8932 (8.7 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 182  bytes 24416 (23.8 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

The standard wifi interface **wlan0** should be available, yet unconfigured since we have not yet connected to an external wifi network (access point).

```plain
wlan0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether b8:27:eb:fe:c8:ab  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

### Connect to the Pi over Wifi

On your laptop or phone, you should now see a new Wifi Network with the name that you specified while running the container. Once connected to this network you should get an IP address assigned to the range specified in the config: `10.60.0.100,10.60.0.150,12h`.

### Connect the Pi to a Wifi Network

Once connected open a web browser and go to http://kyle.rmot.io/. Use the web form to select and connect to any network that is available.

### Troubleshooting

**Unable to open kyle.rmot.io in the web browser:**
It takes a few seconds for the [dnsmasq] in the container to start up. If you connect to the access-point before this service starts up, the device may be assigned an IP outside of the specified range. If this happens, try reconnecting to the AP again. If it still does not resolve, try using the IP of the Raspberry Pi which is 10.60.0.1.


[Noobs]: https://www.raspberrypi.org/downloads/noobs/
[hostapd]: https://w1.fi/hostapd/
[wpa_supplicant]: https://w1.fi/wpa_supplicant/
[dnsmasq]: http://www.thekelleys.org.uk/dnsmasq/doc.html
[AP]: https://en.wikipedia.org/wiki/Wireless_access_point
[Station]: https://en.wikipedia.org/wiki/Station_(networking)
[IOT]: https://en.wikipedia.org/wiki/Internet_of_things
[Docker]: https://www.docker.com/
[Alpine Linux]: https://alpinelinux.org/
