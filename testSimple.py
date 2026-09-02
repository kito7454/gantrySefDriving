import  helpers.gantryHelperSimple
from zaber_motion.ascii import Connection, pvt
from helpers.gantryHelperSimple import GantryHelperSimple
import helpers.remoteFTIRClient as remoteFTIR
import buildGantree
import time
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
import helpers.terahertzHelperSimple as tdh

rt = buildGantree.buildGantree(gantreeFile)
with Connection.open_serial_port('COM6') as connection:
    gh = GantryHelperSimple(connection=connection,root=rt)
    # thz = tdh.TerahertzHelper(gantry=gh, sampleLength=50.8)

    gh.goTo(destination='ftir_front', end_orient=-180, distance_threshold_mm=5, move=True)
    gh.goTo(destination='ftir_front', end_orient=-180, distance_threshold_mm=5, move=True)

    # gh.mailboxPickup(index=0)
    # thz.terahertzDropoffFlipped()
    # thz.terahertzPickupFlipped()
    # gh.mailboxDrop(index=0)
    # gh.dropoffNamed(location="write", clearance=5)
    # time.sleep(3)
    # gh.pickupNamed(location="write", distance_threshold_mm=10, backwards=False, clearance=5)
    # gh.mailboxDrop(index=0,clearance= 10)

    # gh.dropoffBlind(backwards=False,clearance=5,short=True)
    # for i in range(3):
    #     gh.mailboxPickup(index=i)
    # #
    # #     thz.terahertzDropoffFlipped()
    # #     time.sleep(1)
    # #     thz.terahertzPickupFlipped()
    # #
    #     gh.mailboxDrop(index=i+1)

    # for col in range(6):
    #     for row in range(2):
    #         gh.mailboxGoTo(index_y=col,index_z=row)
    #         gh.xyzMoveRelative(xDist=-100)
    #         time.sleep(1)
    #         gh.xyzMoveRelative(xDist=100)
    #         time.sleep(2)