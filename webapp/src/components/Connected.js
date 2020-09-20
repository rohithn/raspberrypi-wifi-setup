import React, { useEffect, useState } from "react";
import status_simple from "../assets/status_simple.png";
import { getConfiguredNetworks } from "../api/wifiApis";

function Connected(props) {
  const [current, setCurrent] = useState();

  useEffect(() => {
    getConfiguredNetworks().then((_networks) => {
      const c = _networks.result.filter((n) => (n.status = "[CURRENT]"));
      if (c) {
        setCurrent(c[0].ssid);
      }
    });
  }, []);

  return (
    <div id="img-container">
      <img className="img-content" src={status_simple} alt="connected" />
      {current ? <h2 className="img-content">Connected to {current}!</h2> : ""}
      <div className="flex-container">
        <button className="red-button" onClick={props.onClick}>
          Reset
        </button>
      </div>
    </div>
  );
}

export default Connected;
