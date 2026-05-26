# need to have SPCFeedthrough running on the Desktop-KK9T5rl and the name server
# gives remote access to SPCHelperPyro on DESKTOP-KK9T5RL
import time

import Pyro5.api

def getRemoteSPC():
    nameserver = Pyro5.api.locate_ns("128.3.108.56",9090)
    uri = nameserver.lookup("remoteSPC")
    print(uri)
    spcRemote = Pyro5.api.Proxy(uri)    # use name server object lookup uri shortcut
    return spcRemote

def movePiStage(remoteObject,axis,value):
    out= remoteObject.query("move " + axis + " " + str(value) + "\n")
    return out

def moveDefinedLocation(remoteObject,location_name):
    coords = None
    if location_name == "etch":
        coords = [128,38,19.5]
    if location_name == "gantry":
        coords = [0,200,19.5]

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
    # movePiStage(remoteObject=spcRemote,axis='x2',value=0)
    # movePiStage(remoteObject=spcRemote, axis='y2', value = 200)
    # movePiStage(remoteObject=spcRemote, axis='z2', value = 20)

    # movePiStage(remoteObject=spcRemote,axis='x2',value=130)
    # movePiStage(remoteObject=spcRemote, axis='y2', value = 38)
    # movePiStage(remoteObject=spcRemote, axis='z2', value = 20)