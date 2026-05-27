import sys
import os
import random
import numpy as np
import warnings

# from benchmarks import *
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import src.active_learning as al

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_predictor():
    x_path = os.path.join(BASE_DIR, 'sampled_data', 'laser_parameters.txt')
    y_path = os.path.join(BASE_DIR, 'sampled_data', 'emissivity.txt')
    
    X_init = np.loadtxt(x_path)
    y_init = np.loadtxt(y_path)

    lb = np.array([0.2, 10, 15])
    ub = np.array([1.3, 700, 28])
    batch_size=8
    n_repeats=1
    sampler='lhs'

    directory = "sampled_data"
    file_path_subsys = os.path.join(BASE_DIR, directory, "required_subsystems.txt")
    with open(file_path_subsys, 'w') as f:
        for i in range(batch_size):
            f.write("Write Optical Keyence Dump\n")

    run = al.activeLearner(X_init, y_init, lb, ub,
                            batch_size, sampler).run(n_repeats)

    optimum_reached = True if True else False
    return optimum_reached

if __name__ == "__main__":
    run_predictor()