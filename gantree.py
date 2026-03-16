import math
import numpy as np
import pandas as pd
import json

import buildGantree

defaultTree = r"C:\Users\v_zor\PycharmProjects\KyleHardcode\curr_gantry.csv"


class GanTree():
    def __init__(self, name='root', x=0.0, y=0.0, z=0.0, theta=None, parent=None):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.parent = parent
        self.children = []
        self.theta = theta if theta is not None else [0, 0]

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

    def traverseFromName(self, name_A, name_B):
        return self.traverse(find(self, name=name_A), find(self, name=name_B))

    def traverseWithOrientation(self, name_A, name_B, start_orient, end_orient):
        path = self.traverse(find(self, name_A), find(self, name_B))
        final, curr = [path[0]], start_orient

        valid = lambda n, a: any(x[0] <= a <= x[1] if isinstance(x, list) else x == a for x in n.theta)
        intersect = lambda ivs1, ivs2: [(max(a, c), min(b, d)) for a, b in ivs1 for c, d in ivs2 if
                                        max(a, c) <= min(b, d)]
        node_intervals = lambda node: [(x, x) if isinstance(x, int) else (x[0], x[1]) for x in node.theta]

        # backprop to find where we can rotate
        def find_rotation_point(target_node):
            target_i = path.index(target_node)
            for j in range(target_i - 1, -1, -1):
                rot_node = path[j]
                # rotation point must have a continuous range covering curr
                rot_ivs = [(lo, hi) for lo, hi in node_intervals(rot_node) if lo < hi and lo <= curr <= hi]
                if not rot_ivs:
                    continue
                # intersect that with every intermediate node up to and including target
                ivs = rot_ivs
                for k in range(j + 1, target_i + 1):
                    ivs = intersect(ivs, node_intervals(path[k]))
                    if not ivs:
                        break
                if not ivs:
                    continue
                lo, hi = ivs[0]
                new_orient = (lo + hi) // 2
                insert_pos = next(
                    (idx for idx, item in enumerate(final) if isinstance(item, GanTree) and item is rot_node), None)
                if insert_pos is not None:
                    return insert_pos, new_orient
            return None, None

        for i in range(1, len(path)):
            node = path[i]
            if valid(node, curr):
                final.append(node)
                continue

            insert_pos, new_orient = find_rotation_point(node)
            if insert_pos is None:
                raise ValueError(f"Impossible to reach {node.name}: no continuous rotation path exists")

            final.insert(insert_pos + 1, MoveArm(curr, new_orient))
            curr = new_orient
            final.append(node)

        if end_orient is not None and curr != end_orient:
            if valid(path[-1], end_orient):
                # try to rotate at the final node itself
                can_move_here = any(
                    isinstance(x, list) and x[0] <= curr <= x[1] and x[0] <= end_orient <= x[1]
                    for x in path[-1].theta
                )
                if can_move_here:
                    final.append(MoveArm(curr, end_orient))
                else:
                    # need to rotate earlier and arrive at end_orient
                    insert_pos, _ = find_rotation_point(path[-1])
                    if insert_pos is None:
                        raise ValueError(f"Cannot reach end orientation {end_orient}")
                    final.insert(insert_pos + 1, MoveArm(curr, end_orient))
            else:
                raise ValueError(f"End node does not support orientation {end_orient}")

        return final


def parse_theta(theta_str):
    """
        Parse theta string with interval notation for arbitrary number of angles.
        Supports:
        - Discrete: [45, 90, 180] = exactly 45, 90, 180
        - Ranges: [[0,90], [45,180]] = angle0: 0-90, angle1: 45-180
        - Mixed: [45, [0,180], 90] = exactly 45, angle0: 0-180, exactly 90

        Returns list where each element is either:
        - int: discrete angle value
        - list: [min, max] range
    """
    if isinstance(theta_str, str):
        try:
            theta_list = json.loads(theta_str.replace("'", '"'))
        except (json.JSONDecodeError, AttributeError):
            return [1, 1, 0]
    else:
        theta_list = theta_str

    if not isinstance(theta_list, list):
        return [90, -90]

    result = []
    for item in theta_list:
        if isinstance(item, list):
            if len(item) == 2:
                result.append([int(item[0]), int(item[1])])
        else:
            result.append(int(item))

    return result if result else [1, 1, 0]


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
    df = pd.read_csv(defaultTree)
    row = df[df["key"] == key]
    return row


import numpy as np


def routeToCoordinates(route):
    # converts a list of the string names of the points to a list of coordinates by looking up csv
    # Filter out MoveArm instructions
    route_points = [p for p in route]
    n = len(route_points)

    if n == 0:
        return np.empty((0, 4), dtype=np.float64)

    coords = np.empty((n, 4), dtype=np.float64)

    for i, key in enumerate(route_points):
        if isinstance(key, MoveArm):
            # skip it cause move arm shouldnt have coords (should stay the same)
            continue
        # print(key)
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


class MoveArm():
    def __init__(self, start_orient, end_orient):
        self.curr = start_orient
        self.end = end_orient

    def __repr__(self):
        return f"Move arm from {self.curr} to {self.end}"


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
    rt = buildGantree.buildGantree("curr_gantry.csv")
    route = rt.traverseWithOrientation("Write", "Storage", 0, 0)
    print(route)
    print(routeToCoordinates(route))