class surface:
    def __init__(self,name,x,y, params = None, substrate_name = "None"):
        self.name = name
        self.x = x
        self.y = y
        self.params = params #dictionary of parameters
        self.substrate_name = substrate_name

    def __str__(self):
        return f"{self.name} {self.x} {self.y}"


class substrate:
    def __init__(self,name = "Empty",material= None,dim=0,params = None):
        self.name = name
        self.material = material
        self.params = params #dictionary for extra parameters such as batch numbers
        self.dim = dim
        self.sample_grid = []

    def fill(self,substrateName , dim):
        self.dim = dim
        self.name = substrateName
        self.surface_grid = [[surface(name = f"{substrateName}",x=col,y=row) for row in range(dim)] for col in range(dim)]
        return

    def add_surface(self,surface):

    def __str__(self):
        return f"Substrate: {self.name} Surfaces: {[[str(self.surface_grid[col][row]) for row in range(self.dim)] for col in range(self.dim)]}"

if __name__ == "__main__":
    sbstr = substrate()
    sbstr.fill_with_samples("sample1", 3)
    print(sbstr)