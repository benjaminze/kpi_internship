# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 12:15:44 2017

@author: 101
"""
from PyQt4 import QtGui


def LayoutPlotWidget(plot_widget, x_label = 'x', y_label = 'y'):
#    plot_widget.setWindowTitle('Measurement Plot')
#    plot_widget.plot(title="Measurement Plot")
#    plot_widget.plot(xlabel=x_label)
    
    
    pass
def WriteToPlotWidget(plot_widget, nr, data_to_plot, channel=None, time=None, symbol_channel_1 = 'o', symbol_channel_2 = 'x'):
        
    nr      = [int(nr)]        
    #  check if both channels were used
    if channel == 1:
        plot_widget.plot(nr ,[float(data_to_plot)],     symbol = symbol_channel_1)
    elif channel == 2:
        plot_widget.plot(nr, [float(data_to_plot)],     symbol = symbol_channel_2)
    else:
        if len(data_to_plot[0]) == 1:
            plot_widget.plot(nr, [float(data_to_plot[1])],  symbol = symbol_channel_2)
        elif len(data_to_plot[1]) == 1:
            plot_widget.plot(nr, [float(data_to_plot[0])],  symbol = symbol_channel_1)
        else:
            plot_widget.plot(nr, [float(data_to_plot[0])],  symbol = symbol_channel_1)
            plot_widget.plot(nr, [float(data_to_plot[1])],  symbol = symbol_channel_2)
            
            
#%% CLASSES
            
#class Progressbar(QtGui.QProgressBar)