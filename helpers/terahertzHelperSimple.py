import time

from helpers.gantryHelperSimple import GantryHelperSimple


class TerahertzHelper:
    """
    Load / unload routines for the terahertz stage.

    Wraps a GantryHelperSimple so the same gantry instance can be shared
    with the mailbox and bath routines.
    """

    FULL_SAMPLE_LENGTH_MM = 76.2
    MIN_SAMPLE_LENGTH_MM = 48.0
    MAX_SAMPLE_LENGTH_MM = 77.0

    def __init__(self, gantry,
                 sampleLength=FULL_SAMPLE_LENGTH_MM,
                 sampleLengthFlipped=50.8,
                 pitchAngle=-90,
                 distanceThresholdMm=250,
                 pickSpeed=25,
                 pickAccel=50,
                 nudgeSpeed=10,
                 nudgeAccel=100,
                 nudgeZSpeed=10,
                 vacuumGrabTime=4.0,
                 vacuumReleaseTime=0.5):
        self.gantry = gantry
        self.sampleLength = sampleLength
        self.sampleLengthFlipped = sampleLengthFlipped
        self.pitchAngle = pitchAngle
        self.distanceThresholdMm = distanceThresholdMm
        self.pickSpeed = pickSpeed
        self.pickAccel = pickAccel
        self.nudgeSpeed = nudgeSpeed
        self.nudgeAccel = nudgeAccel
        self.nudgeZSpeed = nudgeZSpeed
        self.vacuumGrabTime = vacuumGrabTime
        self.vacuumReleaseTime = vacuumReleaseTime

    def _zOffset(self, sampleLength):
        """Correction for samples that aren't a full 3 in."""
        if sampleLength < self.MIN_SAMPLE_LENGTH_MM or sampleLength > self.MAX_SAMPLE_LENGTH_MM:
            raise ValueError("Sample length incompatible: {}".format(sampleLength))
        return self.FULL_SAMPLE_LENGTH_MM - sampleLength

    # ------------------------------------------------------------------ #

    def terahertzDropoff(self, sampleLength=None):
        g = self.gantry
        sampleLength = self.sampleLength if sampleLength is None else sampleLength
        offset = self._zOffset(sampleLength)

        g.goTo(destination="terahertz", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm)
        g.setAngles(self.pitchAngle, 0)

        if offset != 0:  # special case if sample isn't 3 in long
            c = g.position
            g.xyzMove(c[0], c[1], c[2] - offset,
                      self.nudgeSpeed, self.nudgeAccel, self.nudgeZSpeed,
                      wait_until_idle=True)

        g.vacuum(False)
        time.sleep(self.vacuumReleaseTime)

        g.goTo(destination="thz_lift", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm, offset=[0, 0, -offset])
        g.xyzMoveNamed("thz_3")

    # ------------------------------------------------------------------ #

    def terahertzDropoffFlipped(self, sampleLength=None):
        g = self.gantry
        sampleLength = self.sampleLengthFlipped if sampleLength is None else sampleLength
        offset = self._zOffset(sampleLength)

        g.goTo(destination="thz_1", end_orient=0, move=True,
               distance_threshold_mm=self.distanceThresholdMm)
        g.setAngles(self.pitchAngle, 180)
        g.goTo(destination="terahertz_f", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm)

        if offset != 0:  # special case if sample isn't 3 in long
            c = g.position
            g.xyzMove(c[0], c[1], c[2] - offset,
                      self.nudgeSpeed, self.nudgeAccel, self.nudgeZSpeed,
                      wait_until_idle=True)

        g.vacuum(False)
        time.sleep(self.vacuumReleaseTime)

        g.goTo(destination="thz_lift_f", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm, offset=[0, 0, -offset])
        g.xyzMoveRelative(zDist=25)
        g.xyzMoveNamed("thz_2_f")
        g.goTo(destination="thz_1", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm, offset=[0, 0, -offset])

    # ------------------------------------------------------------------ #

    def terahertzPickup(self, sampleLength=None):
        g = self.gantry
        sampleLength = self.sampleLength if sampleLength is None else sampleLength
        offset = self._zOffset(sampleLength)

        g.goTo(destination="thz_3", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm)
        g.setAngles(self.pitchAngle, 0)

        g.xyzMoveNamed("thz_lift", offset=[0, 0, -offset])
        g.xyzMoveNamed("thz_pick", offset=[0, 0, -offset],
                       maxAccel=self.pickAccel, maxSpeed=self.pickSpeed,
                       wait_until_idle=True)

        g.vacuum(True)
        time.sleep(self.vacuumGrabTime)

        # g.xyzMoveNamed("terahertz", offset=[0, 0, -offset])
        g.xyzMoveNamed("thz_4")
        g.goTo(destination="thz_1", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm)

    # ------------------------------------------------------------------ #

    def terahertzPickupFlipped(self, sampleLength=None):
        g = self.gantry
        sampleLength = self.sampleLength if sampleLength is None else sampleLength
        offset = self._zOffset(sampleLength)

        g.goTo(destination="thz_3_f", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm)
        g.setAngles(self.pitchAngle, 180)

        g.xyzMoveNamed("thz_lift_f", offset=[0, 0, -offset])
        g.xyzMoveNamed("thz_pick_f", offset=[0, 0, -offset],
                       maxAccel=self.pickAccel, maxSpeed=self.pickSpeed,
                       wait_until_idle=True)

        g.vacuum(True)
        time.sleep(self.vacuumGrabTime)

        # g.xyzMoveNamed("terahertz_f", offset=[0, 0, -offset])
        g.xyzMoveNamed("thz_4_f")
        g.goTo(destination="thz_1", end_orient=self.pitchAngle, move=True,
               distance_threshold_mm=self.distanceThresholdMm)


if __name__ == "__main__":
    from zaber_motion.ascii import Connection

    with Connection.open_serial_port('COM6') as connection:
        gantry = GantryHelperSimple(connection, root=None)
        thz = TerahertzHelper(gantry)
        thz.terahertzPickup()