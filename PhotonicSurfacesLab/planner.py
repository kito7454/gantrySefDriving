import numpy as np

import PhotonicSurfacesLab.objects as objects

class Planner:
    def __init__(self, num = 7):
        self.substrates = []
        self.total_count = 0
        self.batch_size = 8
        self.global_dim = 4

        for i in range(num):
            # Create the object and append it to the list # by default will just name substrates
            new_object = objects.substrate()
            new_object.fill(substrateName= f"Substrate {str(i)}",dim=self.global_dim)
            self.substrates.append(new_object)


    def add_substrate(self,substrate,slot_index):
        #fills shelf with null substrates that have no info
        self.substrates[slot_index] = substrate
        return self

    def __str__(self):
        return f"Planner Substrates: {[obj.name for obj in self.substrates]})"

    def find_open_substrate(self,required_slots = None):
        if required_slots == None:
            required_slots = self.batch_size
        target_substrate = None
        target_index = 0
        for i in range(len(self.substrates)):
            sub = self.substrates[i]
            available = sub.get_next_available(linear=True)
            if available is not None:
                if available + required_slots < sub.dim ** 2:
                    target_substrate = sub
                    target_index = i
                    break
        if target_substrate is None:
            return None
        return {"substrate": target_substrate,
                "slot_index": target_index}


    def new_batch(self):
        # find available substrate

        for i in range(self.total_count,self.total_count+self.batch_size):
            surf = objects.surface



if __name__ == "__main__":
    p = Planner()
    su = objects.surface(name="substrate_1",x = 0,y=0,params={"batch":0,"batch_index":0})
    # s1.add_surface(su)
    for i in range(5):
        s = objects.surface()
        p.substrates[0].add_surface(s)
    # p.add_substrate(substrate=,slot_index=0)

    # print(p)
    print(p.substrates[0])
    results = p.find_open_substrate()
    print(results["substrate"])
    # print(p.shelf_slots[0].surface_grid != None)
    # print(s1)