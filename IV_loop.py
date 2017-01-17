import time
import logging
import csv
# import matplotlib.pyplot as plt
# import multiprocessing
import progressbar
import os.path

#from scan_misc import Misc 
# from basil.dut import Dut


class IV(object):
    
    
    def __init__(self, devices, max_current, minimum_delay=0.1):

        self.max_current = max_current
        self.minimum_delay = minimum_delay
        self.devices = devices
        self.data = []

    
    def get_device_type(self, device):
        type_arr = device.get_name().split(' ')
        for i, t in enumerate(type_arr):
            if t == u'KEITHLEY':
                vendor = 'keithley'
            if u'MODEL' in t:
                model = type_arr[i+1].split(',')[0]
        if not vendor or not model:
            raise RuntimeError('Could not determine device type!')
        typ = vendor + '_' + model
        return typ    
    
    
    def get_voltage_reading(self, device):
        typ = self.get_device_type(device)
        if typ == 'keithley_2410':
            return float(device.get_voltage().split(',')[0])
        elif typ == 'keithley_6517A':
            return float(device.get_voltage().split(',')[0][:-4])
        else:
            return float(device.get_voltage().split(',')[0])
    

    def get_current_reading(self, device):
        typ = self.get_device_type(device)
        if typ == 'keithley_2410':
            return float(device.get_current().split(',')[1])
        elif typ == 'keithley_6517A':
            return float(device.get_current().split(',')[0][:-4])
        else:
            return float(device.get_current().split(',')[1])
    
    
    def set_temp(self, polarity, temp):
        return

    
    def measure_current(self, device, timeout):
        
#         was_above = False
#         was_below = False
        
        current = float(device.get_current().split(',')[1])
        for i in range(timeout):
            time.sleep(self.minimum_delay)
            measurement = self.get_current_reading(device)
            if measurement < 1e-10 and i > 10:
                break
            if abs(abs(measurement) / abs(current) -1) <= 0.0001:
#                 print abs(abs(measurement) / abs(current) -1)
                break
#             if abs(measurement) > abs(current):
#                 was_above = True
#             if abs(measurement) < abs(current):
#                 was_below = True
#             if was_above and was_below:
#                 break
#             if round(measurement,7) == round(current,7):
#                 break
            current = measurement
        if i > 0 :
            print 'current cycles %i' %i     
        return measurement


    def measure_voltage(self, device, timeout):
        
#         was_above = False
#         was_below = False
        
        voltage = float(device.get_voltage().split(',')[0])
        for i in range(timeout):
            time.sleep(self.minimum_delay)
            measurement = self.get_voltage_reading(device)
            if abs(abs(measurement) / abs(voltage) -1) <= 0.0001:
#                 print abs(abs(measurement) / abs(voltage) -1)
                break
#             if abs(measurement) > abs(voltage):
#                 was_above = True
#             if abs(measurement) < abs(voltage):
#                 was_below = True
#             if was_above and was_below:
#                 break
#             if round(measurement,7) == round(voltage,7):
#                 break
            voltage = measurement
        if i > 0:
            print 'voltage cycles %i' %i    
        return measurement


    def ramp_down(self):
        logging.info('Ramping down all voltages...')
        done = {}
        for key in self.devices.keys():
            done[key] = False
            
        while True:
            for key in self.devices.keys():
                if self.get_device_type(self.devices[key]) == 'keithley_6517A':
                    done[key] = True
                    continue
                value = int(self.get_voltage_reading(self.devices[key]))
                if value != 0.0:
                    step = -1 if (value > 0) else 1
                    self.devices[key].set_voltage(value + step)
                else:
                    done[key] = True
            time.sleep(0.5)
            if all([dev for dev in done.itervalues()]):
                break


    def reset(self):
        self.data = []
        self.ramp_down()
        time.sleep(self.minimum_delay)


    def scan_tsv_res_VOLT(self, file_name, max_Vin, polarity, stepsize, *device):
        try:
            self.reset()  
            logging.info("Starting ...")              
#             self.devices['central'].on()    
            fncounter=1                                                 #creates output .csv
            while os.path.isfile( file_name):
                file_name = file_name.split('.')[0]
                file_name = file_name.split('_')[0]
                file_name = file_name + "_" + str(fncounter) + ".csv"
                fncounter = fncounter + 1
                              
            pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=max_Vin, poll=10, term_width=80).start()               #fancy progress bar
            with open(file_name , 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                    
                f.writerow(['Input voltage [V]', 'Input current [A]'])           #What is written in the output file
                                                                                     
                for x in range(0, max_Vin+1, stepsize):                          #loop over steps                                                                
                    self.devices['central'].set_voltage(x*polarity)          #Set input current
                    self.devices['central'].on()                             
                    input_voltage = self.measure_voltage(self.devices['central'], 100)
                    #self.dut['Sourcemeter'].on()
                    input_current = self.measure_current(self.devices['central'], 100)    
                    logging.info("Set input voltage to %r V" % x*polarity)
                    logging.info("Input current is %r A" % input_current)                              #Logging the readout
                    logging.info("Input voltage is %r V" % input_voltage)
#                     Writing readout in output file
#                     if input_current > 0 :
                    self.data.append([input_voltage, input_current])                   #Writing readout in output file
                    f.writerow(self.data[-1])
#                     elif input_current < 0:
#                         print'warning: outside range! current = %f' % input_current
                    pbar.update(x)  
                    if abs(input_current) >= self.max_current:
                        print 'reached current limit of %f A! aborting' %self.max_current                                                                                                #Maximum values reached?
                        break
                pbar.finish()
                self.ramp_down()
                self.devices['central'].off()
                logging.info('Measurement finished, plotting ...')
                
        except Exception as e:
            logging.error(e)
            self.ramp_down()
            
        return file_name