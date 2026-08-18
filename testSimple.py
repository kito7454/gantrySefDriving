import  helpers.gantryHelperSimple
from zaber_motion.ascii import Connection, pvt
from helpers.gantryHelperSimple import GantryHelperSimple
import buildGantree
import time
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
import helpers.terahertzDropoffHelper as tdh

rt = buildGantree.buildGantree(gantreeFile)
with Connection.open_serial_port('COM6') as connection:
    gh = GantryHelperSimple(connection=connection,root=rt)
    # tdh.terahertzPickupFlipped(deviceGantry=gh.deviceGantry, root=rt, sample_length=50.8)
    for i in range(4):
        gh.mailboxPickup(index=4*i)

        tdh.terahertzDropoffFlipped(deviceGantry=gh.deviceGantry, root=rt, sample_length=50.8)
        tdh.terahertzPickupFlipped(deviceGantry=gh.deviceGantry, root=rt, sample_length=50.8)

        gh.mailboxDrop(index=4*(i+1))

    # for col in range(6):
    #     for row in range(2):
    #         gh.mailboxGoTo(index_y=col,index_z=row)
    #         gh.xyzMoveRelative(xDist=-100)
    #         time.sleep(1)
    #         gh.xyzMoveRelative(xDist=100)
    #         time.sleep(2)