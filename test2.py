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
import helpers.spcPyroClient as spc
import helpers.remoteKeyenceClient as remoteKeyence

import helpers.terahertzDropoffHelper as tdh
import helpers.remoteTHZClient as remoteTHZ
import helpers.remoteFTIRClient as remoteFTIR

# import helpers.ahkHelper as ahk
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
rt = buildGantree.buildGantree(gantreeFile)
print(rt)

actuallyRemoteAHK = False

spcRemote = spc.getRemoteSPC()
# spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch_small")
# spcRemote.switchImageNum(0,"thz")
spcRemote.query("setvar batchNum 19\n")

# with Connection.open_serial_port('COM6') as connection:

    # device_list = connection.detect_devices()
    # deviceGantry = device_list[1]
    # # target the first rotation stage
    # deviceA1 = device_list[2]
    # deviceA2 = device_list[3]
    #
    # gh.goTo(deviceGantry=deviceGantry, root=rt, destination="midpoint", end_orient=0, move=True,
    #         distance_threshold_mm=250)
    # spcRemote = spc.getRemoteSPC()
    #
    # def manufacture(index,sample_length = 76.2):
    #     if sample_length == 50.8:
    #         spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry_small")
    #     else:
    #         spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry")
    #
    #     gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=index,sample_length=sample_length)
    #     gh.dropoffNamed(connection=connection, root=rt, location="write",
    #                     backwards=False, distance_threshold_mm=5, short=True)
    #
    #     if sample_length == 50.8:
    #         spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch_small")
    #     else:
    #         spc.moveDefinedLocation(remoteObject=spcRemote,location_name="etch")
    #
    #     spcRemote.query(f"compile\n")
    #     time.sleep(0.5)
    #     spcRemote.query(f"run\n")
    #     time.sleep(0.5)
    #     spcRemote.wait_until_done()
    #
    #     if sample_length == 50.8:
    #         spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_small")
    #     else:
    #         spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry")
    #
    #     gh.pickupNamed(connection=connection, root=rt, location="write",
    #                    distance_threshold_mm=10, backwards=False)


    # spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch")

    # keyence
    # manufacture(2)
    # gh.dropoffNamed(connection=connection, root=rt, location="keyence",
    #                 backwards=True, distance_threshold_mm=5,short = True)
    # remoteKeyence.main(actuallyRemoteAHK)

    # THZ ITO
    # spcRemote.query(r'load "C:\Users\TeamD\Desktop\demos\cross_demos\12cross.rcp'+"\n")
    # manufacture(0,sample_length=50.8)

    # gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=0, sample_length=50.8)
    # input("Press Enter to continue")
    # remoteTHZ.homeStages()
    # tdh.terahertzDropoff(deviceGantry=deviceGantry, root=rt, sample_length=50.8)
    # # remoteTHZ.startTDS()
    # gh.goTo(deviceGantry=deviceGantry, root=rt, destination="thz_2", end_orient=-90, move=True)
    # input("press Enter To Continue")
    # tdh.terahertzPickup(deviceGantry=deviceGantry, root=rt, sample_length=50.8)

    # gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=0, sample_length=50.8)
    # gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=1,sample_length=76.2)
    # gh.dropoffNamed(connection=connection, root=rt, location="keyence",
    #                 backwards=True, distance_threshold_mm=5,short = True)



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

