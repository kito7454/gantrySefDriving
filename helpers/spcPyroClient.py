# need to have SPCFeedthrough running on the Desktop-KK9T5rl and the name server
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