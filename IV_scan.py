import os
import csv
import time

from IV_loop import IV

# from tsv_scans.playing_with_plots import TSV_res_meas_analysis as TSV
from plot import LfCMOSplot as LF
# from uncertainties import ufloat, unumpy as unp

from basil.dut import Dut


if __name__ == '__main__':
    
    min_vin = 0
    max_vin = 50
    polarity = -1
    climit = 1e-6
    stepsize = 1 
    device_path = '/home/niko/git/LfPassiveCMOS/devices.yaml'
    
    dut = Dut(device_path)
    dut.init()
    workdir = '/media/niko/data/LfPassiveCMOS/LFCMOS-x-5/IVscans'
    os.chdir(workdir)
    f = 'test' + str(max_vin) + 'testtest.csv'
    
    devices = {'central':dut['Sourcemeter']} #,'metal':dut['Sourcemeter2'],'backside':dut['Sourcemeter3']}
     
    iv = IV(devices, f, polarity, climit, min_vin, max_vin, stepsize, minimum_delay= 1)
    filename = iv.scan_IV()
#     filename = iv.scan_IV_small_steps()

#    iv.ramp_to(devices['central'], -50)
#    time.sleep(5)
#    iv.ramp_down()
    t = LF()
    d = t.load_file(os.path.join(workdir,filename))
    t.plot_IV_curve(d[0],d[1],fit=False,logy=True)
