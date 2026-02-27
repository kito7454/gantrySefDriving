import numpy as np
class ShelfHelper():

    # -----------------
    # inputs:
    # position:gantry [x y z] coordinates in millimeters of the first sample pickup (closest towards edge of table)
    # spacing: distance between samples in mm (y axis)
    # status: vector that represents which slots have a sample in them: ie [1,1,0,0,1]
    def __init__(self,position,spacing,status,backwards = False):
        self.position = position
        self.spacing = spacing
        self.status = status

        # creates an array with all different y positions (it is expected x & z constant)
        if backwards:
            self.ys = [self.position[1]-x for x in [self.spacing * j for j in range(len(self.status))]]
        else:
            self.ys = [x + self.position[1] for x in [self.spacing*j for j in range(len(self.status))]]

    # returns the coordinates of specified position i, zero indexed
    def getPosInt(self,i):
        return [self.position[0] ,self.ys[i], self.position[2]]

# sh = ShelfHelper([1,2,1],2,[0,0,0,0])

