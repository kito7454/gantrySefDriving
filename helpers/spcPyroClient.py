# saved as greeting-client.py
import Pyro5.api

# name = input("What is your name? ").strip()
nameserver = Pyro5.api.locate_ns()
uri = nameserver.lookup("remoteSPC")
spcRemote = Pyro5.api.Proxy(uri)    # use name server object lookup uri shortcut
print(spcRemote.ping())
# print(greeting_maker.get_fortune(name))