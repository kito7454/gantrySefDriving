# need to have SPCFeedthrough running on the Desktop-KK9T5rl and the name server
# gives remote access to SPCHelperPyro on DESKTOP-KK9T5RL
import time

import Pyro5.api
import Pyro5.errors

# python -m Pyro5.nameserver -n 128.3.110.157

def connect_to_ns(addresses):
    for ip in addresses:
        try:
            print(f"Attempting to connect to Name Server at {ip}...")
            # Attempt to locate the name server at the specific IP
            ns = Pyro5.api.locate_ns(host=ip)
            print(f"Successfully connected to Name Server at {ip}")
            return ns
        except (Pyro5.api.errors.NamingServiceNotFoundError, Pyro5.errors.CommunicationError) as e:
            print(f"Failed to connect to {ip}: {e}")
            continue  # Try the next address in the list

    raise Exception("Could not connect to any of the provided Name Server addresses.")



def getRemoteSPC():
    # nameserver = Pyro5.api.locate_ns("128.3.108.56",9090)
    nameserver = connect_to_ns(addresses=["128.3.108.56",'128.3.110.157'])
    uri = nameserver.lookup("remoteSPC")
    print(uri)
    spcRemote = Pyro5.api.Proxy(uri)    # use name server object lookup uri shortcut
    return spcRemote

def movePiStage(remoteObject,axis,value):
    out= remoteObject.query("move " + axis + " " + str(value) + "\n")
    time.sleep(1)
    return out

def moveDefinedLocation(remoteObject,location_name):
    coords = None
    if location_name == "etch":
        coords = [154,38,19.5]
    if location_name == "etch_small":
        coords = [85.4,38,19.5]
    if location_name == "gantry":
        coords = [68,195,19.5]
    if location_name == "gantry_small":
        coords = [0,200,19.5]

    #     fix writing coordinates and logic

    if coords is not None:
        movePiStage(remoteObject=remoteObject, axis="x2", value=coords[0])
        movePiStage(remoteObject=remoteObject, axis="y2", value=coords[1])
        movePiStage(remoteObject=remoteObject, axis="z2", value=coords[2])
        time.sleep(0.5)

    return coords

    # SS = 500
    # SP = 0.1
    # i = 12
    # N = 6
    # remoteSPC = spc.getRemoteSPC()
    # remoteSPC.connect()
    # # set individual variables
    # remoteSPC.query(f"setvar speed {SS}\n")
    # remoteSPC.query(f"setvar spacing {SP}\n")
    # remoteSPC.query(f"setvar i0 {i}\n")
    # remoteSPC.query(f"setvar i1 {i}\n")
    # remoteSPC.query(f"setvar dim {N}\n")
    # remoteSPC.query(f"compile\n")

    # spc.query(f"setvar gridSpacing {grid_spacing}\n")
    # spc.query(f"setvar squareSize {square_size}\n")
    # spc.query(f"compile\n")
    # spc.query(f"run\n")

if __name__ == "__main__":
    spcRemote = getRemoteSPC()
    spcRemote.ping()
    # recipeFile = r"C:\Users\TeamD\Desktop\kyle\tangorStandardAutomated.rcp"
    # spcRemote.query(f"load {recipeFile}\n")
    # movePiStage(remoteObject=spcRemote,axis='x2',value=0)
    # movePiStage(remoteObject=spcRemote, axis='y2', value = 200)
    # movePiStage(remoteObject=spcRemote, axis='z2', value = 20)

    moveDefinedLocation(spcRemote,location_name="etch_small  ")