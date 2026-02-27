import time

from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt
import pandas as pd
import numpy as np
# from zaber_motion.dto.ascii import MeasurementSequence
from zaber_motion.ascii import MeasurementSequence
from zaber_motion.ascii.pvt import PvtSequence
from zaber_motion.dto.ascii import PvtAxisType, PvtAxisDefinition
import helpers.webSwitchHelper as wsh

import gantree
# import spcHelper

# ------------------------
# define locations:
# import importantCoordinates
# import webSwitchHelper as wsh
# dummyLoc = importantCoordinates.dummyLoc
# piLoc = importantCoordinates.piLoc
# shelfLoc = importantCoordinates.shelfLoc
########################################
# estabilishes connection to zaber devices
#
# Parameters:
# - connection: zaber api object
########################################
def connect(connection):
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))
    # target the xyz gantry
    device2 = device_list[1]

    # target the first rotation stage
    device3 = device_list[2]

def testMove(axis):
    axis.move_relative(25, Units.LENGTH_MILLIMETRES, True, 2000, Units.VELOCITY_MILLIMETRES_PER_SECOND, 1000,
                           Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

def pvtDrop(connection,backwards = False):

    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device2 = device_list[1]

    # target the first rotation stage
    device3 = device_list[2]
    device4 = device_list[3]

    device = device2
    all_axes = device.all_axes
    all_axes.stop()

    pvt_buffer = device.pvt.get_buffer(1)
    pvt_buffer.erase()
    pvt_ = device.pvt
    pvt_sequence = pvt_.get_sequence(1)

    pvt_sequence.setup_live_composite(
        PvtAxisDefinition(1, PvtAxisType.LOCKSTEP),
        PvtAxisDefinition(3, PvtAxisType.PHYSICAL),
        PvtAxisDefinition(4, PvtAxisType.PHYSICAL)
    )

    if backwards:
        angle = 1
        path = r"C:\Users\TeamD\PycharmProjects\Gantry-Programming\stageliftoffrelBackwards.csv"
        angle2 = 180
        vel = 5
    else:
        path = "C:/Users/TeamD/Desktop/kyle/stageliftoffrel.csv"
        angle = 181
        angle2 = 0
        vel = -5

    data = pvt_sequence.load_sequence_data(path).sequence_data
    r3 = device3.get_axis(1)
    r4 = device4.get_axis(1)

    r4.move_absolute(angle2, Units.ANGLE_DEGREES,wait_until_idle=False)
    r3.move_absolute(angle, Units.ANGLE_DEGREES)
    r3.wait_until_idle()
    r4.wait_until_idle()

    r3.move_velocity(vel, Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND)
    pvt_sequence.points_relative(
        [MeasurementSequence(p.values[1:], p.unit) for p in data.positions],
        [MeasurementSequence(v.values[1:], v.unit) for v in data.velocities],
        MeasurementSequence(data.times.values[1:], data.times.unit)
    )

    # ?rotate stage?

    # pvt_sequence.call(pvt_buffer)

    time.sleep(2.5)
    r3.stop()
    r3.move_absolute(angle, Units.ANGLE_DEGREES)
    r3.wait_until_idle()

    all_axes.wait_until_idle(throw_error_on_fault=True)
    all_axes.stop()

    pvt_sequence.disable()


def xyzMove(device,xpos,ypos,zpos,maxSpeed=200,maxAccel=100,zSpeed=25,wait_until_idle=True):
    # give xyz device ONLY
    # millimetres!!!!!
    ax = device.get_lockstep(1)
    ay = device.get_axis(3)
    az = device.get_axis(4)

    ax.move_absolute(xpos, Units.LENGTH_MILLIMETRES, False, maxSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND, maxAccel,
                           Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
    ay.move_absolute(ypos, Units.LENGTH_MILLIMETRES, False, maxSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND, maxAccel,
                      Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
    az.move_absolute(zpos, Units.LENGTH_MILLIMETRES, wait_until_idle, zSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND, 100,
                     Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

    all_axes = device.all_axes

    if wait_until_idle:
        all_axes.wait_until_idle(throw_error_on_fault=wait_until_idle)

def rotate(device,axNum,angle,wait = True):
    # give xyz device ONLY
    # millimetres!!!!!
    az = device.get_axis(axNum)

    az.move_absolute(angle, Units.ANGLE_DEGREES, wait_until_idle=wait)

# pickups up the sample from specified coordinates [x,y,z] abs mm
def pickup(device,coordinates,backwards = False, clearance = 5):
    # start 5mm away in z
    # xyzMove(device, coordinates[0], coordinates[1], coordinates[2]+5, 80, 50, 25)

    # actually pick up and wait for vacuum

    xyzMove(device, coordinates[0], coordinates[1], coordinates[2], 10, 50, 10)
    wsh.switch(1)
    time.sleep(1)

    # lift away
    delx = 2
    if backwards:
        delx = -delx
    xyzMove(device, coordinates[0]+delx, coordinates[1]+delx, coordinates[2] + clearance, 20, 25, 10)

def pickupNamed(device,root,location,backwards = False, clearance = 5,maxSpeed=500, gantreeCsv = "curr_gantry.csv",distance_threshold_mm = 5):
    goTo(device=device,root=root,destination=location,gantreeCsv=gantreeCsv,distance_threshold_mm=distance_threshold_mm)
    coordinates = pollGantry(device)
    xyzMove(device, coordinates[0], coordinates[1], coordinates[2]-clearance, 10, 50, 10)
    wsh.switch(1)
    time.sleep(1)
    # lift away
    delx = 2
    if backwards:
        delx = -delx
    xyzMove(device, coordinates[0] + delx, coordinates[1] + delx, coordinates[2], 20, 25, 10)

def dropoff(device,coordinates,backwards = False):
    sign = 1
    if backwards:
        sign = -1
    xyzMove(device, coordinates[0] + 3*sign, coordinates[1] + 3*sign, coordinates[2] + 25, 100, 70, 150)
    xyzMove(device, coordinates[0] + 2*sign, coordinates[1] + 2*sign, coordinates[2] + 3, 50, 50, 50)
    xyzMove(device, coordinates[0], coordinates[1], coordinates[2], 10, 100, 10)
    wsh.switch(0)
    pvtDrop(device.connection,backwards)

# TODO
# takes zaber device and SPC client
# def dropOnPiStage(device,client):
    # setPiPos(client,preset = "stage1gantry")
    #
    # c = importantCoordinates.piClose
    # xyzMove(device, c[0], c[1], c[2], zSpeed=60)
    #
    # dropoff(device, importantCoordinates.piLocBig, backwards=False)
    #
    # setPiPos(client,preset = "stage1galvo")

# TODO
# def pickupPiStage(device,client):
    # setPiPos(client,preset = "stage1gantry")
    # time.sleep(2)
    # pickup(device, importantCoordinates.piLocBig)

def setOrientation(connection,backwards = False):

    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device2 = device_list[1]

    # target the first rotation stage
    device3 = device_list[2]
    device4 = device_list[3]

    device = device2
    all_axes = device.all_axes
    all_axes.stop()

    if backwards:
        angle = 1
        angle2 = 180
    else:
        angle = 181
        angle2 = 0

    r3 = device3.get_axis(1)
    r4 = device4.get_axis(1)

    r4.move_absolute(angle2, Units.ANGLE_DEGREES,wait_until_idle=False)
    r3.move_absolute(angle, Units.ANGLE_DEGREES)
    r3.wait_until_idle()
    r4.wait_until_idle()

def navigate(device,root,pointA,pointB,maxSpeed = 500,move = False):
    # device: Zaber gantry device object
    # root: Gantree data structure root
    # Points: String Names of points to move from
    # move: Supply as true if you want gantry to actually move

    route = root.traverseFromName(pointA,pointB)
    print(route)
    coords = gantree.routeToCoordinates(route)


    if move:
        for i in range(len(coords)):
            print("Coordinates: " + str(coords[i]))
            xyzMove(device=device,xpos=coords[i][0],ypos=coords[i][1],zpos=coords[i][2],maxSpeed=maxSpeed, maxAccel=200,zSpeed=250)
    else:
        print(route)

def setPiPos(client,stage = 1,xval = 0,yval=200,zval=16,preset = None):

    if preset is not None:
        if preset == "stage1gantry":
            xval = 0
            yval = 200
            zval = 16
        if preset == "stage1galvo":
            xval = 132.5
            yval = 33
            zval = 16.75
        if preset == "stage2gantry":
            xval = 200
            yval = 200
            zval = 0
            stage = 2

        if stage == 2:
            piX = "x2"
            piY = "y2"
            piZ = "z2"
        else:
            piX = "x1"
            piY = "y1"
            piZ = "z1"


    client.query("move " + piZ + " " + str(zval) + "\n")
    time.sleep(1)
    client.query("move " + piY + " " + str(yval) + "\n")
    time.sleep(1)
    client.query("move " + piX + " " + str(xval) + "\n")
    time.sleep(1)

def setAngles(connection,angle=None,angle2 = None):
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device2 = device_list[1]

    # target the first rotation stage
    device3 = device_list[2]
    device4 = device_list[3]

    device = device2
    all_axes = device.all_axes
    all_axes.stop()

    r3 = device3.get_axis(1)
    r4 = device4.get_axis(1)

    if angle2 is not None:
        r4.move_absolute(angle2, Units.ANGLE_DEGREES,wait_until_idle=False)

    if angle is not None:
        r3.move_absolute(angle, Units.ANGLE_DEGREES)

    r3.wait_until_idle()
    r4.wait_until_idle()

def pollGantry(device):
    # returns the positions of a devices axes
    ax = device.get_lockstep(1)
    ay = device.get_axis(3)
    az = device.get_axis(4)
    return [ax.get_position(Units.LENGTH_MILLIMETRES),ay.get_position(Units.LENGTH_MILLIMETRES),az.get_position(Units.LENGTH_MILLIMETRES)]

def checkClosest(device,gantreeCsv = "curr_gantry.csv"):
    pos = pollGantry(device)
    df = pd.read_csv(gantreeCsv)

    distances = np.sqrt(
        (df['x'] - pos[0]) ** 2 +
        (df['y'] - pos[1]) ** 2 +
        (df['z'] - pos[2]) ** 2
    )

    # 4. Find the row with the minimum distance
    closest_idx = distances.idxmin()
    closest_row = df.loc[closest_idx]
    min_dist = distances.min()

    return {
        "name": closest_row.key,
            "distance": min_dist
            }

    print(f"Closest Entry:\n{closest_row}")
    print(f"Distance: {min_dist}")

def goTo(device,root,destination,maxSpeed=500, gantreeCsv = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv",distance_threshold_mm = 5,move=False):
    # device: Zaber gantry device object
    # root: Gantree data structure root
    # Points: String Names of points to move from
    # move: Supply as true if you want gantry to actually move
    # farthest the gantry can be from a known point before throwing error

    closest = checkClosest(device,gantreeCsv)
    dist = closest.get("distance")
    current_point = closest.get("name")
    if dist < distance_threshold_mm:
        print("gantry found at: " + current_point)
        navigate(device, root, current_point, destination, maxSpeed=500, move=move)
    else:
        print(closest)
        raise ValueError("gantry is lost.")
