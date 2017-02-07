import csv
import os
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from uncertainties import ufloat, unumpy as unp
from scipy.optimize import curve_fit


from tsv_scans.playing_with_plots import TSV_res_meas_analysis as TSV



class LfCMOSplot(object):
    
    def __init__(self):
        self.TSV = TSV()
        self.outformat = 'pdf'
    
    def load_file(self,path):
            if not os.path.split(path)[1].split('.')[1] == 'csv':
                raise IOError('Wrong filetype!')
            self.dirpath = os.path.split(path)[0]
            self.outfile = os.path.join(os.path.split(path)[0], (os.path.split(path)[1].split('.')[0]))
            self.title = os.path.split(path)[1].split('-')[0]
            
            self.f = os.path.split(path)[1]    
                    
            x,y = [], []
            with open(path, 'rb') as datafile:
                linereader = csv.reader(datafile, delimiter=',', quotechar='"')
                _ = linereader.next()
                frow = linereader.next()

                x.append(float(frow[0]))
                y.append(float(frow[1]))
                for row in linereader:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
    
            return x, y
    
    
    def load_file_err(self,path):
            if not os.path.split(path)[1].split('.')[1] == 'csv':
                raise IOError('Wrong filetype!')
            self.dirpath = os.path.split(path)[0]
            self.outfile = os.path.join(os.path.split(path)[0], (os.path.split(path)[1].split('.')[0]))
            self.title = os.path.split(path)[1].split('-')[0]
            
            self.f = os.path.split(path)[1]    
                
            
            x,y =     [], []
            xerr = 0.0002 + 0.0005
            yerr = 0.0005 + 0.0005
            xrel = 0.0012
            yrel = 0.003
            with open(path, 'rb') as datafile:
                linereader = csv.reader(datafile, delimiter=',', quotechar='"')
                _ = linereader.next()
                frow = linereader.next()
                
                ''' introducing syst. uncertainties here: voltage: 0.12 % + 200microV , current: 0.3 % + 500microA
                    for std_dev one stepsize (500micro and 500microA) has been estimated
                '''
    
                x.append(ufloat(frow[0], float(abs(float(frow[0])))*xrel + xerr))
                y.append(ufloat(frow[1], float(abs(float(frow[1])))*yrel + yerr))
                for row in linereader:
                    x.append(ufloat(row[0], float(abs(float(row[0])))*xrel + xerr))
                    y.append(ufloat(row[1], float(abs(float(row[1])))*yrel + yerr))
    
            return x, y
        
    
    def plot_IV_curve(self,x,y,fit,logy):
#         voltage, voltage_std_dev = self.TSV.unpack_uncertainties(x)
#         current, current_std_dev = self.TSV.unpack_uncertainties(y)
        
        plt.clf()
        title = ' IV curve'  
        
        plt.ylabel('Current [$\mathrm{\mu A}$]')
        plt.xlabel('Voltage [V]')
        plt.grid()

        voltage = np.absolute(x)
        current = np.absolute(y)* 1e6
        
        if not logy:
            plt.xlim(0,1.1*np.amax(voltage))     
            plt.ylim(0,1.1*np.amax(current))
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        
        if fit:
            title = ' IV curve fit'
            p, covariance =  curve_fit(self.TSV.fitfunction_line, voltage, current, p0=(0,0))
            plt.plot(voltage, current, 'b.', markersize = 8,label = 'data')
            dummy = np.linspace(min(voltage), max(voltage), 100)
            textstr=('m = %.3f \n b = %.5f' %(p[0],p[1]))
            plt.plot(dummy, self.TSV.fitfunction_line(dummy, *p),'r-', linewidth = 1.2, label = 'fit \n'+ textstr)

            print 'covariance: %r' % (np.sqrt(np.diag(covariance)))
            print 'fit: %r' % p
            name = 'fit'
        elif logy:
            plt.semilogy(voltage, current, '.-', label='data')            
            name = 'plot-LOG'
        else:
            plt.plot(voltage, current, 'b.', markersize = 8,linestyle ='-',label = 'data')  
            name = 'plot'
#         plt.errorbar(x, y, yerr=e, fmt=None)
#         box = AnchoredText('m = %.3f \n b = %.5f' %(p[0],p[1]), bbox_to_anchor=(1,1),loc=1)
#         ax = plt.axes()
#         ax.text(0.1, round(((ax.get_ylim()[1] + ax.get_ylim()[0])/2), 0), textstr, bbox=dict(boxstyle='square', facecolor='white'))
#         ax.add_artist(box)
#         plt.errorbar(voltage,current, voltage_std_dev, current_std_dev, 'b.', markersize = 3, errorevery = 5,label = 'data')
#         plt.draw()
#         loc = leg.get_window_extent().inverse_transformed(ax.transAxes)
#         loc = leg.get_frame().get_bbox().bounds
#         print loc
#         leg_height = loc.p1[1]-loc.p1[0]
#         print leg_height
#         textbox = ax.text(-loc.p0[0]-0.05,-loc.p0[1]-0.05, textstr, bbox=dict(boxstyle='square', facecolor='white'))
        plt.title(self.title + title)
        plt.legend(loc = 'best', numpoints = 1)
        plt.savefig(self.outfile + '-IV-'+ name + '.'+ self.outformat)
        plt.show()
        
if __name__ == '__main__':
    
    workdir = '/media/niko/data/LfPassiveCMOS/LFCMOS-x-4/IVscans'
    f = 'LFCMOS-x-4R-10V.csv'
    
    os.chdir(workdir)
    
    t = LfCMOSplot()
    x,y = t.load_file(os.path.join(workdir,f))
    t.plot_IV_curve(x, y, fit = False, logy = True)