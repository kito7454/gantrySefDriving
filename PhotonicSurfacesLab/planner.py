import PhotonicSurfacesLab.objects as objects

class Planner:
    def __init__(self, num = 7):
        self.shelf_slots = []
        for i in range(num):
            # Create the object and append it to the list # by default will just name substrates
            new_object = objects.substrate()
            self.shelf_slots.append(new_object)

        self.total_count = 0


    def add_substrate(self,substrate,slot_index):
        #fills shelf with null substrates that have no info
        self.shelf_slots[slot_index] = substrate
        return self

    def __str__(self):
        return f"Planner Substrates: {[obj.name for obj in self.shelf_slots]})"

if __name__ == "__main__":
    p = Planner()
    s1= objects.substrate()
    s1.fill_with_samples(substrateName="substrate_1", dim = 4)
    p.add_substrate(substrate=s1,slot_index=0)

    print(p)
    print(p.shelf_slots[0].surface_grid[0][1])
    print(s1)