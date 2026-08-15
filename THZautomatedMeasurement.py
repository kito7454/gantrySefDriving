# moves from shelf to galvo then to keyence then to ir
import datetime

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
import helpers.remoteKeyenceClient as remoteKeyence
import helpers.terahertzDropoffHelper as tdh
import helpers.remoteTHZClient as remoteTHZ
import helpers.remoteFTIRClient as remoteFTIR

# python -m Pyro5.nameserver -n 128.3.110.157

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)

with Connection.open_serial_port('COM6') as connection:

    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]
    remoteTHZ.homeStages()



    # for i in range(2,6):
    for i in range(7):
        remoteTHZ.homeStages()
        time.sleep(5)
        if not remoteTHZ.checkHomed():
            raise ValueError("Home Failure")
        gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=i, sample_length=50.8)
        tdh.terahertzDropoffFlipped(deviceGantry=deviceGantry, root=rt, sample_length=50.8)

        # get out of the way
        gh.goTo(deviceGantry=deviceGantry, root=rt, destination="thz_1", end_orient=-90, move=True,
                distance_threshold_mm=5)
        # input("press Enter To Continue")

        time.sleep(5)
        print(f"{i} starting at: {datetime.datetime.now()}")
        remoteTHZ.startTDS()
        for j in range(64):
            time.sleep(60)
        print(f"{i} finishing at: {datetime.datetime.now()}")

        remoteTHZ.homeStages()
        time.sleep(5)
        if not remoteTHZ.checkHomed():
            raise ValueError("Home Failure")
        tdh.terahertzPickupFlipped(deviceGantry=deviceGantry, root=rt, sample_length=50.8)
        gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=i, sample_length=50.8)