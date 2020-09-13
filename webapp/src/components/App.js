import React, { useState, useEffect } from "react";
import { getNetworks, connectNetwork, getStatus } from "../api/wifiApis";
import Select from "react-select";
import "./App.css";
import status_simple from "../assets/status_simple.png";

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState();
  const [networks, setNetworks] = useState([]);
  const [bssid, setBssid] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getStatus()
      .then((_status) => {
        setIsConnected(_status.result.connected);

        console.log("Network is " + isConnected);

        if (!isConnected && networks.length === 0) {
          console.log("Fetching networks..");
          getNetworks()
            .then((_networks) => {
              if (_networks.result) {
                let list = _networks.result.map((network) => ({
                  label: network.ssid,
                  value: network.bssid,
                }));
                setNetworks(_networks.result.filter((item) => item.ssid));
                setSelectOptions(list.filter((item) => item.label));
              }
            })
            .catch((err) => {
              setError(err);
            });
        }
      })
      .catch((err) => {
        setError(err);
      });
  }, []);

  const handleSubmit = (e) => {
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
        setIsConnected(true);
      })
      .catch((err) => {
        setMessage("");
        setError("Error: Could not connect to network");
        setIsConnected(false);
      });
  };

  const findNetwork = (bssid) => {
    console.log(bssid);
    const result = networks.filter((obj) => {
      return obj.bssid === bssid;
    });
    return result[0];
  };

  const handleSelect = (value) => {
    setSelectedOption(value);
    setBssid(value.value);
    setError("");
    setMessage("");
  };

  let messageDiv = "";
  if (message) {
    messageDiv = <div className="message">{message}</div>;
  }
  if (error) {
    messageDiv = <div className="error">{error}</div>;
  }

  let form = (
    <form id="contact-form" onSubmit={handleSubmit}>
      <h3>Kyle WIFI Setup</h3>
      <h4>Please select the ssid and enter password for your site.</h4>
      <div>
        <label>
          <span>SSID: (required)</span>
          {/* <select
              value={bssid}
              onChange={(e) => handleSelect(e.target.value)}
            >
              {networks.map((option, key) => (
                <option key={key} value={option.bssid}>
                  {option.ssid}
                </option>
              ))}
            </select> */}
          <Select
            className="select"
            options={selectOptions}
            value={selectedOption}
            onChange={(value) => handleSelect(value)}
            placeholder={"Select a network"}
          />
        </label>
      </div>
      <div>
        <label>
          <span>Password:</span>
          <input
            placeholder="Please enter SSID's Password"
            name="password"
            type="password"
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
  );

  let connectedImage = (
    <div id="img-container">
      <img className="img-content" src={status_simple} alt="connected" />
      <h2 className="img-content">WIFI Connected!</h2>
    </div>
  );

  return (
    <div id="main" style={{ paddingTop: "50px", paddingBottom: "50px" }}>
      <div className="wrapper">{isConnected ? connectedImage : form}</div>
    </div>
  );
}

export default App;
