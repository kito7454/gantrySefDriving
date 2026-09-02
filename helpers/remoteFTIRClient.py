import Pyro5.api
# for use with ahkStarter.py on the ftir computer
# The IP address of the AHK computer on your network
SERVER_IP = "128.3.104.207"  # Replace with the actual IP of the AHK machine
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