import React, { useState, useEffect } from "react";
import { getNetworks, connectNetwork } from "../api/wifiApis";
import "./App.css";

function App() {
  const [networks, setNetworks] = useState([]);
  const [bssid, setBssid] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getNetworks().then((_networks) => {
      setNetworks(_networks.result.filter((item) => item.ssid));
    });
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    let ssid,
      type = "";

    const network = findNetwork(bssid);
    if (network) {
      ssid = network.ssid;
      if (network.flag.includes("WPA")) {
        type = "WPA";
      } else if (network.flag.includes("WEP")) {
        type = "WEP";
      } else {
        type = "Open";
      }
    }
    setMessage("Connecting...");
    setError("");

    console.log(ssid, password, type);

    connectNetwork(ssid, password, type)
      .then(() => {
        setMessage("Connected!");
        setError("");
        setNetworks([]);
        setPassword("");
      })
      .catch((err) => {
        setMessage("");
        setError(err.message);
      });
  };

  const findNetwork = (bssid) => {
    const result = networks.filter((obj) => {
      return obj.bssid === bssid;
    });
    return result[0];
  };

  const handleSelect = (value) => {
    setBssid(value);
    setError("");
    setMessage("");
  };

  let messageDiv = "";
  if (message) {
    messageDiv = <div class="message">{message}</div>;
  }
  if (error) {
    messageDiv = <div class="error">{error}</div>;
  }

  return (
    <div id="main" style={{ paddingTop: "50px", paddingBottom: "50px" }}>
      <div className="wrapper">
        <form id="contact-form" onSubmit={handleSubmit}>
          <h3>Kyle WIFI Setup</h3>
          <h4>Please select the ssid and enter password for your site.</h4>
          <div>
            <label>
              <span>SSID: (required)</span>
              <select
                value={bssid}
                onChange={(e) => handleSelect(e.target.value)}
              >
                {networks.map((option, key) => (
                  <option key={key} value={option.bssid}>
                    {option.ssid}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div>
            <label>
              <span>Password:</span>
              <input
                placeholder="Please enter SSID's Password"
                name="password"
                type="text"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
          </div>
          {messageDiv}
          <div>
            <button name="submit" type="submit" id="contact-submit">
              Connect
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
