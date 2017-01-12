import os
import csv
from tsv_scans.measurement_loop import IV as iv



if __name__ == '__main__':
    
    voltage = 70
    climit = 0.00001
    stepsize = 1
    
    device = '/home/niko/git/LfPassiveCMOS/devices.yaml'
    workdir = '/media/niko/data/LfPassiveCMOS/test'
    
    
    iv(device).scan_tsv_res_VOLT(workdir, voltage, climit, 5000, stepsize)
    