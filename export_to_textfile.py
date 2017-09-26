# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 12:33:13 2017

This module creates text-files.
Input: filename, device_idn, table
"""
from PyQt4 import QtGui

## add checkbos with two channels
## second channel in table at same time
## nr of measurement (in exportfile)
##
class ExportToTextfile(QtGui.QTableWidget):
    def __init__(self, filename, device_idn, table):
        self.filename   = filename + '.txt'
        self.idn        = device_idn
        self.table      = table
        
    def WriteToFile(self):
  
        file = open(self.filename, 'w')

        file.write( 'IDN: '+ self.idn + ' \n' 
        + 'All measurement data in [V] \n')

        row_count       = self.table.rowCount()
        column_count    = self.table.columnCount()
        content         = ''
        for row in range(row_count):
            file.write('\n')            
            for column in range(column_count):
                content = self.table.item(row, column).text()                
                file.write(content + '    ')
                
                
        file.close()
        print('Data successfully saved to file')