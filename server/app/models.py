import os


class DnsmasqCfg:
    domain: str             # --domain=kyle.rmot.io",
    address: str            # --address=/#/192.168.27.1",
    dhcp_range: str         # "--dhcp-range=192.168.27.100,192.168.27.150,1h",
    vendor_class: str       # "--dhcp-vendorclass=set:device,IoT",

    def __init__(self, json):
        self.domain = json['domain']
        self.address = json['address']
        self.dhcp_range = json['dhcp_range']
        self.vendor_class = json['vendor_class']


class HostApdCfg:
    ssid: str               # ssid=iotwifi2
    wpa_passphrase: str     # wpa_passphrase=iotwifipass
    channel: str            # channel=6
    ip: str                 # 192.168.27.1

    def __init__(self, json):
        self.ssid = os.environ.get("AP_SSID") or json['ssid']
        self.wpa_passphrase = os.environ.get("AP_PASS") or json['wpa_passphrase']
        self.channel = json['channel']
        self.ip = json['ip']


class WpaSupplicantCfg:
    country: str            # country=US
    cfg_file: str           # /etc/wpa_supplicant/wpa_supplicant.conf

    def __init__(self, json):
        self.country = json['country']
        self.cfg_file = json['cfg_file']


class SetupCfg:
    dnsmasq_cfg: DnsmasqCfg
    hostapd_cfg: HostApdCfg
    wpa_supplicant_cfg: WpaSupplicantCfg

    def __init__(self, json):
        self.dnsmasq_cfg = DnsmasqCfg(json['dnsmasq_cfg'])
        self.hostapd_cfg = HostApdCfg(json['host_apd_cfg'])
        self.wpa_supplicant_cfg = WpaSupplicantCfg(json['wpa_supplicant_cfg'])
