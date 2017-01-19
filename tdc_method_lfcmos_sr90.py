# Script implementing the charge reconstruction of charged particles via the TDC method.
# All measurement (tuning, calibration) + analysis (tdc selection, landau fitting) steps are included here.

import numpy as np

import time

from basil.dut import Dut
from pybar.run_manager import RunManager, run_status  # importing run manager
from pybar.scans.scan_init import InitScan
from pybar.scans.scan_digital import DigitalScan
from pybar.scans.scan_analog import AnalogScan
from pybar.scans.tune_fei4 import Fei4Tuning
from pybar.scans.tune_stuck_pixel import StuckPixelScan
from pybar.scans.scan_threshold_fast import FastThresholdScan
from pybar.scans.tune_noise_occupancy import NoiseOccupancyScan
from pybar.scans.calibrate_hit_or import HitOrCalibration
from pybar.scans.scan_ext_trigger import ExtTriggerScan

from pybar.fei4.register_utils import make_box_pixel_mask_from_col_row

#from IVcurve import IVScan
from IV_loop import IV

import os

if __name__ == "__main__":
    
    os.chdir('/media/niko/data/LfPassiveCMOS/test/FE-test')
    
    #   Tuning
    target_threshold_plsr_dac = 20
    target_charge_plsr_dac = 270
    target_tot = 8
    
    max_bias = -55 #bias voltage for sensor
    
    # Select only AC pixels without edge pixels
    col_span = [2, 7]
    row_span = [336 - 36 + 6, 336 - 5]
    tdc_pixel = make_box_pixel_mask_from_col_row(column=[col_span[0], col_span[1]], row=[row_span[0], row_span[1]])  # edge pixel are not used in analysis

    runmngr = RunManager('configuration.yaml')
  
    runmngr.run_run(run=InitScan)  # to be able to set global register values
#   
#     # FE check and tuning
    runmngr.run_run(run=DigitalScan)
    runmngr.run_run(run=AnalogScan)  # Heat up the Fe a little bit for PlsrDAC scan
#   
#     # Deduce charge in PlsrDAC from PlsrDAC calibration
#   
#   
#     # Manual threshold tuning since fast binary search does not converge
    runmngr.run_run(run=Fei4Tuning, run_conf={'target_threshold': target_threshold_plsr_dac,
                                              'target_tot': target_tot,
                                              'target_charge': target_charge_plsr_dac,
                                              'gdac_tune_bits': range(8, -1, -1)},
                    catch_exception=True)
    runmngr.run_run(run=AnalogScan, run_conf={'scan_parameters': [('PlsrDAC', target_charge_plsr_dac)],
                                              'mask_steps': 3})
    runmngr.run_run(run=FastThresholdScan, run_conf={'mask_steps': 3})
     
    runmngr.run_run(run=StuckPixelScan)
     
    runmngr.run_run(run=NoiseOccupancyScan, run_conf={'occupancy_limit': 0.0001, 'n_triggers': 10000000})  # high occupancy limit to work with strong Sr-90 source
   
#     # TDC calibration
    plsr_dacs = [target_threshold_plsr_dac, 23, 26, 30, 35, 40, 50, 60, 70, 80, 100, 120, 150, 200, 250, 300, 400, 600, 800]  # PlsrDAC range for TDC calibration, should start at threshold
      
    runmngr.run_run(run=HitOrCalibration, run_conf={'reset_rx_on_error': True,
                                                    "pixels": (np.dstack(np.where(tdc_pixel == 1)) + 1).tolist()[0],
                                                    'n_injections': 200,
                                                    "scan_parameters": [('column', None),
                                                                        ('row', None),
                                                                        ('PlsrDAC', plsr_dacs)]
                                                    })
 
 
 
    dut = Dut('devices-noFE.yaml')
    dut.init()
    device = {'one':dut['Sourcemeter']}

    iv = IV(devices = device, max_current = 15e-5)
#     iv_measurement = IVScan(devices)
    iv.ramp_to(device['one'], max_bias)
    for bias in range(max_bias, -50, 5):
        runmngr = RunManager('configuration.yaml')
        time.sleep(1)
        runmngr.run_run(run=InitScan)
        # Enable few DC columns only to avoid noise hits
        runmngr.current_run.register.set_global_register_value("DisableColumnCnfg", 618475290623)  # 0b1000111111111111111111111111111111111111
        # AC pixel
        runmngr.current_run.register.set_pixel_register_value('Enable', tdc_pixel)
        # Ramp voltage
        device['one'].set_voltage(bias)
        mv = iv.get_voltage_reading(device['one']) #iv_measurement.set_voltage(bias)
        print mv
        time.sleep(5)
        # Deactivate noisy pixel
        status = runmngr.run_run(run=NoiseOccupancyScan, run_conf={'occupancy_limit': 0.00005,
                                                                   'n_triggers': 100000,
                                                                   "overwrite_enable_mask": True,  # Reset enable mask
                                                                   "use_enable_mask_for_imon": True,
                                                                   "overwrite_mask": True})
 
        if status != run_status.finished:
            raise RuntimeError('Noise occupancy scan failed, please check')
 
#         runmngr.run_run(run=NoiseOccupancyScan, run_conf={'occupancy_limit': 0.00005,
#                                                           'n_triggers': 2000000,
#                                                           "overwrite_enable_mask": False,
#                                                           "use_enable_mask_for_imon": True,
#                                                           "overwrite_mask": False})
 
        # runmngr.run_run(run=StuckPixelScan)

        # Scintillator trigger source scan
        imon_mask = tdc_pixel ^ 1  # imon mask = not enable mask
        runmngr.current_run.register.set_pixel_register_value("Imon", imon_mask)  # remember: for the selection later index 0 == colum/row 1
 
        runmngr.run_run(run=ExtTriggerScan, run_conf={'comment': 'Sr-90, 20C, V %d, V_IST %1.2f' % (bias, mv),
                                                      'col_span': col_span,
                                                      'row_span': row_span,
                                                      "use_enable_mask_for_imon": False,
                                                      "enable_tdc": True,
                                                      "trigger_delay": 6,
                                                      "trigger_rate_limit": 1000,
                                                      "trigger_latency": 232,
                                                      "trig_count": 0,
                                                      "scan_timeout": 60*60,
                                                      "no_data_timeout": 20,
                                                      'reset_rx_on_error': True,
                                                      "max_triggers": 1000000000})
    iv.ramp_to(device['one'], max_bias)  #iv_measurement.set_voltage(-150)
    
    runmngr.run_run(run=HitOrCalibration, run_conf={'reset_rx_on_error': True,
                                                "pixels": (np.dstack(np.where(tdc_pixel == 1)) + 1).tolist()[0],
                                                'n_injections': 200,
                                                "scan_parameters": [('column', None),
                                                                    ('row', None),
                                                                    ('PlsrDAC', plsr_dacs)]
                                                })
    iv.ramp_down()
    last_voltage = iv.get_voltage_reading(device['one'])
    print 'Bias voltage is %f V' %last_voltage
    if abs(last_voltage) <= 5:
        device['one'].off()
        print 'script finished'
    else:
        print 'Sourcemeter is not off, bias voltage > 2V'