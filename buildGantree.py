import pandas as pd
import numpy as np
import gantree as gt
from helpers.gantryHelperAdvanced import navigate, xyzMove, goTo
from zaber_motion import Units
from zaber_motion.ascii import Connection, pvt
import helpers.gantryHelperAdvanced as gh

def buildGantree(file):
    df = pd.read_csv(file)
    root = gt.GanTree()

    for i in range(len(df)):
        row = df.iloc[i]
        if not np.isnan(row.x):
            # gets pointer to the parent the table specifes
            # must define parenst before children
            # print(row)
            parent = gt.find(root,str(row.parent))
            # print(parent, root)
            theta = gt.parse_theta(row.theta)
            parent.add_child(child_name=row.key,child_x = row.x,child_y=row.y,child_z = row.z,theta=theta)
            # print(parent.name)

    return root

if __name__ == "__main__":
    with Connection.open_serial_port('COM6') as connection:
    # with spcHelper.SPCHelper() as client:
        #
        # gantryHelper.setPiPos(client,preset="stage1gantry")
        # gantryHelper.setPiPos(client, preset="stage2gantry")

        device_list = connection.detect_devices()
        # print(device_list)
        gantry = device_list[1]
        # target the first rotation stage
        angle1 = device_list[2]
        angle2 = device_list[3]

        rt = buildGantree(r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv")


        # goTo(connection, rt, "test_point4", 0, move=True)
        goTo(connection, rt, "shelf_one", 0, move=True)
        goTo(connection, rt, "midpoint", 0, move=True,distance_threshold_mm=500)
        goTo(connection, rt, "bath_up", 0, move=True)
        goTo(connection, rt, "bath_in", -90, move=True)

    # print(route)