from zaber_motion.ascii import Connection
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
import buildGantree
import helpers.spcPyroClient as spc
import time
from helpers.gantryHelperSimple import GantryHelperSimple
# place sample on stage by hand and then let gantry load into shelf

# python -m Pyro5.nameserver -n 128.3.110.157

index = 81
shelf_slot = 0

spcRemote = spc.getRemoteSPC()
with Connection.open_serial_port('COM6') as connection:

    move = True
    etch = False

    if move:
        rt = buildGantree.buildGantree(gantreeFile)
        gh = GantryHelperSimple(connection=connection, root=rt)

    if etch:
        spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry_small")
        spcRemote.query(f"setvar batchNum {str(index)}\n")
        spcRemote.query(f"compile\n")
        spcRemote.switchImageNum(index, "thz")
        time.sleep(20)
        spcRemote.query(f"run\n")
        spcRemote.wait_until_done()

    if move:
        spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry_small")
        gh.pickupNamed(location="write",clearance=5)
        gh.mailboxDrop(index=shelf_slot)
