# -*- coding: utf-8 -*-
"""This module imports data from existing textfile that was created by this program

Inputs: file, QTableWidget
returns device_idn
"""

from PyQt4 import QtGui
from plot_data import PlotData


class ImportFromTextfile(QtGui.QTableWidget):
    def __init__(self, file, table):
        self.file       = file
        self.table      = table
        
        
    
    def ImportData(self, plot_widget):
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
            nr              = current_line[0]
            datetime        = '{} {}'.format(current_line[1],current_line[2])
            data_channel_1  = current_line[3]
            data_channel_2  = current_line[4]
            
            # write to table
            self.table.setItem(row_count, 0, QtGui.QTableWidgetItem(nr))
            self.table.setItem(row_count, 1, QtGui.QTableWidgetItem(datetime))
            self.table.setItem(row_count, 2, QtGui.QTableWidgetItem(data_channel_1))
            self.table.setItem(row_count, 3, QtGui.QTableWidgetItem(data_channel_2))
            
            # plot data
            plot_widget.SetDataPoints(nr,[data_channel_1, data_channel_2])
#            self.table.scrollToBottom()
        
        self.table.resizeColumnsToContents()   
        
        device_idn = textlines[0].split()[1]
        
        return device_idn