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
        
        # Write IDN
        file.write( 'IDN: '+ self.idn + ' \n')
        
        # get table size
        row_count       = self.table.rowCount()
        column_count    = self.table.columnCount()
        
        # Check if table contains data
        if row_count < 2:
            return "No Data!"
        else:
            # get length of table entries
            length_of_data = self.GetLengthOfEntries(row_count,column_count)
            
            
            # Write table header
            for column in range(column_count):
                header_name = self.table.item(0, column).text()
                header_len  = len(header_name)
                nr_spaces   = 4 + length_of_data[column] - header_len
                header      = '{0}{1}'.format(header_name,' '*nr_spaces)
                file.write(header)
            
            # Write table content
            for row in range(1, row_count):
                file.write('\n')            
                for column in range(column_count):
                    content     = self.table.item(row, column).text()                
                    file.write(content + '    ')
                    
                    
            file.close()
            return "Data saved!"
        
        
    def GetLengthOfEntries(self, row_count, column_count):
    
        length_of_data = [0]*column_count
        for column in range(column_count):
            length_of_data[column] = len(self.table.item(1, column).text())
        
        return length_of_data