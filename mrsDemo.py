# moves from shelf to galvo then to keyence then to ir
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt

import buildGantree
import helpers.spcHelper as sh
import numpy as np
# import importantCoordinates
import time
# from zaber_motion.dto.ascii import MeasurementSequence
import helpers.gantryHelper as gantryHelper
import helpers.shelfHelper as sh
import helpers.webSwitchHelper
import helpers.webSwitchHelper as wsh
# import helpers.ahkHelper as ahk

rt = buildGantree.buildGantree()

with Connection.open_serial_port('COM5') as connection:
    with sh.SPCHelper() as client:
        #
        # gantryHelper.setPiPos(client,preset="stage1gantry")
        # gantryHelper.setPiPos(client, preset="stage2gantry")

        device_list = connection.detect_devices()
        device2 = device_list[1]
        # target the first rotation stage
        device3 = device_list[2]
        device4 = device_list[3]



        # pickup from shelf ####

        gantryHelper.setOrientation(connection, backwards=True)
        gantryHelper.pickup(device2, importantCoordinates.shelfLocBig, backwards=True)

        c = importantCoordinates.aboveTheShelf
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=60)
        # ########
        #
        #
        # c = importantCoordinates.piClose
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=60)
        #
        # ########
        #
        # # put on pistage####
        #
        # gantryHelper.setOrientation(connection, backwards=False)
        #
        # gantryHelper.dropOnPiStage(device2, client)
        #
        # print(input("enter to continue"))
        #
        # gantryHelper.pickupPiStage(device2, client)
        #
        #
        # c = importantCoordinates.piClose
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2] + 50, zSpeed=100)
        #
        # gantryHelper.navigate(device2, rt, pointA="piStageClose", pointB="aboveCleaner")
        #
        # # pu tinto cleaner
        # gantryHelper.setAngles(connection=connection, angle=91,angle2=180)
        #
        # c = importantCoordinates.inCleaner
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2] + 50, zSpeed=100)
        #
        # c = importantCoordinates.inCleaner
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=60)
        #
        # time.sleep(3)
        #
        # c = importantCoordinates.inCleaner
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2] + 50, zSpeed=100)
        #
        # # ##########
        #
        # ay = device2.get_axis(3)
        #
        # # shake off ####
        # for i in range(2):
        #     c = importantCoordinates.inCleaner
        #     gantryHelper.xyzMove(device2, c[0], c[1], c[2] + 120, zSpeed=10)
        #
        #     c = importantCoordinates.inCleaner
        #     gantryHelper.xyzMove(device2, c[0], c[1], c[2] + 90, zSpeed=10)
        #
        #     c = importantCoordinates.inCleaner
        #     gantryHelper.xyzMove(device2, c[0], c[1] + 25, c[2] + 90, maxSpeed=10, zSpeed=10)
        #
        #     c = importantCoordinates.inCleaner
        #     gantryHelper.xyzMove(device2, c[0], c[1] + 25, c[2] + 120, zSpeed=10)
        #
        # ##########
        #
        # c = importantCoordinates.aboveCleaner
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=100)
        #
        # # hot plate part#########
        #
        # gantryHelper.setOrientation(connection, backwards=False)
        #
        # c = importantCoordinates.aboveHotPlate
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=100)
        #
        # gantryHelper.dropoff(device2, coordinates=importantCoordinates.onHotPlate, backwards=False)
        # time.sleep(2)
        # gantryHelper.pickup(device2, importantCoordinates.onHotPlate, backwards=True)
        #
        # c = importantCoordinates.aboveHotPlate
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=100)
        #
        # # hot plate to wetting transition###
        #
        # c = importantCoordinates.keyenceFar
        # gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=100)
        #
        # gantryHelper.navigate(device2, rt, pointA="keyenceFar", pointB="aboveWetting")
        #####


        # start of wetting

        c = importantCoordinates.aboveWetting
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=100)

        gantryHelper.setOrientation(connection,backwards=False)

        wettingPts = [importantCoordinates.aboveWetting, importantCoordinates.wettingA, importantCoordinates.wettingB,
                      importantCoordinates.wettingC, importantCoordinates.wettingD, importantCoordinates.wettingE]

        for i in wettingPts:
            c = i
            gantryHelper.xyzMove(device2, c[0], c[1], c[2], maxSpeed=50, zSpeed=50)

        time.sleep(1)

        # drop ###########
        webSwitchHelper.switch(0)
        c = importantCoordinates.wettingE
        gantryHelper.xyzMove(device2, c[0], c[1], c[2] + 10, maxSpeed=50, zSpeed=50)


        # back out to watch
        wettingPtsRev = [importantCoordinates.wettingD, importantCoordinates.wettingC,
                         importantCoordinates.wettingB
                         ]
        for j in wettingPtsRev:
            c = j
            gantryHelper.xyzMove(device2, c[0], c[1], c[2], maxSpeed=50, zSpeed=50)

        # wait until user says to pick back up
        c = importantCoordinates.wettingB
        gantryHelper.xyzMove(device2, c[0], c[1], c[2]+300, maxSpeed=50, zSpeed=50)
        print(input("enter when done with wetting"))

        #carefully go back in####
        wettingPts = [importantCoordinates.wettingB,
                      importantCoordinates.wettingC]
        for i in wettingPts:
            c = i
            gantryHelper.xyzMove(device2, c[0], c[1], c[2], maxSpeed=50, zSpeed=50)

        # go in but 10mm higher
        c = importantCoordinates.wettingD
        gantryHelper.xyzMove(device2, c[0], c[1], c[2]+10, maxSpeed=50, zSpeed=50)
        c = importantCoordinates.wettingE
        gantryHelper.xyzMove(device2, c[0], c[1], c[2]+10, maxSpeed=50, zSpeed=50)


        # pickup
        webSwitchHelper.switch(1)
        c = importantCoordinates.wettingE
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], maxSpeed=50, zSpeed=50)
        time.sleep(0.5)
        #################

        # back out of wetting machine
        wettingPtsRev = [importantCoordinates.wettingE, importantCoordinates.wettingD, importantCoordinates.wettingC,
                         importantCoordinates.wettingB, importantCoordinates.wettingA,
                         importantCoordinates.aboveWetting]

        for j in wettingPtsRev:
            c = j
            gantryHelper.xyzMove(device2, c[0], c[1], c[2], maxSpeed=50, zSpeed=50)
            #############

