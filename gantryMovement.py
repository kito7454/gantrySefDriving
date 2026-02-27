"""
GantryMovement module to control gantry movements using GanTree structure.
Carries out instructions to move the gantry recieved from scheduler.
This should also take care of all error handling and ensure only safe movements are made.
This is a pure server node.
"""

import numpy as np
import time
import zmq

from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt

import gantree as gt
# from helpers.spcHelper import SPCHelper
from helpers.gantryHelper import navigate, xyzMove, pickup, dropoff
# import shelfHelper
# import ahkHelper as ahk
from buildGantree import buildGantree

class GantryMovement:
    def __init__(self):
        self.gantree = buildGantree("curr_gantry.csv")
        self.gantry_channel = 7000  # Default channel number for gantry communication
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
    
    def get_position(self):
        # TODO: Use gantryHelper.py methods to get current position
        print("Getting current gantry position...")
    
    def pickup(self, station):
        # TODO: station dependent pick up sequence, query the gantry MotionTable
        print(f"Picking up from {station}...")\

    def dropoff(self, station):
        # TODO: station dependent drop off sequence, query the gantry MotionTable
        print(f"Dropping off at {station}...")
    
    def swap(self, station, storage_loc):
        # TODO
        print(f"Swapping {station} with storage location {storage_loc}...")
    
    def bath(self):
        # TODO: Need to hold during bath
        print("Starting bath sequence...")
    
    def dump(self):
        # TODO: just take to X and drop off
        print("Starting dump sequence...")

if __name__ == "__main__":
    gantry = GantryMovement()
    gantry.socket.bind(f"tcp://0.0.0.0:{gantry.gantry_channel}")
    midpoint = np.array([1083,565,500])
    # with Connection.open_serial_port('COM6') as connection:
    #     device_list = connection.detect_devices()
    #     crane = device_list[1]
    #     angle1 = device_list[2]
    #     angle2 = device_list[3]
    #     if np.isclose(midpoint < gantry.get_position()): # if position is near center
    #         xyzMove(crane,1083,565,500)
    #     else:
    #         print("ERROR! Please move gantry near midpoint and try again.")
    #         raise(Exception("Dangerous Movement Detected!."))
    while True:
        message = gantry.socket.recv_string()
        if message == "STOP":
            print("Shutting down gantry movement...")
            break

        start, end, swap, job = message.split()
        if swap == "1":
            gantry.swap(start, end)
        elif end == "Dump":
            gantry.pickup(start)
            gantry.dump()
        elif end == "Bath":
            gantry.pickup(start)
            gantry.bath()
            gantry.dropoff(start)
        else:
            gantry.pickup(start)
            gantry.dropoff(end)

        gantry.socket.send_string("DONE")