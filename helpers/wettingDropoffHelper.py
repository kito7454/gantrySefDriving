from zaber_motion.ascii import Connection, pvt
import numpy as np

import time
import helpers.gantryHelperAdvanced as gh
import helpers.webSwitchHelper as wsh

def wettingDropoff(deviceGantry,root):
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="wetting", end_orient=0, move=True,
            distance_threshold_mm=250)
    wsh.switch(0)
    time.sleep(0.5)
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="wetting_lift", end_orient=0, move=True,
            distance_threshold_mm=250)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root = root, location= "wetting_3")

def wettingPickup(deviceGantry,root):
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="wetting_3", end_orient=0, move=True,
            distance_threshold_mm=250)
    gh.xyzMoveNamed(deviceGantry=deviceGantry, root=root, location="wetting_lift")
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="wetting", end_orient=0, move=True,
            distance_threshold_mm=250)
    wsh.switch(1)
    time.sleep(1)
    gh.goTo(deviceGantry=deviceGantry, root=root, destination="wetting_1", end_orient=0, move=True,
            distance_threshold_mm=250)