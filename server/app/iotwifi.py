import sys
import json
import logging
import time
import subprocess
import selectors

from threading import Thread

from models import SetupCfg
import commands
import wpacfg


log = logging.getLogger(__name__)


def run_wifi(config: str):

    log.info("Loading IoT Wifi...")

    with open(config) as json_txt:
        try:
            cfg_dict = json.load(json_txt)
            cfg = SetupCfg(cfg_dict)
        except IOError:
            log.error("Could not read config file:", config)
            return

    log.info("Configuring AP interface...")
    commands.remove_ap_interface()
    commands.add_ap_interface()
    commands.up_ap_interface()
    commands.configure_ap_interface(cfg.hostapd_cfg.ip)

    commands.start_hostapd(cfg.hostapd_cfg.wpa_passphrase,
                           cfg.hostapd_cfg.channel)

    time.sleep(5)

    log.info("Configuring wpa_supplicant...")
    commands.reset_wpa_supplicant(cfg.wpa_supplicant_cfg.country)
    commands.start_wpa_supplicant(cfg.wpa_supplicant_cfg.cfg_file)
    # wpacfg.start_wpa("wlan0", cfg.wpa_supplicant_cfg.cfg_file)

    time.sleep(5)

    log.info("Running an initial scan...")
    # scan_networks()
    logging.info(wpacfg.get_networks("wlan0"))

    time.sleep(5)

    log.info("Starting DNS server...")
    commands.start_dnsmasq(cfg.dnsmasq_cfg.domain, cfg.dnsmasq_cfg.address,
                           cfg.dnsmasq_cfg.dhcp_range, cfg.dnsmasq_cfg.vendor_class)

    log.info("Completed configuration of services.")


def scan_networks():
    return wpacfg.get_networks("wlan0")


def ap_status():
    pass


def configured_networks():
    pass


def connect_network(ssid, password, net_type):
    return wpacfg.connect_to_network("wlan0", ssid, net_type, _pass=password)


def wlan_status():
    return wpacfg.is_associated("wlan0")
