import datetime

import  helpers.gantryHelperSimple
from zaber_motion.ascii import Connection, pvt
from helpers.gantryHelperSimple import GantryHelperSimple
import buildGantree
import helpers.remoteTHZClient as remoteTHZ
import time
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
import helpers.terahertzHelperSimple as tdh

# run this in terminal to allow remote connections
# python -m Pyro5.nameserver -n 128.3.110.157

rt = buildGantree.buildGantree(gantreeFile)
with Connection.open_serial_port('COM6') as connection:
    gh = GantryHelperSimple(connection=connection,root=rt)
    thz = tdh.TerahertzHelper(gantry=gh, sampleLength=50.8)
    # tdh.terahertzPickupFlipped(deviceGantry=gh.deviceGantry, root=rt, sample_length=50.8)
    for i in range(21):
        remoteTHZ.homeStages()
        time.sleep(5)
        if not remoteTHZ.checkHomed():
            raise ValueError("Home Failure")

        gh.mailboxPickup(index=i)
        thz.terahertzDropoffFlipped()
        time.sleep(1)

        print(f"{i} starting at: {datetime.datetime.now()}")
        remoteTHZ.startTDS()
        for j in range(64):
            time.sleep(60)
        print(f"{i} finishing at: {datetime.datetime.now()}")
        remoteTHZ.homeStages()
        time.sleep(5)
        if not remoteTHZ.checkHomed():
            raise ValueError("Home Failure")

        thz.terahertzPickupFlipped()
        gh.mailboxDrop(index=i)
