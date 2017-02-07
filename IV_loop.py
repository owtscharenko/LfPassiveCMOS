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
    
    
    def __init__(self, devices, max_current, minimum_delay=0.5):

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


    def scan_IV(self, file_name, min_Vin, max_Vin, polarity, stepsize, *device):
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
                
                for x in range(min_Vin, max_Vin+1, stepsize):
                    input_voltage = x*polarity                     #loop over steps                                                                
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
            
        return file_name
    
    def scan_IV_small_steps(self, file_name, max_Vin, polarity, steps, stepsize, *device):
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
#                 print self.devices['central'].set_autorange()
                input = 0                                
                for x in range(0, steps):         #loop over steps                                                             
                    self.devices['central'].set_voltage(input*polarity)          #Set input current
                    self.devices['central'].on()
                    input_current = self.measure_current(self.devices['central'], 100)                             
                    input_voltage = self.measure_voltage(self.devices['central'], 100)
                    logging.info("Set input voltage to %r V" % input*polarity)
                    logging.info("Input current is %r A" % input_current)                              #Logging the readout
                    logging.info("Input voltage is %r V" % input_voltage)
#                     Writing readout in output file
                    self.data.append([input_voltage, input_current])                   #Writing readout in output file
                    f.writerow(self.data[-1])
                    pbar.update(input)
                    input += stepsize  
                    if abs(input_current) >= self.max_current:
                        print 'reached current limit of %f A! aborting' %self.max_current                                                                                                #Maximum values reached?
                        break
                    elif input >= max_Vin:
                        print 'reached maximum Voltage of %f V' % input
                        break
                pbar.finish()
                self.ramp_down()
                self.devices['central'].off()
                logging.info('Measurement finished, plotting ...')
                
        except Exception as e:
            logging.error(e)
            self.ramp_down()
            
        return file_name