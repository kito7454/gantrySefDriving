import Pyro5.api

# The IP address of the AHK computer on your network
SERVER_IP = "128.3.110.160"  # Replace with the actual IP of the AHK machine
PORT = 9091

def startFTIRNoScan():
    uri = f"PYRO:ahk.ftir@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as ftir:
        ftir.startFTIRNoScan()

def ping():
    uri = f"PYRO:ahk.ftir@{SERVER_IP}:{PORT}"
    with Pyro5.api.Proxy(uri) as ftir:
        print(ftir.ping())


if __name__ == "__main__":
    startFTIRNoScan()