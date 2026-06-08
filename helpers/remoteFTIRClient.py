import Pyro5.api

# The IP address of the AHK computer on your network
SERVER_IP = "128.3.110.25"  # Replace with the actual IP of the AHK machine
PORT = 9091

def startFTIR():
    uri = f"PYRO:ahk.ftir@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as ftir:
        ftir.startFTIR()

def ping():
    uri = f"PYRO:ahk.ftir@{SERVER_IP}:{PORT}"
    with Pyro5.api.Proxy(uri) as ftir:
        print(ftir.ping())


if __name__ == "__main__":
    # uri = f"PYRO:ahk.ftir@{SERVER_IP}:{PORT}"
    # with Pyro5.api.Proxy(uri) as ftir:
    #     print(ftir.ping())
    startFTIR()