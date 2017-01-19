import os
import csv
import time

from IV_loop import IV

# from tsv_scans.playing_with_plots import TSV_res_meas_analysis as TSV
from plot import LfCMOSplot as LF
# from uncertainties import ufloat, unumpy as unp

from basil.dut import Dut




if __name__ == '__main__':
    
    voltage = 170
    climit = 1e-5
    stepsize = 5  
    device_path = '/home/niko/git/LfPassiveCMOS/devices.yaml'
    
    dut = Dut(device_path)
    dut.init()
    workdir = '/media/niko/data/LfPassiveCMOS/test'
    os.chdir(workdir)
    f = 'LFCMOS-170V.csv'
    
    devices = {'central':dut['Sourcemeter']} #,'metal':dut['Sourcemeter2'],'backside':dut['Sourcemeter3']}
    
    iv = IV(devices = devices, max_current = 15e-5)
#     iv.scan_tsv_res_VOLT(f, voltage,-1, stepsize)
    iv.ramp_to(devices['central'], -50)
#     time.sleep(20)
    iv.ramp_down()
#     t = LF()
#     d = t.load_file(os.path.join(workdir,f))
#     t.plot_IV_curve(d[0],d[1])
