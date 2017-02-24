import time
import logging
import csv
# import matplotlib.pyplot as plt
# import multiprocessing
import progressbar
import os.path
import numpy as np

from pybar.daq.fei4_raw_data import open_raw_data_file
#from scan_misc import Misc 
# from basil.dut import Dut


class IV(object):
    
    
    def __init__(self, devices, filename, polarity, max_current, min_Vin, max_Vin, stepsize, minimum_delay):

        self.max_current = max_current
        self.minimum_delay = minimum_delay
        self.devices = devices
        self.data = []
        self.max_Vin = max_Vin
        self.min_Vin = min_Vin
        self.stepsize = stepsize
        self.file_name = filename
        self.polarity = polarity
        self.voltages = np.arange(min_Vin, max_Vin, stepsize).tolist()
    
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

        current = float(device.get_current().split(',')[1])
        for i in range(timeout):
            time.sleep(self.minimum_delay)
            measurement = self.get_current_reading(device)

           # if abs(measurement) < 5e-9 and i > 2:
            #    break
            if abs(measurement) <= abs(current):
                break
            #if abs(abs(measurement) / abs(current) -1) <= 0.01:
#                 print abs(abs(measurement) / abs(current) -1)
             #   break
            current = measurement
        if i > 0 :
            print 'current cycles %i' %i
        if i == timeout - 1:  # true if the leakage always increased
            raise RuntimeError('Leakage current is not stable')     
        return measurement


    def measure_voltage(self, device, timeout):
        
        voltage = float(device.get_voltage().split(',')[0])
        for i in range(timeout):
            time.sleep(self.minimum_delay)
            measurement = self.get_voltage_reading(device)
            if abs(abs(measurement) / abs(voltage) -1) <= 0.01:
#                 print abs(abs(measurement) / abs(voltage) -1)
                break
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
                if value != 0.0 and abs(value) <= 10:
                    step = -1 if (value > 0) else 1
                    self.devices[key].set_voltage(value + step)
                elif abs(value) > 10:
                    step = -3 if (value > 0) else 3
                    self.devices[key].set_voltage(value + step)
                elif abs(value) > 100:
                    step = -5 if (value > 0) else 5
                    self.devices[key].set_voltage(value + step)
                else:
                    done[key] = True
            time.sleep(0.5)
            if all([dev for dev in done.itervalues()]):
                logging.info('finished ramping down')
                break
    
    def ramp_to(self, dev, max_value):
        logging.info('Ramping voltage to %1.0fV...' % max_value)
        value = int(round(self.get_voltage_reading(dev)))
        if max_value > value:
            step = 1
        else:
            step = -1
        
        while True:
            value = int(round(self.get_voltage_reading(dev)))
            if value != max_value:
                dev.set_voltage(value + step)
            else:
                logging.info('Ramping done. Last value was %i' % value)
                break
    

    def reset(self):
        self.data = []
        self.ramp_down()
        time.sleep(self.minimum_delay)


    def scan_IV(self):
        try:
            self.reset()  
            logging.info("Starting ...")              
