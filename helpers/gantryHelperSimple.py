import math
import os
import time

import numpy as np
import pandas as pd

from zaber_motion import Units
from zaber_motion.ascii import Connection, MeasurementSequence
from zaber_motion.dto.ascii import PvtAxisType, PvtAxisDefinition

import helpers.webSwitchHelper as wsh
import gantree
from helpers.gantryHelperAdvanced import linearIndexToCoords


class GantryHelperSimple:
    """
    Object oriented wrapper around the Zaber XYZ gantry + 2 rotary stages.

    Everything that used to be passed around (connection, deviceGantry, root,
    gantreeCsv, speeds, clearances, sample length, ...) is now instance state.
    Any method argument left as None falls back to the corresponding property.
    """

    # ------------------------------------------------------------------ #
    # class level constants / defaults
    # ------------------------------------------------------------------ #
    DEFAULT_TREE = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"
    PVT_DIR = r"C:\Users\v_zor\PycharmProjects\KyleHardcode"

    FULL_SAMPLE_LENGTH_MM = 76.2
    MIN_SAMPLE_LENGTH_MM = 48.0
    MAX_SAMPLE_LENGTH_MM = 77.0

    # axis map on the gantry device
    X_LOCKSTEP = 1
    Y_AXIS = 3
    Z_AXIS = 4

    # (short, backwards) -> pvt drop profile
    PVT_PROFILES = {
        (False, False): dict(file="stageliftoffrel.csv",
                             angle=0, angle2=0, vel=-4.8, del_theta=-14.4,
                             label="dropping"),
        (False, True):  dict(file="stageliftoffrelBackwards.csv",
                             angle=-180, angle2=180, vel=4.8, del_theta=14.4,
                             label="dropping backwards"),
        (True, False):  dict(file="stageliftoffrelShort.csv",
                             angle=0, angle2=0, vel=-4.8, del_theta=-7.2,
                             label="short dropping"),
        (True, True):   dict(file="stageliftoffrelBackwardsShort.csv",
                             angle=-180, angle2=180, vel=4.8, del_theta=7.2,
                             label="short dropping backwards"),
    }

    # ------------------------------------------------------------------ #
    # construction
    # ------------------------------------------------------------------ #
    def __init__(self,
                 connection,
                 root=None,
                 gantreeCsv=None,
                 gantryIndex=1,
                 pitchIndex=2,
                 rollIndex=3,
                 # motion defaults
                 maxSpeed=250,
                 maxAccel=200,
                 zSpeed=250,
                 moveSpeed=200,
                 moveAccel=100,
                 moveZSpeed=25,
                 rotationVelocity=13,
                 # task defaults
                 backwards=False,
                 clearance=10,
                 sampleLength=FULL_SAMPLE_LENGTH_MM,
                 distanceThresholdMm=5,
                 mailboxSpacing=25.4 * 2.55,
                 mailboxColumns=7,
                 mailboxRows=3,
                 mailboxAngleIncrement = -0.9,
                 vacuumSettle=1.0,
                 pvtDwell=2.5,
                 offset=(0.0, 0.0, 0.0),
                 verbose=True):

        self.connection = connection
        self.root = root
        self.gantreeCsv = gantreeCsv if gantreeCsv is not None else self.DEFAULT_TREE

        self.gantryIndex = gantryIndex
        self.pitchIndex = pitchIndex
        self.rollIndex = rollIndex

        self.maxSpeed = maxSpeed
        self.maxAccel = maxAccel
        self.zSpeed = zSpeed
        self.moveSpeed = moveSpeed
        self.moveAccel = moveAccel
        self.moveZSpeed = moveZSpeed
        self.rotationVelocity = rotationVelocity

        self.backwards = backwards
        self.clearance = clearance
        self.sampleLength = sampleLength
        self.distanceThresholdMm = distanceThresholdMm
        self.mailboxSpacing = mailboxSpacing
        self.mailboxColumns = mailboxColumns
        self.mailboxRows = mailboxRows
        self.mailboxAngleIncrement = mailboxAngleIncrement
        self.vacuumSettle = vacuumSettle
        self.pvtDwell = pvtDwell
        self.offset = list(offset)
        self.verbose = verbose

        self._treeDf = None
        self.deviceList = []
        self.deviceGantry = None
        self.devicePitch = None
        self.deviceRoll = None
        self.refreshDevices()

    @classmethod
    def fromSerialPort(cls, port, **kwargs):
        """Convenience constructor. Caller owns / closes the connection."""
        connection = Connection.open_serial_port(port)
        return cls(connection, **kwargs)

    def refreshDevices(self):
        """Re-run detect_devices() and re-bind the device properties."""
        self.deviceList = self.connection.detect_devices()
        self._log("Found {} devices".format(len(self.deviceList)))
        self.deviceGantry = self.deviceList[self.gantryIndex]
        self.devicePitch = self.deviceList[self.pitchIndex]
        self.deviceRoll = self.deviceList[self.rollIndex]
        return self.deviceList

    def _log(self, msg):
        if self.verbose:
            print(msg)

    # ------------------------------------------------------------------ #
    # axis / state properties
    # ------------------------------------------------------------------ #
    @property
    def axX(self):
        return self.deviceGantry.get_lockstep(self.X_LOCKSTEP)

    @property
    def axY(self):
        return self.deviceGantry.get_axis(self.Y_AXIS)

    @property
    def axZ(self):
        return self.deviceGantry.get_axis(self.Z_AXIS)

    @property
    def axPitch(self):
        return self.devicePitch.get_axis(1)

    @property
    def axRoll(self):
        return self.deviceRoll.get_axis(1)

    @property
    def allAxes(self):
        return self.deviceGantry.all_axes

    @property
    def position(self):
        """Current [x, y, z] of the gantry in mm (old pollGantry)."""
        return [self.axX.get_position(Units.LENGTH_MILLIMETRES),
                self.axY.get_position(Units.LENGTH_MILLIMETRES),
                self.axZ.get_position(Units.LENGTH_MILLIMETRES)]

    @property
    def pitch(self):
        return self.axPitch.get_position(Units.ANGLE_DEGREES)

    @property
    def roll(self):
        return self.axRoll.get_position(Units.ANGLE_DEGREES)

    @property
    def treeDf(self):
        """Cached gantree csv. Call reloadTree() after editing the file."""
        if self._treeDf is None:
            self._treeDf = pd.read_csv(self.gantreeCsv)
        return self._treeDf

    def reloadTree(self):
        self._treeDf = None
        return self.treeDf

    # kept for backwards compatibility with the old function names
    def pollGantry(self):
        return self.position

    def pollAngle(self, device=None):
        device = device if device is not None else self.devicePitch
        return device.get_axis(1).get_position(Units.ANGLE_DEGREES)

    # ------------------------------------------------------------------ #
    # small helpers
    # ------------------------------------------------------------------ #
    def _resolve(self, value, attr):
        return getattr(self, attr) if value is None else value

    def _orientationAngle(self, backwards=None):
        backwards = self._resolve(backwards, "backwards")
        return -180 if backwards else 0

    def _sampleOffset(self, sampleLength=None, backwards=None):
        """Long axis correction for samples that are not a full 3 in."""
        sampleLength = self._resolve(sampleLength, "sampleLength")
        backwards = self._resolve(backwards, "backwards")

        if sampleLength < self.MIN_SAMPLE_LENGTH_MM or sampleLength > self.MAX_SAMPLE_LENGTH_MM:
            raise ValueError("Sample length incompatible: {}".format(sampleLength))

        offset = self.FULL_SAMPLE_LENGTH_MM - sampleLength
        return -offset if backwards else offset

    def vacuum(self, on):
        wsh.switch(1 if on else 0)

    # ------------------------------------------------------------------ #
    # primitive motion
    # ------------------------------------------------------------------ #
    def xyzMove(self, xpos, ypos, zpos,
                maxSpeed=None, maxAccel=None, zSpeed=None, wait_until_idle=True):
        maxSpeed = self._resolve(maxSpeed, "moveSpeed")
        maxAccel = self._resolve(maxAccel, "moveAccel")
        zSpeed = self._resolve(zSpeed, "moveZSpeed")

        self.axX.move_absolute(xpos, Units.LENGTH_MILLIMETRES, False,
                               maxSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND,
                               maxAccel, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
        self.axY.move_absolute(ypos, Units.LENGTH_MILLIMETRES, False,
                               maxSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND,
                               maxAccel, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
        self.axZ.move_absolute(zpos, Units.LENGTH_MILLIMETRES, wait_until_idle,
                               zSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND,
                               100, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

        if wait_until_idle:
            self.allAxes.wait_until_idle(throw_error_on_fault=True)

    def xyzMoveRelative(self, xDist=0, yDist=0, zDist=0,
                maxSpeed=None, maxAccel=None, zSpeed=None, wait_until_idle=True):
        maxSpeed = self._resolve(maxSpeed, "moveSpeed")
        maxAccel = self._resolve(maxAccel, "moveAccel")
        zSpeed = self._resolve(zSpeed, "moveZSpeed")
        dists = [xDist, yDist, zDist]
        for index,ax in enumerate([self.axX,self.axY,self.axZ]):

            ax.move_relative(dists[index], Units.LENGTH_MILLIMETRES, False,
                                   maxSpeed, Units.VELOCITY_MILLIMETRES_PER_SECOND,
                                   maxAccel, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

        if wait_until_idle:
            self.allAxes.wait_until_idle(throw_error_on_fault=True)

    def moveX(self, distance, velocity=100, acceleration=50):
        """Relative move of the lockstep long axis."""
        self.axX.move_relative(position=distance,
                               unit=Units.LENGTH_MILLIMETRES,
                               velocity=velocity,
                               velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
                               acceleration=acceleration,
                               acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

    def testMove(self, axis=None):
        axis = axis if axis is not None else self.axY
        axis.move_relative(25, Units.LENGTH_MILLIMETRES, True,
                           2000, Units.VELOCITY_MILLIMETRES_PER_SECOND,
                           1000, Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)

    def rotate(self, axNum, angle, wait=True):
        self.deviceGantry.get_axis(axNum).move_absolute(
            angle, Units.ANGLE_DEGREES, wait_until_idle=wait)

    def setAngles(self, angle=None, angle2=None, velocity=None):
        """angle -> pitch stage, angle2 -> roll stage. None leaves an axis alone."""
        velocity = self._resolve(velocity, "rotationVelocity")
        self.allAxes.stop()

        if angle2 is not None:
            self.axRoll.move_absolute(position=angle2, unit=Units.ANGLE_DEGREES,
                                      velocity=velocity,
                                      velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
                                      wait_until_idle=False)
        if angle is not None:
            self.axPitch.move_absolute(position=angle, unit=Units.ANGLE_DEGREES,
                                       velocity=velocity,
                                       velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
                                       wait_until_idle=False)

        self.axPitch.wait_until_idle()
        self.axRoll.wait_until_idle()

    def setOrientation(self, backwards=None):
        backwards = self._resolve(backwards, "backwards")
        angle = -180 if backwards else 0
        angle2 = 180 if backwards else 0

        self.allAxes.stop()
        self.axRoll.move_absolute(angle2, Units.ANGLE_DEGREES, wait_until_idle=False)
        self.axPitch.move_absolute(angle, Units.ANGLE_DEGREES)
        self.axPitch.wait_until_idle()
        self.axRoll.wait_until_idle()

    # ------------------------------------------------------------------ #
    # pvt release
    # ------------------------------------------------------------------ #
    def pvtDrop(self, backwards=None, short=False, dwell=None,mailboxPitchException = False):
        backwards = self._resolve(backwards, "backwards")
        dwell = self._resolve(dwell, "pvtDwell")

        profile = self.PVT_PROFILES[(bool(short), bool(backwards))]
        pathPVT = os.path.join(self.PVT_DIR, profile["file"])
        self._log(profile["label"])

        self.allAxes.stop()

        pvt_buffer = self.deviceGantry.pvt.get_buffer(1)
        pvt_buffer.erase()
        pvt_sequence = self.deviceGantry.pvt.get_sequence(1)
        pvt_sequence.setup_live_composite(
            PvtAxisDefinition(self.X_LOCKSTEP, PvtAxisType.LOCKSTEP),
            PvtAxisDefinition(self.Y_AXIS, PvtAxisType.PHYSICAL),
            PvtAxisDefinition(self.Z_AXIS, PvtAxisType.PHYSICAL),
        )

        data = pvt_sequence.load_sequence_data(pathPVT).sequence_data

        # park the rotaries at the drop orientation
        self.axRoll.move_absolute(profile["angle2"], Units.ANGLE_DEGREES, wait_until_idle=False)
        if not mailboxPitchException:
            self.axPitch.move_absolute(profile["angle"], Units.ANGLE_DEGREES)
            self.axPitch.wait_until_idle()
        pitchVal =self.axPitch.get_position(unit=Units.ANGLE_DEGREES)
        if abs(pitchVal) > abs(2.5*self.mailboxAngleIncrement):
            raise ValueError("pitch angle misalignment pitch={}".format(pitchVal))

        self.axRoll.wait_until_idle()

        # peel the sample off while the gantry runs the pvt lift-off
        self.axPitch.move_relative(profile["del_theta"], Units.ANGLE_DEGREES,
                                   velocity=abs(profile["vel"]),
                                   velocity_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
                                   wait_until_idle=False)

        pvt_sequence.points_relative(
            [MeasurementSequence(p.values[1:], p.unit) for p in data.positions],
            [MeasurementSequence(v.values[1:], v.unit) for v in data.velocities],
            MeasurementSequence(data.times.values[1:], data.times.unit),
        )

        time.sleep(dwell)
        self.axPitch.stop()
        self.axPitch.move_absolute(profile["angle"], Units.ANGLE_DEGREES)
        self.axPitch.wait_until_idle()

        self.allAxes.wait_until_idle(throw_error_on_fault=True)
        self.allAxes.stop()
        pvt_sequence.disable()

    # ------------------------------------------------------------------ #
    # tree lookups / localization
    # ------------------------------------------------------------------ #
    def lookupCoordinates(self, key):
        return self.treeDf.loc[self.treeDf['key'] == key].iloc[0]

    # def checkClosest(self):
    #     pos = self.position
    #     df = self.treeDf
    #
    #     distances = np.sqrt((df['x'] - pos[0]) ** 2 +
    #                         (df['y'] - pos[1]) ** 2 +
    #                         (df['z'] - pos[2]) ** 2)
    #
    #     closest_idx = distances.idxmin()
    #     closest_row = df.loc[closest_idx]
    #     min_dist = distances.min()
    #
    #     # special case: buried inside the shelf/mailbox, far from any node
    #     if min_dist > self.distanceThresholdMm:
    #         s1_row = self.lookupCoordinates("shelf_one")
    #         in_shelf = all([(s1_row['x']-pos[0]) < 120,
    #                         (s1_row['x'] - pos[0]) > -10,
    #                         abs(pos[1] - s1_row['y']) < 626,
    #                         abs(pos[2] - s1_row['z']) < 130])
    #         print([pos[0] - s1_row['x'],pos[1] - s1_row['y'],pos[2] - s1_row['z']])
    #         if in_shelf:
    #             return {"name": "in_shelf", "distance": 1}
    #
    #     return {"name": closest_row.key, "distance": min_dist}

    # Envelope of the mailbox. y is loose because that is the long travel
    # along the face of the fixture.
    def inMailbox(self, pos=None):
        """True if the tool is inside the mailbox envelope."""
        pos = self.position if pos is None else pos
        row = self.lookupCoordinates("mailbox_back")
        return all([(row['x']-pos[0]) < 120,
                            (row['x'] - pos[0]) > -10,
                            abs(pos[1] - row['y']) < 626,
                            abs(pos[2] - row['z']) < 150])

    def checkClosest(self):
        pos = self.position
        df = self.treeDf

        distances = np.sqrt((df['x'] - pos[0]) ** 2 +
                            (df['y'] - pos[1]) ** 2 +
                            (df['z'] - pos[2]) ** 2)

        closest_idx = distances.idxmin()
        min_dist = distances.min()

        result = {"name": df.loc[closest_idx].key,
                  "distance": min_dist,
                  "inMailbox": self.inMailbox(pos=pos),
                  "position": pos}

        # Deep in the mailbox and far from every node: the tree can't localize us.
        if min_dist > 24 and result["inMailbox"]:
            result["name"] = "in_mailbox"
            result["distance"] = 1

        return result


    # ------------------------------------------------------------------ #
    # routed motion
    # ------------------------------------------------------------------ #
    def navigate(self, pointA, pointB, end_orient, maxSpeed=None, move=False, offset=None):
        maxSpeed = self._resolve(maxSpeed, "maxSpeed")
        offset = self._resolve(offset, "offset")

        start_orient = round(self.pitch, 1) if move else 0
        route = self.root.traverseWithOrientation(pointA, pointB, start_orient, end_orient)
        coords = gantree.routeToCoordinates(route)

        if not move:
            self._log(route)
            return route

        for i in range(len(coords)):
            if isinstance(route[i], gantree.MoveArm):
                curr_point = route[i].end
                if curr_point > 170 or (-10 < curr_point < 10) or curr_point < -170:
                    self.setAngles(curr_point, -curr_point)
                else:
                    self.setAngles(curr_point, self.roll)
                self._log(route[i])
                continue

            self.xyzMove(xpos=coords[i][0] + offset[0],
                         ypos=coords[i][1] + offset[1],
                         zpos=coords[i][2] + offset[2],
                         maxSpeed=maxSpeed, maxAccel=self.maxAccel, zSpeed=self.zSpeed)
        return route

    def goTo(self, destination, end_orient=0, maxSpeed=None,
             distance_threshold_mm=None, move=False, offset=None):
        distance_threshold_mm = self._resolve(distance_threshold_mm, "distanceThresholdMm")
        pos = self.position
        closest = self.checkClosest()
        if closest["name"] == "in_shelf":
            s1_row = self.lookupCoordinates("shelf_one")
            self.xyzMove(s1_row['x'],pos[1],pos[2])
            self.xyzMoveNamed(location="shelf_one",)
            closest = self.checkClosest()

        if closest["distance"] >= distance_threshold_mm:
            raise ValueError("gantry is lost. closest={}".format(closest))

        return self.navigate(closest["name"], destination, end_orient=end_orient,
                             maxSpeed=maxSpeed, move=move, offset=offset)

    def xyzMoveNamed(self, location, maxSpeed=None, maxAccel=None, zSpeed=None,
                     wait_until_idle=True, offset=None):
        """Straight line move to a named point. Collision danger, use with care."""
        offset = self._resolve(offset, "offset")
        row = self.lookupCoordinates(location)
        self.xyzMove(xpos=row['x'] + offset[0],
                     ypos=row['y'] + offset[1],
                     zpos=row['z'] + offset[2],
                     maxSpeed=maxSpeed, maxAccel=maxAccel, zSpeed=zSpeed,
                     wait_until_idle=wait_until_idle)

    # ------------------------------------------------------------------ #
    # pick up
    # ------------------------------------------------------------------ #
    def pickup(self, coordinates, backwards=None, clearance=5):
        backwards = self._resolve(backwards, "backwards")

        self.xyzMove(coordinates[0], coordinates[1], coordinates[2], 10, 50, 10)
        self.vacuum(True)
        time.sleep(self.vacuumSettle)

        delx = -2 if backwards else 2
        self.xyzMove(coordinates[0] + delx, coordinates[1] + delx,
                     coordinates[2] + clearance, 20, 25, 10)

    def pickupBlind(self, backwards=None, clearance=None, sampleLength=None):
        backwards = self._resolve(backwards, "backwards")
        clearance = self._resolve(clearance, "clearance")
        offset = self._sampleOffset(sampleLength, backwards)   # validates length

        c = self.position

        if offset != 0:
            self.xyzMove(c[0], c[1], c[2], 10, 50, 10)

        self.xyzMove(c[0], c[1], c[2] - clearance, 10, 50, 10)
        self.vacuum(True)
        time.sleep(self.vacuumSettle)

        delx = -2 if backwards else 2
        self.xyzMove(c[0] + delx, c[1], c[2], 20, 25, 10)

    def pickupBlindWiggle(self, backwards=None, clearance=None, sampleLength=None):
        backwards = self._resolve(backwards, "backwards")
        clearance = self._resolve(clearance, "clearance")
        offset = self._sampleOffset(sampleLength, backwards)

        c = self.position

        if offset != 0:
            self.xyzMove(c[0] - offset, c[1], c[2], 10, 50, 10)

        self.xyzMove(c[0] - offset, c[1], c[2] - clearance, 10, 50, 10)
        self.vacuum(True)
        time.sleep(self.vacuumSettle)

        delx = -2 if backwards else 2
        self.xyzMove(c[0] + delx, c[1] + delx, c[2], 20, 25, 10)

    def pickupNamed(self, location, backwards=None, clearance=None,
                    distance_threshold_mm=None, sampleLength=None):
        backwards = self._resolve(backwards, "backwards")
        self.goTo(destination=location, end_orient=self._orientationAngle(backwards),
                  distance_threshold_mm=distance_threshold_mm, move=True)
        self.pickupBlind(backwards=backwards, clearance=clearance, sampleLength=sampleLength)

    # ------------------------------------------------------------------ #
    # drop off
    # ------------------------------------------------------------------ #
    def dropoff(self, coordinates, backwards=None):
        backwards = self._resolve(backwards, "backwards")
        sign = -1 if backwards else 1

        self.xyzMove(coordinates[0] + 3 * sign, coordinates[1] + 3 * sign,
                     coordinates[2] + 25, 100, 70, 150)
        self.xyzMove(coordinates[0] + 2 * sign, coordinates[1] + 2 * sign,
                     coordinates[2] + 3, 50, 50, 50)
        self.xyzMove(coordinates[0], coordinates[1], coordinates[2], 10, 100, 10)
        self.vacuum(False)
        self.pvtDrop(backwards=backwards)

    def dropoffBlind(self, backwards=None, clearance=None, short=False, sampleLength=None,mailboxPitchException = False):
        backwards = self._resolve(backwards, "backwards")
        clearance = self._resolve(clearance, "clearance")
        self._sampleOffset(sampleLength, backwards)   # validates length

        c = self.position
        self.xyzMove(c[0], c[1], c[2], 100, 70, 150)
        self.xyzMove(c[0], c[1], c[2] - clearance + 2, 50, 50, 50)
        self.xyzMove(c[0], c[1], c[2] - clearance, 10, 100, 10)
        self.vacuum(False)
        self.pvtDrop(backwards=backwards, short=short,mailboxPitchException=mailboxPitchException)
        self.xyzMove(c[0], c[1], c[2], 10, 100, 10)

    def dropoffBlindWiggle(self, backwards=None, clearance=None, short=False, sampleLength=None):
        backwards = self._resolve(backwards, "backwards")
        clearance = self._resolve(clearance, "clearance")
        offset = self._sampleOffset(sampleLength, backwards)
        sign = -1 if backwards else 1

        c = self.position
        self.xyzMove(c[0] + 3 * sign - offset, c[1] + 3 * sign, c[2], 100, 70, 150)
        self.xyzMove(c[0] + 2 * sign - offset, c[1] + 2 * sign, c[2] - clearance + 2, 50, 50, 50)
        self.xyzMove(c[0] - offset, c[1], c[2] - clearance, 10, 100, 10)
        self.vacuum(False)
        self.pvtDrop(backwards=backwards, short=short)
        self.xyzMove(c[0], c[1], c[2], 10, 100, 10)

    def dropoffNamed(self, location, backwards=None, clearance=None, maxSpeed=None,
                     distance_threshold_mm=None, short=False, sampleLength=None):
        backwards = self._resolve(backwards, "backwards")
        self.goTo(destination=location, end_orient=self._orientationAngle(backwards),
                  maxSpeed=maxSpeed, distance_threshold_mm=distance_threshold_mm)


    def mailboxGoTo(self, index_y, index_z, spacing=None,mailboxAngleIncrement=None, backwards=None,
                    approachSpeed=200, approachAccel=100):
        """
        Move to a mailbox slot. Zero indexed in both axes.
        Recommended use with pickupBlind / dropoffBlind.

        Reference: mailbox_las = [1471, 624.5, 19]
        spacing = (624.5 - 236.25) / 6 = 64.7
        """
        spacing = self._resolve(spacing, "mailboxSpacing")
        backwards = self._resolve(backwards, "backwards")
        mailboxAngleIncrement = self._resolve(mailboxAngleIncrement, "mailboxAngleIncrement")

        if index_y >= self.mailboxColumns:
            raise IndexError("mailbox y index too high: {} (max {})"
                             .format(index_y, self.mailboxColumns - 1))
        if index_z >= self.mailboxRows:
            raise IndexError("mailbox z index too high: {} (max {})"
                             .format(index_z, self.mailboxRows - 1))

        s1_row = self.lookupCoordinates("mailbox_back")
        ypos = s1_row['y'] + spacing * index_y
        zpos = s1_row['z'] + spacing * index_z + index_z*abs(150*math.sin(math.radians(mailboxAngleIncrement)))
        # account for mailbox angle

        closest = self.checkClosest()

        if closest["inMailbox"]:
            # Already lined up with the mailbox face, slide straight to the slot.
            self._log("in mailbox ({} @ {:.1f} mm)".format(closest["name"], closest["distance"]))
            self.xyzMove(s1_row['x'], ypos, zpos,
                         maxSpeed=approachSpeed, maxAccel=approachAccel,
                         zSpeed=25, wait_until_idle=True)
        else:
            self._log("out of mailbox ({} @ {:.1f} mm)".format(closest["name"], closest["distance"]))
            self.goTo(destination="mailbox_back",
                      end_orient=self._orientationAngle(backwards),
                      maxSpeed=self.maxSpeed, move=True)
            self.xyzMove(s1_row['x'], ypos, zpos,
                         maxSpeed=approachSpeed, maxAccel=approachAccel,
                         zSpeed=100, wait_until_idle=True)

    #     adjust angle
        if index_z > 0:
            axPitch = self.axPitch
            axPitch.move_absolute(position = index_z*mailboxAngleIncrement, unit= Units.ANGLE_DEGREES,
                         velocity= 13,velocity_unit= Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
                         wait_until_idle=False)

    def linearIndexToCoords(linIndex, columns=7, rows=3):
        ypos = linIndex % 7

        zpos = linIndex // 7
        return {
            "ypos": ypos,
            "zpos": zpos
        }

    def mailboxDrop(self,index=None,index_y = None,index_z = None,clearance=10):
        if all([index is None,index_y is None,index_z is None]):
            raise IndexError("supply either linear index or yz coords")
        if index is not None:
            vals = linearIndexToCoords(index)
        else:
            vals = [index_y, index_z]
        self.mailboxGoTo(index_y=vals['ypos'],index_z=vals['zpos'])
        self.xyzMoveRelative(xDist=-100)
        self.dropoffBlind(backwards=False, short=True,clearance=clearance,mailboxPitchException=True)
        self.axPitch.move_absolute(self.mailboxAngleIncrement * vals['zpos'])
        self.xyzMoveRelative(xDist=100)

    def mailboxPickup(self,index=None,index_y = None,index_z = None,clearance=10):
        if all([index is None,index_y is None,index_z is None]):
            raise IndexError("supply either linear index or yz coords")
        if index is not None:
            vals = linearIndexToCoords(index)
        else:
            vals = [index_y, index_z]
        self.mailboxGoTo(index_y=vals['ypos'],index_z=vals['zpos'])
        self.xyzMoveRelative(xDist=-100)
        self.pickupBlind(backwards=False,clearance=clearance)
        self.axPitch.move_absolute(self.mailboxAngleIncrement * vals['zpos'])
        self.xyzMoveRelative(xDist=100)

    #
    # def mailboxGoTo(self, index_y, index_z, spacing=None, backwards=None,
    #                 approachSpeed=200, approachAccel=100):
    #     """
    #     Move to a mailbox slot. Zero indexed in both axes.
    #     Recommended use with pickupBlind / dropoffBlind.
    #
    #     Reference: mailbox_las = [1471, 624.5, 19]
    #     spacing = (624.5 - 236.25) / 6 = 64.7
    #     """
    #     spacing = self._resolve(spacing, "mailboxSpacing")
    #     backwards = self._resolve(backwards, "backwards")
    #
    #     if index_y >= self.mailboxColumns:
    #         raise IndexError("mailbox y index too high: {} (max {})"
    #                          .format(index_y, self.mailboxColumns - 1))
    #     if index_z >= self.mailboxRows:
    #         raise IndexError("mailbox z index too high: {} (max {})"
    #                          .format(index_z, self.mailboxRows - 1))
    #
    #     pos = self.position
    #     s1_row = self.lookupCoordinates("mailbox_back")
    #     ypos = s1_row['y'] + spacing * index_y
    #     zpos = s1_row['z'] + spacing * index_z
    #
    #     # If the tool is already lined up with the mailbox in x and z we can
    #     # slide straight to the slot. y is loose because that is the long
    #     # travel along the face of the mailbox.
    #     in_shelf = all([
    #         abs(pos[0] - s1_row['x']) < 5,
    #         abs(pos[1] - s1_row['y']) < 626,
    #         abs(pos[2] - s1_row['z']) < 5,
    #     ])
    #
    #     if in_shelf:
    #         self._log("in shelf")
    #         self.xyzMove(s1_row['x'], ypos, zpos,
    #                      maxSpeed=approachSpeed, maxAccel=approachAccel,
    #                      zSpeed=25, wait_until_idle=True)
    #     else:
    #         self._log("out shelf")
    #         self.goTo(destination="mailbox_up",
    #                   end_orient=self._orientationAngle(backwards),
    #                   maxSpeed=self.maxSpeed, move=True)
    #         self.xyzMove(s1_row['x'], ypos, zpos,
    #                      maxSpeed=approachSpeed, maxAccel=approachAccel,
    #                      zSpeed=100, wait_until_idle=True)