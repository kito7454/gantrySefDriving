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
    #
    gh.pickupNamed(connection=connection, root=rt, location="shelf_one", distance_threshold_mm=300)
    gh.dropoffNamed(connection=connection, root=rt, location="write", backwards=False, distance_threshold_mm=5)

    # gh.goTo(deviceGantry=deviceGantry,root=rt,destination="shelf_one",end_orient=0,move=True,distance_threshold_mm=100)

    # gh.pickupNamed(connection=connection, root=rt, location="write", distance_threshold_mm=30)
    # gh.goTo(connection=connection, root=rt, destination="bath_in", end_orient=-90, maxSpeed=250, move=True, distance_threshold_mm=5)
    # gh.goTo(connection=connection, root=rt, destination="bath_up", end_orient=0, maxSpeed=250, move=True,
    #         distance_threshold_mm=5)
    # gh.dropoffNamed(connection=connection, root=rt, location="shelf_one", backwards=False, distance_threshold_mm=5)

    # gh.setOrientation(connection, backwards=False)

    #gh.dropoffBlind(connection=connection,backwards=False,clearance=10)