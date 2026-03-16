# moves from shelf to galvo then to keyence then to ir
# DONT FORGET TO START PI STAGE REMOTE SERVER
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
use_acs = False

with Connection.open_serial_port('COM6') as connection:
    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

    ###############

    # gh.pickupNamed(connection = connection,root=rt,location="shelf_one",distance_threshold_mm=30)

    for i in range(1):
        # gh.shelfGoTo(deviceGantry, rt, 0, spacing=25.4 * 2.5)
        gh.pickupNamed(connection=connection, root=rt, location="shelf_one", distance_threshold_mm=30)
        # gh.pickupBlind(deviceGantry, rt)
        if use_acs:
            acs.movePiStage("y2", 200)
            acs.movePiStage("x2", 0)

        gh.pickupNamed(connection=connection, root=rt, location="write", distance_threshold_mm=30)
        if use_acs:
            acs.movePiStage("y2",100)
            acs.movePiStage("x2", 100)


        gh.shelfGoTo(deviceGantry, rt, 1, spacing=25.4 * 2.5)
        gh.pickupBlind(deviceGantry)

        # place keyence
        gh.dropoffNamed(connection = connection, root=rt, location="keyence_place", backwards=True, distance_threshold_mm=5)
        gh.goTo(connection=connection, root=rt, destination="storage", maxSpeed=250, move=True, distance_threshold_mm=30)

        if use_acs:
            acs.movePiStage("y2", 200)
            acs.movePiStage("x2", 0)

        gh.pickupNamed(connection = connection, root=rt, location="write", distance_threshold_mm=30)
        gh.goTo(connection=connection, root=rt, destination="bath_up", maxSpeed=250, move=True, distance_threshold_mm=5)
        gh.bath_routine(deviceGantry = deviceGantry,connection=connection,root=rt)
        gh.shelfGoTo(deviceGantry, rt, 1, spacing=25.4 * 2.5)
        gh.dropoffBlind(deviceGantry)

        # take back keyence sample

        gh.goTo(connection=connection, root=rt, destination="storage", maxSpeed=100, move=True, distance_threshold_mm=150)
        gh.setOrientation(connection=connection, backwards=True)
        gh.pickupNamed(connection = connection,root=rt,location="keyence_place")
        gh.goTo(connection=connection, root=rt, destination="storage", maxSpeed=100, move=True, distance_threshold_mm=150)
        gh.setOrientation(connection=connection,backwards=False)
        gh.shelfGoTo(deviceGantry, rt, 0, spacing=25.4 * 2.5)
        gh.dropoffBlind(deviceGantry)

