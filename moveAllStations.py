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
import helpers.shelfHelper as sh
import helpers.webSwitchHelper
import helpers.webSwitchHelper as wsh
import helpers.spcPyroClient as spc
import helpers.wettingDropoffHelper as wdh

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)

with Connection.open_serial_port('COM6') as connection:

    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

    gh.goTo(deviceGantry=deviceGantry, root=rt, destination="storage", end_orient=0, move=True,
            distance_threshold_mm=250)

    def manufacture(index):
        gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=index)
        gh.dropoffNamed(connection=connection, root=rt, location="write",
                        backwards=False, distance_threshold_mm=5,short = True)
        time.sleep(0.5)
        gh.pickupNamed(connection=connection, root=rt, location="write",
                       distance_threshold_mm=10, backwards=False)

        gh.goTo(deviceGantry=deviceGantry, root=rt, destination="bath_in", end_orient=-90, move=True,
                distance_threshold_mm=250)

    manufacture(0)
    wdh.wettingDropoff(deviceGantry=deviceGantry, root=rt)

    manufacture(1)
    gh.dropoffNamed(connection=connection, root=rt, location="keyence",
                    backwards=True, distance_threshold_mm=5,short = True)

    manufacture(2)
    gh.dropoffNamed(connection=connection, root=rt, location="ftir",
                    backwards=True, distance_threshold_mm=5,short = True)

    # gh.dropoffNamed(connection=connection, root=rt, location="keyence",
    #                 backwards=True, distance_threshold_mm=5,short = True)
    #
    # # time.sleep(1)
    # gh.pickupNamed(connection=connection, root=rt, location="keyence", distance_threshold_mm=10,backwards=True)
    # gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=0)

    # gh.dropoffBlind(connection=connection,clearance=10,backwards=False,short=True)

