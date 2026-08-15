# moves from shelf to galvo then to keyence then to ir
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt

import buildGantree
import helpers.spcHelper as sh
import numpy as np
# import importantCoordinates
import time
# from zaber_motion.dto.ascii import MeasurementSequence
import helpers.gantryHelperAdvanced as gh
import helpers.terahertzDropoffHelper as tdh
import helpers.shelfHelper as sh
import helpers.webSwitchHelper
import helpers.webSwitchHelper as wsh
import helpers.spcPyroClient as spc


# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)

# remoteFTIR.ping()
# remoteTHZ.homeStages()

with Connection.open_serial_port('COM6') as connection:

    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

#
    spcRemote = spc.getRemoteSPC()
    # spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_short")
    def manufacture(index,sample_length = 76.2,batchStartNum = 0):
        # batch start num is sample number last done
        if sample_length == 50.8:
            spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry_small")
        else:
            spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry")

        gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=index,sample_length=sample_length)
        gh.dropoffNamed(connection=connection, root=rt, location="write",
                        backwards=False, distance_threshold_mm=5, short=True)

        if sample_length == 50.8:
            spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch_small")
        else:
            spc.moveDefinedLocation(remoteObject=spcRemote,location_name="etch")

        spcRemote.query(f"setvar batchNum {str(batchStartNum + index)}\n")
        spcRemote.switchImageNum(batchStartNum + index,"thz")

        time.sleep(20)
        spcRemote.query(f"compile\n")
        time.sleep(0.5)
        spcRemote.query(f"run\n")
        time.sleep(0.5)
        spcRemote.wait_until_done()

        if sample_length == 50.8:
            spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_small")
        else:
            spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry")

        gh.pickupNamed(connection=connection, root=rt, location="write",
                       distance_threshold_mm=10, backwards=False)
#     spcRemote.query("run\n")
#     spcRemote.wait_until_done()
# q
#     tdh.terahertzDropoff(deviceGantry=deviceGantry, root=rt,sample_length=50.8)
#     tdh.terahertzPickup(deviceGantry=deviceGantry, root=rt,sample_length=50.8)
#     left off on substrate 9 (5+4)

    # redo sample 19
    for i in range(7):
        manufacture(index=i,sample_length=50.8,batchStartNum=33) #put batch start as the sample you want to start on
        gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=i, sample_length=50.8)
    #########
