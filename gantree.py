import math
import numpy as np
import pandas as pd
import json

import buildGantree

class GanTree():
    def __init__(self, name='root', x=0.0, y=0.0, z=0.0, theta=None, parent=None):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.parent = parent
        self.children = []
        self.theta = theta if theta is not None else [1, 1, 0]
    
    def __repr__(self):
        return f"{self.name} @ ({self.x}, {self.y}, {self.z}, {self.theta})"

    def add_child(self, child_name, child_x, child_y, child_z, theta):
        child = GanTree(name=child_name, x=child_x, y=child_y, z=child_z, theta=theta, parent=self)
        self.children.append(child)
        return child

    def is_leaf(self):
        return True if len(self.children) == 0 else False

    def is_root(self):
        return True if self.parent is None else False

    def dist_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

    def to_root(self, path=None):
        """
        Finds path from state to root
        """
        if path is None:
            path = []
        path.append(self)
        if self.parent is not None:
            self.parent.to_root(path)
        return path

    def traverse(self, a, b):
        """
        Finds a path of connected points from a to b.

        Params:
            a - start state
            b - end state

        Return:
            path - list of state names to traverse in order
        """
        path_a = a.to_root()
        path_b = b.to_root()

        ca = None

        for s in path_a:
            if s in path_b:
                ca = s  # common ancestor
                break

        if ca == None:
            raise Exception("disconnected tree")

        return path_a[:path_a.index(ca) + 1] + list(reversed(path_b[:path_b.index(ca)]))

    def traverseFromName(self,name_A,name_B):
        return self.traverse(find(self, name=name_A), find(self, name=name_B))

    def traverseWithOrientation(self, name_A, name_B, start_orientation, end_orientation):
        start_node = find(self, name_A)
        end_node = find(self, name_B)

        if start_orientation >= len(start_node.theta) or not start_node.theta[start_orientation]:
            raise ValueError(f"Start orientation {start_orientation} is not safe at {name_A}")

        path_nodes = self.traverse(start_node, end_node)
        
        final_path = [start_node.name]
        current_orientation = start_orientation

        for i in range(len(path_nodes) - 1):
            current_node = path_nodes[i]
            next_node = path_nodes[i+1]

            if current_orientation < len(next_node.theta) and next_node.theta[current_orientation]:
                final_path.append(next_node.name)
                continue

            other_orientation = 1 - current_orientation

            if current_node.theta[2] and other_orientation < len(next_node.theta) and next_node.theta[other_orientation]:
                final_path.append("flip around")
                final_path.append(next_node.name)
                current_orientation = other_orientation
                continue

            if next_node.theta[2] and other_orientation < len(next_node.theta) and next_node.theta[other_orientation]:
                final_path.append(next_node.name)
                final_path.append("flip around")
                current_orientation = other_orientation
                continue

        end_node_final = find(self, final_path[-1] if final_path[-1] != "flip around" else final_path[-2])
        if current_orientation < len(end_node_final.theta) and not end_node_final.theta[current_orientation]:
            if end_node_final.theta[2]:
                final_path.append("flip around")
                current_orientation = 1 - current_orientation
            else:
                raise Exception(f"Cannot get to {name_B}")
        
        return final_path

def parse_theta(theta_str):
    """
    Parse theta string like '[1,0,1]' into array [theta0, theta1, canflip]
    """
    if isinstance(theta_str, str):
        try:
            theta_list = json.loads(theta_str.replace("'", '"'))
            return [int(theta_list[0]), int(theta_list[1]), int(theta_list[2])]
        except (json.JSONDecodeError, AttributeError, IndexError):
            return [1, 1, 0]
    return [1, 1, 0]

def fill(gantree, treefile):
    """
    Build Tree from treefile
    """
    with open(treefile, "r") as f:
        lines = [line.strip().split() for line in f]

    remaining = lines.copy()
    while remaining:
        next_round = []
        for params in remaining:
            name, x, y, z, theta, parent = params
            p = find(gantree, parent)
            if p is not None:
                theta_array = parse_theta(theta)
                p.add_child(name, float(x), float(y), float(z), theta_array)
            else:
                next_round.append(params)
        if len(next_round) == len(remaining):
            # No progress made; break to avoid infinite loop
            print("Warning: could not find parents for:", [p[5] for p in remaining])
            break
        remaining = next_round

def store(gantree, outfile):
    """
    Stores current tree in outfile
    """
    with open(outfile, "a") as f:
        f.write(f"{gantree.name} {gantree.x} {gantree.y} {gantree.z} {gantree.theta} {gantree.parent}\n")
    for i in gantree.children:
        store(i, outfile)

    return


def find(root, name):
    """
    Find actual state in tree from root
    """
    if root.name == name:
        return root

    for s in root.children:
        result = find(s, name)
        if result is not None:
            return result
    return None


def where(root, posx, posy, posz, treefile):
    """
    Find nearest state to current position
    """
    all_states = []
    with open(treefile, "r") as f:
        for line in f:
            params = line.split()
            # create disconnected gantrees
            all_states.append(GanTree(params[0], params[1], params[2], params[3]))

    loc = GanTree('temp', posx, posy, posz)
    min_dist = float('inf')
    for s in all_states:
        d = loc.dist_to(s)
        if d < min_dist:
            nearest = s
            min_dist = d

    return find(root, nearest.name)


def tableLookup(key):
    df = pd.read_csv(r"curr_gantry.csv")
    row = df[df["key"] == key]
    return row

import numpy as np

def routeToCoordinates(route):
    # converts a list of the string names of the points to a list of coordinates by looking up csv
    route_points = [p for p in route if p != "flip around"]
    n = len(route_points)

    if n == 0:
        return np.empty((0, 4), dtype=np.float64)

    coords = np.empty((n, 4), dtype=np.float64)

    for i, key in enumerate(route_points):
        print(key)
        row = tableLookup(str(key.name))

        coords[i, 0] = float(row["x"].iloc[0])
        coords[i, 1] = float(row["y"].iloc[0])
        coords[i, 2] = float(row["z"].iloc[0])
        
        theta_val = row["theta"].iloc[0]
        if isinstance(theta_val, str):
            coords[i, 3] = 0.0
        else:
            coords[i, 3] = float(theta_val)

    return coords

class MotionTable():
    def __init__(self):
        self.connections = {}

    def fill(self, motionfile):
        with open(motionfile, "r") as f:
            for line in f:  # should look like: start end command
                params = line.split()
                self.connections[(params[0], params[1])] = params[2]

        return

    def path2motion(self, path):
        """
        Takes in a string of nodes to path through and applies each transition by looking up from motion table
        """
        commands = []
        for i in range(len(path) - 1):
            try:
                commands.append(self.connections[(path[i], path[i + 1])])
            except KeyError:
                print(f"Invalid path segment: {path[i]} to {path[i + 1]}")
                return None
        return commands

if __name__ == "__main__":
    rt = buildGantree.build()
    route = rt.traverseWithOrientation("Write", "Storage", 0, 0)
    print(route)
    print(routeToCoordinates(route))
