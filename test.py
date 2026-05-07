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
import helpers.terahertzDropoffHelper as tdh
import helpers.shelfHelper as sh
import helpers.webSwitchHelper
import helpers.webSwitchHelper as wsh
import helpers.spcPyroClient as spc
import helpers.wettingDropoffHelper as wdh
import helpers.fakeTHZ as thz
import helpers.remoteWettingClient as remoteWetting
import helpers.remoteKeyenceClient as remoteKeyence

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

    # remoteWetting.main(True)
    # remoteKeyence.main(True)

    gh.goTo(deviceGantry=deviceGantry, root=rt, destination="storage", end_orient=0, move=True,
            distance_threshold_mm=15)

    gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=0)
    # gh.dropoffNamed(connection=connection, root=rt, location="ftir",
    #                 backwards=True, distance_threshold_mm=5,short = True)

    # wdh.wettingDropoff(deviceGantry=deviceGantry, root=rt)
    # tdh.terahertzDropoff(deviceGantry=deviceGantry, root=rt)
    #
    # with Connection.open_serial_port('COM7') as connectionTHZ:
    #     gh.shelfPickup(deviceGantry=deviceGantry, rt=rt, index=0)
    #     thz.meet_Gantry(connectionTHZ)
    #     tdh.terahertzDropoff(deviceGantry=deviceGantry, root=rt)
    #     gh.goTo(deviceGantry=deviceGantry, root=rt, destination="thz_1", end_orient=0, move=True,
    #             distance_threshold_mm=250)
    #     thz.measure_THZ(connectionTHZ)

    #
    # gh.dropoffNamed(connection=connection, root=rt, location="keyence",
    #                 backwards=True, distance_threshold_mm=5,short = True)
    #
    # # time.sleep(1)
    # gh.pickupNamed(connection=connection, root=rt, location="keyence", distance_threshold_mm=10,backwards=True)
    gh.shelfDropoff(deviceGantry=deviceGantry, rt=rt, index=0)

    # gh.dropoffBlind(connection=connection,clearance=10,backwards=False,short=True)

    # gh.dropoffBlind(connection=connection,clearance=10,backwards=True)
    # gh.pickupNamed(connection=connection, root=rt, location="shelf_one", distance_threshold_mm=140)
    # for i in range(1):
    #     gh.shelfPickup(deviceGantry=deviceGantry,rt = rt,index =i)
    #     gh.goTo(deviceGantry=deviceGantry, root=rt, destination="bath_in", end_orient=-90, move=True,
    #             distance_threshold_mm=5)
    #
    #     gh.pickupNamed(connection=connection, root=rt, location="shelf_one", distance_threshold_mm=140)

    # gh.goTo(deviceGantry=deviceGantry, root=rt, destination="midpoint", end_orient=0, move=True,
    #         distance_threshold_mm=100)




    # SS = 500
    # SP = 0.1
    # i = 12
    # N = 6
    # remoteSPC = spc.getRemoteSPC()
    # remoteSPC.switchImageNum(1)
    # time.sleep(0.5)
    # remoteSPC.switchImageNum(2)
    # time.sleep(0.5)
    # remoteSPC.switchImageNum(3)
    # remoteSPC.switchImageNum(2)
    # remoteSPC.connect()
    # # set individual variables
    # remoteSPC.query(f"setvar speed {SS}\n")
    # remoteSPC.query(f"setvar spacing {SP}\n")
    # remoteSPC.query(f"setvar i0 {i}\n")
    # remoteSPC.query(f"setvar i1 {i}\n")
    # remoteSPC.query(f"setvar dim {N}\n")
    # remoteSPC.query(f"compile\n")

    # spc.query(f"setvar gridSpacing {grid_spacing}\n")
    # spc.query(f"setvar squareSize {square_size}\n")
    # spc.query(f"compile\n")
    # spc.query(f"run\n")

    # remoteSPC.switchImageNum(4)
    # for i in range(8):
    #     remoteSPC.switchImageNum(i+1)
    #     time.sleep(0.5)
    #     remoteSPC.query("compile\n")
    #     time.sleep(0.5)
    # remoteSPC.query("run\n")
    # remoteSPC.wait_until_done()
    # print("done")

    # gh.setOrientation(connection, backwards=False)

    #gh.dropoffBlind(connection=connection,backwards=False,clearance=10)