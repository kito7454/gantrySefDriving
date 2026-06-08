import Pyro5.api

# The IP address of the AHK computer on your network
SERVER_IP = "131.243.31.184"  # Replace with the actual IP of the AHK machine
PORT = 9090

def main(start = False):
    # Connect to the remote object using its URI
    uri = f"PYRO:ahk.routine@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as ar:
        if start:
            print(ar.run_selected([0,1,2,3]))
            return "started"
        else:
            print(ar.ping())
            return "pinged keyence start server"

def startKeyence():
    # Connect to the remote object using its URI
    uri = f"PYRO:ahk.routine@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as keyence:
            print(keyence.run_selected([0,1,2,3]))
            return "started"

if __name__ == "__main__":
    main()