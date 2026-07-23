import Pyro5.api

# The IP address of the AHK computer on your network
SERVER_IP = "128.3.110.114"  # Replace with the actual IP of the AHK machine
PORT = 9090
uri = f"PYRO:ahk.thz@{SERVER_IP}:{PORT}"

def homeStages():
    uri = f"PYRO:ahk.thz@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as thz:
        thz.homeStages()

def startTDS():
    uri = f"PYRO:ahk.thz@{SERVER_IP}:{PORT}"

    with Pyro5.api.Proxy(uri) as thz:
        thz.startTDS()

def checkHomed():
    with Pyro5.api.Proxy(uri) as thz:
        coords = thz.checkCoordinates()
        return bool(coords == [0,0])

if __name__ == "__main__":
    # homeStages()
    print(checkHomed())
    # with Pyro5.api.Proxy(uri) as thz:
    #     print(thz.checkCoordinates())

    # with Pyro5.api.Proxy(uri) as thz:
    #     thz.ping()
    # startTDS()

    # main()