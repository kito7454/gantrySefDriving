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
import remoteHTTP.acsClient as acs

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.build(gantreeFile)
print(rt)

with Connection.open_serial_port('COM6') as connection:
    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

    ###############

    # gh.pickupNamed(device=deviceGantry,root=rt,location="shelf_one",distance_threshold_mm=30)

    for i in range(1):
        # gh.shelfGoTo(deviceGantry, rt, 0, spacing=25.4 * 2.5)
        gh.pickupNamed(device=deviceGantry, root=rt, location="shelf_one", distance_threshold_mm=30)
        # gh.pickupBlind(deviceGantry, rt)
        acs.movePiStage("y2", 200)
        acs.movePiStage("x2", 0)
        gh.dropoffNamed(device=deviceGantry, root=rt, location="write", backwards=False)
        acs.movePiStage("y2",100)
        acs.movePiStage("x2", 100)


        gh.shelfGoTo(deviceGantry, rt, 1, spacing=25.4 * 2.5)
        gh.pickupBlind(deviceGantry)

        gh.goTo(device=deviceGantry, root=rt, destination="bath_up", maxSpeed=250, move=True, distance_threshold_mm=5)
        gh.bath_routine(deviceGantry = deviceGantry,connection=connection,root=rt)
        gh.shelfGoTo(deviceGantry, rt, 0, spacing=25.4 * 2.5)
        gh.dropoffBlind(deviceGantry)

        acs.movePiStage("y2", 200)
        acs.movePiStage("x2", 0)
        gh.pickupNamed(device=deviceGantry, root=rt, location="write", distance_threshold_mm=30)
        gh.goTo(device=deviceGantry, root=rt, destination="bath_up", maxSpeed=250, move=True, distance_threshold_mm=5)
        gh.bath_routine(deviceGantry = deviceGantry,connection=connection,root=rt)
        gh.shelfGoTo(deviceGantry, rt, 1, spacing=25.4 * 2.5)
        gh.dropoffBlind(deviceGantry)