#             self.devices['central'].on()    
            fncounter=1                                                 #creates output .csv
            while os.path.isfile( self.file_name):
                self.file_name = self.file_name.split('.')[0]
                self.file_name = self.file_name.split('_')[0]
                self.file_name = self.file_name + "_" + str(fncounter) + ".csv"
                fncounter = fncounter + 1
                              
            pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=self.max_Vin, poll=10, term_width=80).start()               #fancy progress bar
            with open(self.file_name , 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                f.writerow(['Input voltage [V]', 'Input current [A]'])           #What is written in the output file
                
                for x in range(self.min_Vin, self.max_Vin+1, self.stepsize):
                    input_voltage = x*self.polarity                     #loop over steps                                                                
                    self.devices['central'].set_voltage(input_voltage)
                    time.sleep(self.minimum_delay)          #Set input current
                    self.devices['central'].on()
                    input_current = self.measure_current(self.devices['central'], 50)                             
#                    input_voltage = self.measure_voltage(self.devices['central'], 50)
                    logging.info("Set input voltage to %r V" % input_voltage)
                    logging.info("Input current is %r A" % input_current)                              #Logging the readout
                    self.data.append([input_voltage, input_current])                   #Writing readout in output file
                    f.writerow(self.data[-1])
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
            
        return self.file_name
    
    def scan_IV_small_steps(self):
        try:
            self.reset()  
            logging.info("Starting ...")              
#             self.devices['central'].on()    
            fncounter=1                                                 #creates output .csv
            while os.path.isfile( self.file_name):
                self.file_name = self.file_name.split('.')[0]
                self.file_name = self.file_name.split('_')[0]
                self.file_name = self.file_name + "_" + str(fncounter) + ".csv"
                fncounter = fncounter + 1
                              
            pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=self.max_Vin, poll=10, term_width=80).start()               #fancy progress bar
            with open(self.file_name , 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                    
                f.writerow(['Input voltage [V]', 'Input current [A]'])           #What is written in the output file
#                 print self.devices['central'].set_autorange()
                input = 0                                
                for x in range(0, 500000):
                    input_voltage =  input*self.polarity        #loop over steps                                                             
                    self.devices['central'].set_voltage(input_voltage)          #Set input current
                    self.devices['central'].on()
                    input_current = self.measure_current(self.devices['central'], 50)                             
#                     input_voltage = self.measure_voltage(self.devices['central'], 100)
                    logging.info("Set input voltage to %r V" % input*self.polarity)
                    logging.info("Input current is %r A" % input_current)                              #Logging the readout
                    logging.info("Input voltage is %r V" % input_voltage)
#                     Writing readout in output file
                    self.data.append([input_voltage, input_current])                   #Writing readout in output file
                    f.writerow(self.data[-1])
                    pbar.update(input)
                    input += self.stepsize  
                    if abs(input_current) >= self.max_current:
                        print 'reached current limit of %f A! aborting' %self.max_current                                                                                                #Maximum values reached?
                        break
                    elif input >= self.max_Vin:
                        print 'reached maximum Voltage of %f V' % input
                        break
                pbar.finish()
                self.ramp_down()
                self.devices['central'].off()
                logging.info('Measurement finished, plotting ...')
                
        except Exception as e:
            logging.error(e)
            self.ramp_down()
            
        return self.file_name
    
    
    def scan_IV_h5(self):
        logging.info('Measure IV for V = %s' % self.voltages)
        description = [('voltage', np.float), ('current', np.float)]
        data = open_raw_data_file.h5_file.create_table(self.raw_data_file.h5_file.root, name='IV_data', description=np.zeros((1, ), dtype=description).dtype, title='Data from the IV scan')

        progress_bar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=len(self.voltages), term_width=80)
        progress_bar.start()

        for index, voltage in enumerate(self.voltages):
            if self.stop_run.is_set():
                break
#             if voltage > 0:
#                 RuntimeError('Voltage has to be negative! Abort to protect device.')
            if self.abort_run.is_set():
                break
            if abs(voltage) <= abs(self.max_Vin):
                self.dut['Sourcemeter'].set_voltage(voltage)
                self.actual_voltage = voltage
                time.sleep(self.minimum_delay)
            else:
                logging.info('Maximum voltage with %f V reached, abort', voltage)
                break
            current_string = self.dut['Sourcemeter'].get_current()
            current = float(current_string.split(',')[1])
            if abs(current) > abs(self.max_current):
                logging.info('Maximum current with %e I reached, abort', current)
                break
            logging.info('V = %f, I = %e', voltage, current)
            max_repeat = 50
            for i in range(max_repeat):  # repeat current measurement until stable (current does not increase)
                time.sleep(self.minimum_delay)
                actual_current = float(self.dut['Sourcemeter'].get_current().split(',')[1])
                if abs(actual_current) > abs(self.max_current):
                    logging.info('Maximum current with %e I reached, abort', actual_current)
                    break
                if (abs(actual_current) < abs(current)):  # stable criterion
                    break
                current = actual_current
            if i == max_repeat - 1:  # true if the leakage always increased
                raise RuntimeError('Leakage current is not stable')
            else:
                a = np.array([(voltage, current)], dtype=description)
                data.append(a)
            progress_bar.update(index)
        progress_bar.finish()
        data.flush()