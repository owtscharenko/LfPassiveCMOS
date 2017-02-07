import os
import csv
import time
import sys

from IV_loop import IV

# from tsv_scans.playing_with_plots import TSV_res_meas_analysis as TSV
from plot import LfCMOSplot as LF
from pybar.scans import scan_iv
# from uncertainties import ufloat, unumpy as unp

from basil.dut import Dut


if __name__ == '__main__':
    
    max_voltage = 400
    start_voltage = 1
    polarity = 1
    climit = 1e-6
    stepsize = 1
    device_path = '/home/niko/git/LfPassiveCMOS/devices.yaml'
    
    fragment = 'A'
    die = '1'
    structure = 'F'
    
    dut = Dut(device_path)
    dut.init()
    
    workdir = '/home/niko/Desktop/measurements/LFCMOS/Teststructures/Fragment-'+ fragment + '/die' + die + '/' + structure
    print 
    if not os.path.exists(workdir):
        os.mkdir(workdir)
    if not os.getcwd() == workdir:
        os.chdir(workdir)   
    if stepsize > 1:
        f = structure + '-normal-bias-big-steps' + str(max_voltage) + 'V.csv'
    else:
        f = structure + '-normal-bias-new-IVloop' + str(max_voltage) + 'V.csv'
    
    devices = {'central':dut['Sourcemeter']} #,'metal':dut['Sourcemeter2'],'backside':dut['Sourcemeter3']}
     
    iv = IV(devices = devices, max_current = climit, minimum_delay= 0.5)
    iv.scan_IV(f, min_Vin = start_voltage, max_Vin = max_voltage , polarity = polarity, stepsize = stepsize)
#    iv.scan_IV_small_steps(f, voltage,polarity,5000, stepsize)
#    iv.ramp_to(devices['central'], -50)
#    time.sleep(5)
#    iv.ramp_down()
    print 'output file written to: %s' % os.getcwd()
    t = LF()
    d = t.load_file(os.path.join(workdir,f))

    t.plot_IV_curve(d[0],d[1],fit=False,logy=True)
