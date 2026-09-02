# moves from shelf to galvo then to keyence then to ir
# must have the image selected in SPCb
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt

import buildGantree
import helpers.spcHelper as sh
import numpy as np
# import importantCoordinates
import time
# from zaber_motion.dto.ascii import MeasurementSequence
import helpers.gantryHelperSimple as gh
import helpers.shelfHelper as sh
import helpers.webSwitchHelper as wsh
import helpers.spcPyroClient as spc



# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)

with Connection.open_serial_port('COM6') as connection:
    gh = gh.GantryHelperSimple(connection=connection, root=rt)
    spcRemote = spc.getRemoteSPC()
    # spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_short")
        
    for index in range(3):
        gh.mailboxPickup(index=index)
        

        spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry")
        time.sleep(0.5)

        gh.dropoffNamed(location='write', backwards=False, clearance=5)
        
        spc.moveDefinedLocation(remoteObject=spcRemote,location_name="etch")
        time.sleep(0.5)

        spcRemote.switchImageNum(index+1)
        time.sleep(1)
        # spcRemote.query("compile\n")
        spcRemote.query("run\n")
        spcRemote.wait_until_done()

        spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry")
        time.sleep(0.5)

        gh.pickupNamed(location="write", distance_threshold_mm=10, backwards=False,clearance=5)

        gh.mailboxDrop(index=index, clearance=9)
