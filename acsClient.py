# client.py
import time

import requests
import json

SERVER = r"http://DESKTOP-KK9T5RL.dhcp.lbl.gov:5000"

TOKEN  = "CHANGE_ME_TO_RANDOM_STRING"   # must match server token


def run_remote(command: str):
    url = f"{SERVER}/exec"
    # Note: requests.post(..., json=payload) automatically sets Content-Type to application/json
    headers = {"X-Auth-Token": TOKEN}
    payload = {"cmd": command}

    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code == 400:
        print(f"Server rejected request. Response body: {resp.text}")

    resp.raise_for_status()
    return resp.json()

def send_spc_command(command: str):
    result = run_remote(command)
    # print("Response:", result)
    print("Status: " + result.get("status"))
    print("Received: " + result.get("received"))
    return result.get("received")

def movePiStage(axis: str, value: float):
    # axis: pi stage axis string ie: "x1" or "z2"
    #value: where you want one axis to go to
    reply = send_spc_command("move " + axis + " " + str(value))
    time.sleep(0.5)
    return reply



# if __name__ == "__main__":

    # result = run_remote("compile")
    # result = movePiStage(axis="x2", value=0)
    # result = movePiStage(axis="y2", value= 200)
    # Or if you want to be specific to the new keys:

