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
rt = buildGantree.build(gantreeFile)
print(rt)

with Connection.open_serial_port('COM6') as connection:
    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

    # gh.pollGantry(deviceGantry)
    # gh.navigate(deviceGantry, rt,pointA="midpoint",pointB="galvo_up",move=True)
    # print(gh.checkClosest(deviceGantry,gantreeFile).get("distance"))
    # gh.goTo(device = deviceGantry,root=rt,destination="midpoint",maxSpeed=100,move=True,gantreeCsv=gantreeFile,distance_threshold_mm=600)
    # print("at initial position")
    #
    ###############

    # gh.pickupNamed(device=deviceGantry,root=rt,location="shelf_one",distance_threshold_mm=30)
    # gh.dropoffNamed(device=deviceGantry, root=rt, location="write", backwards=False)
    # gh.pickupNamed(device=deviceGantry, root=rt, location="write", distance_threshold_mm=30)
    # gh.goTo(device=deviceGantry, root=rt, destination="bath_up", maxSpeed=250, move=True, distance_threshold_mm=5)
    # gh.bath_routine(deviceGantry = deviceGantry,connection=connection,root=rt)
    # gh.dropoffNamed(device=deviceGantry, root=rt, location="shelf_one", backwards=False)

    # gh.goTo(device=deviceGantry, root=rt, destination="midpoint", maxSpeed=250, move=True, distance_threshold_mm=30)
    #
    # gh.pickupNamed(device=deviceGantry,root=rt,location="shelf_one")
    # gh.dropoffNamed(device=deviceGantry, root=rt, location="write", backwards=False)
    #
    # gh.pickupNamed(device=deviceGantry,root=rt,location="write", backwards=False)
    # gh.dropoffNamed(device=deviceGantry, root=rt, location="shelf_one",backwards=False,distance_threshold_mm=100)
    # gh.goTo(device=deviceGantry, root=rt, destination="midpoint", maxSpeed=250, move=True, distance_threshold_mm=150)
    gh.shelfGoTo(deviceGantry,rt,2,spacing = 25.4*2.5)