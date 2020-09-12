const baseUrl = "http://kyle.rmot.io/";

export function getNetworks() {
  return fetch(baseUrl + "scan")
    .then(handleResponse)
    .catch(handleError);
}

export function connectNetwork(ssid, password, type) {
  return fetch(baseUrl + "connect", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      ssid,
      password,
      type,
    }),
  })
    .then(handleResponse)
    .catch(handleError);
}

async function handleResponse(response) {
  if (response.ok) return response.json();
  if (response.status === 400) {
    // So, a server-side validation error occurred.
    // Server side validation returns a string error message, so parse as text instead of json.
    const error = await response.text();
    throw new Error(error);
  }
  throw new Error("Network error");
}

// In a real app, would likely call an error logging service.
function handleError(error) {
  // eslint-disable-next-line no-console
  console.error("API call failed. " + error);
  throw error;
}
