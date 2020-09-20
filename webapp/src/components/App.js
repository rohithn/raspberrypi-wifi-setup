import React, { useState, useEffect, useRef } from "react";
import {
  getNetworks,
  connectNetwork,
  resetNetwork,
  getStatus,
} from "../api/wifiApis";
import "./App.css";
import Connected from "./Connected";
import NetworkSelect from "./NetworkSelect";

function App() {
  const [isConnected, setIsConnected] = useState();
  const [networks, setNetworks] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const formRef = useRef();

  useEffect(() => {
    console.log("Fetching status..");
    getStatus()
      .then((_status) => {
        setIsConnected(_status.result.connected);
      })
      .catch((err) => {
        setError(err.message);
      });
  }, []);

  useEffect(() => {
    if (!isConnected) {
      fetchNetworks();
    }
  }, [isConnected]);

  const fetchNetworks = () => {
    console.log("Fetching networks..");
    getNetworks()
      .then((_networks) => {
        if (_networks.result) {
          const results = _networks.result.filter((item) => item.ssid);
          setNetworks(results);
        }
      })
      .catch((err) => {
        if (err.message) {
          setError(err.message);
        } else {
          setError(err.toString());
        }
      });
  };

  const handleSubmit = (ssid, type, password) => {
    console.log(ssid, password, type);

    setError("");
    setMessage("Connecting...");

    if (!ssid) {
      setError("SSID cannot be empty");
      setMessage("");
      return;
    }

    if (type !== "OPEN" && !password) {
      setError("Password cannot be empty.");
      setMessage("");
      return;
    }

    connectNetwork(ssid, password, type)
      .then(() => {
        setMessage("Connected!");
        setError("");
        setNetworks([]);
        setIsConnected(true);
      })
      .catch((err) => {
        setMessage("");
        if (err.result && !err.result.connected) {
          setError("Could not connect to network");
        } else {
          formRef.current.resetForm();
          setError(err.toString());
        }
        setIsConnected(false);
      });
  };

  const handleReset = () => {
    resetNetwork()
      .then(() => {
        setMessage("");
        setError("");
        setNetworks([]);
        setIsConnected(false);
      })
      .catch((err) => {
        setMessage("");
        setError(err);
        setIsConnected(false);
      });
  };

  let messageDiv = "";
  if (message) {
    messageDiv = <div className="message">{message}</div>;
  }
  if (error) {
    messageDiv = <div className="error">{error}</div>;
  }

  return (
    <div id="main" style={{ paddingTop: "50px", paddingBottom: "50px" }}>
      <div className="wrapper">
        <div className="content">
          {isConnected ? (
            <Connected onClick={handleReset} />
          ) : (
            <NetworkSelect
              ref={formRef}
              options={networks}
              onSubmit={handleSubmit}
            />
          )}
          <div>{messageDiv}</div>
        </div>
      </div>
    </div>
  );
}

export default App;
