from zaber_motion import Units
from zaber_motion.ascii import Connection
import time

def connect(connection):
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))
    # target the xyz gantry
    deviceX = device_list[1]

    # target the first rotation stage
    deviceY = device_list[2]

def meet_Gantry(connection):
    device_list = connection.detect_devices()
    deviceX = device_list[0]
    deviceY = device_list[1]

    aX=deviceX.get_axis(1)
    aY = deviceY.get_axis(1)

    aX.move_absolute(0, Units.LENGTH_MILLIMETRES,wait_until_idle=True)
    aY.move_absolute(0, Units.LENGTH_MILLIMETRES, wait_until_idle=True)


def measure_THZ(connection):
    device_list = connection.detect_devices()
    deviceX = device_list[0]
    deviceY = device_list[1]

    aX = deviceX.get_axis(1)
    aY = deviceY.get_axis(1)

    aX.move_absolute(75, Units.LENGTH_MILLIMETRES, False)
    aY.move_absolute(30, Units.LENGTH_MILLIMETRES, False)



if __name__ == "__main__":
    with Connection.open_serial_port('COM7') as connection:
        meet_Gantry(connection)
        # time.sleep(1)
        # measure_THZ(connection)
