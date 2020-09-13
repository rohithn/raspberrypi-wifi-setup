import logging
import subprocess
import selectors
import threading
import fileinput


class WpaNetwork:
    bssid: str
    frequency: str
    signal_level: str
    flags: str
    ssid: str


class Command(threading.Thread):

    def __init__(self, cmd, cmd_input=None, fail_on_error=True):
        self.cmd = cmd
        self.cmd_input = cmd_input
        self.fail_on_error = fail_on_error
        threading.Thread.__init__(self)

    def run(self):

        logging.info(f'cmd: {" ".join(map(str, self.cmd))}')

        p = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)

        if self.cmd_input:
            logging.debug(self.cmd_input)
            p.stdin.write(self.cmd_input)
            p.stdin.close()

        while(True):
            # returns None while subprocess is running
            retcode = p.poll()
            line = p.stdout.readline()
            if line:
                logging.info(line)
            if retcode is not None:
                break
        p.stdout.close()
        if p.returncode > 0:
            err = p.stderr.read()
            logging.error(err)
            p.stderr.close()
            if self.fail_on_error:
                raise Exception(err)


def reset_wpa_supplicant(country):
    logging.info("Resetting wpa_supplicant.conf..")
    cmd1 = ["mv", "/etc/wpa_supplicant/wpa_supplicant.conf",
            "/etc/wpa_supplicant/old_wpa_supplicant.conf"]
    process_cmd(cmd1)
    cmd2 = ["cp", "/cfg/wpa_supplicant.conf",
            "/etc/wpa_supplicant/wpa_supplicant.conf"]
    process_cmd(cmd2)
    cmd3 = ["sed", "-i",
            f"/country=/c\country={country}", "/etc/wpa_supplicant/wpa_supplicant.conf"]
    process_cmd(cmd3)


def remove_ap_interface():
    logging.info("Removing existing interface (uap0) for access point..")
    cmd = ["iw", "dev", "uap0", "del"]
    process_cmd(cmd, fail_on_error=False)


def add_ap_interface():
    logging.info("Adding interface (uap0) for access point..")
    cmd = ["iw", "phy", "phy0", "interface", "add", "uap0", "type", "__ap"]
    process_cmd(cmd)


def up_ap_interface():
    logging.info("Bringing up access point interface (uap0)...")
    cmd = ["ifconfig", "uap0", "up"]
    process_cmd(cmd)


def down_ap_interface():
    logging.info("Bringing down access point interface (uap0)...")
    cmd = ["ifconfig", "uap0", "down"]
    process_cmd(cmd)


def configure_ap_interface(access_point_ip: str):
    logging.info(
        f"Configuring access point interface (uap0) with IP: {access_point_ip}")
    cmd = ["ifconfig", "uap0", access_point_ip]
    process_cmd(cmd)


def enable_ap():
    logging.info("Enabling access point interface (uap0)...")
    cmd = ["hostapd_cli", "-i", "uap0", "enable"]
    process_cmd(cmd)


def disable_ap():
    logging.info("Disabling access point interface (uap0)..")
    cmd = ["hostapd_cli", "-i", "uap0", "disable"]
    process_cmd(cmd)


def start_hostapd(wpa_passphrase, channel, ssid=None):
    logging.info("Starting hostapd...")
    if not ssid:
        ssid = get_ssid()

    cfg = ('interface=uap0\n'
           'ssid={0}\n'
           'hw_mode=g\n'
           'channel={1}\n'
           'ctrl_interface=/var/run/hostapd\n'
           'ctrl_interface_group=0\n'
           'macaddr_acl=0\n'
           'auth_algs=1\n'
           'ignore_broadcast_ssid=0\n'
           'wpa=2\n'
           'wpa_passphrase={2}\n'
           'wpa_key_mgmt=WPA-PSK\n'
           'wpa_pairwise=TKIP\n'
           'rsn_pairwise=CCMP\n').format(ssid, channel, wpa_passphrase)
    cmd = [
        "hostapd",
        "/dev/stdin"
    ]

    # process_cmd(cmd, cmd_input=cfg)
    cmd_exec = Command(cmd, cmd_input=cfg)
    cmd_exec.start()


def start_wpa_supplicant(config_file_path):
    logging.info("Starting wpa_supplicant...")

    cmd = ["wpa_cli", "terminate"]
    process_cmd(cmd)

    cmd = [
        "wpa_supplicant",
        "-Dnl80211",
        "-iwlan0",
        "-c" + config_file_path
    ]
    # process_cmd(cmd)

    cmd_exec = Command(cmd)
    cmd_exec.start()


def start_dnsmasq(domain, address, dhcp_range, vendor_class):
    logging.info("Starting dnsmasq")
    cmd = ["dnsmasq",
           "--no-hosts",  # Don't read the hostnames in /etc/hosts.
           "--keep-in-foreground",
           "--interface=uap0",
           "--log-queries",
           "--no-resolv",
           "--domain=" + domain,
           "--address=" + address,
           "--dhcp-range=" + dhcp_range,
           "--dhcp-vendorclass=" + vendor_class,
           "--dhcp-authoritative",
           "--log-facility=-",
           ]
    # process_cmd(cmd)
    cmd_exec = Command(cmd)
    cmd_exec.start()


def wpa_scan():
    logging.info("Running Scan...")
    cmd = ["wpa_cli", "-i", "wlan0", "scan"]
    return process_cmd(cmd)


def wpa_scanresults():
    logging.info("Fetching Scan Results")
    cmd = ["wpa_cli", "-i", "wlan0", "scan_results"]
    return process_cmd(cmd)


def get_ssid():

    # Create a ssid for this node
    vcgencmd_result = subprocess.Popen(
        ['/opt/vc/bin/vcgencmd', 'otp_dump'], stdout=subprocess.PIPE)

    grep = subprocess.Popen(
        ['grep', '^28'], stdin=vcgencmd_result.stdout, stdout=subprocess.PIPE)

    node_id = grep.communicate()[0].decode(
        'UTF-8').split(':')[1].strip().encode('utf-8')

    new_ssid = "kyle-{}".format(node_id.decode('UTF-8'))

    return new_ssid


def process_cmd(cmd, cmd_input=None, fail_on_error=True):

    logging.info(f'cmd: {" ".join(map(str, cmd))}')

    result = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="utf8")
    logging.info(result.stdout)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return process.communicate()
