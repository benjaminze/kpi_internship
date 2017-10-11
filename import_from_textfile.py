# -*- coding: utf-8 -*-
"""This module imports data from existing textfile that was created by this program

Inputs: file, QTableWidget
returns device_idn
"""

from PyQt4 import QtGui
from collections import OrderedDict
#from measurementGUI import WriteToPlotWidget
from utils import WriteToPlotWidget

class ImportFromTextfile(QtGui.QTableWidget, QtGui.QGraphicsView):
    def __init__(self, file, table, plot_widget):
        self.file           = file
        self.table          = table
        self.plot_widget    = plot_widget 
        
    
    def ImportData(self):
         # split text in lines
        textlines       = self.file.read().splitlines()
        
        # clear table and set columnCount
        self.table.    setRowCount(0)
        self.table.    setColumnCount(4)
        
        # enable horzontal header and hide vertical header
        self.table.verticalHeader().   setVisible(False)
        self.table.horizontalHeader(). setVisible(True )
        
        # write header to table
        headers = textlines[2].split()
        for i,header in enumerate(headers):
            self.table.setHorizontalHeaderItem(i, QtGui.QTableWidgetItem(header))
        
        
        # split lines in columns
        for line in textlines[3:]:
            current_line = line.split()            
            
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            
            # read values
            table_conent = OrderedDict([ ('nr',             current_line[0]),
                                 ('datetime',       '{} {}'.format(current_line[1],current_line[2])),
                                 ('data_channel_1', current_line[3]),
                                 ('data_channel_2', current_line[4])])
            
#            nr              = current_line[0]
#            datetime        = '{} {}'.format(current_line[1],current_line[2])
#            data_channel_1  = current_line[3]
#            data_channel_2  = current_line[4]
            
            # write to table
#            self.table.setItem(row_count, 0, QtGui.QTableWidgetItem(nr))
#            self.table.setItem(row_count, 1, QtGui.QTableWidgetItem(datetime))
#            self.table.setItem(row_count, 2, QtGui.QTableWidgetItem(data_channel_1))
#            self.table.setItem(row_count, 3, QtGui.QTableWidgetItem(data_channel_2))
            
            for i,key in enumerate(table_conent):
                self.table.setItem(row_count, i, QtGui.QTableWidgetItem(table_conent[key]))
             
            # plot data
            WriteToPlotWidget(self.plot_widget,table_conent['nr'],[table_conent['data_channel_1'], table_conent['data_channel_2']])
#            self.table.scrollToBottom()
        
        self.table.resizeColumnsToContents()   
        
        device_idn = textlines[0].split()[1]
        
        return device_idn
        
        
#    def WriteToPlotWidget(self, nr, data_to_plot, channel=None, time=None, symbol_channel_1 = 'o', symbol_channel_2 = 'x'):
#        
#        nr      = [int(nr)]        
#        #  check if both channels were used
#        if channel == 1:
#            self.plot_widget.plot(nr ,[float(data_to_plot)],     symbol = symbol_channel_1)
#        elif channel == 2:
#            self.plot_widget.plot(nr, [float(data_to_plot)],     symbol = symbol_channel_2)
#        else:
#            if len(data_to_plot[0]) == 1:
#                self.plot_widget.plot(nr, [float(data_to_plot[1])],  symbol = symbol_channel_2)
#            elif len(data_to_plot[1]) == 1:
#                self.plot_widget.plot(nr, [float(data_to_plot[0])],  symbol = symbol_channel_1)
#            else:
#                self.plot_widget.plot(nr, [float(data_to_plot[0])],  symbol = symbol_channel_1)
#                self.plot_widget.plot(nr, [float(data_to_plot[1])],  symbol = symbol_channel_2)