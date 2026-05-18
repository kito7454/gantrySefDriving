from logging import exception

import numpy as np
from reactivex import throw
from scipy.constants import fine_structure


class surface:
    def __init__(self,x = None,y = None,name = "Surface", params = None, substrate_name = "None"):
        self.name = name
        self.x = x #col
        self.y = y #row
        self.params = params #dictionary of parameters
        self.substrate_name = substrate_name

    def __str__(self):
        return f"{self.name} X:{self.x} Y:{self.y}"


class substrate:
    def __init__(self,name = "Substrate",material= None,dim=0,params = None):
        self.name = name
        self.material = material
        self.params = params #dictionary for extra parameters such as batch numbers
        self.dim = dim
        self.num_available = dim**2 - 1
        self.sample_grid = []
        self.surface_grid = []
    #     by default substrates are empty and have nothing

    def fill(self,substrateName , dim):
        # fills substrate with empty surfaces in the specified dimension
        # separate from init because nxn dimension not necessarily specified at object creation
        self.dim = dim
        self.name = substrateName
        self.surface_grid = np.full((dim, dim), None, dtype=object)
        return

    def add_surface(self,surface):
        surface.substrate_name = self.name
        if surface.y is None:
            [row,col] = self.get_next_available()
            surface.y= row
            surface.x = col
        self.surface_grid[surface.y,surface.x] = surface

    def get_next_available(self,linear = False):
        # returns first availble position in [row, col] format
        # assert linear to provide linear index instead
        num_full = np.count_nonzero(self.surface_grid != None)
        first_slot= num_full #linear index
        if first_slot > self.dim**2 - 1:
            return None
        else:
            if linear:
                return first_slot
            return np.unravel_index(first_slot, shape=(self.dim, self.dim)) #linear to 2d)


    # possible useful inverse:
    # np.ravel_multi_index((row, col), (self.dim,self.dim))

    # def get_open_slots(self):


    def __str__(self):
        return f"Substrate: {self.name} Dim:{str(self.dim)}x{str(self.dim)} Surfaces: {[[str(self.surface_grid[col][row]) for row in range(self.dim)] for col in range(self.dim)]}"


if __name__ == "__main__":
    sbstr = substrate()
    sbstr.fill("sample1", 3)
    print(sbstr)