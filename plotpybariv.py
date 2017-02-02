import numpy as np
import tables as tb
import logging
import os
import matplotlib.pyplot as plt
import time



if __name__ == "__main__":


    os.chdir('/media/niko/data/LfPassiveCMOS/LFCMOS3/IVscans')
    with tb.open_file('21_lfcmos03with0ohmbiasr_iv_scan' + '.h5' , 'r+') as in_file_h5: # , tb.open_file('15_lfcmos03with0ohmbiasr_iv_scan.h5' , 'r+') as in_file_h5_2 :
        data = in_file_h5.root.IV_data[:]
        #data_2 = in_file_h5_2.root.IV_data[:]
            # Plot and fit result
        x, y = np.absolute(data['voltage']), np.absolute(data['current']) * 1e6
        plt.clf()
#             plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.semilogy(x, y, '.-', label='data')
        plt.title('IV curve')
        plt.ylabel('Current [uA]')
        plt.xlabel('Voltage [V]')
        plt.grid(True)
        plt.legend(loc=0)
        plt.savefig('blub.pdf')
            
