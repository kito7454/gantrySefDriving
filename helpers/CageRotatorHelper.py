"""
Example Title: K10CR1_pythonnet.py
Example Date of Creation(YYYY-MM-DD) 2023-02-23
Example Date of Last Modification on Github 2025-04-09
Version of Python: 3.11
Version of the Thorlabs SDK used: 1.14.52
==================
Example Description
Using the .NET Dlls
Example runs the K10CR1 or K10CR2 stage. It shows how to initialize, home and move.
Tested with K10CR2
"""
import clr
import time
import pandas as pd

# Write in file paths of dlls needed.
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")

# Import functions from dlls.
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal
#
class RotatorHelper:
    def __init__(self):
        self.device = None
        self.calibrationFile = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\RotationCalibrationCurve.xlsx"
        self.table = pd.read_excel(self.calibrationFile)

    def connect(self,serial_no = "55536584"):
        try:
            # Build device list.
            DeviceManagerCLI.BuildDeviceList()

            # Connect to device.
            self.device = CageRotator.CreateCageRotator(serial_no)
            self.device.Connect(serial_no)

            # Ensure that the device settings have been initialized.
            # if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert self.device.IsSettingsInitialized() is True

            # Start polling loop and enable device.
            self.device.StartPolling(250)  # 250ms polling rate.
            time.sleep(0.5)
            self.device.EnableDevice()
            time.sleep(0.5)  # Wait for device to enable.
            # Get Device Information and display description.
            device_info = self.device.GetDeviceInfo()
            print(device_info.Description)
            motor_config = self.device.LoadMotorConfiguration(serial_no,
                                    DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        except Exception as e:
            print(e)

    def home(self):
        if self.device is None:
            self.connect()
        print("Homing Device")
        self.device.Home(60000)  # 60 second timeout.
        print("Done")

    def moveTo(self,Angle):
        self.device.MoveTo(Decimal(Angle), 60000)

    def setPower(self,DesiredPower):
#         interpolate power from calibration curve
        if DesiredPower < self.table.Power[1]:
            print("Desired Power Too Low")
            return
        if DesiredPower > max(self.table.Power):
            print("Desired Power Too High")
            return
        i=0
        while self.table.Power[i] < DesiredPower:
            i=i+1
        PHigh = self.table.Power[i]
        PLow = self.table.Power[i-1]
        AngleHigh = self.table.Angle[i]
        AngleLow = self.table.Angle[i-1]
        interpolatedAngle = ((DesiredPower - PLow)/(PHigh-PLow)) * (AngleHigh-AngleLow) + AngleLow
        print(f"Angle: {interpolatedAngle} Power: {DesiredPower}")
        self.device.MoveTo(Decimal(interpolatedAngle), 60000)

        return interpolatedAngle

    def close(self):
        # Stop polling loop and disconnect device before program finishes.
        self.device.StopPolling()
        self.device.Disconnect()



def main():
    helper = RotatorHelper()
    helper.connect()

    helper.setPower(2)
    helper.close()


if __name__ == "__main__":
    main()
