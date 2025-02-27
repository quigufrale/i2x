# Copyright (C) 2023 Battelle Memorial Institute
# file: grid_upgrades.py
# from a saved HCA solution, estimates the limiting branch upgrades

import sys
import numpy as np
import i2x.bes_upgrades as bes
import json
import math

if __name__ == '__main__':
  bes.print_limiting_branches (results_file = 'hca_out.json', case_file = 'hca_case.m')

