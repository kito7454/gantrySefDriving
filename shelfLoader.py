import  helpers.gantryHelperSimple
from zaber_motion.ascii import Connection, pvt
from helpers.gantryHelperSimple import GantryHelperSimple
import buildGantree
import time
gantreeFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
import helpers.terahertzHelperSimple as tdh

rt = buildGantree.buildGantree(gantreeFile)

i = 20

with Connection.open_serial_port('COM6') as connection:
    gh = GantryHelperSimple(connection=connection,root=rt)
    # thz = tdh.TerahertzHelper(gantry=gh, sampleLength=50.8)

    # gh.goTo(destination='write', end_orient=0, distance_threshold_mm=5, move=True)
    gh.pickupNamed(location="write", distance_threshold_mm=10, backwards=False, clearance=5)
    gh.mailboxDrop(index=i,clearance=10)
    gh.goTo(destination='galvo_back', end_orient=0, distance_threshold_mm=5, move=True)
