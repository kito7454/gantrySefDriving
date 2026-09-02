# moves from shelf to galvo then to keyence then to ir
# for 50x50mm substrates
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt

import buildGantree
import helpers.spcPyroClient as spc
import datetime
import helpers.remoteFTIRClient as remoteFTIR
import helpers.terahertzHelperSimple as tdh
from zaber_motion.ascii import Connection, pvt
from helpers.gantryHelperSimple import GantryHelperSimple
import buildGantree
import helpers.remoteTHZClient as remoteTHZ
import time
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
# admin cmd this to start nameserver
# python -m Pyro5.nameserver -n 128.3.110.157

rt = buildGantree.buildGantree(gantreeFile)
with Connection.open_serial_port('COM6') as connection:
    gh = GantryHelperSimple(connection=connection,root=rt)
    spcRemote = spc.getRemoteSPC()
    thz = tdh.TerahertzHelper(gantry=gh, sampleLength=50.8)


    # spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_short")
    def manufacture(index,sample_length = 76.2):
        # batch start num is sample number last done
        if sample_length == 50.8:
            spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry_small")
        else:
            spc.moveDefinedLocation(remoteObject=spcRemote,location_name="gantry")

        gh.mailboxPickup(index=index)
        gh.dropoffNamed(location='write', backwards=False, clearance=5)
        # gh.dropoffNamed(connection=connection, root=rt, location="write",
        #                 backwards=False, distance_threshold_mm=5, short=True)

        if sample_length == 50.8:
            spc.moveDefinedLocation(remoteObject=spcRemote, location_name="etch_small")
        else:
            spc.moveDefinedLocation(remoteObject=spcRemote,location_name="etch")

        time.sleep(3)

        spcRemote.query(f"compile\n")
        time.sleep(0.5)

        spcRemote.query(f"run\n")
        time.sleep(0.5)
        spcRemote.wait_until_done()

        if sample_length == 50.8:
            spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry_small")
        else:
            spc.moveDefinedLocation(remoteObject=spcRemote, location_name="gantry")

        gh.pickupNamed(location="write", distance_threshold_mm=10, backwards=False,clearance=5)

    #
    # manufacture(index=0,sample_length=50.8) #put batch start as the sample you want to start on
    #
    # # ############manufacturing part
    #
    # # thz part##############
    # remoteTHZ.homeStages()
    # time.sleep(4)
    # if not remoteTHZ.checkHomed():
    #     raise ValueError("Home Failure")
    # thz.terahertzDropoffFlipped()
    # time.sleep(1)
    #
    # remoteTHZ.startTDS()
    # inp = input("press when thz done")
    # remoteTHZ.homeStages()
    # time.sleep(4)
    # if not remoteTHZ.checkHomed():
    #     raise ValueError("Home Failure")
    #
    # thz.terahertzPickupFlipped()
    # #########################
    #
    # # ftir stuff######
    #
    # # gh.goTo("ftir_front",end_orient=-180,maxSpeed=200)
    # # gh.mailboxPickup(index=0)
    # gh.dropoffNamed(location='ftir', backwards=True, clearance=5)
    # # gh.goTo(destination = "ftir_front",end_orient=-180)
    #
    # remoteFTIR.startFTIRNoScan()
    # ftirinp = input("press to continue")

    gh.pickupNamed(location="ftir",backwards=True,clearance=5)

    gh.mailboxDrop(index=0,clearance=9)

    ####################



    # gh.mailboxDrop(index=0,clearance=9)
    #########
