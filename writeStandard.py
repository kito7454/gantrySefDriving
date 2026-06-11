# moves from shelf to galvo then to keyence then to ir
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt
from datetime import datetime
import buildGantree
import helpers.spcHelper as sh
import numpy as np
# import importantCoordinates
import time
# from zaber_motion.dto.ascii import MeasurementSequence
import helpers.gantryHelperAdvanced as gh

import helpers.spcPyroClient as spc
import helpers.CageRotatorHelper

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)

actuallyRemoteAHK = False
x_locations = [-20,-16,-12]
y_locations = [-8,-8,-8]
# Get the current date and time
now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d %H:%M")
date = formatted_date
powers = [3,4,5]

with Connection.open_serial_port('COM6') as connection:

    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]

    # gh.goTo(deviceGantry=deviceGantry, root=rt, destination="storage", end_orient=0, move=True,
    #         distance_threshold_mm=250)
    spcRemote = spc.getRemoteSPC()

    spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry")

    gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=0, sample_length=76.2)
    gh.dropoffNamed(connection=connection, root=rt, location="write",
                    backwards=False, distance_threshold_mm=5, short=True)

    spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch")
    # set power
    helper = helpers.CageRotatorHelper.RotatorHelper()
    helper.connect()

    spcRemote.query(f'setvar date "{date}"\n')
    time.sleep(0.5)

    def manufactureStandard(index, sample_length = 76.2):
        # enter standard parameters into spc

        spcRemote.query(f"setvar xloc {str(x_locations[index])}\n")
        time.sleep(0.5)
        spcRemote.query(f"setvar yloc {str(y_locations[index])}\n")
        time.sleep(0.5)
        spcRemote.query(f'setvar powerText "{powers[index]}W"\n')
        time.sleep(0.5)


        helper.setPower(powers[index])

        spcRemote.query(f"compile\n")
        time.sleep(0.5)
        spcRemote.query(f"run\n")
        time.sleep(0.5)
        spcRemote.wait_until_done()

    for i in range(3):
        manufactureStandard(i)

    helper.close()
    spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry")
    gh.pickupNamed(connection=connection, root=rt, location="write",
                    backwards=False, distance_threshold_mm=5)
    gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=0, sample_length=76.2)




    # FTIR AL######
    # spcRemote.query(r'load "C:\Users\TeamD\Desktop\kyle\9x9_template.rcp'+"\n")
    # manufacture(1)
    # gh.pickupNamed(connection=connection, root=rt, location="ftir", backwards=True)
    # gh.dropoffNamed(connection=connection, root=rt, location="ftir",
    #                 backwards=True, distance_threshold_mm=5,short = True)
    # # remoteFTIR.startFTIR()
    # remoteFTIR.ping()
    # input("press Enter To Continue")
    # gh.pickupNamed(connection=connection, root=rt, location="ftir", backwards=True)
    # gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=1)



    # manufacture(2)
    # gh.dropoffNamed(connection=connection, root=rt, location="ftir",
    #                 backwards=True, distance_threshold_mm=5,short = True)

    # time.sleep(1)
    # gh.pickupNamed(connection=connection, root=rt, location="keyence", distance_threshold_mm=10,backwards=True)
    # gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=0)
    #
    # gh.dropoffBlind(connection=connection,clearance=10,backwards=False,short=True)

