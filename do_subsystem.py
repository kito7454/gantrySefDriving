# moves from shelf to galvo then to keyence then to ir
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt
import buildGantree

import numpy as np
import time
# from zaber_motion.dto.ascii import MeasurementSequence
import helpers.gantryHelperAdvanced as gh
import helpers.shelfHelper as sh
import helpers.webSwitchHelper as wsh

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)


def do_subsystem_operation(self, sample_id, args):


with Connection.open_serial_port('COM6') as connection:
    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]
    #
