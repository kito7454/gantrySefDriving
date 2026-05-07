import numpy as np
from scipy.constants import fine_structure


class surface:
    def __init__(self,x = None,y = None,name = "Surface", params = None, substrate_name = "None"):
        self.name = name
        self.x = x #col
        self.y = y #row
        self.params = params #dictionary of parameters
        self.substrate_name = substrate_name

    def __str__(self):
        return f"{self.name} {self.x} {self.y}"


class substrate:
    def __init__(self,name = "Substrate",material= None,dim=0,params = None):
        self.name = name
        self.material = material
        self.params = params #dictionary for extra parameters such as batch numbers
        self.dim = dim
        self.num_available = dim**2 - 1
        self.sample_grid = []

    def fill(self,substrateName , dim):
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
            return np.unravel_index(first_slot, shape=(self.dim, self.dim))


    # possible useful inverse:
    # np.ravel_multi_index((row, col), (self.dim,self.dim))

    # def get_open_slots(self):


    def __str__(self):
        return f"Substrate: {self.name} Surfaces: {[[str(self.surface_grid[col][row]) for row in range(self.dim)] for col in range(self.dim)]}"


if __name__ == "__main__":
    sbstr = substrate()
    sbstr.fill_with_samples("sample1", 3)
    print(sbstr)