# after wetting, get into position for IR image - before keyence
#ideally, keyence to shelf at very end

        # ir part #########
        c = importantCoordinates.irFar
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=120)

        gantryHelper.setAngles(connection=connection, angle=90, angle2=200)

        c = importantCoordinates.irLoc
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=120)

        # simulate take ir pic
        time.sleep(4)

        c = importantCoordinates.irFar
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=120)

        gantryHelper.setOrientation(connection=connection, backwards=True)


        #     keyence part ##########

        c = importantCoordinates.keyenceFar
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=100)

        # go to keyence #####
        gantryHelper.setOrientation(connection, backwards=True)
        gantryHelper.navigate(device2, rt, pointA="keyenceFar", pointB="keyenceClose")

        ####place on keyence and pick back up###########

        gantryHelper.dropoff(device2, importantCoordinates.keyLoc, backwards=True)

        c = importantCoordinates.keyenceClose
        gantryHelper.xyzMove(device2, c[0], c[1], c[2], zSpeed=60)

        print(input("enter when done with keyence"))

        gantryHelper.pickup(device2, importantCoordinates.keyLoc, backwards=True)

        gantryHelper.navigate(device2, rt, pointA="keyenceClose", pointB="midpoint")

        ##########



        gantryHelper.navigate(device2, rt, pointA="midpoint", pointB="aboveShelf")

        # #####################

        gantryHelper.setOrientation(connection, backwards=True)

        gantryHelper.dropoff(device2, coordinates=importantCoordinates.shelfLocBig, backwards=True)


