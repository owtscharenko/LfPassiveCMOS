# Script to test the IBL irradiation R&D samples

from pybar.run_manager import RunManager  # importing run manager
from pybar.scans.scan_init import InitScan
from pybar.scans.test_register import RegisterTest
from pybar.scans.scan_digital import DigitalScan
from pybar.scans.scan_analog import AnalogScan
from pybar.scans.tune_fei4 import Fei4Tuning
from pybar.scans.tune_stuck_pixel import StuckPixelScan
from pybar.scans.scan_threshold_fast import FastThresholdScan
from pybar.scans.tune_noise_occupancy import NoiseOccupancyScan
import os


if __name__ == "__main__":   
    
    os.chdir('/media/niko/data/LfPassiveCMOS/test/FE-test')
    
    target_threshold = 55  # in PlsrDAC (assuming 1 PlsrDAC = 55 electrons)
    target_charge = 280  # in PlsrDAC (assuming 1 PlsrDAC = 55 electrons)
    target_tot = 8
  
    runmngr = RunManager('configuration.yaml')
    runmngr.run_run(run=InitScan)  # to be able to set global register values

    # FE check and tuning
    runmngr.run_run(run=RegisterTest)
    runmngr.run_run(run=DigitalScan)
    runmngr.run_run(run=AnalogScan)  # heat up the Fe a little bit for PlsrDAC scan
#                    
#     runmngr.run_run(run=Fei4Tuning, run_conf={'target_threshold': target_threshold,
#                                               'target_tot': target_tot,
#                                               'target_charge': target_charge},
#                     catch_exception=False)
#     runmngr.run_run(run=AnalogScan, run_conf={'scan_parameters': [('PlsrDAC', target_charge)]})
#     runmngr.run_run(run=FastThresholdScan)
#     runmngr.run_run(run=StuckPixelScan)
#     runmngr.run_run(run=NoiseOccupancyScan, run_conf={'occupancy_limit': 0,
#                                                       'n_triggers': 1000000})
