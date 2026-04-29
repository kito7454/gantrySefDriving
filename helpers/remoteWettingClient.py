import Pyro5.api

# The IP address of the AHK computer on your network
SERVER_IP = "128.3.106.50"  # Replace with the actual IP of the AHK machine
# SERVER_IP = "198.128.212.249
# "
PORT = 9090

def main(start = False):
    # Connect to the remote object using its URI
    uri = f"PYRO:ahk.routine@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as ar:

        if start:
            print(ar.remoteStartWetting())
            return 'started'
        else:
            print(ar.ping())
            return "pinged"

if __name__ == "__main__":
    main()