import os
import csv
import time

from IV_loop import IV

# from tsv_scans.playing_with_plots import TSV_res_meas_analysis as TSV
from plot import LfCMOSplot as LF
# from uncertainties import ufloat, unumpy as unp

from basil.dut import Dut


if __name__ == '__main__':
    
    voltage = 10
    polarity = -1
    climit = 1e-4
    stepsize = 0.1 
    device_path = '/home/niko/git/LfPassiveCMOS/devices.yaml'
    
    dut = Dut(device_path)
    dut.init()
    workdir = '/media/niko/data/LfPassiveCMOS/LFCMOS-x-4/IVscans'
    os.chdir(workdir)
    f = 'LFCMOS-x-4L-100mV-steps-nocover-' + str(voltage) + 'V.csv'
    
    devices = {'central':dut['Sourcemeter']} #,'metal':dut['Sourcemeter2'],'backside':dut['Sourcemeter3']}
     
    iv = IV(devices = devices, max_current = climit, minimum_delay= 1)
#     iv.scan_IV(f, voltage,polarity, stepsize)
    iv.scan_IV_small_steps(f, voltage,polarity,5000, stepsize)
#    iv.ramp_to(devices['central'], -50)
#    time.sleep(5)
#    iv.ramp_down()
    t = LF()
    d = t.load_file(os.path.join(workdir,f))
    t.plot_IV_curve(d[0],d[1],fit=False,logy=True)
