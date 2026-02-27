# client.py
import requests
import json

# SERVER = r"http://localhost:5000"

TOKEN  = "CHANGE_ME_TO_RANDOM_STRING"   # must match server token


def run_remote(command: str, SERVER = r"http://localhost:5000"):
    url = f"{SERVER}/exec"
    # Note: requests.post(..., json=payload) automatically sets Content-Type to application/json
    headers = {"X-Auth-Token": TOKEN}
    payload = {"cmd": command}

    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code == 400:
        print(f"Server rejected request. Response body: {resp.text}")

    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    # example usage
    result = run_remote("ls")
    print("Response:", result)
    # Or if you want to be specific to the new keys:
    print("Status:", result.get("status"))
    print("Received:", result.get("received"))
    payload_back = result.get("received")
    data = json.loads(payload_back)
    # Extracting
    for k, v in data.items():
        print(k)  # cmd
        print(v)  # ls

