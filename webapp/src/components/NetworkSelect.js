import React, {
  useState,
  useEffect,
  forwardRef,
  useImperativeHandle,
} from "react";
import Select from "react-select";

const NetworkSelect = forwardRef((props, ref) => {
  const typeOptions = [
    { label: "WPA", value: "WPA" },
    { label: "WEP", value: "WEP" },
    { label: "None", value: "OPEN" },
  ];

  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState();
  const [selectedType, setSelectedType] = useState();
  const [ssid, setSsid] = useState("");
  const [type, setType] = useState("");
  const [password, setPassword] = useState("");

  useImperativeHandle(ref, () => ({
    resetForm() {
      setSsid("");
      setPassword("");
      setSelectedOption(null);
      setSelectedType(null);
    },
  }));

  useEffect(() => {
    if (props.options) {
      let list = props.options.map((network) => ({
        label: network.ssid,
        value: network.bssid,
      }));
      console.log("Setting networks", list);
      setOptions(list.filter((item) => item.label));
    }
  }, [props.options]);

  const handleNetworkSelect = (value) => {
    setSelectedOption(value);
    setSsid(value.label);

    const network = findNetwork(value.value);

    if (network) {
      const netType = getNetworkSecurity(network);
      setType(netType);
      setSelectedType(
        typeOptions.filter((t) => {
          return t.value === netType;
        })
      );
    }
  };

  const handleTypeSelect = (value) => {
    setSelectedType(value);
    setType(value.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    props.onSubmit(ssid, type, password);
  };

  const findNetwork = (bssid) => {
    const result = props.options.filter((obj) => {
      return obj.bssid === bssid;
    });
    return result[0];
  };

  const getNetworkSecurity = (network) => {
    if (network.flag.includes("WPA")) {
      return "WPA";
    } else if (network.flag.includes("WEP")) {
      return "WEP";
    } else {
      return "OPEN";
    }
  };

  return (
    <form id="contact-form" onSubmit={handleSubmit}>
      <h3>Kyle WIFI Setup</h3>
      <h4>Please select the ssid and enter password for your site.</h4>
      <div>
        <label>
          <span>Select network:</span>
          <div className="input-container">
            <Select
              className="network-select"
              options={options}
              value={selectedOption}
              onChange={(value) => handleNetworkSelect(value)}
              placeholder={"Select a network"}
            />
          </div>
        </label>
        <label>
          <span>SSID: (Required)</span>
          <input
            placeholder="Enter network SSID"
            id="ssid"
            name="ssid"
            type="text"
            value={ssid}
            onChange={(e) => {
              setSsid(e.target.value);
              setSelectedOption(null);
            }}
          />
        </label>
        <label>
          <span>Network Security:</span>
          <div className="input-container">
            <Select
              className="type-select"
              options={typeOptions ? typeOptions : typeOptions[2]}
              value={selectedType}
              onChange={(value) => handleTypeSelect(value)}
              placeholder={"Select type"}
            />
          </div>
        </label>
        {type === "OPEN" ? (
          ""
        ) : (
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
        )}
        <button name="submit" type="submit" id="contact-submit">
          Connect
        </button>
      </div>
    </form>
  );
});

export default NetworkSelect;
