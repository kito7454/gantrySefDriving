from zaber_motion.ascii import Connection, pvt
import numpy as np

import time
import helpers.gantryHelperAdvanced as gh
import helpers.webSwitchHelper as wsh

def terahertzDropoff(deviceGantry, root):
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="terahertz", end_orient=-90, move=True,
            distance_threshold_mm=250)
    wsh.switch(0)
    time.sleep(0.5)
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_lift", end_orient=-90, move=True,
            distance_threshold_mm=250)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root = root, location= "thz_3")

def terahertzPickup(deviceGantry, root):
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_3", end_orient=-90, move=True,
            distance_threshold_mm=250)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="thz_lift")
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_pick", end_orient=-90, move=True,
            distance_threshold_mm=250)
    wsh.switch(1)
    time.sleep(2)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="terahertz")
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="thz_1", end_orient=-90, move=True,
            distance_threshold_mm=250)