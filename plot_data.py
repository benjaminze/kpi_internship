# -*- coding: utf-8 -*-
"""
Create PlotWidget and plot data points to widget
"""
from PyQt4 import QtGui
import pyqtgraph as pg

class PlotData(QtGui.QApplication):
    def __init__(self, symbol_channel_1 = 'o', symbol_channel_2 = 'x'):
        # create PlotWidget       
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.show()        
        
        
        self.symbol_channel_1 = symbol_channel_1
        self.symbol_channel_2 = symbol_channel_2
        
        
    
    def SetDataPoints(self, nr, data_to_plot, channel=None, time=None):
        
        nr      = [int(nr)]        
        #  check if both channels were used
        if channel == 1:
            self.plot_widget.plot(nr ,[float(data_to_plot)],     symbol = self.symbol_channel_1)
        elif channel == 2:
            self.plot_widget.plot(nr, [float(data_to_plot)],     symbol = self.symbol_channel_2)
        else:
            if len(data_to_plot[0]) == 1:
                self.plot_widget.plot(nr, [float(data_to_plot[1])],  symbol = self.symbol_channel_2)
            elif len(data_to_plot[1]) == 1:
                self.plot_widget.plot(nr, [float(data_to_plot[0])],  symbol = self.symbol_channel_1)
            else:
                self.plot_widget.plot(nr, [float(data_to_plot[0])],  symbol = self.symbol_channel_1)
                self.plot_widget.plot(nr, [float(data_to_plot[1])],  symbol = self.symbol_channel_2)
    
    def Close(self):
        self.plot_widget.close()
        