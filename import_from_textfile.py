# -*- coding: utf-8 -*-
"""This module imports data from existing textfile that was created by this program

Inputs: file, QTableWidget
returns device_idn
"""

from PyQt4 import QtGui, QtCore
from collections import OrderedDict
#from measurementGUI import WriteToPlotWidget
from utils import WriteToPlotWidget

class ImportFromTextfile(QtGui.QTableWidget, QtGui.QGraphicsView):
    def __init__(self, file, table, plot_widget):
        self.file           = file
        self.table          = table
        self.plot_widget    = plot_widget 
               
        self.textlines = []
        self.first_row_table_content  = 3
        self.last_row_table_content   = 0 #changed in ImportData
        # timerImport for import
        self.timer_counter_import = self.first_row_table_content
        
         # clear table and set columnCount
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        
        # enable horizontal header and hide vertical header
        self.table.verticalHeader().   setVisible(False)
        self.table.horizontalHeader(). setVisible(True )        
        
    def ReadFile(self):
        
         # split text in lines
        self.textlines       = self.file.read().splitlines()
    
        # write header to table
        headers = self.textlines[2].split()
        for i,header in enumerate(headers):
            self.table.setHorizontalHeaderItem(i, QtGui.QTableWidgetItem(header))
        
        self.last_row_table_content = len(self.textlines)
  
    def GetDeviceIDN(self):    
        device_idn = self.textlines[0].split()[1]
        return device_idn
        
    def WriteToTableAndPlot(self):
            
            
        current_line = self.textlines[self.timer_counter_import].split()            
        
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        
        # read values
        table_conent = OrderedDict([ ('nr',             current_line[0]),
                                      ('datetime',       '{} {}'.format(current_line[1],current_line[2])),
                                       ('data_channel_1', current_line[3]),
                                        ('data_channel_2', current_line[4])])
        
        for i,key in enumerate(table_conent):
            self.table.setItem(row_count, i, QtGui.QTableWidgetItem(table_conent[key]))

        self.table.resizeColumnsToContents() 
        self.table.scrollToBottom()
        # plot data
        WriteToPlotWidget(self.plot_widget,table_conent['nr'],
                          [table_conent['data_channel_1'], table_conent['data_channel_2']])
#           self.table.scrollToBottom()
    
  
    
        self.timer_counter_import += 1
    
