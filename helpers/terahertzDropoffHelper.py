from zaber_motion.ascii import Connection, pvt
import numpy as np

import time
import helpers.gantryHelperAdvanced as gh
import helpers.webSwitchHelper as wsh

def terahertzDropoff(deviceGantry, root,sample_length = 76.2):
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="terahertz", end_orient=-90, move=True,
            distance_threshold_mm=250)


    if sample_length != 76.2: #special case if sample isnt 3in long
        offset = 76.2 - sample_length  # used to account for samples that arent 3in long
        if sample_length < 48 or sample_length > 77:
            raise Exception("Sample length incompatible")
        coordinates = gh.pollGantry(deviceGantry)
        gh.xyzMove(deviceGantry, coordinates[0], coordinates[1], coordinates[2]-offset, 10, 100, 10,wait_until_idle=True)

    wsh.switch(0)
    time.sleep(0.5)
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_lift", end_orient=-90, move=True,
            distance_threshold_mm=250,offset=[0,0,-offset])
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root = root, location= "thz_3")

def terahertzPickup(deviceGantry, root,sample_length = 76.2):
    offset = 76.2 - sample_length  # used to account for samples that arent 3in long
    if sample_length < 48 or sample_length > 77:
        raise Exception("Sample length incompatible")
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_3", end_orient=-90, move=True,
            distance_threshold_mm=250)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="thz_lift",offset=[0,0,-offset])

    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="thz_pick",
                    offset=[0,0,-offset],maxAccel=50,maxSpeed=25,wait_until_idle=True)

    wsh.switch(1)
    time.sleep(4)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="terahertz",offset=[0,0,-offset])
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="thz_4")
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_1", end_orient=-90, move=True,
            distance_threshold_mm=250)