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
import helpers.gantryHelperAdvanced as gh
import helpers.shelfHelper as sh
import helpers.webSwitchHelper as wsh
import helpers.spcPyroClient as spc



# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)

with Connection.open_serial_port('COM6') as connection:
    remoteSPC = spc.getRemoteSPC()
    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

    for i in range(3):

        gh.shelfPickup(deviceGantry=deviceGantry,rt = rt,index =i)

        spc.moveDefinedLocation(remoteObject=remoteSPC,location_name="gantry")
        time.sleep(0.5)

        gh.dropoffNamed(connection=connection, root=rt, location="write", backwards=False, distance_threshold_mm=5)

        spc.moveDefinedLocation(remoteObject=remoteSPC,location_name="etch")
        time.sleep(0.5)

        remoteSPC.switchImageNum(i+1)
        time.sleep(1)
        # remoteSPC.query("compile\n")
        remoteSPC.query("run\n")
        remoteSPC.wait_until_done()

        spc.moveDefinedLocation(remoteObject=remoteSPC,location_name="gantry")
        time.sleep(0.5)

        gh.pickupNamed(connection=connection, root=rt, location="write")
        gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=i)
