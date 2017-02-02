from IV_loop import IV
from basil.dut import Dut
import os
import time

if __name__ == "__main__":
    
    os.chdir('/media/niko/data/LfPassiveCMOS/test/FE-test')
    
    max_bias = -185 #bias voltage for sensor
#     
    dut = Dut('devices-noFE.yaml')
    dut.init()
    device = {'one':dut['Sourcemeter']}
# 
    iv = IV(devices = device, max_current = 1e-4)
    iv.ramp_down()
    device['one'].off()
#    iv.ramp_to(device['one'], max_bias)
    current = iv.get_current_reading(device['one'])*1000000
    voltage = iv.get_voltage_reading(device['one'])
    print 'current is %f microA' % current
    print 'voltage is %f V' % voltage