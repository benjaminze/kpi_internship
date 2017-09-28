# -*- coding: utf-8 -*-
"""
This module creates text-files.
Input: filename, device_idn, table
returns string
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
        
        # open file
        file = open(self.filename, 'w')
        
        # write IDN
        file.write( 'IDN: '+ self.idn + ' \n')
        
        # get table size
        row_count       = self.table.rowCount()
        column_count    = self.table.columnCount()
        
        # check if table contains data
        if row_count < 1:
            return "No Data!"
        else:
            # get length of table entries
            length_of_data = self.GetLengthOfEntries(row_count,column_count)
            
            
            # write table header
            for column in range(column_count):
                header_name = self.table.horizontalHeaderItem(column).text()
                header_len  = len(header_name)
                nr_spaces   = 4 + length_of_data[column] - header_len
                header      = '{}{}'.format(header_name,' '*nr_spaces)
                file.write(header)
            
            # write table content
            for row in range(row_count):
                file.write('\n')            
                for column in range(column_count):
                    content     = self.table.item(row, column).text()                
                    file.write('{}{}'.format(content, ' '*4))
                    
            # close file
            file.close()
            return "Data saved!"
        
        
    def GetLengthOfEntries(self, row_count, column_count):
        
        # get length of data n the first row
        # it is enough to check the first because all following rows have the same layout
        length_of_data = [0]*column_count
        for column in range(column_count):
            length_of_data[column] = len(self.table.item(0, column).text())
        
        return length_of_data