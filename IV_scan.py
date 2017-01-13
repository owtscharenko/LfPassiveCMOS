import os
import csv

from IV_loop import IV

# from tsv_scans.playing_with_plots import TSV_res_meas_analysis as TSV
from plot import LfCMOSplot as LF
# from uncertainties import ufloat, unumpy as unp

from basil.dut import Dut



if __name__ == '__main__':
    
    voltage = 10
    climit = 1e-5
    stepsize = 1  
    device_path = '/home/niko/git/LfPassiveCMOS/devices.yaml'
    
    dut = Dut(device_path)
    dut.init()
    workdir = '/media/niko/data/LfPassiveCMOS/test'
    os.chdir(workdir)
    f = 'testvia.csv'
    
    devices = {'central':dut['Sourcemeter1']} #,'metal':dut['Sourcemeter2'],'backside':dut['Sourcemeter3']}
    
    print devices['central'].get_name()
#     iv = IV(devices = devices, max_current = 15e-5)
#     iv.scan_tsv_res_VOLT(f, voltage, climit, 5000, stepsize)
    t = LF()
    d = t.load_file(os.path.join(workdir,f))
    t.plot_IV_curve(d[0],d[1])