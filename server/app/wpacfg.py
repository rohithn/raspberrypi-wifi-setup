#!/usr/bin/env python
# -*- coding: utf-8 -*-
# glenn@sensepost.com / @glennzw
# Handle wireless networking from Python
# The name (evil.py) is a play on 'wicd'
from subprocess import Popen, call, PIPE
import errno
from types import *
import logging
import sys
import logging
import time
import argparse
import re
import shlex


"""
This bit of code allows you to control wireless networking
via Python. I chose to encapsualte wpa_supplicant because
it has the most consistent output with greatest functionality.
Currently supports OPEN, WPA[2], and WEP.
#e.g:
>>> iface = get_wnics()[0]
>>> start_wpa(iface)
>>> networks = get_networks(iface)
>>> connect_to_network(iface, "myHomeNetwork", "WPA", "singehackshackscomounaniña")
>>> is_associated(iface)
True
>>> do_dhcp(iface)
>>> has_ip(iface)
True
"""


def run_program(rcmd):
    """
    Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
    Returns output if successful, or None and logs error if not.
    """

    cmd = shlex.split(rcmd)
    executable = cmd[0]

    try:
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, encoding="utf8")
        response_stdout, response_stderr = proc.communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            logging.debug(
                "Unable to locate '%s' program. Is it in your path?" % executable)
        else:
            logging.error(
                "O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)))
    except ValueError as e:
        logging.debug("Value error occured. Check your parameters.")
    else:
        if proc.wait() != 0:
            logging.debug("Executable '%s' returned with the error: \"%s\"" % (
                executable, response_stderr))
            return response_stderr
        else:
            logging.debug("Executable '%s' returned successfully. First line of response was \"%s\"" % (
                executable, response_stdout.split('\n')[0]))
            return response_stdout


def start_wpa(_iface, config_file):
    """
    Terminates any running wpa_supplicant process, and then starts a new one.
    """
    run_program("wpa_cli terminate")
    time.sleep(1)
    run_program(
        f"wpa_supplicant -B -Dwext,nl80211 -i {_iface} -C /var/run/wpa_supplicant -c {config_file} -f /var/log/wpa_supplicant.log")


def get_wnics():
    """
    Kludgey way to get wireless NICs, not sure if cross platform.
    """
    r = run_program("iwconfig")
    ifaces = []
    for line in r.split("\n"):
        if "IEEE" in line:
            ifaces.append(line.split()[0])
    return ifaces


def get_networks(iface, retry=10):
    """
    Grab a list of wireless networks within range, and return a list of dicts describing them.
    """
    while retry > 0:
        if "OK" in run_program("wpa_cli -i %s scan" % iface):
            networks = []
            r = run_program("wpa_cli -i %s scan_result" % iface).strip()
            if "bssid" in r and len(r.split("\n")) > 1:
                for line in r.split("\n")[1:]:
                    b, fr, s, f = line.split()[:4]
                    ss = " ".join(line.split()[4:])  # Hmm, dirty
                    networks.append(
                        {"bssid": b, "freq": fr, "sig": s, "ssid": ss, "flag": f})
                return networks
        retry -= 1
        logging.debug("Couldn't retrieve networks, retrying")
        time.sleep(0.5)
    logging.error("Failed to list networks")


def _disconnect_all(_iface):
    """
    Disconnect all wireless networks.
    """
    lines = run_program("wpa_cli -i %s list_networks" % _iface).split("\n")
    if lines:
        for line in lines[1:-1]:
            run_program("wpa_cli -i %s remove_network %s" %
                        (_iface, line.split()[0]))


def connect_to_network(_iface, _ssid, _type, _pass=None):
    """
    Associate to a wireless network. Support _type options:
    *WPA[2], WEP, OPEN
    """
    _disconnect_all(_iface)
    time.sleep(1)
    if run_program("wpa_cli -i %s add_network" % _iface) == "0\n":
        if run_program('wpa_cli -i %s set_network 0 ssid \'"%s"\'' % (_iface, _ssid)) == "OK\n":
            if _type == "OPEN":
                run_program(
                    "wpa_cli -i %s set_network 0 auth_alg OPEN" % _iface)
                run_program(
                    "wpa_cli -i %s set_network 0 key_mgmt NONE" % _iface)
            elif _type == "WPA" or _type == "WPA2":
                run_program(
                    f'wpa_cli -i {_iface} set_network 0 psk \'"{_pass}"\'')
            elif _type == "WEP":
                run_program(f"wpa_cli -i {_iface} set_network 0 wep_key {_pass}" %
                            (_iface, _pass))
            else:
                logging.error("Unsupported type")

            run_program(f"wpa_cli -i {_iface} enable_network 0")

            retry = 10
            while retry > 0:
                logging.info(
                    f"Checking if the network is connected, retry {retry}")
                if is_associated(_iface):
                    logging.info("Network connected, saving config..")
                    run_program(f"wpa_cli -i {_iface} save_config")
                    run_program(f"wpa_cli -i {_iface} select_network 0")
                    return True
                retry -= 1
                logging.debug("Not connected, retrying")
                time.sleep(1)

    return False


def is_associated(_iface):
    """
    Check if we're associated to a network.
    """
    if "wpa_state=COMPLETED" in run_program("wpa_cli -i %s status" % _iface):
        return True
    return False


def has_ip(_iface):
    """
    Check if we have an IP address assigned
    """
    status = run_program("wpa_cli -i %s status" % _iface)
    r = re.search("ip_address=(.*)", status)
    if r:
        return r.group(1)
    return False


def do_dhcp(_iface):
    """
    Request a DHCP lease.
    """
    run_program("dhclient %s" % _iface)
