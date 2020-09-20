import os
import logging
import subprocess

from flask import Flask, request, render_template
from flask_cors import CORS

import iotwifi

from itertools import dropwhile, takewhile


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    return {'result': {'connected': iotwifi.wlan_status()}}


@app.route('/list')
def list():
    nets = iotwifi.configured_networks()
    return {'result': nets}


@app.route("/scan")
def scan():
    networks = iotwifi.scan_networks()
    return {'result': networks}


@app.route("/connect", methods=['POST'])
def connect():
    data = request.get_json()
    ssid = data["ssid"]
    password = data["password"]
    net_type = data["type"]
    res = iotwifi.connect_network(ssid, password, net_type)
    if res:
        return {'result': {'connected': res}}
    else:
        return {'result': {'connected': res}}, 400


@app.route("/reset", methods=['POST'])
def reset():
    res = iotwifi.reset_networks()
    if res:
        return {'result': {'connected': res}}
    else:
        return {'result': {'connected': res}}, 400


if __name__ == "__main__":
    log.info("Starting IoT Wifi...")

    # Configure system to start ap and wifi
    iotwifi.run_wifi("/cfg/wificfg.json")

    app.run(debug=False, host='0.0.0.0', port=80)
