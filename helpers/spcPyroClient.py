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
