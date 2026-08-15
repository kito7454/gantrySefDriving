# moves from shelf to galvo then to keyence then to ir
import datetime

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
import helpers.webSwitchHelper as wsh
import helpers.spcPyroClient as spc
import helpers.remoteKeyenceClient as remoteKeyence
import helpers.terahertzDropoffHelper as tdh
import helpers.remoteTHZClient as remoteTHZ
import helpers.remoteFTIRClient as remoteFTIR

# python -m Pyro5.nameserver -n 128.3.110.157

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)

with Connection.open_serial_port('COM6') as connection:

    device_list = connection.detect_devices()
    deviceGantry = device_list[1]
    # target the first rotation stage
    deviceA1 = device_list[2]
    deviceA2 = device_list[3]
    remoteTHZ.homeStages()
    spcRemote = spc.getRemoteSPC()

    gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=0, sample_length=50.8)

    # manufacture
    spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_small")
    gh.dropoffNamed(connection=connection, root=rt, location="write",
                    backwards=False, distance_threshold_mm=5, short=True)

    spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch_small")
    time.sleep(1)
    spcRemote.query(f"compile\n")
    time.sleep(0.5)
    spcRemote.query(f"run\n")
    time.sleep(0.5)
    spcRemote.wait_until_done()

    spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_small")
    gh.pickupNamed(connection=connection, root=rt, location="write",
                   distance_threshold_mm=10, backwards=False)
######################

    # THZ
    remoteTHZ.homeStages()
    time.sleep(5)
    if not remoteTHZ.checkHomed():
        raise ValueError("Home Failure")

    tdh.terahertzDropoffFlipped(deviceGantry=deviceGantry, root=rt, sample_length=50.8)
    # get out of the way
    gh.goTo(deviceGantry=deviceGantry, root=rt, destination="thz_1", end_orient=-90, move=True,
            distance_threshold_mm=5)
    print(f"starting TDS at: {datetime.datetime.now()}")
    remoteTHZ.startTDS()
    time.sleep(1)
    inp = input("press to continue")

    remoteTHZ.homeStages()
    time.sleep(5)
    if not remoteTHZ.checkHomed():
        raise ValueError("Home Failure")
    tdh.terahertzPickupFlipped(deviceGantry=deviceGantry, root=rt, sample_length=50.8)
########################

    # ftir
    gh.dropoffNamed(connection=connection, root=rt, location="ftir",
                    backwards=True, distance_threshold_mm=5, short=True)
    gh.goTo(deviceGantry=deviceGantry, root=rt, destination="ftir_front", end_orient=-180, move=True,
            distance_threshold_mm=5)
    remoteFTIR.startFTIRNoScan()
    ftirinp = input("press to continue")
    gh.pickupNamed(connection=connection, root=rt, location="ftir",
                   distance_threshold_mm=10, backwards=True)
#################

    # Keyence
    gh.dropoffNamed(connection=connection, root=rt, location="keyence",
                                    backwards=True, distance_threshold_mm=5,short = True)
    keyinp = input("press to continue")
    gh.pickupNamed(connection=connection, root=rt, location="keyence",
                   distance_threshold_mm=10, backwards=True)
###############


    gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=0, sample_length=50.8)